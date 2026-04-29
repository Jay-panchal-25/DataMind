from fastapi import APIRouter
from pydantic import BaseModel

from services.chat_service import ChatService
from routes.upload_router import DATASTORE

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(request: ChatRequest):

    df = DATASTORE.get("df")
    memory = DATASTORE.get("memory")

    if df is None or df.empty:
        return {
            "type": "text",
            "content": "Please upload a dataset first."
        }

    try:
        chat_service = ChatService(df, memory=memory)
        result = chat_service.process(request.message)

        # safe fallback (important for LLM errors / crashes)
        if result is None:
            return {
                "type": "text",
                "content": "I couldn't process your request."
            }

        return result

    except Exception as e:
        return {
            "type": "text",
            "content": f"Chat error: {str(e)}"
        }
