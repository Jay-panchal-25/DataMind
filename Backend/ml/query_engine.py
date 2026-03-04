import re
from difflib import get_close_matches

import pandas as pd


class QueryEngine:

    def __init__(self, df: pd.DataFrame):
        self.df = df

        # Map user words to pandas operations.
        self.operation_map = {
            "max": ["max", "maximum", "highest", "largest", "top"],
            "min": ["min", "minimum", "lowest", "smallest"],
            "mean": ["mean", "average", "avg"],
            "sum": ["sum", "total"],
            "count": ["count", "number"],
            "median": ["median"],
            "std": ["std", "standard deviation"],
            "var": ["variance"],
        }

        # Filter operator patterns: "column > value", "column == value", etc.
        self.filter_pattern = re.compile(
            r"([a-zA-Z0-9_]+)\s*(==|!=|>=|<=|>|<)\s*(['\"]?[a-zA-Z0-9_.]+['\"]?)"
        )
        self.filter_text_pattern = re.compile(
            r"([a-zA-Z0-9_]+)\s*"
            r"(greater than or equal to|less than or equal to|greater than|less than|not equal to|equal to|equals)"
            r"\s*(['\"]?[a-zA-Z0-9_.]+['\"]?)",
            re.IGNORECASE,
        )

        # Group by trigger words
        self.groupby_keywords = ["group by", "grouped by", "per", "by each", "for each"]

        # Operation keywords to exclude from column detection
        self._operation_words = {
            word
            for keywords in self.operation_map.values()
            for word in keywords
        }

    # ------------------------------------------------------------------ #
    #  Existing detection helpers                                         #
    # ------------------------------------------------------------------ #

    def detect_operation(self, query):
        query = query.lower()
        for op, keywords in self.operation_map.items():
            for word in keywords:
                if word in query:
                    return op
        return None

    def _collect_column_candidates(self, text, stop_words, col_lower_map):
        candidates = []

        for col in self.df.columns:
            col_lower = col.lower()
            if col_lower in stop_words:
                continue
            if re.search(rf"\b{re.escape(col_lower)}\b", text):
                candidates.append(col)

        query_tokens = re.findall(r"\b[a-zA-Z0-9_]+\b", text)
        filtered_tokens = [t for t in query_tokens if t not in stop_words]

        for token in filtered_tokens:
            if token in col_lower_map:
                col = col_lower_map[token]
                if col not in candidates:
                    candidates.append(col)

        if not candidates and filtered_tokens:
            best_match = get_close_matches(
                " ".join(filtered_tokens),
                list(col_lower_map.keys()),
                n=1,
                cutoff=0.7,
            )
            if best_match:
                candidates.append(col_lower_map[best_match[0]])

        return candidates

    def detect_column(self, query, operation=None, groupby=None, filters=None):
        query_lower = query.lower()
        filters = filters or []
        excluded = {c for c, _, _ in filters}
        if groupby:
            excluded.add(groupby)

        # Remove operation words and groupby keywords from token pool
        # so "average" doesn't partially match "age", "sum" doesn't match "summary" etc.
        stop_words = self._operation_words | {
             "per", "each", "for",
            "where", "and", "or", "the", "of", "in", "is",
            "what", "show", "me", "find", "get", "give",
        }

        col_lower_map = {col.lower(): col for col in self.df.columns}

        # Prefer metric segment before groupby/filter clauses.
        cut_points = []
        for kw in self.groupby_keywords + ["where", "filter", "only"]:
            idx = query_lower.find(kw)
            if idx != -1:
                cut_points.append(idx)
        metric_text = query_lower[:min(cut_points)] if cut_points else query_lower

        metric_candidates = self._collect_column_candidates(metric_text, stop_words, col_lower_map)
        all_candidates = self._collect_column_candidates(query_lower, stop_words, col_lower_map)
        candidates = metric_candidates + [c for c in all_candidates if c not in metric_candidates]

        for col in candidates:
            if col in excluded:
                continue
            if operation in {"mean", "sum", "median", "std", "var", "min", "max"}:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    return col
                continue
            return col

        # Fall back to any candidate if exclusion/numeric preference removed everything.
        for col in candidates:
            if col not in excluded:
                return col

        return None

    # ------------------------------------------------------------------ #
    #  New: filter detection                                              #
    # ------------------------------------------------------------------ #

    def detect_filter(self, query):
        """
        Detects filter conditions in the query.
        Returns a list of (column, operator, value) tuples, or [].

        Example: "where age > 30 and salary >= 50000"
          → [('age', '>', 30), ('salary', '>=', 50000)]
        """
        matches = self.filter_pattern.findall(query)
        filters = []
        op_phrase_map = {
            "greater than": ">",
            "less than": "<",
            "greater than or equal to": ">=",
            "less than or equal to": "<=",
            "equal to": "==",
            "equals": "==",
            "not equal to": "!=",
        }

        col_lower_map = {col.lower(): col for col in self.df.columns}

        for raw_col, op, raw_val in matches:
            col_key = raw_col.lower()

            # Match to actual dataframe column
            if col_key in col_lower_map:
                actual_col = col_lower_map[col_key]
            else:
                close = get_close_matches(col_key, list(col_lower_map.keys()), n=1, cutoff=0.7)
                if not close:
                    continue
                actual_col = col_lower_map[close[0]]

            # Strip surrounding quotes from value
            value = raw_val.strip("'\"")

            # Try numeric cast
            try:
                value = float(value)
                if value.is_integer():
                    value = int(value)
            except ValueError:
                pass  # keep as string

            filters.append((actual_col, op, value))

        # Natural language operators: "age greater than 30"
        text_matches = self.filter_text_pattern.findall(query)
        for raw_col, phrase, raw_val in text_matches:
            col_key = raw_col.lower()

            if col_key in col_lower_map:
                actual_col = col_lower_map[col_key]
            else:
                close = get_close_matches(col_key, list(col_lower_map.keys()), n=1, cutoff=0.7)
                if not close:
                    continue
                actual_col = col_lower_map[close[0]]

            op = op_phrase_map.get(phrase.lower())
            if not op:
                continue

            value = raw_val.strip("'\"")
            try:
                value = float(value)
                if value.is_integer():
                    value = int(value)
            except ValueError:
                pass

            item = (actual_col, op, value)
            if item not in filters:
                filters.append(item)

        return filters

    # ------------------------------------------------------------------ #
    #  New: group-by detection                                            #
    # ------------------------------------------------------------------ #

    def detect_groupby(self, query):
        """
        Detects a group-by column from natural language.
        Returns the column name string, or None.

        Example: "average salary group by department"  → 'department'
        """
        query_lower = query.lower()

        triggered = False
        trigger_end = -1

        for kw in self.groupby_keywords:
            idx = query_lower.find(kw)
            if idx != -1:
                triggered = True
                trigger_end = max(trigger_end, idx + len(kw))

        col_lower_map = {col.lower(): col for col in self.df.columns}

        # Fallback: support "by <column>" phrasing (e.g., "average salary by department")
        if not triggered:
            by_match = re.search(r"\bby\s+([a-zA-Z0-9_]+)\b", query_lower)
            if by_match:
                token = by_match.group(1)
                if token in col_lower_map:
                    return col_lower_map[token]
                close = get_close_matches(token, list(col_lower_map.keys()), n=1, cutoff=0.7)
                if close:
                    return col_lower_map[close[0]]
            return None

        # Look for a column name after the trigger keyword
        # but before any "where" clause
        remainder = query_lower[trigger_end:]

        # Stop at "where" so we don't pick up filter columns as groupby
        where_idx = remainder.find("where")
        if where_idx != -1:
            remainder = remainder[:where_idx]

        tokens = re.findall(r"\b[a-zA-Z0-9_]+\b", remainder)

        for token in tokens:
            if token in col_lower_map:
                return col_lower_map[token]

        # Fuzzy fallback
        if tokens:
            close = get_close_matches(tokens[0], list(col_lower_map.keys()), n=1, cutoff=0.7)
            if close:
                return col_lower_map[close[0]]

        return None

    # ------------------------------------------------------------------ #
    #  execute (filter + groupby wired in; core logic untouched)          #
    # ------------------------------------------------------------------ #

    def execute(self, query):

        operation = self.detect_operation(query)
        filters   = self.detect_filter(query)
        groupby   = self.detect_groupby(query)
        column    = self.detect_column(query, operation=operation, groupby=groupby, filters=filters)

        if operation is None:
            return "Operation not found"

        if column is None:
            return "Column not found"

        if column not in self.df.columns:
            return f"{column} not in dataframe"

        try:
            # 1. Apply filters first
            data = self.df.copy()
            applied_filters = []

            for col, op, val in filters:
                if col not in data.columns:
                    continue
                if   op == "==": data = data[data[col] == val]
                elif op == "!=": data = data[data[col] != val]
                elif op == ">":  data = data[data[col] >  val]
                elif op == ">=": data = data[data[col] >= val]
                elif op == "<":  data = data[data[col] <  val]
                elif op == "<=": data = data[data[col] <= val]
                applied_filters.append((col, op, val))

            # 2. Apply group-by if present
            if groupby:
                grouped = data.groupby(groupby)[column]
                op_map = {
                    "max":    grouped.max,
                    "min":    grouped.min,
                    "mean":   grouped.mean,
                    "sum":    grouped.sum,
                    "count":  grouped.count,
                    "median": grouped.median,
                    "std":    grouped.std,
                    "var":    grouped.var,
                }
                if operation not in op_map:
                    return "Unsupported operation"

                result = op_map[operation]().to_dict()

                return {
                    "operation": operation,
                    "column": column,
                    "groupby": groupby,
                    "filters": applied_filters,
                    "result": result,
                }

            # 3. No group-by — same as before
            op_map = {
                "max":    data[column].max,
                "min":    data[column].min,
                "mean":   data[column].mean,
                "sum":    data[column].sum,
                "count":  data[column].count,
                "median": data[column].median,
                "std":    data[column].std,
                "var":    data[column].var,
            }

            if operation not in op_map:
                return "Unsupported operation"

            result = op_map[operation]()

            return {
                "operation": operation,
                "column": column,
                "filters": applied_filters,
                "result": result,
            }

        except Exception as e:
            return str(e)
