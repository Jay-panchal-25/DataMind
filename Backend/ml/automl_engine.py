import pandas as pd
import numpy as np

from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from pandas.api.types import is_bool_dtype, is_numeric_dtype, is_object_dtype, is_string_dtype


class AutoMLEngine:

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.model = None
        self.problem_type = None
        self.encoders = {}
        self.scaler = None
        self.best_model_name = None
        self.feature_columns = []

    def detect_problem_type(self, target_col):
        if is_numeric_dtype(self.df[target_col]):
            return "regression"

        if (
            is_object_dtype(self.df[target_col])
            or is_string_dtype(self.df[target_col])
            or is_bool_dtype(self.df[target_col])
        ):
            return "classification"

        return "regression"

    def preprocess(self, target_col):
        df = self.df.dropna().copy()

        X = df.drop(columns=[target_col])
        y = df[target_col]
        self.feature_columns = X.columns.tolist()

        for col in X.columns:
            if is_object_dtype(X[col]) or is_string_dtype(X[col]) or is_bool_dtype(X[col]):
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.encoders[col] = le
            elif not is_numeric_dtype(X[col]):
                X[col] = pd.to_numeric(X[col], errors="coerce")

        if is_object_dtype(y) or is_string_dtype(y) or is_bool_dtype(y):
            le = LabelEncoder()
            y = le.fit_transform(y.astype(str))
            self.encoders[target_col] = le

        self.scaler = StandardScaler()
        X = self.scaler.fit_transform(X)

        return X, y

    def get_models(self):
        if self.problem_type == "classification":
            return {
                "rf": RandomForestClassifier(n_estimators=100, random_state=42),
                "gb": GradientBoostingClassifier(random_state=42),
            }

        return {
            "rf": RandomForestRegressor(n_estimators=100, random_state=42),
            "gb": GradientBoostingRegressor(random_state=42),
        }

    def train(self, target_col):
        self.problem_type = self.detect_problem_type(target_col)
        X, y = self.preprocess(target_col)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        models = self.get_models()

        best_score = -float("inf")
        best_model = None
        best_name = None
        results = {}

        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            if self.problem_type == "classification":
                score = accuracy_score(y_test, preds)
            else:
                score = r2_score(y_test, preds)

            results[name] = float(score)

            if score > best_score:
                best_score = score
                best_model = model
                best_name = name

        self.model = best_model
        self.best_model_name = best_name

        metrics = (
            {"accuracy": float(best_score)}
            if self.problem_type == "classification"
            else {
                "r2": float(best_score),
                "rmse": float(np.sqrt(mean_squared_error(y_test, best_model.predict(X_test)))),
            }
        )

        return best_score, X_test, results, metrics

    def explain(self, X_sample):
        try:
            import shap

            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_sample)

            if isinstance(shap_values, list):
                shap_values = shap_values[0]

            importance = np.abs(shap_values).mean(axis=0)
            return importance.tolist()

        except Exception:
            return [0.0] * X_sample.shape[1]

    def predict_single(self, raw_inputs: dict):
        if not self.feature_columns:
            return None, "Prediction model is not initialized."

        missing_features = [
            column for column in self.feature_columns
            if column not in raw_inputs
        ]
        if missing_features:
            return None, f"Missing input values for: {', '.join(missing_features)}"

        row = {}
        for column in self.feature_columns:
            value = raw_inputs[column]

            if column in self.encoders:
                encoder = self.encoders[column]
                classes = set(encoder.classes_)
                value_as_text = str(value)
                if value_as_text not in classes:
                    return None, (
                        f"Unknown value '{value}' for {column}. "
                        f"Expected one of: {', '.join(map(str, encoder.classes_[:10]))}"
                    )
                row[column] = encoder.transform([value_as_text])[0]
            else:
                try:
                    row[column] = float(value)
                except Exception:
                    return None, f"Could not convert {column} value '{value}' to a number."

        input_df = pd.DataFrame([row], columns=self.feature_columns)
        transformed = self.scaler.transform(input_df)
        prediction = self.model.predict(transformed)[0]

        return prediction, None

    def run(self, target_col, prediction_inputs=None):
        if target_col not in self.df.columns:
            return {"error": f"{target_col} not found"}

        _, X_test, all_scores, metrics = self.train(target_col)
        sample = X_test[:50]
        importance = self.explain(sample)

        feature_importance = {
            feature: float(score)
            for feature, score in zip(self.feature_columns, importance)
        }

        prediction_value = None
        if prediction_inputs:
            prediction_value, error = self.predict_single(prediction_inputs)
            if error:
                return {"error": error}

            if target_col in self.encoders:
                prediction_value = self.encoders[target_col].inverse_transform(
                    [int(prediction_value)]
                )[0]
            elif isinstance(prediction_value, np.generic):
                prediction_value = prediction_value.item()

        return {
            "type": "prediction",
            "model": self.best_model_name,
            "task_type": self.problem_type,
            "target": target_col,
            "metrics": metrics,
            "predictions": [prediction_value] if prediction_inputs else None,
            "all_model_scores": all_scores,
            "feature_importance": feature_importance,
            "input_values": prediction_inputs or None,
        }
