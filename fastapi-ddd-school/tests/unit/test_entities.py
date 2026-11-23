import pytest

from src.core.exceptions import BusinessRuleError
from src.domain.entities.classroom import Classroom
from src.domain.entities.school import School
from src.domain.entities.student import Student
from src.domain.entities.teacher import Teacher
from src.domain.value_objects.gender import Gender


def test_school_strips_and_requires_text():
    assert School(name="  A  ", abbreviation="B", address="C").name == "A"
    with pytest.raises(BusinessRuleError):
        School(name="   ", abbreviation="B", address="C")


@pytest.mark.parametrize("year_level", [0, -1, True, "1"])
def test_classroom_rejects_invalid_year_level(year_level):
    with pytest.raises(BusinessRuleError):
        Classroom(school_id=1, year_level=year_level, section="1")


def test_gender_is_parsed():
    assert Student(classroom_id=1, first_name="A", last_name="B", gender="F").gender is Gender.FEMALE
    with pytest.raises(BusinessRuleError):
        Student(classroom_id=1, first_name="A", last_name="B", gender="X")


def test_teacher_assigns_classrooms_of_same_school():
    teacher = Teacher(school_id=1, first_name="A", last_name="B", gender=Gender.MALE)
    teacher.assign_classrooms([
        Classroom(id=3, school_id=1, year_level=1, section="1"),
        Classroom(id=2, school_id=1, year_level=1, section="2"),
    ])
    assert teacher.classroom_ids == [2, 3]


def test_teacher_rejects_classroom_of_other_school():
    teacher = Teacher(school_id=1, first_name="A", last_name="B", gender=Gender.MALE)
    with pytest.raises(BusinessRuleError, match=r"\[7\]"):
        teacher.assign_classrooms([
            Classroom(id=2, school_id=1, year_level=1, section="1"),
            Classroom(id=7, school_id=2, year_level=1, section="1"),
        ])
    assert teacher.classroom_ids == []
