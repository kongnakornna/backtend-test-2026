from dataclasses import dataclass

from src.core.exceptions import BusinessRuleError
from src.domain.value_objects.text import non_blank


@dataclass
class Classroom:
    school_id: int
    year_level: int  # ชั้นปี
    section: str  # ทับ
    id: int | None = None

    def __post_init__(self) -> None:
        if isinstance(self.year_level, bool) or not isinstance(self.year_level, int) or self.year_level < 1:
            raise BusinessRuleError("year_level must be an integer >= 1")
        self.section = non_blank(self.section, "section", 20)
