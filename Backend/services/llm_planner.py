import re

from pydantic import BaseModel, Field

from services.llm_service import llm_service


class FilterSchema(BaseModel):
    column: str
    operator: str
    value: str | int | float | bool | None = None


class PlannerSchema(BaseModel):
    intent: str = "unknown"
    operations: list[str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    groupby: str | None = None
    chart_type: str | None = None
    target: str | None = None
    task_type: str | None = None
    prediction_inputs: dict[str, str | int | float | bool] = Field(
        default_factory=dict
    )
    filters: list[FilterSchema] = Field(default_factory=list)


class LLMPlanner:
    def __init__(self):
        self.system_prompt = """
You are DataMind Planner AI.

Extract a structured dataset plan from the user request.
Valid intents:
- analytics
- visualization
- prediction
- unknown

Rules:
- Use only the provided columns.
- For analytics, capture aggregate operations like max, min, mean, sum, count.
- For visualization, choose one chart type from bar, line, pie, scatter, histogram.
- For prediction, capture the target and feature inputs.
- If the request is vague or unrelated, return intent=unknown.
"""

    def _normalize_text(self, value: str):
        return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()

    def _match_columns(self, query: str, columns: list[str]):
        normalized_query = self._normalize_text(query)
        matched = []

        for column in columns or []:
            normalized_column = self._normalize_text(column)
            compact_column = normalized_column.replace(" ", "")

            if (
                normalized_column and normalized_column in normalized_query
            ) or (
                compact_column and compact_column in normalized_query.replace(" ", "")
            ):
                matched.append(column)

        return matched

    def _coerce_value(self, value):
        if value is None:
            return value

        if isinstance(value, bool | int | float):
            return value

        raw = str(value).strip().strip("'\"")

        if re.fullmatch(r"-?\d+", raw):
            return int(raw)

        if re.fullmatch(r"-?\d+\.\d+", raw):
            return float(raw)

        return raw

    def _extract_filters(self, query: str, columns: list[str]):
        filters = []

        for column in columns or []:
            escaped = re.escape(column)
            patterns = [
                (rf"{escaped}\s*(>=|<=|!=|==|>|<)\s*([^\s,]+)", None),
                (rf"{escaped}\s+is\s+([^\s,]+)", "=="),
                (rf"{escaped}\s+equals\s+([^\s,]+)", "=="),
            ]

            for pattern, forced_operator in patterns:
                match = re.search(pattern, query, flags=re.IGNORECASE)
                if not match:
                    continue

                if forced_operator is None:
                    operator, value = match.groups()
                else:
                    operator = forced_operator
                    value = match.group(1)

                filters.append(
                    {
                        "column": column,
                        "operator": operator,
                        "value": self._coerce_value(value),
                    }
                )
                break

        return filters

    def _extract_operations(self, query: str):
        lower_query = query.lower()
        mapping = [
            ("average", "mean"),
            ("mean", "mean"),
            ("sum", "sum"),
            ("total", "sum"),
            ("count", "count"),
            ("maximum", "max"),
            ("highest", "max"),
            ("max", "max"),
            ("minimum", "min"),
            ("lowest", "min"),
            ("min", "min"),
        ]

        operations = []
        for keyword, operation in mapping:
            if keyword in lower_query and operation not in operations:
                operations.append(operation)

        return operations

    def _extract_groupby(self, query: str, columns: list[str]):
        lower_query = query.lower()

        for phrase in ["group by ", "grouped by ", "per ", "by "]:
            if phrase not in lower_query:
                continue

            tail = lower_query.split(phrase, 1)[1]
            for column in columns or []:
                if column.lower() in tail:
                    return column

        return None

    def _has_grouping_language(self, query: str):
        normalized = self._normalize_text(query)
        return any(
            phrase in normalized
            for phrase in ["group by", "grouped by", " based on ", " per ", " by "]
        ) or normalized.startswith("group ")

    def _has_listing_language(self, query: str):
        normalized = self._normalize_text(query)
        return any(
            token in normalized.split()
            for token in ["show", "list", "display", "give", "find"]
        )

    def _extract_prediction_target(self, query: str, columns: list[str]):
        normalized_query = self._normalize_text(query)

        for column in sorted(columns or [], key=len, reverse=True):
            normalized_column = self._normalize_text(column)
            if not normalized_column:
                continue

            if re.search(
                rf"\b(?:predict|forecast|estimate)\b\s+{re.escape(normalized_column)}\b",
                normalized_query,
            ):
                return column

        matched_columns = self._match_columns(query, columns)
        return matched_columns[-1] if matched_columns else None

    def _extract_prediction_inputs(
        self,
        query: str,
        columns: list[str],
        target: str | None = None,
    ):
        inputs = {}
        feature_columns = [column for column in (columns or []) if column != target]
        extracted_filters = self._extract_filters(query, feature_columns)

        for item in extracted_filters:
            inputs[item["column"]] = item["value"]

        search_text = query
        if target:
            target_match = re.search(
                rf"\b{re.escape(target)}\b(.*)$",
                query,
                flags=re.IGNORECASE,
            )
            if target_match:
                search_text = target_match.group(1)

        lowered = search_text.lower()
        if " when " in lowered:
            search_text = search_text[lowered.index(" when ") + 6:]
        elif " for " in lowered:
            search_text = search_text[lowered.index(" for ") + 5:]
        elif lowered.strip().startswith("with "):
            search_text = search_text.strip()[5:]

        for column in feature_columns:
            match = re.search(
                rf"{re.escape(column)}\s*(?:=|is|:)?\s*([a-zA-Z0-9\.\-_]+)",
                search_text,
                flags=re.IGNORECASE,
            )
            if match:
                inputs[column] = self._coerce_value(match.group(1))

        return inputs

    def _fallback_plan(self, query: str, columns: list[str]):
        lower_query = query.lower()
        matched_columns = self._match_columns(query, columns)
        filters = self._extract_filters(query, columns)
        operations = self._extract_operations(query)

        chart_keywords = {
            "histogram": "histogram",
            "scatter": "scatter",
            "line": "line",
            "pie": "pie",
            "bar": "bar",
            "chart": "bar",
            "graph": "bar",
            "plot": "line",
            "visualize": "bar",
        }

        intent = "unknown"
        chart_type = None
        target = matched_columns[-1] if matched_columns else None
        prediction_inputs = {}

        if any(word in lower_query for word in ["predict", "forecast", "estimate"]):
            intent = "prediction"
            target = self._extract_prediction_target(query, columns)
            prediction_inputs = self._extract_prediction_inputs(
                query,
                columns,
                target=target,
            )
        elif any(word in lower_query for word in chart_keywords):
            intent = "visualization"
            for keyword, chart_name in chart_keywords.items():
                if keyword in lower_query:
                    chart_type = chart_name
                    break
        elif (
            bool(operations)
            or bool(matched_columns)
            or bool(filters)
            or any(
                word in lower_query
                for word in ["analyze", "analysis", "show", "what", "find", "list", "give me"]
            )
        ):
            intent = "analytics"

        groupby = self._extract_groupby(query, columns)

        return {
            "intent": intent,
            "operations": operations,
            "columns": matched_columns,
            "groupby": groupby,
            "chart_type": chart_type,
            "target": target,
            "task_type": None,
            "prediction_inputs": prediction_inputs,
            "filters": filters,
        }

    def _build_steps(self, plan: dict, columns: list[str]):
        steps = []

        for item in plan.get("filters") or []:
            steps.append(
                {
                    "action": "filter",
                    "column": item["column"],
                    "operator": item["operator"],
                    "value": item["value"],
                }
            )

        groupby = plan.get("groupby")
        if groupby:
            steps.append({"action": "groupby", "columns": [groupby]})

        operations = plan.get("operations") or []
        selected_columns = [
            column
            for column in (plan.get("columns") or [])
            if column in (columns or []) and column != groupby
        ]

        if operations:
            if not selected_columns and groupby:
                selected_columns = [
                    column for column in (columns or []) if column != groupby
                ][:1]
            elif not selected_columns and columns:
                selected_columns = [columns[0]]

            if selected_columns:
                steps.append(
                    {
                        "action": "aggregate",
                        "operations": {
                            column: operations if len(operations) > 1 else operations[0]
                            for column in selected_columns
                        },
                    }
                )
        elif selected_columns:
            steps.append(
                {
                    "action": "select",
                    "columns": selected_columns,
                }
            )

        return steps

    def _is_incomplete_analysis_request(
        self,
        query: str,
        columns: list[str],
        operations: list[str],
        filters: list[dict],
        groupby: str | None,
        steps: list[dict],
    ):
        if operations or filters:
            return False

        if groupby and not operations:
            return True

        if self._has_grouping_language(query) and not operations:
            return True

        if steps:
            return False

        if columns and self._has_listing_language(query):
            return False

        return True

    def _normalize_plan(self, raw_plan: dict, query: str, columns: list[str]):
        fallback_plan = self._fallback_plan(query, columns)

        intent = raw_plan.get("intent") or fallback_plan.get("intent", "unknown")
        raw_columns = (
            raw_plan.get("columns")
            or fallback_plan.get("columns")
            or self._match_columns(query, columns)
        )
        chart_type = raw_plan.get("chart_type") or fallback_plan.get("chart_type")
        groupby = raw_plan.get("groupby") or fallback_plan.get("groupby")
        target = raw_plan.get("target") or fallback_plan.get("target")
        filters = raw_plan.get("filters") or fallback_plan.get("filters") or []
        operations = raw_plan.get("operations") or fallback_plan.get("operations") or []
        prediction_inputs = (
            raw_plan.get("prediction_inputs")
            or fallback_plan.get("prediction_inputs")
            or {}
        )

        if isinstance(operations, str):
            operations = [operations]

        operations = [
            item for item in operations if item in {"max", "min", "mean", "sum", "count"}
        ]

        value_columns = [column for column in raw_columns if column != groupby]

        if intent == "prediction":
            extracted_target = self._extract_prediction_target(query, columns)
            if extracted_target:
                target = extracted_target

            extracted_prediction_inputs = self._extract_prediction_inputs(
                query,
                columns,
                target=target,
            )
            if extracted_prediction_inputs:
                prediction_inputs = {
                    **prediction_inputs,
                    **extracted_prediction_inputs,
                }

            if target in prediction_inputs:
                prediction_inputs.pop(target, None)

        normalized = {
            "type": "unknown",
            "operation": operations[0] if operations else "none",
            "operations": operations,
            "columns": raw_columns,
            "groupby": groupby,
            "chart": chart_type,
            "chart_type": chart_type,
            "x": groupby or (raw_columns[0] if raw_columns else None),
            "y": value_columns[0] if value_columns else (raw_columns[0] if raw_columns else None),
            "target": target or (value_columns[-1] if value_columns else (raw_columns[-1] if raw_columns else None)),
            "task_type": raw_plan.get("task_type") or fallback_plan.get("task_type"),
            "prediction_inputs": prediction_inputs,
            "filters": filters,
        }

        if intent == "analytics":
            steps = self._build_steps(
                {
                    "operations": operations,
                    "columns": raw_columns,
                    "groupby": groupby,
                    "filters": filters,
                },
                columns,
            )
            if self._is_incomplete_analysis_request(
                query,
                raw_columns,
                operations,
                filters,
                groupby,
                steps,
            ):
                normalized["type"] = "unknown"
            else:
                normalized["type"] = "analysis"
                normalized["steps"] = steps
        elif intent == "visualization":
            normalized["type"] = "visualization"
            if normalized["chart"] == "histogram":
                normalized["y"] = None
        elif intent == "prediction":
            normalized["type"] = "prediction"

        return normalized

    def plan(self, query: str, columns: list[str] | None = None, context=None):
        columns = columns or []
        prompt = f"""
Available columns: {columns}
Conversation context: {context or []}
User query: {query}
"""

        llm_result, _ = llm_service.invoke_structured(
            self.system_prompt,
            prompt,
            PlannerSchema,
            temperature=0,
        )
        if llm_result is not None:
            return self._normalize_plan(llm_result.model_dump(), query, columns)

        raw_plan = self._fallback_plan(query, columns)
        return self._normalize_plan(raw_plan, query, columns)


def generate_plan(query: str, columns=None, context=None):
    planner = LLMPlanner()

    try:
        return planner.plan(query=query, columns=columns or [], context=context)
    except Exception as exc:
        return {
            "type": "error",
            "message": f"Planner error: {str(exc)}",
        }
