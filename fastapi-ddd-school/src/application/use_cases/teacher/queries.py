from src.application.dto.details import TeacherDetail
from src.application.dto.pagination import Page, PageParams
from src.application.use_cases.base import UseCase, get_or_404
from src.domain.entities.teacher import Teacher
from src.domain.repositories.criteria import PersonCriteria


class ListTeachers(UseCase):
    async def execute(self, *, criteria: PersonCriteria, params: PageParams) -> Page[Teacher]:
        items, total = await self.uow.teachers.search(
            criteria, offset=params.offset, limit=params.page_size
        )
        return Page(items=items, total=total, page=params.page, page_size=params.page_size)


class GetTeacherDetail(UseCase):
    async def execute(self, teacher_id: int) -> TeacherDetail:
        teacher: Teacher = await get_or_404(self.uow.teachers, teacher_id, "Teacher")
        classrooms = await self.uow.classrooms.get_many(teacher.classroom_ids)
        return TeacherDetail(
            id=teacher.id,
            school_id=teacher.school_id,
            first_name=teacher.first_name,
            last_name=teacher.last_name,
            gender=teacher.gender,
            classrooms=classrooms,
        )
