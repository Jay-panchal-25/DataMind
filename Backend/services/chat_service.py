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
                "content": "Please enter a message."
            }

        # Step 1: detect intent
        intent = self.intent_detector.detect(user_message)

        # Step 2: route to correct engine

        if intent in ("analytics", "filter", "groupby"):
            # All three intents use QueryEngine — it handles filter/groupby internally
            result = self.query_engine.execute(user_message)

            return {
                "type": "text",
                "content": self._format_analytics_response(result)
            }
        
        elif intent == "visualization":

            chart_data = self.visualization_engine.generate_graph(user_message)

            if isinstance(chart_data, str):
                return {
                    "type": "text",
                    "content": chart_data
                }

            return {
                "type": "chart",
                "content": chart_data
            }
        else:

            return {
                "type": "text",
                "content": "I could not understand your query."
            }

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

        # Format filter description
        filter_text = ""
        if filters:
            parts = [f"{col} {op} {val}" for col, op, val in filters]
            filter_text = f" (filtered by: {', '.join(parts)})"

        # Format groupby result (dict of group → value)
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
                lines.append(f"  • {group}: {val}")
            return "\n".join(lines)

        # Format plain scalar result
        if hasattr(value, "item"):
            try:
                value = value.item()
            except Exception:
                pass

        if isinstance(value, float):
            value = round(value, 2)

        return f"The {operation_text} of {column}{filter_text} is {value}."