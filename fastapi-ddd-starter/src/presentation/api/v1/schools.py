from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.application.use_cases.school import (
    CreateSchool,
    CreateSchoolInput,
    DeleteSchool,
    GetSchoolDetail,
    ListSchools,
    UpdateSchool,
    UpdateSchoolInput,
)
from src.domain.repositories import SchoolRepository
from src.infrastructure.db.session import get_db
from src.infrastructure.repositories.school_repository import (
    SQLAlchemySchoolRepository,
)
from src.presentation.schemas.school import (
    SchoolCreate,
    SchoolDetailOut,
    SchoolOut,
    SchoolUpdate,
)

router = APIRouter(prefix="/schools", tags=["schools"])

NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "School not found"}}


def get_repository(db: Session = Depends(get_db)) -> SchoolRepository:
    return SQLAlchemySchoolRepository(db)


@router.post("/", response_model=SchoolOut, status_code=status.HTTP_201_CREATED)
def create_school(
    payload: SchoolCreate,
    repository: SchoolRepository = Depends(get_repository),
):
    return CreateSchool(repository).execute(CreateSchoolInput(**payload.model_dump()))


@router.get("/", response_model=list[SchoolOut])
def list_schools(
    name: str | None = Query(default=None),
    repository: SchoolRepository = Depends(get_repository),
):
    return ListSchools(repository).execute(name=name)


@router.get("/{school_id}/", response_model=SchoolDetailOut, responses=NOT_FOUND)
def get_school_detail(
    school_id: int,
    repository: SchoolRepository = Depends(get_repository),
):
    detail = GetSchoolDetail(repository).execute(school_id)
    return SchoolDetailOut(
        **SchoolOut.model_validate(detail.school).model_dump(),
        classroom_count=detail.counts.classroom_count,
        teacher_count=detail.counts.teacher_count,
        student_count=detail.counts.student_count,
    )


@router.put("/{school_id}/", response_model=SchoolOut, responses=NOT_FOUND)
def update_school(
    school_id: int,
    payload: SchoolUpdate,
    repository: SchoolRepository = Depends(get_repository),
):
    return UpdateSchool(repository).execute(
        UpdateSchoolInput(school_id=school_id, **payload.model_dump())
    )


@router.delete(
    "/{school_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=NOT_FOUND,
)
def delete_school(
    school_id: int,
    repository: SchoolRepository = Depends(get_repository),
):
    DeleteSchool(repository).execute(school_id)
