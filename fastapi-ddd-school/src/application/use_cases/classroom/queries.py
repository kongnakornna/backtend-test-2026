from src.application.dto.details import ClassroomDetail
from src.application.dto.pagination import Page, PageParams
from src.application.use_cases.base import UseCase, get_or_404
from src.domain.entities.classroom import Classroom
from src.domain.repositories.criteria import PersonCriteria


class ListClassrooms(UseCase):
    async def execute(self, *, school_id: int | None, params: PageParams) -> Page[Classroom]:
        items, total = await self.uow.classrooms.search(
            school_id=school_id, offset=params.offset, limit=params.page_size
        )
        return Page(items=items, total=total, page=params.page, page_size=params.page_size)


class GetClassroomDetail(UseCase):
    async def execute(self, classroom_id: int) -> ClassroomDetail:
        classroom: Classroom = await get_or_404(self.uow.classrooms, classroom_id, "Classroom")
        in_room = PersonCriteria(classroom_id=classroom_id)
        teachers, _ = await self.uow.teachers.search(in_room)
        students, _ = await self.uow.students.search(in_room)
        return ClassroomDetail(
            id=classroom.id,
            school_id=classroom.school_id,
            year_level=classroom.year_level,
            section=classroom.section,
            teachers=teachers,
            students=students,
        )
