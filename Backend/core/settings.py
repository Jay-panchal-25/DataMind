import os

from dotenv import load_dotenv

load_dotenv()


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_list(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default

    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    APP_NAME = os.getenv("APP_NAME", "DataMind")
    API_PREFIX = os.getenv("API_PREFIX", "")
    CORS_ORIGINS = _parse_list(
        os.getenv("CORS_ORIGINS"),
        ["http://localhost:5173", "http://127.0.0.1:5173"],
    )
    CORS_ALLOW_CREDENTIALS = _parse_bool(
        os.getenv("CORS_ALLOW_CREDENTIALS"),
        False,
    )
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))
    APPLY_OUTLIER_CORRECTION = _parse_bool(
        os.getenv("APPLY_OUTLIER_CORRECTION"),
        False,
    )
    SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", "90"))
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    LLM_FALLBACK_MODELS = _parse_list(
        os.getenv("LLM_FALLBACK_MODELS"),
        ["gemini-2.0-flash", "gemini-1.5-flash"],
    )
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    AUTOML_CACHE_SIZE = int(os.getenv("AUTOML_CACHE_SIZE", "6"))
    AUTOML_CV_FOLDS = int(os.getenv("AUTOML_CV_FOLDS", "3"))


settings = Settings()
