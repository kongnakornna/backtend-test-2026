from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.domain.exceptions import SchoolNotFoundError
from src.infrastructure.db.session import Base, engine
from src.presentation.api.v1.schools import router as schools_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Starter convenience: create tables on startup. Use Alembic migrations
    # once the schema starts changing.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="School API DDD", lifespan=lifespan)


@app.exception_handler(SchoolNotFoundError)
def school_not_found_handler(request: Request, exc: SchoolNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


app.include_router(schools_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health():
    return {"status": "ok"}
