from typing import Annotated

from pydantic import BaseModel, Field, PositiveInt, StringConstraints

from src.presentation.schemas.common import OutModel, PatchModel, PersonSummaryOut

YearLevel = Annotated[int, Field(ge=1, description="ชั้นปี")]
Section = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20), Field(description="ทับ")
]


class ClassroomIn(BaseModel):
    school_id: PositiveInt
    year_level: YearLevel
    section: Section


class ClassroomPatch(PatchModel):
    school_id: PositiveInt | None = None
    year_level: YearLevel | None = None
    section: Section | None = None


class ClassroomOut(OutModel):
    id: int
    school_id: int
    year_level: int
    section: str


class ClassroomDetailOut(ClassroomOut):
    teachers: list[PersonSummaryOut]
    students: list[PersonSummaryOut]
