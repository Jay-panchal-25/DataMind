from dateutil import parser
from word2number import w2n
import pandas as pd

MISSING_TOKENS = {"na", "n/a", "null", "none", "-", "--", "?", ""}


def _parse_number_words(value):
    if pd.isna(value):
        return pd.NA

    text = str(value).strip().lower()
    if not text:
        return pd.NA

    try:
        return w2n.word_to_num(text)
    except (ValueError, TypeError):
        return pd.NA


def data_cleaner(df):
    """Clean mixed tabular data with dtype inference, imputation, and outlier filtering."""

    # Normalize baseline dtypes (important for pandas 3.x compatibility)
    # Safely convert dtypes without forcing Int64 on float columns
    for col in df.columns:
        try:
            df[col] = df[col].convert_dtypes()
        except Exception:
            pass  # keep original dtype if conversion fails

    # Normalize column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
    )

    # Ensure unique column names
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

    # --- STRING CLEANING + NUMERIC INFERENCE ---
    for col in df.columns:
        if not pd.api.types.is_string_dtype(df[col]):
            continue

        s = (
            df[col]
            .astype("string")
            .str.strip()
            .str.lower()
            .replace(r"\s+", " ", regex=True)
        )

        s = s.str.replace(r"[^a-z0-9\s\.\-\/]", "", regex=True)
        s = s.where(~s.isin(MISSING_TOKENS), pd.NA)

        converted = pd.to_numeric(s, errors="coerce")

        missing_numeric_mask = converted.isna() & s.notna()
        if missing_numeric_mask.any():
            word_converted = pd.to_numeric(
                s[missing_numeric_mask].apply(_parse_number_words),
                errors="coerce",
            )
            converted.loc[missing_numeric_mask] = word_converted

        non_missing = s.notna()
        valid_count = non_missing.sum()

        if valid_count == 0:
            df[col] = s
            continue

        numeric_mask = converted.notna() & non_missing
        numeric_ratio = numeric_mask.sum() / valid_count

        if numeric_ratio >= 0.7:
            # FIX: check full column (dropna) not just numeric_values subset
            all_numeric = converted.dropna()
            if len(all_numeric) > 0 and (all_numeric % 1 == 0).all():
                df[col] = converted.astype("Int64")
            else:
                df[col] = converted.astype("Float64")
        else:
            df[col] = s

    df = df.drop_duplicates()

    # --- SECONDARY TYPE INFERENCE ---
    def fix_dtypes(frame: pd.DataFrame, threshold: float = 0.6):
        for col in frame.columns:
            s = frame[col]

            # Skip already typed columns
            if (
                pd.api.types.is_numeric_dtype(s)
                or pd.api.types.is_datetime64_any_dtype(s)
                or pd.api.types.is_bool_dtype(s)
            ):
                continue

            if not pd.api.types.is_string_dtype(s):
                continue

            s = s.astype("string").str.strip()

            # ------------------------
            # 1️⃣ BOOLEAN CHECK FIRST
            # ------------------------
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

            bool_vals = s.str.lower().map(bool_map)
            bool_ratio = bool_vals.notna().mean()

            if bool_ratio >= threshold:
                frame[col] = bool_vals.astype("boolean")
                continue

            # ------------------------
            # 2️⃣ DATE CHECK BEFORE NUMERIC
            # ------------------------
            dt = pd.to_datetime(s, errors="coerce", dayfirst=True)
            dt_ratio = dt.notna().mean()

            if dt_ratio >= threshold:
                frame[col] = dt
                continue

            # ------------------------
            # 3️⃣ NUMERIC CHECK
            # ------------------------
            s_clean = (
                s.str.lower()
                .replace({"<na>": pd.NA})
                .str.replace(r"[^\d\.\-]", "", regex=True)
            )

            num = pd.to_numeric(s_clean, errors="coerce")

            # Word number conversion
            missing_num_mask = num.isna() & s.notna()
            if missing_num_mask.any():
                word_num = pd.to_numeric(
                    s[missing_num_mask].str.lower().apply(_parse_number_words),
                    errors="coerce",
                )
                num.loc[missing_num_mask] = word_num

            num_ratio = num.notna().mean()

            if num_ratio >= threshold:
                # FIX: check full column (dropna) not just a subset
                all_num = num.dropna()
                if len(all_num) > 0 and (all_num % 1 == 0).all():
                    frame[col] = num.astype("Int64")
                else:
                    frame[col] = num.astype("Float64")

        return frame

    df = fix_dtypes(df)

    def fix_date_columns(df, threshold=0.6, min_year=1900, max_year=2100):
        """
        Robust date normalization.
        Handles:
        - 23/2/1987
        - 2024-01-01
        - 01/02/2024
        - Excel serial numbers
        - Mixed formats
        """

        for col in df.columns:

            # Skip if already datetime
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                continue

            # Only attempt on string columns
            if not pd.api.types.is_string_dtype(df[col]):
                continue

            s = df[col].astype("string").str.strip()

            # Skip mostly numeric-looking columns (likely IDs)
            numeric_like_ratio = s.str.fullmatch(r"\d+").mean()
            if numeric_like_ratio > 0.8:
                continue

            def parse_value(val):
                if pd.isna(val) or val == "":
                    return pd.NaT

                # Excel serial number
                if str(val).isdigit() and len(str(val)) <= 5:
                    try:
                        base = pd.Timestamp("1899-12-30")
                        return base + pd.to_timedelta(int(val), unit="D")
                    except:
                        return pd.NaT

                try:
                    dt = parser.parse(str(val), dayfirst=True, fuzzy=False)
                except Exception:
                    try:
                        dt = parser.parse(str(val), dayfirst=False, fuzzy=False)
                    except Exception:
                        return pd.NaT

                # Year validation
                if dt.year < min_year or dt.year > max_year:
                    return pd.NaT

                return pd.to_datetime(dt.date())

            parsed = s.apply(parse_value)

            valid_ratio = parsed.notna().mean()

            if valid_ratio >= threshold:
                df[col] = parsed

        return df

    df = fix_date_columns(df)

    return df