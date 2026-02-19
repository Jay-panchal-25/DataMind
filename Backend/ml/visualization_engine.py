# ml/visualization_engine.py

class VisualizationEngine:

    def __init__(self, df):
        self.df = df


    def detect_chart_type(self, query):

        query = query.lower()

        if "histogram" in query or "distribution" in query:
            return "histogram"

        elif "pie" in query:
            return "pie"

        elif "bar" in query:
            return "bar"

        elif "line" in query:
            return "line"

        elif "scatter" in query:
            return "scatter"

        else:
            return "bar"



    def detect_column(self, query):

        for col in self.df.columns:
            if col.lower() in query.lower():
                return col

        return None


    def generate_graph(self, query):

        chart_type = self.detect_chart_type(query)
        column = self.detect_column(query)

        if column is None:
            return "Column not found"


        # BAR CHART (categorical count)
        if chart_type == "bar":

            counts = self.df[column].value_counts()

            return {
                "chart_type": "bar",
                "labels": counts.index.tolist(),
                "values": counts.values.tolist(),
                "column": column
            }


        # HISTOGRAM
        elif chart_type == "histogram":

            counts, bins = self._histogram_data(self.df[column])

            return {
                "chart_type": "histogram",
                "labels": bins,
                "values": counts,
                "column": column
            }
        
        # PIE CHART (categorical proportion)
        elif chart_type == "pie":

            counts = self.df[column].value_counts()

            return {
                "chart_type": "pie",
                "labels": counts.index.tolist(),
                "values": counts.values.tolist(),
                "column": column
            }



        # LINE CHART
        elif chart_type == "line":

            return {
                "chart_type": "line",
                "labels": list(range(len(self.df[column]))),
                "values": self.df[column].tolist(),
                "column": column
            }


        # SCATTER
        elif chart_type == "scatter":

            numeric_cols = self.df.select_dtypes(include='number').columns

            if len(numeric_cols) < 2:
                return "Need at least 2 numeric columns"

            x = numeric_cols[0]
            y = numeric_cols[1]

            return {
                "chart_type": "scatter",
                "x": self.df[x].tolist(),
                "y": self.df[y].tolist(),
                "x_column": x,
                "y_column": y
            }



    # helper histogram
    def _histogram_data(self, series, bins=10):

        counts, bin_edges = self._numpy_hist(series, bins)

        labels = []

        for i in range(len(bin_edges) - 1):
            labels.append(
                f"{round(bin_edges[i],2)}-{round(bin_edges[i+1],2)}"
            )

        return counts, labels


    def _numpy_hist(self, series, bins):

        import numpy as np

        counts, bin_edges = np.histogram(series.dropna(), bins=bins)

        return counts.tolist(), bin_edges.tolist()
