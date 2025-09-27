import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from .routes.advisor import router as advisor_router
from .utils.error_handlers import register_error_handlers


def configure_logging(debug: bool) -> None:
    """Configura el sistema de logging."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
    )


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI."""
    configure_logging(settings.debug)

    fastapi_app = FastAPI(title=settings.app_name, version=settings.app_version)
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi_app.include_router(advisor_router)
    register_error_handlers(fastapi_app)

    return fastapi_app


app: Any = create_app()
