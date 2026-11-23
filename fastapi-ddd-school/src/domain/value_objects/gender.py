from enum import StrEnum

from src.core.exceptions import BusinessRuleError


class Gender(StrEnum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

    @classmethod
    def parse(cls, value: "Gender | str") -> "Gender":
        try:
            return cls(value)
        except ValueError:
            allowed = ", ".join(g.value for g in cls)
            raise BusinessRuleError(f"gender must be one of: {allowed}") from None
