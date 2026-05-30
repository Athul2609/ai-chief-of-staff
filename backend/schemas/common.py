from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    db: str
    ollama: str
    model: str


class ErrorResponse(BaseModel):
    detail: str
