from fastapi import APIRouter, Depends, Query, status

from src.application.dto.inputs import TeacherInput
from src.application.dto.pagination import PageParams
from src.application.unit_of_work import UnitOfWork
from src.application.use_cases.teacher.commands import CreateTeacher, DeleteTeacher, UpdateTeacher
from src.application.use_cases.teacher.queries import GetTeacherDetail, ListTeachers
from src.domain.repositories.criteria import PersonCriteria
from src.domain.value_objects.gender import Gender
from src.presentation.dependencies.database import get_uow
from src.presentation.dependencies.pagination import page_params
from src.presentation.schemas.common import ERROR_RESPONSES, PageOut
from src.presentation.schemas.teacher import TeacherDetailOut, TeacherIn, TeacherOut, TeacherPatch

router = APIRouter(prefix="/teachers", tags=["teachers"], responses=ERROR_RESPONSES)


@router.get("", response_model=PageOut[TeacherOut])
async def list_teachers(
    school: int | None = Query(None, description="school id"),
    classroom: int | None = Query(None, description="classroom id"),
    firstname: str | None = Query(None, description="contains, case-insensitive"),
    lastname: str | None = Query(None, description="contains, case-insensitive"),
    gender: Gender | None = Query(None),
    params: PageParams = Depends(page_params),
    uow: UnitOfWork = Depends(get_uow),
):
    criteria = PersonCriteria(
        school_id=school,
        classroom_id=classroom,
        first_name=firstname,
        last_name=lastname,
        gender=gender,
    )
    return await ListTeachers(uow).execute(criteria=criteria, params=params)


@router.post("", response_model=TeacherOut, status_code=status.HTTP_201_CREATED)
async def create_teacher(body: TeacherIn, uow: UnitOfWork = Depends(get_uow)):
    return await CreateTeacher(uow).execute(TeacherInput(**body.model_dump()))


@router.get("/{teacher_id}", response_model=TeacherDetailOut)
async def get_teacher(teacher_id: int, uow: UnitOfWork = Depends(get_uow)):
    return await GetTeacherDetail(uow).execute(teacher_id)


@router.put("/{teacher_id}", response_model=TeacherOut)
async def replace_teacher(teacher_id: int, body: TeacherIn, uow: UnitOfWork = Depends(get_uow)):
    return await UpdateTeacher(uow).execute(teacher_id, body.model_dump())


@router.patch("/{teacher_id}", response_model=TeacherOut)
async def update_teacher(teacher_id: int, body: TeacherPatch, uow: UnitOfWork = Depends(get_uow)):
    return await UpdateTeacher(uow).execute(teacher_id, body.changes())


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(teacher_id: int, uow: UnitOfWork = Depends(get_uow)) -> None:
    await DeleteTeacher(uow).execute(teacher_id)
