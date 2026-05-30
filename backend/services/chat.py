from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Conversation, Message


async def get_or_create_conversation(db: AsyncSession, session_id: str) -> Conversation:
    result = await db.execute(
        select(Conversation).where(Conversation.session_id == session_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        conversation = Conversation(
            session_id=session_id,
            created_at=datetime.utcnow(),
        )
        db.add(conversation)
        await db.flush()
    return conversation


async def get_conversation_messages(db: AsyncSession, session_id: str) -> list[Message]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.session_id == session_id)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        return []
    return list(conversation.messages)


async def save_message(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=datetime.utcnow(),
    )
    db.add(message)
    await db.flush()
    return message
