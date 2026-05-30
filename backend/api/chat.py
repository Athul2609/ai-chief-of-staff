import json
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from db.base import AsyncSessionLocal, get_db
from db.models import Message
from schemas.chat import ChatRequest, ConversationHistory, MessageSchema
from services.chat import get_conversation_messages, get_or_create_conversation, save_message

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()

_SYSTEM_PROMPT = (
    "You are an AI Chief of Staff — a personal assistant for a university student named Alex Johnson. "
    "You help with academic questions, deadlines, grades, research, and general advice. "
    "Be concise and direct. When you don't know something, say so."
)


def _to_lc_messages(history: list[Message], new_message: str) -> list:
    lc = [SystemMessage(content=_SYSTEM_PROMPT)]
    for msg in history:
        if msg.role == "user":
            lc.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc.append(AIMessage(content=msg.content))
    lc.append(HumanMessage(content=new_message))
    return lc


@router.post("/")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    session_id = request.session_id or str(uuid.uuid4())

    conversation = await get_or_create_conversation(db, session_id)
    history = await get_conversation_messages(db, session_id)
    await save_message(db, conversation.id, "user", request.message)
    await db.commit()

    conversation_id = conversation.id
    lc_messages = _to_lc_messages(history, request.message)
    llm = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url, think=False)

    async def event_stream():
        full_response = ""
        yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"
        try:
            async for chunk in llm.astream(lc_messages):
                if chunk.content:
                    full_response += chunk.content
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
        finally:
            if full_response:
                async with AsyncSessionLocal() as save_db:
                    await save_message(save_db, conversation_id, "assistant", full_response)
                    await save_db.commit()
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "http://localhost:3000",
        },
    )


@router.get("/{session_id}/messages", response_model=ConversationHistory)
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    messages = await get_conversation_messages(db, session_id)
    return ConversationHistory(
        session_id=session_id,
        messages=[MessageSchema.model_validate(m) for m in messages],
    )
