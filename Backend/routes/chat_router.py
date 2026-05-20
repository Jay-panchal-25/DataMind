import logging

from fastapi import APIRouter, Header, HTTPException, status

from schemas.api import ChatRequest, ChatResponse
from services.chat_service import ChatService
from services.session_store import session_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    x_session_id: str | None = Header(default=None),
):
    state = session_store.get(x_session_id)
    normalized_message = request.message.strip().lower()
    greeting_tokens = {"hi", "hello", "hey", "hola", "namaste"}

    if normalized_message.rstrip("!. ") in greeting_tokens:
        if state is None or state.df is None or state.df.empty:
            return {
                "type": "text",
                "content": "Hello! Upload a dataset first, then ask me about your data.",
            }

    if state is None or state.df is None or state.df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset session not found. Please upload a dataset first.",
        )

    try:
        chat_service = ChatService(
            state.df,
            memory=state.memory,
            session_state=state,
            quality=state.quality,
        )
        result = chat_service.process(request.message)
        if result is None:
            return {
                "type": "text",
                "content": "I couldn't process your request.",
            }
        return result
    except Exception as exc:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(exc)}",
        ) from exc
