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

    def detect_operation(self, query):
        query = query.lower()

        for op, keywords in self.operation_map.items():
            for word in keywords:
                if word in query:
                    return op

        return None

    def detect_column(self, query):
        query_lower = query.lower()
        query_tokens = re.findall(r"[a-zA-Z0-9_]+", query_lower)

        # Exact column name appears in query.
        for col in self.df.columns:
            if col.lower() in query_lower:
                return col

        # Exact token match to column name.
        for token in query_tokens:
            for col in self.df.columns:
                if token == col.lower():
                    return col

        # Fallback for slight misspellings.
        lower_to_original = {col.lower(): col for col in self.df.columns}
        best_match = get_close_matches(
            " ".join(query_tokens),
            list(lower_to_original.keys()),
            n=1,
            cutoff=0.7,
        )

        if best_match:
            return lower_to_original[best_match[0]]

        return None

    def execute(self, query):

        operation = self.detect_operation(query)
        column = self.detect_column(query)

        if operation is None:
            return "Operation not found"

        if column is None:
            return "Column not found"

        if column not in self.df.columns:
            return f"{column} not in dataframe"

        try:

            if operation == "max":
                result = self.df[column].max()

            elif operation == "min":
                result = self.df[column].min()

            elif operation == "mean":
                result = self.df[column].mean()

            elif operation == "sum":
                result = self.df[column].sum()

            elif operation == "count":
                result = self.df[column].count()

            elif operation == "median":
                result = self.df[column].median()

            elif operation == "std":
                result = self.df[column].std()

            elif operation == "var":
                result = self.df[column].var()

            else:
                return "Unsupported operation"

            return {
                "operation": operation,
                "column": column,
                "result": result,
            }

        except Exception as e:
            return str(e)
