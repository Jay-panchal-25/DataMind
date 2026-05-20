import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from core.settings import settings

try:
    from xgboost import XGBClassifier, XGBRegressor
except ImportError:
    XGBClassifier = None
    XGBRegressor = None


class AutoMLEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.problem_type = None
        self.best_model_name = None
        self.model = None
        self.feature_columns = []
        self.target_column = None
        self.transformed_feature_names = []
        self.target_labels = None

    def detect_problem_type(self, target_col: str):
        target = self.df[target_col]

        if pd.api.types.is_bool_dtype(target):
            return "classification"

        if pd.api.types.is_numeric_dtype(target):
            unique_count = target.nunique(dropna=True)
            uniqueness_ratio = unique_count / max(len(target.dropna()), 1)
            if 2 <= unique_count <= 12 and uniqueness_ratio <= 0.2:
                return "classification"
            return "regression"

        return "classification"

    def _normalize_features(self, frame: pd.DataFrame):
        normalized = frame.copy()

        for column in normalized.columns:
            series = normalized[column]

            if pd.api.types.is_numeric_dtype(series):
                normalized[column] = pd.to_numeric(series, errors="coerce").astype(float)
                continue

            if pd.api.types.is_bool_dtype(series):
                normalized[column] = (
                    series.astype("boolean").astype("object").where(series.notna(), None)
                )
                continue

            normalized[column] = (
                series.astype("object").where(pd.notna(series), None)
            )

        return normalized

    def _prepare_dataset(self, target_col: str):
        data = self.df.dropna(subset=[target_col]).copy()
        if data.empty:
            raise ValueError("No training rows remain after removing empty target values.")

        X = self._normalize_features(data.drop(columns=[target_col]).copy())
        y = data[target_col].copy()
        self.feature_columns = X.columns.tolist()
        self.target_column = target_col
        self.target_labels = None

        if self.problem_type == "regression":
            y = pd.to_numeric(y, errors="coerce").astype(float)
        elif self.problem_type == "classification" and not pd.api.types.is_numeric_dtype(y):
            categories = pd.Categorical(y.astype(str))
            self.target_labels = {
                index: label for index, label in enumerate(categories.categories.tolist())
            }
            y = pd.Series(categories.codes, index=y.index)

        numeric_features = X.select_dtypes(include="number").columns.tolist()
        categorical_features = [
            column for column in X.columns if column not in numeric_features
        ]

        numeric_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "encoder",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,
                    ),
                ),
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_pipeline, numeric_features),
                ("cat", categorical_pipeline, categorical_features),
            ],
            remainder="drop",
        )

        return X, y, preprocessor

    def get_models(self):
        if self.problem_type == "classification":
            models = {
                "logistic_regression": LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
                "random_forest": RandomForestClassifier(
                    n_estimators=250,
                    random_state=42,
                    class_weight="balanced",
                ),
            }
            if XGBClassifier is not None:
                models["xgboost"] = XGBClassifier(
                    n_estimators=250,
                    max_depth=6,
                    learning_rate=0.08,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    eval_metric="logloss",
                    random_state=42,
                )
            return models

        models = {
            "linear_regression": LinearRegression(),
            "random_forest": RandomForestRegressor(
                n_estimators=250,
                random_state=42,
            ),
        }
        if XGBRegressor is not None:
            models["xgboost"] = XGBRegressor(
                n_estimators=350,
                max_depth=6,
                learning_rate=0.08,
                subsample=0.9,
                colsample_bytree=0.9,
                objective="reg:squarederror",
                random_state=42,
            )
        return models

    def _score_pipeline(self, pipeline, X, y):
        scoring = "accuracy" if self.problem_type == "classification" else "r2"
        folds = min(settings.AUTOML_CV_FOLDS, max(len(X), 2))
        if self.problem_type == "classification":
            class_counts = y.value_counts()
            if class_counts.min() < 2 or folds < 2:
                return None
            folds = min(folds, int(class_counts.min()))
        elif folds < 2:
            return None

        scores = cross_val_score(pipeline, X, y, cv=folds, scoring=scoring)
        mean_score = float(np.mean(scores))
        if np.isnan(mean_score) or np.isinf(mean_score):
            return None
        return mean_score

    def _extract_feature_names(self):
        if self.model is None:
            return []

        preprocessor = self.model.named_steps["preprocessor"]
        try:
            feature_names = preprocessor.get_feature_names_out()
            return [str(item) for item in feature_names]
        except Exception:
            return self.feature_columns

    def _collect_metrics(self, y_test, predictions):
        if self.problem_type == "classification":
            return {
                "accuracy": float(accuracy_score(y_test, predictions)),
                "f1_weighted": float(
                    f1_score(y_test, predictions, average="weighted")
                ),
            }

        return {
            "r2": float(r2_score(y_test, predictions)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
            "mae": float(mean_absolute_error(y_test, predictions)),
        }

    def _metric_for_selection(self, metrics: dict):
        value = (
            metrics.get("accuracy")
            if self.problem_type == "classification"
            else metrics.get("r2")
        )

        if value is not None:
            value = float(value)
            if not np.isnan(value) and not np.isinf(value):
                return value

        if self.problem_type == "regression":
            rmse = metrics.get("rmse")
            if rmse is not None:
                rmse = float(rmse)
                if not np.isnan(rmse) and not np.isinf(rmse):
                    return -rmse

        return None

    def train(self, target_col: str):
        self.problem_type = self.detect_problem_type(target_col)
        X, y, preprocessor = self._prepare_dataset(target_col)

        if len(X) < 5:
            raise ValueError("Prediction requires at least 5 non-empty rows.")

        stratify = (
            y if self.problem_type == "classification" and y.nunique() > 1 else None
        )
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=stratify,
        )

        best_score = -float("inf")
        best_pipeline = None
        best_name = None
        model_scores = {}
        holdout_metrics = {}

        for name, model in self.get_models().items():
            pipeline = Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
                    ("model", model),
                ]
            )

            cv_score = self._score_pipeline(pipeline, X_train, y_train)
            pipeline.fit(X_train, y_train)
            predictions = pipeline.predict(X_test)
            metrics = self._collect_metrics(y_test, predictions)

            selection_score = cv_score
            if selection_score is None:
                selection_score = self._metric_for_selection(metrics)
            if selection_score is None:
                selection_score = -float("inf")

            model_scores[name] = {
                "cv_score": None if cv_score is None else float(cv_score),
                "holdout": metrics,
            }
            holdout_metrics[name] = metrics

            if best_pipeline is None or selection_score > best_score:
                best_score = selection_score
                best_pipeline = pipeline
                best_name = name

        if best_pipeline is None:
            raise ValueError(
                "Could not train a usable prediction model for this dataset."
            )

        self.model = best_pipeline
        self.best_model_name = best_name
        self.transformed_feature_names = self._extract_feature_names()

        best_predictions = best_pipeline.predict(X_test)
        metrics = self._collect_metrics(y_test, best_predictions)
        metrics["selection_score"] = float(best_score)

        return {
            "metrics": metrics,
            "all_model_scores": model_scores,
            "training_rows": int(len(X_train)),
            "validation_rows": int(len(X_test)),
        }

    def feature_importance(self):
        if self.model is None:
            return {}

        estimator = self.model.named_steps["model"]
        importances = getattr(estimator, "feature_importances_", None)
        if importances is None:
            return {}

        feature_names = self.transformed_feature_names or self.feature_columns
        pairs = [
            (name, float(score))
            for name, score in zip(feature_names, importances)
        ]
        pairs.sort(key=lambda item: item[1], reverse=True)
        return dict(pairs[:12])

    def predict_single(self, raw_inputs: dict):
        if self.model is None:
            return None, "Prediction model is not initialized."

        missing_features = [
            column for column in self.feature_columns if column not in raw_inputs
        ]
        if missing_features:
            return None, f"Missing input values for: {', '.join(missing_features)}"

        input_df = self._normalize_features(pd.DataFrame(
            [{column: raw_inputs.get(column) for column in self.feature_columns}]
        ))

        try:
            prediction = self.model.predict(input_df)[0]
        except Exception as exc:
            return None, f"Prediction failed: {str(exc)}"

        if isinstance(prediction, np.generic):
            prediction = prediction.item()

        if self.problem_type == "classification" and self.target_labels is not None:
            prediction = self.target_labels.get(int(prediction), prediction)

        return prediction, None

    def run(self, target_col, prediction_inputs=None):
        if target_col not in self.df.columns:
            return {"error": f"{target_col} not found"}

        training_summary = self.train(target_col)
        prediction_value = None

        if prediction_inputs:
            prediction_value, error = self.predict_single(prediction_inputs)
            if error:
                return {"error": error}

        return {
            "type": "prediction",
            "model": self.best_model_name,
            "task_type": self.problem_type,
            "target": target_col,
            "metrics": training_summary["metrics"],
            "predictions": [prediction_value] if prediction_inputs else None,
            "all_model_scores": training_summary["all_model_scores"],
            "feature_importance": self.feature_importance(),
            "input_values": prediction_inputs or None,
            "training_rows": training_summary["training_rows"],
            "validation_rows": training_summary["validation_rows"],
            "xgboost_available": XGBClassifier is not None and XGBRegressor is not None,
        }
