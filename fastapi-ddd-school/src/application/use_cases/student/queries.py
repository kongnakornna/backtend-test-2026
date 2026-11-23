from src.application.dto.details import StudentDetail
from src.application.dto.pagination import Page, PageParams
from src.application.use_cases.base import UseCase, get_or_404
from src.domain.entities.classroom import Classroom
from src.domain.entities.student import Student
from src.domain.repositories.criteria import PersonCriteria


class ListStudents(UseCase):
    async def execute(self, *, criteria: PersonCriteria, params: PageParams) -> Page[Student]:
        items, total = await self.uow.students.search(
            criteria, offset=params.offset, limit=params.page_size
        )
        return Page(items=items, total=total, page=params.page, page_size=params.page_size)


class GetStudentDetail(UseCase):
    async def execute(self, student_id: int) -> StudentDetail:
        student: Student = await get_or_404(self.uow.students, student_id, "Student")
        classroom: Classroom = await get_or_404(self.uow.classrooms, student.classroom_id, "Classroom")
        return StudentDetail(
            id=student.id,
            classroom_id=student.classroom_id,
            first_name=student.first_name,
            last_name=student.last_name,
            gender=student.gender,
            classroom=classroom,
        )
