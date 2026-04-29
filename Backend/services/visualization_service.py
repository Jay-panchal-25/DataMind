import pandas as pd
import io
import base64


def generate_visualization(df: pd.DataFrame, plan: dict):
    """
    Generate chart from LLM plan using Matplotlib
    Returns base64 encoded image
    """

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        chart_type = plan.get("chart") or plan.get("chart_type")
        x_col = plan.get("x")
        y_col = plan.get("y")
        filters = plan.get("filters") or []

        data = df.copy()

        for filter_item in filters:
            column = filter_item.get("column")
            operator = filter_item.get("operator")
            value = filter_item.get("value")

            if column not in data.columns:
                return {"error": f"Column '{column}' not found"}

            if operator == "==":
                data = data[data[column] == value]
            elif operator == "!=":
                data = data[data[column] != value]
            elif operator == ">":
                data = data[data[column] > value]
            elif operator == ">=":
                data = data[data[column] >= value]
            elif operator == "<":
                data = data[data[column] < value]
            elif operator == "<=":
                data = data[data[column] <= value]
            else:
                return {"error": f"Unsupported operator '{operator}'"}

        # ---------------- VALIDATION ----------------
        if x_col not in df.columns:
            return {"error": f"Column '{x_col}' not found"}

        if chart_type not in ["histogram", "pie"] and y_col not in df.columns:
            return {"error": f"Column '{y_col}' not found"}

        # ---------------- CREATE PLOT ----------------
        plt.figure()

        # -------- BAR CHART --------
        if chart_type == "bar":
            grouped = data.groupby(x_col)[y_col].mean()

            plt.bar(grouped.index.astype(str), grouped.values)
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.title(f"{y_col} by {x_col}")

        # -------- LINE CHART --------
        elif chart_type == "line":
            data = data[[x_col, y_col]].dropna()

            plt.plot(data[x_col], data[y_col])
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.title(f"{y_col} vs {x_col}")

        # -------- SCATTER --------
        elif chart_type == "scatter":
            data = data[[x_col, y_col]].dropna()

            plt.scatter(data[x_col], data[y_col])
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.title(f"{y_col} vs {x_col}")

        # -------- HISTOGRAM --------
        elif chart_type == "histogram":
            if not pd.api.types.is_numeric_dtype(data[x_col]):
                return {"error": "Histogram requires numeric column"}

            plt.hist(data[x_col].dropna(), bins=10)
            plt.xlabel(x_col)
            plt.ylabel("Frequency")
            plt.title(f"Distribution of {x_col}")

        # -------- PIE --------
        elif chart_type == "pie":
            pie_source = _prepare_pie_data(data[x_col])

            if pie_source.empty:
                return {"error": f"No values available for pie chart on '{x_col}'"}

            plt.pie(
                pie_source.values,
                labels=pie_source.index.astype(str),
                autopct="%1.1f%%"
            )
            plt.title(f"Distribution of {x_col}")

        else:
            return {"error": f"Unsupported chart type '{chart_type}'"}

        # ---------------- SAVE TO BASE64 ----------------
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()

        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        return {"image": image_base64}

    except Exception as e:
        return {
            "error": str(e)
        }


def _prepare_pie_data(series: pd.Series):
    clean_series = series.dropna()
    if clean_series.empty:
        return pd.Series(dtype="int64")

    if pd.api.types.is_numeric_dtype(clean_series) and clean_series.nunique() > 8:
        bins = min(6, clean_series.nunique())
        binned = pd.cut(clean_series, bins=bins, include_lowest=True)
        return binned.value_counts().sort_index()

    counts = clean_series.astype(str).value_counts()

    if len(counts) > 8:
        top_counts = counts.head(7)
        other_total = counts.iloc[7:].sum()
        if other_total > 0:
            top_counts.loc["Other"] = other_total
        return top_counts

    return counts
