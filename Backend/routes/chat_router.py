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

    if df is None:
        return {
            "type": "text",
            "content": "Please upload a dataset first."
        }

    chat_service = ChatService(df)

    result = chat_service.process(request.message)

    return result
