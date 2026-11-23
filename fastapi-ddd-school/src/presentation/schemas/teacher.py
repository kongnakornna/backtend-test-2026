from pydantic import BaseModel, Field, PositiveInt

from src.domain.value_objects.gender import Gender
from src.presentation.schemas.classroom import ClassroomOut
from src.presentation.schemas.common import OutModel, PatchModel, PersonName


class TeacherIn(BaseModel):
    school_id: PositiveInt
    first_name: PersonName
    last_name: PersonName
    gender: Gender
    classroom_ids: list[PositiveInt] = Field(default_factory=list)


class TeacherPatch(PatchModel):
    school_id: PositiveInt | None = None
    first_name: PersonName | None = None
    last_name: PersonName | None = None
    gender: Gender | None = None
    classroom_ids: list[PositiveInt] | None = None


class TeacherOut(OutModel):
    id: int
    school_id: int
    first_name: str
    last_name: str
    gender: Gender
    classroom_ids: list[int]


class TeacherDetailOut(OutModel):
    id: int
    school_id: int
    first_name: str
    last_name: str
    gender: Gender
    classrooms: list[ClassroomOut]
