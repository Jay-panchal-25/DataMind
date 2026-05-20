import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from core.data_loader import DataLoader
from core.pipeline_manager import run_pipeline
from core.settings import settings
from schemas.api import UploadResponse
from services.dataset_report import build_dataset_report
from services.insight_generator import InsightGenerator
from services.insight_summarizer import summarize_insights
from services.json_utils import to_json_safe
from services.session_store import session_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in DataLoader.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format. Supported: {sorted(DataLoader.SUPPORTED_FORMATS)}",
        )

    payload = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(payload) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File is too large. Max upload size is {settings.MAX_UPLOAD_MB} MB.",
        )

    try:
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp.write(payload)
        temp.close()

        result = await run_in_threadpool(run_pipeline, temp.name)
        df = result.get("data")
        stats = result.get("stats") or {}
        quality = result.get("quality") or {}

        if df is None or df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data returned from pipeline.",
            )

        insights = InsightGenerator(df).generate()
        summary = summarize_insights(insights)
        report = build_dataset_report(df, stats, insights)

        state = session_store.create_or_replace(
            df=df,
            stats=stats,
            report=report,
            quality=quality,
            insights=insights,
            upload_name=file.filename,
        )

        return {
            "session_id": state.session_id,
            "message": "Upload successful",
            "columns": list(df.columns),
            "rows": len(df),
            "stats": to_json_safe(stats),
            "insights": to_json_safe(insights),
            "summary": summary,
            "report": to_json_safe(report),
            "quality": to_json_safe(quality),
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Upload processing failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(exc)}",
        ) from exc
    finally:
        if "temp" in locals():
            Path(temp.name).unlink(missing_ok=True)
