from typing import Any
import os

from dotenv import load_dotenv
from pydantic import BaseModel

from core.settings import settings

load_dotenv()

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None


class LangChainLLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key and ChatGoogleGenerativeAI is not None)

    def _models(self) -> list[str]:
        candidates = [settings.LLM_MODEL, *settings.LLM_FALLBACK_MODELS]
        return [item for item in candidates if item]

    def _client(self, model_name: str, temperature: float):
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=temperature,
            timeout=12,
            max_retries=1,
        )

    def invoke_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ):
        if not self.is_available():
            return None, "LangChain Gemini client is not configured."

        temp = settings.LLM_TEMPERATURE if temperature is None else temperature
        last_error = "Unknown LLM error."

        for model_name in self._models():
            try:
                client = self._client(model_name, temp)
                response = client.invoke(
                    [
                        ("system", system_prompt.strip()),
                        ("human", user_prompt.strip()),
                    ]
                )
                text = self._stringify_content(getattr(response, "content", response))
                if text:
                    return text.strip(), None
            except Exception as exc:
                last_error = str(exc)
                if self._should_abort(last_error):
                    break

        return None, last_error

    def invoke_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_model: type[BaseModel],
        temperature: float = 0,
    ):
        if not self.is_available():
            return None, "LangChain Gemini client is not configured."

        last_error = "Unknown LLM error."

        for model_name in self._models():
            try:
                client = self._client(model_name, temperature)
                structured_client = client.with_structured_output(schema_model)
                response = structured_client.invoke(
                    [
                        ("system", system_prompt.strip()),
                        ("human", user_prompt.strip()),
                    ]
                )
                if isinstance(response, schema_model):
                    return response, None
                if isinstance(response, BaseModel):
                    return schema_model.model_validate(response.model_dump()), None
                if isinstance(response, dict):
                    return schema_model.model_validate(response), None
            except Exception as exc:
                last_error = str(exc)
                if self._should_abort(last_error):
                    break

        return None, last_error

    def _stringify_content(self, value: Any):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            parts = []
            for item in value:
                text = getattr(item, "text", None)
                if text:
                    parts.append(text)
                elif isinstance(item, dict) and item.get("text"):
                    parts.append(str(item["text"]))
                else:
                    parts.append(str(item))
            return "\n".join(part for part in parts if part)
        return str(value)

    def _should_abort(self, error_text: str):
        lowered = (error_text or "").lower()
        return any(
            phrase in lowered
            for phrase in [
                "timed out",
                "deadline",
                "permission",
                "api key",
                "quota",
                "connection",
                "unavailable",
            ]
        )


llm_service = LangChainLLMService()
