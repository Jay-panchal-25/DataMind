from core.data_loader import DataLoader
from core.data_cleaner import data_cleaner
from core.outlier_detector import clean

import pandas as pd


def run_pipeline(file_path):
    """
    Full data pipeline:
    - Load
    - Clean
    - Outlier handling
    - Return cleaned data + stats
    """

    stats = {}

    # ----------------------------
    # STEP 1: LOAD
    # ----------------------------
    df, metadata = DataLoader().load(file_path)
    stats["metadata"] = metadata

    original_shape = df.shape

    # ----------------------------
    # STEP 2: INITIAL ANALYSIS
    # ----------------------------
    stats["initial"] = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": df.isna().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum())
    }

    # ----------------------------
    # STEP 3: CLEANING
    # ----------------------------
    before_clean = df.copy()

    df = data_cleaner(df)

    stats["cleaning"] = {
        "rows_after_cleaning": df.shape[0],
        "columns_after_cleaning": df.shape[1],
        "duplicates_removed": int(original_shape[0] - df.shape[0]),
        "columns_normalized": list(df.columns)
    }

    # ----------------------------
    # STEP 4: OUTLIER HANDLING
    # ----------------------------
    before_outlier = df.copy()

    df = clean(df)

    numeric_cols = df.select_dtypes(include="number").columns

    outlier_changes = {}

    for col in numeric_cols:
        before_series = before_outlier[col]
        after_series = df[col]

        changed = (before_series != after_series).sum()

        if changed > 0:
            outlier_changes[col] = int(changed)

    stats["outliers"] = {
        "columns_affected": outlier_changes,
        "total_changes": sum(outlier_changes.values())
    }

    # ----------------------------
    # FINAL OUTPUT
    # ----------------------------
    stats["final"] = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_remaining": df.isna().sum().to_dict()
    }

    return {
        "data": df,
        "stats": stats
    }