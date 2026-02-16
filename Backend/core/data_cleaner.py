
from dateutil import parser

from word2number import w2n
import pandas as pd

MISSING_TOKENS = {"na", "n/a", "null", "none", "-", "--", "?", ""}


def _parse_number_words(value):
    # Convert words like "ten" into numbers; invalid values become missing.
    if pd.isna(value):
        return pd.NA
    
    text = str(value).strip().lower()
    if not text:
        return pd.NA

    # Defensive check: keep graceful behavior if dependency is unavailable.
    if w2n is None:
        return pd.NA

    try:
        return w2n.word_to_num(text)
    except (ValueError, TypeError):
        return pd.NA


def data_cleaner(df):
    """Clean mixed tabular data with dtype inference, imputation, and outlier filtering."""
    # Normalize column names: lowercase, trim, remove punctuation, and replace spaces with "_".
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
    )

    # Ensure duplicate names are unique: col, col.1, col.2, ...
    counts = {}
    new_cols = []
    for col in df.columns:
        if col not in counts:
            counts[col] = 0
            new_cols.append(col)
        else:
            counts[col] += 1
            new_cols.append(f"{col}.{counts[col]}")
    df.columns = new_cols

    # Clean object columns and convert numeric-like text when confidence is high.
    for col in df.select_dtypes(include="object").columns:
        # 1) Normalize text values.
        s = (
            df[col].astype(str).str.strip().str.lower().replace(r"\s+", " ", regex=True)
        )

        # 2) Keep safe characters (letters, digits, space, dot, minus, slash).
        s = s.str.replace(r"[^a-z0-9\s\.\-\/]", "", regex=True)

        # 3) Normalize known missing tokens.
        s = s.where(~s.isin(MISSING_TOKENS), pd.NA)

        # 4) Score numeric vs string content.
        converted = pd.to_numeric(s, errors="coerce")
        # Parse number words only where direct numeric parsing failed.
        missing_numeric_mask = converted.isna() & s.notna()
        if missing_numeric_mask.any():
            word_converted = pd.to_numeric(
                s[missing_numeric_mask].apply(_parse_number_words), errors="coerce"
            )
            converted.loc[missing_numeric_mask] = word_converted
        non_missing = s.notna()
        valid_count = non_missing.sum()

        if valid_count == 0:
            df[col] = s
            continue

        numeric_mask = converted.notna() & non_missing

        numeric_ratio = numeric_mask.sum() / valid_count

        # 5) Cast to dominant type when numeric confidence is high.
        if numeric_ratio >= 0.7:
            numeric_values = converted[numeric_mask]
            if (numeric_values % 1 == 0).all():
                df[col] = converted.astype("Int64")
            else:
                df[col] = converted.astype("Float64")
        else:
            df[col] = s

    # Remove duplicate rows after basic normalization.
    df = df.drop_duplicates()

    def fix_dtypes(frame: pd.DataFrame, threshold: float = 0.6) -> pd.DataFrame:
        # Infer numeric/datetime/bool types for object columns.
        for col in frame.columns:
            s = frame[col]

            if pd.api.types.is_numeric_dtype(s) or pd.api.types.is_datetime64_any_dtype(
                s
            ):
                continue

            if s.dtype != "object":
                continue

            s_clean = (
                s.astype(str)
                .str.strip()
                .str.lower()
                .replace({"<na>": pd.NA})
                .str.replace(r"[^\d\.\-]", "", regex=True)  # keep numeric-friendly chars
            )

            # Try normal numeric parsing first.
            num = pd.to_numeric(s_clean, errors="coerce")
            # Parse number words for values still unparsed.
            missing_num_mask = num.isna() & s.notna()
            if missing_num_mask.any():
                source_text = s.astype(str).str.strip().str.lower()
                word_num = pd.to_numeric(
                    source_text[missing_num_mask].apply(_parse_number_words),
                    errors="coerce",
                )
                num.loc[missing_num_mask] = word_num
            num_ratio = num.notna().mean()

            dt = pd.to_datetime(s, errors="coerce", infer_datetime_format=True)
            dt_ratio = dt.notna().mean()

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
            bool_vals = s.map(bool_map)
            bool_ratio = bool_vals.notna().mean()

            if num_ratio >= threshold and num_ratio >= dt_ratio:
                frame[col] = num
            elif dt_ratio >= threshold:
                frame[col] = dt
            elif bool_ratio >= threshold:
                frame[col] = bool_vals

        return frame

    df = fix_dtypes(df)



    def fix_date_columns(df):
        def parse_date(value):
            if pd.isna(value):
                    return pd.NaT
            try:
                # Parse mixed date formats and standardize output shape.
                dt = parser.parse(str(value), dayfirst=False)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                return pd.NaT

        # Convert object columns to dates only when a majority can be parsed.
        for col in df.select_dtypes(include="object").columns:
            parsed_col = df[col].apply(parse_date)

            if parsed_col.notna().sum() > len(df) * 0.5:
                df[col] = parsed_col

        return df

    df = fix_date_columns(df)

    return df
