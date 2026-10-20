from fastapi import FastAPI

from app.api.routes import router as prices_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_title,
        description=settings.description,
        version="1.0.0",
    )
    application.include_router(prices_router, prefix="/api/v1")
    return application


app = create_app()
