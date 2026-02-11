from sklearn.ensemble import IsolationForest

class OutlierDetector:
    def __init__(self, contamination=0.05):
        self.contamination = contamination

    def detect(self, df):
        numeric_cols = df.select_dtypes(include="number").columns

        if len(numeric_cols) == 0 or len(df) < 10:
            return df, {"removed": 0}

        iso = IsolationForest(
            contamination=self.contamination,
            random_state=42
        )

        preds = iso.fit_predict(df[numeric_cols])
        mask = preds == 1

        cleaned_df = df[mask]

        report = {
            "removed": (~mask).sum()
        }

        return cleaned_df, report
