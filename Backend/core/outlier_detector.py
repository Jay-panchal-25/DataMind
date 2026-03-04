import numpy as np
import pandas as pd


def clean(df: pd.DataFrame, method: str = "median", threshold: float = 3.0) -> pd.DataFrame:
    """
    Fix both NA values and outliers in one function.
    - NA      : filled with mean or median
    - Outliers: detected with Z-Score, replaced with mean or median

    Args:
        df        : Input DataFrame
        method    : "mean" or "median"
        threshold : Z-score cutoff (default 3.0)
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        # --- Step 1: Fix NA first ---
        na_count = df[col].isna().sum()
        if na_count > 0:
            fix_value = df[col].median() if method == "median" else df[col].mean()
            df[col] = df[col].fillna(fix_value)
            print(f"[{col}] {na_count} NA(s) filled with {method} = {fix_value:.4f}")
        else:
            print(f"[{col}] No missing values")

        # --- Step 2: Fix Outliers ---
        mean = df[col].mean()
        std  = df[col].std()

        if std == 0:
            print(f"[{col}] Skipped outlier check — all values are the same")
            continue

        z_scores = (df[col] - mean).abs() / std
        outliers = z_scores > threshold
        count = outliers.sum()

        if count > 0:
            fix_value = df[col].median() if method == "median" else df[col].mean()
            df.loc[outliers, col] = fix_value
            print(f"[{col}] {count} outlier(s) fixed with {method} = {fix_value:.4f}")
        else:
            print(f"[{col}] No outliers found")

    return df


