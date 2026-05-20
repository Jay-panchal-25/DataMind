import numpy as np
import pandas as pd


IDENTIFIER_KEYWORDS = {"id", "code", "index"}


def analyze_outliers(
    df: pd.DataFrame,
    *,
    apply_changes: bool = False,
    method: str = "median",
    iqr_multiplier: float = 2.0,
):
    output = df.copy()
    numeric_cols = output.select_dtypes(include=[np.number]).columns
    columns_affected = {}
    candidate_counts = {}

    for col in numeric_cols:
        if _is_identifier_like(col, output[col]):
            continue

        series = pd.to_numeric(output[col], errors="coerce").astype("Float64")
        non_null = series.dropna()

        if non_null.empty or non_null.nunique() <= 2:
            output[col] = series
            continue

        q1 = non_null.quantile(0.25)
        q3 = non_null.quantile(0.75)
        iqr = q3 - q1

        if pd.isna(iqr) or iqr == 0:
            output[col] = series
            continue

        lower_bound = q1 - iqr_multiplier * iqr
        upper_bound = q3 + iqr_multiplier * iqr
        outlier_mask = (series < lower_bound) | (series > upper_bound)
        candidate_count = int(outlier_mask.sum())

        if candidate_count <= 0:
            output[col] = series
            continue

        candidate_counts[col] = candidate_count
        if apply_changes:
            replacement = non_null.median() if method == "median" else non_null.mean()
            series.loc[outlier_mask] = replacement
            columns_affected[col] = candidate_count

        output[col] = series

    return output, {
        "applied": apply_changes,
        "candidate_columns": candidate_counts,
        "columns_affected": columns_affected,
        "total_candidates": int(sum(candidate_counts.values())),
        "total_changes": int(sum(columns_affected.values())),
    }


def _is_identifier_like(column_name: str, series: pd.Series):
    normalized = column_name.lower().strip()

    if normalized in IDENTIFIER_KEYWORDS or normalized.endswith("_id"):
        return True

    non_null = series.dropna()
    if non_null.empty:
        return False

    uniqueness_ratio = non_null.nunique() / len(non_null)
    return uniqueness_ratio > 0.98 and non_null.is_monotonic_increasing
