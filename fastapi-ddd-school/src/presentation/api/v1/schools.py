from fastapi import APIRouter, Depends, Query, status

from src.application.dto.inputs import SchoolInput
from src.application.dto.pagination import PageParams
from src.application.unit_of_work import UnitOfWork
from src.application.use_cases.school.commands import CreateSchool, DeleteSchool, UpdateSchool
from src.application.use_cases.school.queries import GetSchoolDetail, ListSchools
from src.presentation.dependencies.database import get_uow
from src.presentation.dependencies.pagination import page_params
from src.presentation.schemas.common import ERROR_RESPONSES, PageOut
from src.presentation.schemas.school import SchoolDetailOut, SchoolIn, SchoolOut, SchoolPatch

router = APIRouter(prefix="/schools", tags=["schools"], responses=ERROR_RESPONSES)


@router.get("", response_model=PageOut[SchoolOut])
async def list_schools(
    name: str | None = Query(None, description="ชื่อโรงเรียน (contains, ไม่สนตัวพิมพ์)"),
    params: PageParams = Depends(page_params),
    uow: UnitOfWork = Depends(get_uow),
):
    return await ListSchools(uow).execute(name=name, params=params)


@router.post("", response_model=SchoolOut, status_code=status.HTTP_201_CREATED)
async def create_school(body: SchoolIn, uow: UnitOfWork = Depends(get_uow)):
    return await CreateSchool(uow).execute(SchoolInput(**body.model_dump()))


@router.get("/{school_id}", response_model=SchoolDetailOut)
async def get_school(school_id: int, uow: UnitOfWork = Depends(get_uow)):
    return await GetSchoolDetail(uow).execute(school_id)


@router.put("/{school_id}", response_model=SchoolOut)
async def replace_school(school_id: int, body: SchoolIn, uow: UnitOfWork = Depends(get_uow)):
    return await UpdateSchool(uow).execute(school_id, body.model_dump())


@router.patch("/{school_id}", response_model=SchoolOut)
async def update_school(school_id: int, body: SchoolPatch, uow: UnitOfWork = Depends(get_uow)):
    return await UpdateSchool(uow).execute(school_id, body.changes())


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school(school_id: int, uow: UnitOfWork = Depends(get_uow)) -> None:
    await DeleteSchool(uow).execute(school_id)
