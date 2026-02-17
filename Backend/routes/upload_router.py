import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File

from core.data_loader import DataLoader
from core.pipeline_manager import run_pipeline

router = APIRouter()

# simple global storage
DATASTORE = {"df": None}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    # check file format
    suffix = Path(file.filename).suffix.lower()

    if suffix not in DataLoader.SUPPORTED_FORMATS:
        return {"error": f"Unsupported format. Supported: {DataLoader.SUPPORTED_FORMATS}"}

    try:
        # save file temporarily
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp.write(await file.read())
        temp.close()

        # run pipeline
        result = run_pipeline(temp.name)

        df = result.get("data")

        if df is None:
            return {"error": "No data returned from pipeline"}

        # store globally
        DATASTORE["df"] = df

        return {
            "message": "Upload successful",
            "columns": list(df.columns),
            "rows": len(df)
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        # delete temp file
        if "temp" in locals():
            Path(temp.name).unlink(missing_ok=True)
