from pydantic import BaseModel, PositiveInt

from src.domain.value_objects.gender import Gender
from src.presentation.schemas.classroom import ClassroomOut
from src.presentation.schemas.common import OutModel, PatchModel, PersonName


class StudentIn(BaseModel):
    classroom_id: PositiveInt
    first_name: PersonName
    last_name: PersonName
    gender: Gender


class StudentPatch(PatchModel):
    classroom_id: PositiveInt | None = None
    first_name: PersonName | None = None
    last_name: PersonName | None = None
    gender: Gender | None = None


class StudentOut(OutModel):
    id: int
    classroom_id: int
    first_name: str
    last_name: str
    gender: Gender


class StudentDetailOut(StudentOut):
    classroom: ClassroomOut
