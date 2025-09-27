"""Compatibilidad para ejecutar la aplicación con `python app.py`."""

from app.main import app

__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    from config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
