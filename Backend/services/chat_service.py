from ml.intent_detector import IntentDetector
from ml.query_engine import QueryEngine
from ml.visualization_engine import VisualizationEngine


class ChatService:

    def __init__(self, dataframe):
        self.df = dataframe
        self.intent_detector = IntentDetector()
        self.query_engine = QueryEngine(dataframe)
        self.visualization_engine = VisualizationEngine(dataframe)

    def process(self, user_message: str):
        if not user_message or not user_message.strip():
            return {
                "type": "text",
                "content": "Please enter a message.",
            }

        intent = self.intent_detector.detect(user_message)

        if intent in ("analytics", "filter", "groupby"):
            result = self.query_engine.execute(user_message)

            if isinstance(result, dict) and result.get("kind") == "table":
                if self._is_single_value_table(result):
                    return {
                        "type": "text",
                        "content": self._single_value_text_from_table(result),
                    }
                return {
                    "type": "table",
                    "content": result,
                }

            if isinstance(result, dict):
                if self._is_single_value_result_dict(result):
                    return {
                        "type": "text",
                        "content": self._single_value_text_from_result(result),
                    }
                table_payload = self._result_dict_to_table(result)
                if self._is_single_value_table(table_payload):
                    return {
                        "type": "text",
                        "content": self._single_value_text_from_table(table_payload),
                    }
                return {
                    "type": "table",
                    "content": table_payload,
                }

            return {
                "type": "text",
                "content": self._format_analytics_response(result),
            }

        if intent == "visualization":
            chart_data = self.visualization_engine.generate_graph(user_message)

            if isinstance(chart_data, str):
                return {
                    "type": "text",
                    "content": chart_data,
                }

            return {
                "type": "chart",
                "content": chart_data,
            }

        return {
            "type": "text",
            "content": "I could not understand your query.",
        }

    def _to_python_scalar(self, value):
        if hasattr(value, "item"):
            try:
                return value.item()
            except Exception:
                return value
        return value

    def _result_dict_to_table(self, result: dict):
        column = result.get("column")
        value = result.get("result")
        groupby = result.get("groupby")
        filters = result.get("filters", [])

        if groupby and isinstance(value, dict):
            rows = []
            for grp, val in value.items():
                rows.append({
                    groupby: self._to_python_scalar(grp),
                    column: self._to_python_scalar(val),
                })
            return {
                "kind": "table",
                "title": f"{column} by {groupby}",
                "columns": [groupby, column],
                "rows": rows,
                "row_count": len(rows),
            }

        scalar_value = self._to_python_scalar(value)
        row = {column: scalar_value}
        if filters:
            row["filters"] = "; ".join([f"{c} {o} {v}" for c, o, v in filters])

        return {
            "kind": "table",
            "title": f"{column} result",
            "columns": list(row.keys()),
            "rows": [row],
            "row_count": 1,
        }

    def _is_single_value_table(self, table: dict) -> bool:
        if not isinstance(table, dict):
            return False
        columns = table.get("columns", [])
        rows = table.get("rows", [])
        if len(rows) != 1:
            return False

        if len(columns) == 1:
            return True

        if len(columns) == 2 and "filters" in columns:
            return True

        return False

    def _single_value_text_from_table(self, table: dict) -> str:
        rows = table.get("rows", [])
        if not rows:
            return "No result found."

        row = rows[0]
        for key, val in row.items():
            if key == "filters":
                continue
            return f"{key}: {val}"

        return "No result found."

    def _is_single_value_result_dict(self, result: dict) -> bool:
        if not isinstance(result, dict):
            return False
        if result.get("groupby") is not None:
            return False
        value = result.get("result")
        return not isinstance(value, dict)

    def _single_value_text_from_result(self, result: dict) -> str:
        operation = result.get("operation", "result")
        column = result.get("column", "value")
        value = self._to_python_scalar(result.get("result"))

        operation_text = {
            "max": "maximum",
            "min": "minimum",
            "mean": "average",
            "sum": "sum",
            "count": "count",
            "median": "median",
            "std": "standard deviation",
            "var": "variance",
        }.get(operation, operation)

        return f"Your {operation_text} {column} is {value}."

    def _format_analytics_response(self, result):
        if isinstance(result, str):
            if result == "Operation not found":
                return "I could not detect the calculation. Try asking for max, min, average, sum, count, median, std, or variance."
            if result == "Column not found":
                return "I could not detect the column name. Please mention a column from your dataset."
            return result

        if not isinstance(result, dict):
            return str(result)

        operation = result.get("operation")
        column = result.get("column")
        value = result.get("result")
        groupby = result.get("groupby")
        filters = result.get("filters", [])

        if operation is None or column is None:
            return str(result)

        operation_text = {
            "max": "maximum",
            "min": "minimum",
            "mean": "average",
            "sum": "sum",
            "count": "count",
            "median": "median",
            "std": "standard deviation",
            "var": "variance",
        }.get(operation, operation)

        filter_text = ""
        if filters:
            parts = [f"{col} {op} {val}" for col, op, val in filters]
            filter_text = f" (filtered by: {', '.join(parts)})"

        if groupby and isinstance(value, dict):
            lines = [f"The {operation_text} of {column} grouped by {groupby}{filter_text}:"]
            for group, val in value.items():
                if hasattr(val, "item"):
                    try:
                        val = val.item()
                    except Exception:
                        pass
                if isinstance(val, float):
                    val = round(val, 2)
                lines.append(f"  - {group}: {val}")
            return "\n".join(lines)

        if hasattr(value, "item"):
            try:
                value = value.item()
            except Exception:
                pass

        if isinstance(value, float):
            value = round(value, 2)

        return f"The {operation_text} of {column}{filter_text} is {value}."
