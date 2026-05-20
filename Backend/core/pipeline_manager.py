from core.data_loader import DataLoader
from core.data_cleaner import data_cleaner
from core.outlier_detector import analyze_outliers
from core.quality_analyzer import assess_dataset_quality
from core.settings import settings


def run_pipeline(file_path):
    stats = {}

    raw_df, metadata = DataLoader().load(file_path)
    stats["metadata"] = metadata

    stats["initial"] = {
        "rows": raw_df.shape[0],
        "columns": raw_df.shape[1],
        "column_names": raw_df.columns.astype(str).tolist(),
        "missing_values": raw_df.isna().sum().to_dict(),
        "duplicate_rows": int(raw_df.duplicated().sum()),
    }

    cleaned_df, cleaning_report = data_cleaner(raw_df)
    stats["cleaning"] = {
        "rows_after_cleaning": cleaned_df.shape[0],
        "columns_after_cleaning": cleaned_df.shape[1],
        "duplicates_removed": cleaning_report["duplicates_removed"],
        "column_mapping": cleaning_report["column_mapping"],
        "inference": cleaning_report["inference"],
    }

    processed_df, outlier_report = analyze_outliers(
        cleaned_df,
        apply_changes=settings.APPLY_OUTLIER_CORRECTION,
    )
    stats["outliers"] = outlier_report

    stats["final"] = {
        "rows": processed_df.shape[0],
        "columns": processed_df.shape[1],
        "missing_remaining": processed_df.isna().sum().to_dict(),
    }

    quality = assess_dataset_quality(processed_df)

    return {
        "data": processed_df,
        "stats": stats,
        "quality": quality,
    }
