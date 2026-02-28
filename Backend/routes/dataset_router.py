from fastapi import APIRouter, Query, HTTPException
from routes.upload_router import DATASTORE
import numpy as np
import pandas as pd

router = APIRouter()

@router.get("/dataset")
def get_dataset(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    df = DATASTORE.get("df")

    if df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")

    total_rows = len(df)
    total_pages = (total_rows // page_size) + (
        1 if total_rows % page_size else 0
    )

    start = (page - 1) * page_size
    end = start + page_size

    paginated_df = df.iloc[start:end].copy()

    # ✅ FIX: Format datetime columns to YYYY-MM-DD (remove T00:00:00)
    datetime_cols = paginated_df.select_dtypes(include=["datetime64[ns]", "datetime64"]).columns
    for col in datetime_cols:
        paginated_df[col] = paginated_df[col].dt.strftime("%Y-%m-%d")

    # 🔥 Keep your original JSON safety logic
    paginated_df = paginated_df.astype("object").where(
        pd.notna(paginated_df),
        "Unknown"
    )

    records = paginated_df.to_dict(orient="records")

    return {
        "page": page,
        "total_pages": total_pages,
        "columns": df.columns.tolist(),
        "data": records
    }