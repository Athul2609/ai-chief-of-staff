import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from db.base import get_db
from schemas.common import HealthResponse

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    db_status = await _check_db(db)
    ollama_status = await _check_ollama()
    overall = "ok" if db_status == "ok" and ollama_status == "ok" else "degraded"
    return HealthResponse(status=overall, db=db_status, ollama=ollama_status, model=settings.ollama_model)


async def _check_db(db: AsyncSession) -> str:
    try:
        await db.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "unreachable"


async def _check_ollama() -> str:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            return "ok" if response.status_code == 200 else "unreachable"
    except Exception:
        return "unreachable"
