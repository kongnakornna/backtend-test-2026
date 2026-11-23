"""Use cases tested against mocked repositories — no database involved."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.dto.inputs import ClassroomInput, TeacherInput
from src.application.use_cases.classroom.commands import CreateClassroom, UpdateClassroom
from src.application.use_cases.school.queries import GetSchoolDetail
from src.application.use_cases.teacher.commands import CreateTeacher, UpdateTeacher
from src.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from src.domain.entities.classroom import Classroom
from src.domain.entities.school import School, SchoolStats
from src.domain.entities.teacher import Teacher
from src.domain.repositories.classroom_repository import ClassroomRepository
from src.domain.repositories.school_repository import SchoolRepository
from src.domain.repositories.student_repository import StudentRepository
from src.domain.repositories.teacher_repository import TeacherRepository
from src.domain.value_objects.gender import Gender


@pytest.fixture
def uow():
    uow = MagicMock()
    uow.schools = AsyncMock(spec=SchoolRepository)
    uow.classrooms = AsyncMock(spec=ClassroomRepository)
    uow.teachers = AsyncMock(spec=TeacherRepository)
    uow.students = AsyncMock(spec=StudentRepository)
    uow.commit = AsyncMock()
    uow.schools.get.return_value = School(id=1, name="A", abbreviation="A", address="A")
    uow.teachers.save.side_effect = lambda teacher: teacher
    uow.classrooms.save.side_effect = lambda classroom: classroom
    return uow


def teacher_input(**overrides) -> TeacherInput:
    data = {"school_id": 1, "first_name": "A", "last_name": "B", "gender": Gender.MALE, "classroom_ids": [5]}
    data.update(overrides)
    return TeacherInput(**data)


async def test_create_teacher_rejects_classroom_of_other_school(uow):
    uow.classrooms.get_many.return_value = [Classroom(id=5, school_id=2, year_level=1, section="1")]
    with pytest.raises(BusinessRuleError):
        await CreateTeacher(uow).execute(teacher_input())
    uow.teachers.save.assert_not_awaited()
    uow.commit.assert_not_awaited()


async def test_create_teacher_rejects_missing_classroom(uow):
    uow.classrooms.get_many.return_value = []
    with pytest.raises(BusinessRuleError, match="do not exist"):
        await CreateTeacher(uow).execute(teacher_input())


async def test_create_teacher_rejects_missing_school(uow):
    uow.schools.get.return_value = None
    with pytest.raises(BusinessRuleError, match="School 1 does not exist"):
        await CreateTeacher(uow).execute(teacher_input())


async def test_create_teacher_saves_and_commits(uow):
    uow.classrooms.get_many.return_value = [Classroom(id=5, school_id=1, year_level=1, section="1")]
    teacher = await CreateTeacher(uow).execute(teacher_input(classroom_ids=[5, 5]))
    assert teacher.classroom_ids == [5]
    uow.commit.assert_awaited_once()


async def test_update_teacher_without_classroom_ids_rechecks_existing(uow):
    uow.teachers.get.return_value = Teacher(
        id=9, school_id=1, first_name="A", last_name="B", gender=Gender.MALE, classroom_ids=[5]
    )
    uow.classrooms.get_many.return_value = [Classroom(id=5, school_id=1, year_level=1, section="1")]
    uow.schools.get.return_value = School(id=2, name="B", abbreviation="B", address="B")
    with pytest.raises(BusinessRuleError):
        await UpdateTeacher(uow).execute(9, {"school_id": 2})


async def test_create_classroom_conflict(uow):
    uow.classrooms.exists_duplicate.return_value = True
    with pytest.raises(ConflictError):
        await CreateClassroom(uow).execute(ClassroomInput(school_id=1, year_level=1, section="1"))
    uow.classrooms.save.assert_not_awaited()


async def test_update_classroom_move_blocked_by_teachers(uow):
    uow.classrooms.get.return_value = Classroom(id=3, school_id=1, year_level=1, section="1")
    uow.teachers.exists_in_classroom_from_other_school.return_value = True
    with pytest.raises(BusinessRuleError, match="teachers from another school"):
        await UpdateClassroom(uow).execute(3, {"school_id": 2})
    uow.teachers.exists_in_classroom_from_other_school.assert_awaited_once_with(3, 2)


async def test_get_school_detail_not_found(uow):
    uow.schools.get.return_value = None
    with pytest.raises(NotFoundError):
        await GetSchoolDetail(uow).execute(42)


async def test_get_school_detail_combines_stats(uow):
    uow.schools.get_stats.return_value = SchoolStats(classroom_count=2, teacher_count=3, student_count=4)
    detail = await GetSchoolDetail(uow).execute(1)
    assert (detail.classroom_count, detail.teacher_count, detail.student_count) == (2, 3, 4)
