from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler
import pandas as pd


class DataImputer:

    def __init__(self, strategy="knn", n_neighbors=5, enforce_positive=True):
        self.strategy = strategy
        self.n_neighbors = n_neighbors
        self.enforce_positive = enforce_positive

    def fit_transform(self, df: pd.DataFrame):

        numeric_cols = df.select_dtypes(include="number").columns

        if len(numeric_cols) == 0:
            return df, {}

        report = {}

        # STEP 1: Handle missing values
        if self.strategy == "knn":

            scaler = StandardScaler()
            scaled = scaler.fit_transform(df[numeric_cols])

            imputer = KNNImputer(n_neighbors=self.n_neighbors)
            imputed = imputer.fit_transform(scaled)

            restored = scaler.inverse_transform(imputed)

            df[numeric_cols] = restored
            report["method"] = "KNN"

        elif self.strategy == "median":

            df[numeric_cols] = df[numeric_cols].fillna(
                df[numeric_cols].median()
            )

            report["method"] = "Median"

        elif self.strategy == "mean":

            df[numeric_cols] = df[numeric_cols].fillna(
                df[numeric_cols].mean()
            )

            report["method"] = "Mean"


        # STEP 2: Enforce positive values (>0)
        if self.enforce_positive:

            for col in numeric_cols:

                positive_median = df[df[col] > 0][col].median()

                df.loc[df[col] <= 0, col] = positive_median

            report["positive_enforced"] = True


        # STEP 3: Convert to integer
        df[numeric_cols] = (
            df[numeric_cols]
            .round()
            .astype("Int64")
        )

        report["converted_to_int"] = True

        return df, report
