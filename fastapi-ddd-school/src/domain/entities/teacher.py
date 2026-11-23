from dataclasses import dataclass, field

from src.core.exceptions import BusinessRuleError
from src.domain.entities.classroom import Classroom
from src.domain.value_objects.gender import Gender
from src.domain.value_objects.text import non_blank


@dataclass
class Teacher:
    school_id: int
    first_name: str
    last_name: str
    gender: Gender
    classroom_ids: list[int] = field(default_factory=list)
    id: int | None = None

    def __post_init__(self) -> None:
        self.first_name = non_blank(self.first_name, "first_name", 100)
        self.last_name = non_blank(self.last_name, "last_name", 100)
        self.gender = Gender.parse(self.gender)

    def assign_classrooms(self, classrooms: list[Classroom]) -> None:
        """Domain rule: a teacher may only teach classrooms of their own school."""
        foreign = sorted(c.id for c in classrooms if c.school_id != self.school_id)
        if foreign:
            raise BusinessRuleError(
                f"Classrooms {foreign} do not belong to school {self.school_id}"
            )
        self.classroom_ids = sorted({c.id for c in classrooms})
