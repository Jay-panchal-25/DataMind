# services/chat_service.py

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

        if intent == "analytics":

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

        if operation is None or column is None:
            return str(result)

        # Convert numpy/pandas scalar types to plain Python values when possible.
        if hasattr(value, "item"):
            try:
                value = value.item()
            except Exception:
                pass

        if isinstance(value, float):
            value = round(value, 2)

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

        return f"The {operation_text} of {column} is {value}."
