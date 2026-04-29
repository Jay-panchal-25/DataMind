import os

from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    genai = None

load_dotenv()

DEFAULT_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or genai is None:
        return None

    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


def get_model_candidates():
    configured = os.getenv("GEMINI_MODEL", "").strip()
    fallback = os.getenv("GEMINI_FALLBACK_MODELS", "").strip()

    candidates = []

    if configured:
        candidates.append(configured)

    if fallback:
        candidates.extend(
            [item.strip() for item in fallback.split(",") if item.strip()]
        )

    for model in DEFAULT_MODELS:
        if model not in candidates:
            candidates.append(model)

    return candidates


def generate_text(system_prompt: str, user_prompt: str, temperature: float = 0.2):
    client = get_client()
    if client is None:
        return None, "Gemini client is not configured."

    last_error = "Unknown Gemini error."

    for model in get_model_candidates():
        try:
            response = client.models.generate_content(
                model=model,
                contents=f"{system_prompt.strip()}\n\n{user_prompt.strip()}",
                config={"temperature": temperature},
            )

            text = getattr(response, "text", None)
            if text and text.strip():
                return text.strip(), None
        except Exception as exc:
            last_error = str(exc)
            continue

    return None, last_error
