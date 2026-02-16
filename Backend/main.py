import pandas as pd

from ml.intent_detector import IntentDetector
from ml.query_engine import QueryEngine
from ml.visualization_engine import VisualizationEngine


class MainEngine:

    def __init__(self, df):

        self.df = df

        self.intent_detector = IntentDetector()
        self.query_engine = QueryEngine(df)
        self.visual_engine = VisualizationEngine(df)


    def process_query(self, query):

        intent = self.intent_detector.detect(query)

        print(f"Detected intent: {intent}")

        if intent == "analytics":

            return self.query_engine.execute(query)

        elif intent == "visualization":

            return self.visual_engine.generate_graph(query)

        else:

            return {
                "status": "error",
                "message": "Intent not supported"
            }


# ------------------ RUN APPLICATION ------------------

if __name__ == "__main__":

    # Sample dataset (replace with your uploaded dataset later)
    data = {
        "salary": [25000, 30000, 40000, 35000, 45000],
        "age": [22, 25, 30, 28, 35]
    }

    df = pd.DataFrame(data)

    engine = MainEngine(df)

    print("DataMind AI Started (type 'exit' to stop)")

    while True:

        user_query = input("\nEnter your query: ")

        if user_query.lower() == "exit":
            break

        result = engine.process_query(user_query)

        print("Result:", result)
