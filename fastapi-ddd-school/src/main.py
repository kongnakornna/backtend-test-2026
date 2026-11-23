from fastapi import APIRouter, FastAPI

from src.core.config import get_settings
from src.core.logging import setup_logging
from src.presentation.api.v1 import classrooms, schools, students, teachers
from src.presentation.exception_handlers import register_exception_handlers


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(title=settings.app_name, version="1.0.0")
    register_exception_handlers(app)

    api_v1 = APIRouter(prefix="/api/v1")
    for module in (schools, classrooms, teachers, students):
        api_v1.include_router(module.router)
    app.include_router(api_v1)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
