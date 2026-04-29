import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from fastapi.concurrency import run_in_threadpool

from core.data_loader import DataLoader
from core.pipeline_manager import run_pipeline
from services.dataset_report import build_dataset_report
from services.insight_generator import InsightGenerator
from services.json_utils import to_json_safe
from services.insight_summarizer import summarize_insights
from services.memory_manager import MemoryManager

router = APIRouter()

# simple global storage (can upgrade later)
DATASTORE = {"df": None, "stats": None, "report": None, "memory": MemoryManager()}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    suffix = Path(file.filename).suffix.lower()

    # ----------------------------
    # VALIDATION
    # ----------------------------
    if suffix not in DataLoader.SUPPORTED_FORMATS:
        return {
            "error": f"Unsupported format. Supported: {DataLoader.SUPPORTED_FORMATS}"
        }

    try:
        # ----------------------------
        # SAVE TEMP FILE
        # ----------------------------
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp.write(await file.read())
        temp.close()

        # ----------------------------
        # RUN PIPELINE
        # ----------------------------
        result = await run_in_threadpool(run_pipeline, temp.name)

        df = result.get("data")
        stats = result.get("stats")

        if df is None:
            return {"error": "No data returned from pipeline"}

        # ----------------------------
        # GENERATE INSIGHTS
        # ----------------------------
        insights = InsightGenerator(df).generate()

        # ----------------------------
        # LLM SUMMARY
        # ----------------------------
        summary = summarize_insights(insights)

        # ----------------------------
        # DATASET REPORT
        # ----------------------------
        report = build_dataset_report(df, stats, insights)

        # ----------------------------
        # STORE DATA
        # ----------------------------
        DATASTORE["df"] = df
        DATASTORE["stats"] = to_json_safe(stats)
        DATASTORE["report"] = report
        DATASTORE["memory"].clear()

        # ----------------------------
        # FINAL RESPONSE
        # ----------------------------
        return {
            "message": "Upload successful",
            "columns": list(df.columns),
            "rows": len(df),
            "stats": to_json_safe(stats),
            "insights": to_json_safe(insights),
            "summary": summary,
            "report": report
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if "temp" in locals():
            Path(temp.name).unlink(missing_ok=True)
