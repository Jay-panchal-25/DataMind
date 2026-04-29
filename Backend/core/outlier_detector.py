import numpy as np
import pandas as pd


IDENTIFIER_KEYWORDS = {"id", "code", "index"}


def clean(df: pd.DataFrame, method: str = "median", iqr_multiplier: float = 2.0) -> pd.DataFrame:
    """
    Fill missing numeric values and replace numeric outliers using an IQR-based rule.
    This is more reliable than z-score for small and skewed datasets.
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        if _is_identifier_like(col, df[col]):
            continue

        series = pd.to_numeric(df[col], errors="coerce").astype("Float64")

        if series.isna().any():
            fill_value = series.median() if method == "median" else series.mean()
            series = series.fillna(fill_value)

        non_null = series.dropna()
        if non_null.empty or non_null.nunique() <= 2:
            df[col] = series
            continue

        q1 = non_null.quantile(0.25)
        q3 = non_null.quantile(0.75)
        iqr = q3 - q1

        if pd.isna(iqr) or iqr == 0:
            df[col] = series
            continue

        lower_bound = q1 - iqr_multiplier * iqr
        upper_bound = q3 + iqr_multiplier * iqr
        outlier_mask = (series < lower_bound) | (series > upper_bound)

        if outlier_mask.any():
            replacement = non_null.median() if method == "median" else non_null.mean()
            series.loc[outlier_mask] = replacement

        df[col] = series

    return df


def _is_identifier_like(column_name: str, series: pd.Series):
    normalized = column_name.lower().strip()

    if normalized in IDENTIFIER_KEYWORDS or normalized.endswith("_id"):
        return True

    non_null = series.dropna()
    if non_null.empty:
        return False

    uniqueness_ratio = non_null.nunique() / len(non_null)
    return uniqueness_ratio > 0.98 and non_null.is_monotonic_increasing
