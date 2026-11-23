from typing import Annotated

from pydantic import BaseModel, StringConstraints

from src.presentation.schemas.common import OutModel, PatchModel

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
Abbreviation = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Address = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]


class SchoolIn(BaseModel):
    name: Name
    abbreviation: Abbreviation
    address: Address


class SchoolPatch(PatchModel):
    name: Name | None = None
    abbreviation: Abbreviation | None = None
    address: Address | None = None


class SchoolOut(OutModel):
    id: int
    name: str
    abbreviation: str
    address: str


class SchoolDetailOut(SchoolOut):
    classroom_count: int
    teacher_count: int
    student_count: int
