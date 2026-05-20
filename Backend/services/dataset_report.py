import pandas as pd

from services.json_utils import to_json_safe


def build_dataset_report(df: pd.DataFrame, stats: dict | None, insights: dict | None):
    stats = stats or {}
    insights = insights or {}

    metadata = stats.get("metadata", {})
    initial_missing = stats.get("initial", {}).get("missing_values", {})
    final_missing = stats.get("final", {}).get("missing_remaining", {})

    missing_before = sum(int(value or 0) for value in initial_missing.values())
    missing_after = sum(int(value or 0) for value in final_missing.values())

    report = {
        "overview": {
            "file_name": metadata.get("file_name"),
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "memory_usage_mb": metadata.get("memory_usage_mb", 0),
            "file_size_mb": metadata.get("file_size_mb", 0),
        },
        "fixes": {
            "duplicates_removed": int(
                stats.get("cleaning", {}).get("duplicates_removed", 0)
            ),
            "missing_before": int(missing_before),
            "missing_after": int(missing_after),
            "missing_filled": int(max(missing_before - missing_after, 0)),
            "outlier_updates": int(
                stats.get("outliers", {}).get("total_changes", 0)
            ),
            "normalized_columns": stats.get("cleaning", {}).get(
                "columns_normalized", []
            ),
        },
        "warnings": _build_warnings(stats, insights),
    }

    return to_json_safe(report)


def _build_warnings(stats: dict, insights: dict):
    warnings = []

    duplicates_removed = int(stats.get("cleaning", {}).get("duplicates_removed", 0))
    if duplicates_removed > 0:
        warnings.append(f"Removed {duplicates_removed} duplicate rows.")

    outlier_updates = int(stats.get("outliers", {}).get("total_changes", 0))
    if outlier_updates > 0:
        warnings.append(f"Corrected {outlier_updates} outlier values.")
    elif int(stats.get("outliers", {}).get("total_candidates", 0)) > 0:
        warnings.append("Potential outliers were detected but not auto-corrected.")

    remaining_missing = {
        column: int(value or 0)
        for column, value in (stats.get("final", {}).get("missing_remaining", {}) or {}).items()
        if int(value or 0) > 0
    }
    if remaining_missing:
        columns = ", ".join(list(remaining_missing.keys())[:4])
        warnings.append(f"Some missing values still remain in: {columns}.")

    strong_correlations = insights.get("correlation") or []
    if strong_correlations:
        top_pair = strong_correlations[0]
        warnings.append(
            f"Strong correlation detected between {top_pair['feature_1']} and {top_pair['feature_2']}."
        )

    return warnings
