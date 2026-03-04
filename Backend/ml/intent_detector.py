class IntentDetector:

    def __init__(self):

        self.intent_keywords = {

            "groupby": [
                "group by",
                "grouped by",
                "per",
                "by each",
                "for each",
            ],

            "filter": [
                "where",
                "filter",
                "only",
                "greater than",
                "less than",
                "equal to",
                "not equal",
                "base on",
                ">=",
                "<=",
                "!=",
                "==",
                ">",
                "<",
            ],

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
                "show graph",
                "pie chart",
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
                "variance",
            ],
        }

        # priority order (important)
        self.priority = [
            "visualization",
            "groupby",
            "filter",
            "analytics",
        ]

    def detect(self, query: str) -> str:

        if not query:
            return "unknown"

        query = query.lower().strip()

        for intent in self.priority:
            keywords = self.intent_keywords[intent]
            for keyword in keywords:
                if keyword in query:
                    return intent

        return "unknown"
