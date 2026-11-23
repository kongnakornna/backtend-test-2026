from dataclasses import dataclass

from src.domain.entities.classroom import Classroom
from src.domain.entities.student import Student
from src.domain.entities.teacher import Teacher
from src.domain.value_objects.gender import Gender


@dataclass
class SchoolDetail:
    id: int
    name: str
    abbreviation: str
    address: str
    classroom_count: int
    teacher_count: int
    student_count: int


@dataclass
class ClassroomDetail:
    id: int
    school_id: int
    year_level: int
    section: str
    teachers: list[Teacher]
    students: list[Student]


@dataclass
class TeacherDetail:
    id: int
    school_id: int
    first_name: str
    last_name: str
    gender: Gender
    classrooms: list[Classroom]


@dataclass
class StudentDetail:
    id: int
    classroom_id: int
    first_name: str
    last_name: str
    gender: Gender
    classroom: Classroom
