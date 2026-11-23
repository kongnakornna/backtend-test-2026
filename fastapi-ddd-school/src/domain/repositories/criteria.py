from dataclasses import dataclass

from src.domain.value_objects.gender import Gender


@dataclass(frozen=True)
class PersonCriteria:
    """Search filters shared by teachers and students. None = no filter."""

    school_id: int | None = None
    classroom_id: int | None = None
    first_name: str | None = None  # case-insensitive "contains"
    last_name: str | None = None  # case-insensitive "contains"
    gender: Gender | None = None
