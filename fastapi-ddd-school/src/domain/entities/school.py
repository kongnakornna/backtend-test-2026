from dataclasses import dataclass

from src.domain.value_objects.text import non_blank


@dataclass
class School:
    name: str
    abbreviation: str
    address: str
    id: int | None = None

    def __post_init__(self) -> None:
        self.name = non_blank(self.name, "name", 255)
        self.abbreviation = non_blank(self.abbreviation, "abbreviation", 50)
        self.address = non_blank(self.address, "address", 1000)


@dataclass(frozen=True)
class SchoolStats:
    classroom_count: int
    teacher_count: int
    student_count: int
