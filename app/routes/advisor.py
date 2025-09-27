from datetime import datetime
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from config import Settings, get_settings
from ..models.schemas import (
    AdvisorResponse,
    ConsultaRequest,
    EjemploContextoResponse,
    ErrorResponse,
    HealthResponse,
    TestOpenAIResponse,
)
from ..services.openai_service import OpenAIService

router = APIRouter(prefix="/api/v1", tags=["advisor"])
logger = logging.getLogger(__name__)


def get_openai_service(settings: Annotated[Settings, Depends(get_settings)]) -> OpenAIService:
    return OpenAIService(settings=settings)


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    """Endpoint de health check."""

    try:
        return HealthResponse(
            status="healthy",
            service=settings.app_name,
            version=settings.app_version,
            timestamp=datetime.utcnow(),
        )
    except Exception as exc:  # pragma: no cover - fallback in caso improbable
        logger.error("Error en health check: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="Error interno del servidor",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=str(exc),
            ).model_dump(),
        ) from exc


@router.post(
    "/generar-respuesta",
    response_model=AdvisorResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def generar_respuesta(
    consulta: ConsultaRequest,
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)],
) -> AdvisorResponse:
    """Genera la respuesta del asesor utilizando OpenAI."""

    if not openai_service.api_key:
        logger.error("OpenAI API key no configurada")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error="Servicio no configurado correctamente",
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
                details={"missing": "OPENAI_API_KEY"},
            ).model_dump(),
        )

    try:
        resultado = await run_in_threadpool(
            openai_service.generate_advisor_response,
            consulta.asesor,
            consulta.contexto,
        )
    except ValueError as exc:
        logger.warning("Error de validación de configuración: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error=str(exc),
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ).model_dump(),
        ) from exc
    except Exception as exc:
        logger.error("Error interno en generar_respuesta: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="Error interno del servidor",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=str(exc),
            ).model_dump(),
        ) from exc

    logger.info(
        "Respuesta generada para asesor %s, success: %s",
        consulta.asesor,
        resultado.get("success"),
    )

    return AdvisorResponse(**resultado)


@router.get("/ejemplo-contexto", response_model=EjemploContextoResponse)
async def ejemplo_contexto() -> EjemploContextoResponse:
    """Devuelve ejemplos de contexto válidos."""

    ejemplos = {
        "ejemplos": [
            {
                "descripcion": "Consulta por repuestos",
                "asesor": "Andrea Gómez",
                "contexto": "nombre_cliente: 'Juan Pérez', sucursal: 'Yamaha Aceitar 134', repuesto/equipamiento_interes: 'bujías', motivo: 'repuestos_equipamiento', tipo_consulta: 'repuesto'",
            },
            {
                "descripcion": "Consulta por servicio técnico",
                "asesor": "Carlos Rodríguez",
                "contexto": "nombre_cliente: 'María González', sucursal: 'Yamaha Centro', repuesto/equipamiento_interes: 'revisión motor', motivo: 'servicio_tecnico', tipo_consulta: 'mantenimiento'",
            },
            {
                "descripcion": "Consulta general",
                "asesor": "Ana Silva",
                "contexto": "nombre_cliente: 'Cliente', sucursal: 'Yamaha Norte', repuesto/equipamiento_interes: 'información general', motivo: 'consulta_general', tipo_consulta: 'informacion'",
            },
        ],
        "formato_requerido": {
            "asesor": "string (1-100 caracteres)",
            "contexto": "string (1-2000 caracteres)",
        },
    }

    return EjemploContextoResponse(**ejemplos)


@router.post(
    "/test-openai",
    response_model=TestOpenAIResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
)
async def test_openai(
    settings: Annotated[Settings, Depends(get_settings)],
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)],
) -> TestOpenAIResponse:
    """Endpoint para probar la conexión con OpenAI (solo en desarrollo)."""

    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(
                error="Endpoint solo disponible en modo debug",
                code=status.HTTP_403_FORBIDDEN,
            ).model_dump(),
        )

    resultado = await run_in_threadpool(
        openai_service.generate_advisor_response,
        "Test",
        "nombre_cliente: 'Test', motivo: 'test'",
    )

    if not resultado.get("success"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error="Error en conexión con OpenAI",
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
                details=resultado.get("raw_response"),
            ).model_dump(),
        )

    return TestOpenAIResponse(openai_status="OK", test_result=AdvisorResponse(**resultado))
