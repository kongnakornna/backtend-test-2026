from dataclasses import dataclass
from typing import Optional


@dataclass
class School:
    id: Optional[int]
    name: str
    abbreviation: str
    address: str


@dataclass(frozen=True)
class SchoolCounts:
    classroom_count: int
    teacher_count: int
    student_count: int
