from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

class DataImputer:
    def __init__(self, strategy="knn", n_neighbors=5):
        self.strategy = strategy
        self.n_neighbors = n_neighbors

    def fit_transform(self, df: pd.DataFrame):
        numeric_cols = df.select_dtypes(include="number").columns

        if len(numeric_cols) == 0:
            return df, {}

        report = {}

        if self.strategy == "knn":
            scaler = StandardScaler()
            scaled = scaler.fit_transform(df[numeric_cols])

            imputer = KNNImputer(n_neighbors=self.n_neighbors)
            imputed = imputer.fit_transform(scaled)

            restored = scaler.inverse_transform(imputed)

            df[numeric_cols] = restored
            # Enforce business rule: numeric values must be non-negative integers.
            df[numeric_cols] = (
                df[numeric_cols]
                .clip(lower=0)
                .round()
                .astype("Int64")
            )
            report["method"] = "KNN"

        elif self.strategy == "median":
            df[numeric_cols] = df[numeric_cols].fillna(
                df[numeric_cols].median()
            )
            # Keep output consistent across strategies.
            df[numeric_cols] = (
                df[numeric_cols]
                .clip(lower=0)
                .round()
                .astype("Int64")
            )
            report["method"] = "Median"

        return df, report
