from src.application.dto.details import SchoolDetail
from src.application.dto.pagination import Page, PageParams
from src.application.use_cases.base import UseCase, get_or_404
from src.domain.entities.school import School


class ListSchools(UseCase):
    async def execute(self, *, name: str | None, params: PageParams) -> Page[School]:
        items, total = await self.uow.schools.search(
            name=name, offset=params.offset, limit=params.page_size
        )
        return Page(items=items, total=total, page=params.page, page_size=params.page_size)


class GetSchoolDetail(UseCase):
    async def execute(self, school_id: int) -> SchoolDetail:
        school: School = await get_or_404(self.uow.schools, school_id, "School")
        stats = await self.uow.schools.get_stats(school_id)
        return SchoolDetail(
            id=school.id,
            name=school.name,
            abbreviation=school.abbreviation,
            address=school.address,
            classroom_count=stats.classroom_count,
            teacher_count=stats.teacher_count,
            student_count=stats.student_count,
        )
