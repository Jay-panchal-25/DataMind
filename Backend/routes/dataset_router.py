from fastapi import APIRouter, Query, HTTPException
from routes.upload_router import DATASTORE

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

    paginated_df = df.iloc[start:end]

    return {
        "page": page,
        "total_pages": total_pages,
        "columns": df.columns.tolist(),
        "data": paginated_df.to_dict(orient="records")
    }