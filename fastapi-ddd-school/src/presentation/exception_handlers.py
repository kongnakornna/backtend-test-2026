from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions import AppError, BusinessRuleError, ConflictError, NotFoundError

_STATUS_BY_ERROR: dict[type[AppError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    BusinessRuleError: 422,
}


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    status_code = next(
        (code for error_type, code in _STATUS_BY_ERROR.items() if isinstance(exc, error_type)),
        status.HTTP_400_BAD_REQUEST,
    )
    return JSONResponse(status_code=status_code, content={"detail": exc.message, "code": exc.code})


async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation failed",
            "code": "validation_error",
            "errors": jsonable_encoder(exc.errors()),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
