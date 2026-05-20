from fastapi import APIRouter, Header, HTTPException, Query, status
import pandas as pd

from schemas.api import DatasetResponse
from services.json_utils import to_json_safe
from services.session_store import session_store

router = APIRouter()


@router.get("/dataset", response_model=DatasetResponse)
def get_dataset(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    x_session_id: str | None = Header(default=None),
):
    state = session_store.get(x_session_id)
    if state is None or state.df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset session not found. Please upload a dataset again.",
        )

    df = state.df
    total_rows = len(df)
    total_pages = max((total_rows + page_size - 1) // page_size, 1)

    if page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Page {page} is out of range. Total pages: {total_pages}.",
        )

    start = (page - 1) * page_size
    end = start + page_size

    paginated_df = df.iloc[start:end].copy()
    datetime_cols = paginated_df.select_dtypes(
        include=["datetime64[ns]", "datetime64"]
    ).columns

    for col in datetime_cols:
        paginated_df[col] = paginated_df[col].dt.strftime("%Y-%m-%d")

    paginated_df = paginated_df.astype("object").where(
        pd.notna(paginated_df),
        None,
    )

    return {
        "page": page,
        "total_pages": total_pages,
        "columns": df.columns.tolist(),
        "data": to_json_safe(paginated_df.to_dict(orient="records")),
        "stats": to_json_safe(state.stats),
        "report": to_json_safe(state.report),
        "quality": to_json_safe(state.quality),
    }
