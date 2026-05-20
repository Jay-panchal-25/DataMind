import pandas as pd


def assess_dataset_quality(df: pd.DataFrame):
    total_cells = max(len(df.index) * max(len(df.columns), 1), 1)
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = [
        column
        for column in df.columns
        if column not in numeric_columns
    ]

    warnings = []
    recommendations = []
    identifier_like = []

    if len(df) < 50:
        warnings.append("Dataset is small; model quality may be unstable.")
        recommendations.append("Collect more rows before relying on predictions.")

    if missing_cells / total_cells > 0.15:
        warnings.append("Dataset still contains a meaningful amount of missing data.")
        recommendations.append("Review high-missing columns before training models.")

    if duplicate_rows > 0:
        warnings.append("Duplicate rows are present in the cleaned dataset.")

    for column in df.columns:
        series = df[column].dropna()
        if series.empty:
            continue

        uniqueness_ratio = series.nunique() / max(len(series), 1)
        if uniqueness_ratio > 0.95 and len(series) > 25:
            identifier_like.append(column)

    if identifier_like:
        recommendations.append(
            "Treat likely identifier columns carefully during modeling: "
            + ", ".join(identifier_like[:5])
        )

    if not numeric_columns:
        warnings.append("No numeric columns were detected.")
    if not categorical_columns:
        recommendations.append("Categorical variety is limited; chart options may be reduced.")

    model_ready = (
        len(df) >= 25
        and len(df.columns) >= 2
        and missing_cells / total_cells <= 0.4
    )

    return {
        "model_ready": model_ready,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_ratio": round(missing_cells / total_cells, 4),
        "duplicate_rows": duplicate_rows,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "identifier_like_columns": identifier_like,
        "warnings": warnings,
        "recommendations": recommendations,
    }
