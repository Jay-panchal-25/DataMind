from fastapi import APIRouter
from pydantic import BaseModel
from routes.upload_router import DATASTORE
import pandas as pd

router = APIRouter()


class SelectionRequest(BaseModel):
    chart_type: str
    x: str
    y: str | None = None   # 🔥 y is optional for histogram


@router.get("/columns")
def get_columns():

    df = DATASTORE.get("df")

    if df is None or df.empty:
        return {"columns": []}

    return {"columns": list(df.columns)}


@router.post("/generate-graph")
def generate_graph(request: SelectionRequest):

    df = DATASTORE.get("df")

    if df is None or df.empty:
        return {"error": "Dataset not loaded"}

    # -------------------------
    # HISTOGRAM (Single Column)
    # -------------------------
    if request.chart_type == "histogram":

        if request.x not in df.columns:
            return {"error": "Invalid column selected"}

        if not pd.api.types.is_numeric_dtype(df[request.x]):
            return {"error": "Histogram requires numeric column"}

        return {
            "chart_type": "histogram",
            "x": request.x,
            "data": df[request.x].dropna().tolist()
        }

    # -------------------------
    # All Other Charts Require X and Y
    # -------------------------
    if request.x not in df.columns or request.y not in df.columns:
        return {"error": "Invalid columns selected"}

    data_df = df[[request.x, request.y]].dropna()

    # BAR → Mean aggregation
    if request.chart_type == "bar":

        if not pd.api.types.is_numeric_dtype(data_df[request.y]):
            return {"error": "Y column must be numeric for bar chart"}
            
        grouped = (
            data_df
            .groupby(request.x)[request.y]
            .mean()
            .reset_index()
            )
        

        return {
            "chart_type": "bar",
            "aggregation": "mean",
            "x": request.x,
            "y": request.y,
            "data": grouped.to_dict(orient="records")
        }

    # PIE → Mean aggregation
    elif request.chart_type == "pie":

        if not pd.api.types.is_numeric_dtype(data_df[request.y]):
            return {"error": "Y column must be numeric for pie chart"}

        grouped = (
            data_df
            .groupby(request.x)[request.y]
            .mean()
            .reset_index()
        )

        return {
            "chart_type": "pie",
            "aggregation": "mean",
            "x": request.x,
            "y": request.y,
            "data": grouped.to_dict(orient="records")
        }

    # LINE
    elif request.chart_type == "line":

        return {
            "chart_type": "line",
            "aggregation": "none",
            "x": request.x,
            "y": request.y,
            "data": data_df.to_dict(orient="records")
        }

    # SCATTER
    elif request.chart_type == "scatter":

        return {
            "chart_type": "scatter",
            "aggregation": "none",
            "x": request.x,
            "y": request.y,
            "data": data_df.to_dict(orient="records")
        }

    return {"error": "Unsupported chart type"}