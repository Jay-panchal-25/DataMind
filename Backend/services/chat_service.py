import re

import pandas as pd

from services.execution_engine import execute_analysis
from services.llm_planner import generate_plan
from services.memory_manager import MemoryManager
from services.model_registry import model_registry
from services.visualization_service import generate_visualization


class ChatService:
    def __init__(self, dataframe, memory=None, session_state=None, quality=None):
        self.df = dataframe
        self.memory = memory or MemoryManager()
        self.session_state = session_state
        self.quality = quality or {}

    def process(self, user_message: str):
        if not user_message or not user_message.strip():
            return {
                "type": "text",
                "content": "Please enter a message."
            }

        smalltalk_response = self._handle_smalltalk(user_message)
        if smalltalk_response is not None:
            self.memory.add(user_message, smalltalk_response)
            return smalltalk_response

        context = self.memory.get_context()
        plan = generate_plan(
            query=user_message,
            columns=list(self.df.columns),
            context=context
        )

        if plan.get("type") == "error":
            return {
                "type": "text",
                "content": plan.get("message")
            }

        if plan.get("type") == "unknown":
            fallback_response = self._handle_extreme_lookup(user_message)
            if fallback_response is not None:
                self.memory.add(user_message, fallback_response)
                return fallback_response

            response = {
                "type": "text",
                "content": (
                    "I couldn't map that to a dataset task yet. Try asking for a summary, "
                    "grouped metric, chart, filter, or prediction."
                )
            }
            self.memory.add(user_message, response)
            return response

        self.memory.set_last_plan(plan)

        if plan["type"] == "analysis":
            result = execute_analysis(self.df, plan)

            if "error" in result:
                response = {
                    "type": "text",
                    "content": result["error"]
                }
            elif result.get("type") == "table":
                response = {
                    "type": "table",
                    "content": {
                        "columns": result.get("columns", []),
                        "rows": result.get("rows", []),
                    }
                }
            else:
                response = {
                    "type": "text",
                    "content": result.get("content", "No result returned.")
                }

        elif plan["type"] == "visualization":
            result = generate_visualization(self.df, plan)

            if "error" in result:
                response = {
                    "type": "text",
                    "content": result["error"]
                }
            else:
                response = {
                    "type": "chart",
                    "content": result
                }

        elif plan["type"] == "prediction":
            target = plan.get("target")
            if not target:
                response = {
                    "type": "text",
                    "content": "Please specify which column you want to predict.",
                }
                self.memory.add(user_message, response)
                return response

            cached_bundle = (
                model_registry.get(self.session_state, target)
                if self.session_state is not None
                else None
            )

            if cached_bundle is not None:
                result = dict(cached_bundle.result)
                if plan.get("prediction_inputs"):
                    prediction_value, error = cached_bundle.engine.predict_single(
                        plan.get("prediction_inputs")
                    )
                    if error:
                        result = {"error": error}
                    else:
                        result["predictions"] = [prediction_value]
                        result["input_values"] = plan.get("prediction_inputs")
                        result["cached"] = True
            else:
                from ml.automl_engine import AutoMLEngine

                automl = AutoMLEngine(self.df)
                try:
                    result = automl.run(
                        target,
                        prediction_inputs=plan.get("prediction_inputs"),
                    )
                except Exception as exc:
                    result = {"error": str(exc)}
                if "error" not in result and self.session_state is not None:
                    cached_result = dict(result)
                    cached_result["predictions"] = None
                    cached_result["input_values"] = None
                    model_registry.set(
                        self.session_state,
                        target,
                        automl,
                        cached_result,
                    )

            if "error" in result:
                response = {
                    "type": "text",
                    "content": result["error"]
                }
            else:
                result["quality_warnings"] = self.quality.get("warnings", [])
                response = {
                    "type": "prediction",
                    "content": result
                }

        else:
            response = {
                "type": "text",
                "content": "Could not understand request"
            }

        self.memory.add(user_message, response)
        return response

    def _handle_smalltalk(self, user_message: str):
        normalized = user_message.strip().lower()
        if re.fullmatch(
            r"(hi+|hello+|hey+|good morning|good afternoon|good evening|hola|namaste)[\!\.\s]*",
            normalized,
        ):
            return {
                "type": "text",
                "content": "Hello! Your dataset is ready. Ask me a question about the data."
            }

        return None

    def _handle_extreme_lookup(self, user_message: str):
        lower_query = user_message.lower()

        if not any(token in lower_query for token in ["max", "maximum", "highest", "min", "minimum", "lowest"]):
            return None

        if not any(token in lower_query for token in ["who", "name", "person", "customer", "employee", "row", "record"]):
            return None

        operation = "max" if any(token in lower_query for token in ["max", "maximum", "highest"]) else "min"
        metric_column = self._resolve_metric_column(lower_query)
        if metric_column is None:
            return None

        metric_series = pd.to_numeric(self.df[metric_column], errors="coerce").dropna()
        if metric_series.empty:
            return None

        target_value = metric_series.max() if operation == "max" else metric_series.min()
        matched_rows = self.df.loc[metric_series.index][metric_series == target_value]

        if matched_rows.empty:
            return None

        display_columns = self._resolve_display_columns(lower_query, metric_column)
        result_columns = [*display_columns, metric_column]
        result = matched_rows[result_columns].copy()

        if len(result) == 1 and display_columns:
            values = [
                str(result.iloc[0][column])
                for column in display_columns
                if pd.notna(result.iloc[0][column])
            ]
            subject = ", ".join(values) if values else "Matching row"
            return {
                "type": "text",
                "content": f"{subject} has the {operation} {metric_column}: {target_value}"
            }

        return {
            "type": "table",
            "content": {
                "columns": result.columns.tolist(),
                "rows": result.astype("object").where(pd.notna(result), None).to_dict(orient="records"),
            },
        }

    def _resolve_metric_column(self, lower_query: str):
        normalized_query = self._normalize_text(lower_query)
        matched_columns = []

        for column in self.df.columns:
            normalized_column = self._normalize_text(column)
            compact_column = normalized_column.replace(" ", "")

            if (
                normalized_column and normalized_column in normalized_query
            ) or (
                compact_column and compact_column in normalized_query.replace(" ", "")
            ):
                matched_columns.append(column)

        numeric_columns = [
            column for column in matched_columns
            if pd.api.types.is_numeric_dtype(self.df[column])
        ]
        if numeric_columns:
            return numeric_columns[-1]

        last_plan = self.memory.get_last_plan()
        if last_plan:
            target = last_plan.get("target")
            if target in self.df.columns and pd.api.types.is_numeric_dtype(self.df[target]):
                return target

        fallback_numeric = [
            column for column in self.df.columns
            if pd.api.types.is_numeric_dtype(self.df[column])
        ]
        return fallback_numeric[0] if fallback_numeric else None

    def _resolve_display_columns(self, lower_query: str, metric_column: str):
        preferred_keywords = ["name", "customer", "employee", "person", "client", "user"]

        semantic_matches = [
            column for column in self.df.columns
            if column != metric_column
            and any(keyword in column.lower() for keyword in preferred_keywords)
        ]
        if semantic_matches:
            return semantic_matches[:2]

        fallback = [
            column for column in self.df.columns
            if column != metric_column
            and not pd.api.types.is_numeric_dtype(self.df[column])
            and not pd.api.types.is_datetime64_any_dtype(self.df[column])
        ]
        return fallback[:2]

    def _normalize_text(self, value: str):
        return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()
