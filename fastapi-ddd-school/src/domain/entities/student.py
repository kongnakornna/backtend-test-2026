from dataclasses import dataclass

from src.domain.value_objects.gender import Gender
from src.domain.value_objects.text import non_blank


@dataclass
class Student:
    classroom_id: int
    first_name: str
    last_name: str
    gender: Gender
    id: int | None = None

    def __post_init__(self) -> None:
        self.first_name = non_blank(self.first_name, "first_name", 100)
        self.last_name = non_blank(self.last_name, "last_name", 100)
        self.gender = Gender.parse(self.gender)
