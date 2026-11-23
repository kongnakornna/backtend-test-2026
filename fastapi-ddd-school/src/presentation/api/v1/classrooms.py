from fastapi import APIRouter, Depends, Query, status

from src.application.dto.inputs import ClassroomInput
from src.application.dto.pagination import PageParams
from src.application.unit_of_work import UnitOfWork
from src.application.use_cases.classroom.commands import (
    CreateClassroom,
    DeleteClassroom,
    UpdateClassroom,
)
from src.application.use_cases.classroom.queries import GetClassroomDetail, ListClassrooms
from src.presentation.dependencies.database import get_uow
from src.presentation.dependencies.pagination import page_params
from src.presentation.schemas.classroom import (
    ClassroomDetailOut,
    ClassroomIn,
    ClassroomOut,
    ClassroomPatch,
)
from src.presentation.schemas.common import ERROR_RESPONSES, PageOut

router = APIRouter(prefix="/classrooms", tags=["classrooms"], responses=ERROR_RESPONSES)


@router.get("", response_model=PageOut[ClassroomOut])
async def list_classrooms(
    school: int | None = Query(None, description="school id"),
    params: PageParams = Depends(page_params),
    uow: UnitOfWork = Depends(get_uow),
):
    return await ListClassrooms(uow).execute(school_id=school, params=params)


@router.post("", response_model=ClassroomOut, status_code=status.HTTP_201_CREATED)
async def create_classroom(body: ClassroomIn, uow: UnitOfWork = Depends(get_uow)):
    return await CreateClassroom(uow).execute(ClassroomInput(**body.model_dump()))


@router.get("/{classroom_id}", response_model=ClassroomDetailOut)
async def get_classroom(classroom_id: int, uow: UnitOfWork = Depends(get_uow)):
    return await GetClassroomDetail(uow).execute(classroom_id)


@router.put("/{classroom_id}", response_model=ClassroomOut)
async def replace_classroom(classroom_id: int, body: ClassroomIn, uow: UnitOfWork = Depends(get_uow)):
    return await UpdateClassroom(uow).execute(classroom_id, body.model_dump())


@router.patch("/{classroom_id}", response_model=ClassroomOut)
async def update_classroom(classroom_id: int, body: ClassroomPatch, uow: UnitOfWork = Depends(get_uow)):
    return await UpdateClassroom(uow).execute(classroom_id, body.changes())


@router.delete("/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom(classroom_id: int, uow: UnitOfWork = Depends(get_uow)) -> None:
    await DeleteClassroom(uow).execute(classroom_id)
