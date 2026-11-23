from fastapi import APIRouter, Depends, Query, status

from src.application.dto.inputs import StudentInput
from src.application.dto.pagination import PageParams
from src.application.unit_of_work import UnitOfWork
from src.application.use_cases.student.commands import CreateStudent, DeleteStudent, UpdateStudent
from src.application.use_cases.student.queries import GetStudentDetail, ListStudents
from src.domain.repositories.criteria import PersonCriteria
from src.domain.value_objects.gender import Gender
from src.presentation.dependencies.database import get_uow
from src.presentation.dependencies.pagination import page_params
from src.presentation.schemas.common import ERROR_RESPONSES, PageOut
from src.presentation.schemas.student import StudentDetailOut, StudentIn, StudentOut, StudentPatch

router = APIRouter(prefix="/students", tags=["students"], responses=ERROR_RESPONSES)


@router.get("", response_model=PageOut[StudentOut])
async def list_students(
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
    return await ListStudents(uow).execute(criteria=criteria, params=params)


@router.post("", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
async def create_student(body: StudentIn, uow: UnitOfWork = Depends(get_uow)):
    return await CreateStudent(uow).execute(StudentInput(**body.model_dump()))


@router.get("/{student_id}", response_model=StudentDetailOut)
async def get_student(student_id: int, uow: UnitOfWork = Depends(get_uow)):
    return await GetStudentDetail(uow).execute(student_id)


@router.put("/{student_id}", response_model=StudentOut)
async def replace_student(student_id: int, body: StudentIn, uow: UnitOfWork = Depends(get_uow)):
    return await UpdateStudent(uow).execute(student_id, body.model_dump())


@router.patch("/{student_id}", response_model=StudentOut)
async def update_student(student_id: int, body: StudentPatch, uow: UnitOfWork = Depends(get_uow)):
    return await UpdateStudent(uow).execute(student_id, body.changes())


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(student_id: int, uow: UnitOfWork = Depends(get_uow)) -> None:
    await DeleteStudent(uow).execute(student_id)
