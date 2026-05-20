from word2number import w2n
import pandas as pd

MISSING_TOKENS = {"na", "n/a", "null", "none", "-", "--", "?", ""}
NON_NEGATIVE_KEYWORDS = {
    "age",
    "salary",
    "bonus",
    "income",
    "revenue",
    "price",
    "cost",
    "total",
    "wage",
    "pay",
    "earning",
    "profit",
    "fee",
    "tax",
    "rent",
    "amount",
    "balance",
    "budget",
    "expense",
    "spend",
    "sale",
    "quantity",
    "qty",
    "count",
    "population",
    "weight",
    "height",
    "distance",
    "score",
    "rating",
}


def _normalize_columns(columns):
    normalized = (
        pd.Index(columns)
        .astype(str)
        .str.strip()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
        .str.lower()
    )

    counts = {}
    output = []
    mapping = {}

    for original, cleaned in zip(columns, normalized):
        if cleaned not in counts:
            counts[cleaned] = 0
            final_name = cleaned
        else:
            counts[cleaned] += 1
            final_name = f"{cleaned}.{counts[cleaned]}"

        output.append(final_name)
        mapping[str(original)] = final_name

    return output, mapping


def _parse_number_words(value):
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if not text:
        return pd.NA

    try:
        return w2n.word_to_num(text.lower())
    except (ValueError, TypeError):
        return pd.NA


def _normalize_string_series(series: pd.Series):
    normalized = (
        series.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )
    lower_series = normalized.str.lower()
    return normalized.where(~lower_series.isin(MISSING_TOKENS), pd.NA)


def _infer_string_columns(frame: pd.DataFrame):
    inference_report = {
        "numeric_columns": [],
        "boolean_columns": [],
        "datetime_columns": [],
        "sensitive_numeric_columns": [],
    }

    for col in frame.columns:
        series = frame[col]
        if not pd.api.types.is_string_dtype(series):
            continue

        clean_series = _normalize_string_series(series)
        converted = pd.to_numeric(clean_series, errors="coerce")

        missing_numeric_mask = converted.isna() & clean_series.notna()
        if missing_numeric_mask.any():
            word_converted = pd.to_numeric(
                clean_series[missing_numeric_mask].apply(_parse_number_words),
                errors="coerce",
            )
            converted.loc[missing_numeric_mask] = word_converted

        valid_count = clean_series.notna().sum()
        numeric_ratio = (
            (converted.notna() & clean_series.notna()).sum() / valid_count
            if valid_count
            else 0
        )

        if numeric_ratio >= 0.8:
            non_missing = converted.dropna()
            if len(non_missing) > 0 and (non_missing % 1 == 0).all():
                frame[col] = converted.astype("Int64")
            else:
                frame[col] = converted.astype("Float64")
            inference_report["numeric_columns"].append(col)

            if any(keyword in col for keyword in NON_NEGATIVE_KEYWORDS):
                if (converted.dropna() < 0).any():
                    inference_report["sensitive_numeric_columns"].append(col)
            continue

        bool_map = {
            "true": True,
            "false": False,
            "yes": True,
            "no": False,
            "1": True,
            "0": False,
            "y": True,
            "n": False,
        }
        bool_vals = clean_series.str.lower().map(bool_map)
        if bool_vals.notna().mean() >= 0.85:
            frame[col] = bool_vals.astype("boolean")
            inference_report["boolean_columns"].append(col)
            continue

        parsed_dates = pd.to_datetime(clean_series, errors="coerce", dayfirst=True)
        if parsed_dates.notna().mean() >= 0.8:
            frame[col] = parsed_dates
            inference_report["datetime_columns"].append(col)
            continue

        frame[col] = clean_series

    return frame, inference_report


def data_cleaner(df: pd.DataFrame):
    report = {
        "column_mapping": {},
        "duplicates_removed": 0,
        "inference": {},
    }

    cleaned = df.copy()
    for col in cleaned.columns:
        try:
            cleaned[col] = cleaned[col].convert_dtypes()
        except Exception:
            pass

    normalized_columns, mapping = _normalize_columns(cleaned.columns)
    cleaned.columns = normalized_columns
    report["column_mapping"] = mapping

    original_rows = len(cleaned)
    cleaned = cleaned.drop_duplicates().copy()
    report["duplicates_removed"] = int(original_rows - len(cleaned))

    for col in cleaned.columns:
        if pd.api.types.is_string_dtype(cleaned[col]):
            cleaned[col] = _normalize_string_series(cleaned[col])

    cleaned, inference_report = _infer_string_columns(cleaned)
    report["inference"] = inference_report

    return cleaned, report
