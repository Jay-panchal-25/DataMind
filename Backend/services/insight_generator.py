import pandas as pd
import numpy as np


class InsightGenerator:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    # ----------------------------
    # MAIN FUNCTION
    # ----------------------------
    def generate(self):

        insights = {
            "summary": self._basic_summary(),
            "missing": self._missing_info(),
            "numeric": self._numeric_insights(),
            "categorical": self._categorical_insights(),
            "correlation": self._correlation_insights()
        }

        return insights

    # ----------------------------
    # BASIC SUMMARY
    # ----------------------------
    def _basic_summary(self):
        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": list(self.df.columns)
        }

    # ----------------------------
    # MISSING VALUES
    # ----------------------------
    def _missing_info(self):
        missing = self.df.isna().sum()

        return {
            col: int(count)
            for col, count in missing.items()
            if count > 0
        }

    # ----------------------------
    # NUMERIC INSIGHTS
    # ----------------------------
    def _numeric_insights(self):
        numeric_cols = self.df.select_dtypes(include=np.number).columns

        insights = []

        for col in numeric_cols:
            series = self.df[col].dropna()

            if series.empty:
                continue

            insights.append({
                "column": col,
                "mean": round(series.mean(), 2),
                "median": round(series.median(), 2),
                "min": series.min(),
                "max": series.max(),
                "std": round(series.std(), 2)
            })

        return insights

    # ----------------------------
    # CATEGORICAL INSIGHTS
    # ----------------------------
    def _categorical_insights(self):
        cat_cols = self.df.select_dtypes(include="object").columns

        insights = []

        for col in cat_cols:
            top_values = self.df[col].value_counts().head(3)

            insights.append({
                "column": col,
                "top_values": top_values.to_dict()
            })

        return insights

    # ----------------------------
    # CORRELATION INSIGHTS
    # ----------------------------
    def _correlation_insights(self):
        numeric_df = self.df.select_dtypes(include=np.number)

        if numeric_df.shape[1] < 2:
            return []

        corr_matrix = numeric_df.corr()

        strong_pairs = []

        seen_pairs = set()

        for i in corr_matrix.columns:
            for j in corr_matrix.columns:
                if i == j:
                    continue

                pair_key = tuple(sorted((i, j)))
                if pair_key in seen_pairs:
                    continue

                value = corr_matrix.loc[i, j]

                if abs(value) > 0.7:
                    seen_pairs.add(pair_key)
                    strong_pairs.append({
                        "feature_1": i,
                        "feature_2": j,
                        "correlation": round(value, 2)
                    })

        return strong_pairs
