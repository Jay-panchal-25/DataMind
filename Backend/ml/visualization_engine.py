import matplotlib.pyplot as plt
import seaborn as sns
import os


class VisualizationEngine:

    def __init__(self, df):
        self.df = df

        # create graphs folder
        self.output_dir = "graphs"
        os.makedirs(self.output_dir, exist_ok=True)


    def detect_chart_type(self, query):

        query = query.lower()

        if "histogram" in query or "distribution" in query:
            return "histogram"

        elif "bar" in query:
            return "bar"

        elif "line" in query:
            return "line"

        elif "scatter" in query:
            return "scatter"

        elif "box" in query:
            return "box"

        else:
            return "histogram"  # default


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

        plt.figure(figsize=(8, 5))

        if chart_type == "histogram":
            sns.histplot(self.df[column], kde=True)

        elif chart_type == "bar":
            self.df[column].value_counts().plot(kind="bar")

        elif chart_type == "line":
            self.df[column].plot(kind="line")

        elif chart_type == "scatter":

            numeric_cols = self.df.select_dtypes(include='number').columns

            if len(numeric_cols) >= 2:
                sns.scatterplot(
                    x=self.df[numeric_cols[0]],
                    y=self.df[numeric_cols[1]]
                )
            else:
                return "Need 2 numeric columns for scatter"

        elif chart_type == "box":
            sns.boxplot(y=self.df[column])


        filename = f"{column}_{chart_type}.png"
        filepath = os.path.join(self.output_dir, filename)

        plt.title(f"{chart_type} of {column}")
        plt.savefig(filepath)
        plt.close()

        return {
            "chart_type": chart_type,
            "column": column,
            "file": filepath
        }
