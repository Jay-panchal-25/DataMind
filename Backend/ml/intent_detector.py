class IntentDetector:

    def __init__(self):

        # define intent keywords
        self.intent_keywords = {

            "visualization": [
                "plot",
                "graph",
                "chart",
                "histogram",
                "visualize",
                "distribution",
                "bar chart",
                "line chart",
                "scatter",
                "show graph"
                "pie chart"
            ],

            "analytics": [
                "max",
                "maximum",
                "highest",
                "min",
                "minimum",
                "lowest",
                "average",
                "avg",
                "mean",
                "sum",
                "total",
                "count",
                "median",
                "std",
                "variance"
            ]

        }

        # priority order (important)
        self.priority = [
            "visualization",
            "analytics"
        ]


    def detect(self, query: str) -> str:

        if not query:
            return "unknown"

        query = query.lower().strip()

        # check intents based on priority
        for intent in self.priority:

            keywords = self.intent_keywords[intent]

            for keyword in keywords:

                if keyword in query:
                    return intent

        return "unknown"
