from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ConsultaRequest(BaseModel):
    asesor: str = Field(..., min_length=1, max_length=100, description="Nombre del asesor")
    contexto: str = Field(..., min_length=1, max_length=2000, description="Contexto de la consulta")

    @field_validator("asesor", "contexto")
    @classmethod
    def strip_values(cls, value: str) -> str:
        return value.strip()


class AdvisorResponse(BaseModel):
    success: bool
    motivo: Optional[str] = Field(default=None, max_length=200)
    mensaje: Optional[str] = Field(default=None, max_length=1000)
    mensaje_original: Optional[str] = Field(default=None, max_length=1000)
    error: Optional[str] = Field(default=None, max_length=500)
    raw_response: Optional[str] = Field(default=None, max_length=2000)


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: Optional[int] = None
    details: Optional[Any] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime


class TestOpenAIResponse(BaseModel):
    openai_status: str
    test_result: AdvisorResponse


class ContextExample(BaseModel):
    descripcion: str
    asesor: str
    contexto: str


class EjemploContextoResponse(BaseModel):
    ejemplos: List[ContextExample]
    formato_requerido: Dict[str, str]
