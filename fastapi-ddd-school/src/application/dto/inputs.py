from dataclasses import dataclass, field

from src.domain.value_objects.gender import Gender


@dataclass(frozen=True)
class SchoolInput:
    name: str
    abbreviation: str
    address: str


@dataclass(frozen=True)
class ClassroomInput:
    school_id: int
    year_level: int
    section: str


@dataclass(frozen=True)
class TeacherInput:
    school_id: int
    first_name: str
    last_name: str
    gender: Gender
    classroom_ids: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class StudentInput:
    classroom_id: int
    first_name: str
    last_name: str
    gender: Gender
