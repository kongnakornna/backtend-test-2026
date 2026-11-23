from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from src.domain.value_objects.gender import Gender

T = TypeVar("T")

PersonName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class OutModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PageOut(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ErrorOut(BaseModel):
    detail: str
    code: str


class PatchModel(BaseModel):
    """Base for PATCH bodies: every field optional, but an explicit null is rejected."""

    @model_validator(mode="after")
    def _reject_nulls(self) -> "PatchModel":
        nulls = sorted(name for name in self.model_fields_set if getattr(self, name) is None)
        if nulls:
            raise ValueError(f"Fields cannot be null: {', '.join(nulls)}")
        return self

    def changes(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class PersonSummaryOut(OutModel):
    id: int
    first_name: str
    last_name: str
    gender: Gender


ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorOut, "description": "Resource not found"},
    409: {"model": ErrorOut, "description": "Conflicts with existing data"},
    422: {"description": "Validation error or business rule violation"},
}
