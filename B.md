
# Project B: FastAPI DDD 

> ส่วนนี้เป็น **starter ที่รันได้จริง** สำหรับ module `school` และมีโครงสร้าง DDD ครบ layer ส่วน `classroom/teacher/student` ให้สร้างตาม pattern เดียวกัน

## B.1 โครงสร้าง

```text
fastapi-ddd-school/
├── requirements.txt
├── src/
│   ├── core/
│   │   └── config.py
│   ├── domain/
│   │   ├── entities.py
│   │   └── repositories.py
│   ├── infrastructure/
│   │   ├── db/
│   │   │   └── session.py
│   │   ├── models.py
│   │   └── repositories/
│   │       └── school_repository.py
│   ├── application/
│   │   └── use_cases/
│   │       └── school.py
│   ├── presentation/
│   │   ├── schemas/
│   │   │   └── school.py
│   │   └── api/
│   │       └── v1/
│   │           └── schools.py
│   └── main.py
```

## B.2 `requirements.txt`

```txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
sqlalchemy==2.0.30
pydantic-settings==2.2.1
alembic==1.13.1
```

## B.3 `src/core/config.py`

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./school.db"
    api_v1_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"


settings = Settings()
```

## B.4 `src/infrastructure/db/session.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.core.config import settings


connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## B.5 `src/infrastructure/models.py`

```python
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.session import Base


teacher_classroom = Table(
    "teacher_classroom",
    Base.metadata,
    Column("teacher_id", ForeignKey("teachers.id"), primary_key=True),
    Column("classroom_id", ForeignKey("classrooms.id"), primary_key=True),
)


class SchoolModel(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    abbreviation: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(Text)

    classrooms = relationship("ClassroomModel", back_populates="school")
    teachers = relationship("TeacherModel", back_populates="school")


class ClassroomModel(Base):
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"))
    year_level: Mapped[int] = mapped_column(Integer)
    section: Mapped[str] = mapped_column(String(50))

    school = relationship("SchoolModel", back_populates="classrooms")
    students = relationship("StudentModel", back_populates="classroom")
    teachers = relationship(
        "TeacherModel",
        secondary=teacher_classroom,
        back_populates="classrooms",
    )


class TeacherModel(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(1))

    school = relationship("SchoolModel", back_populates="teachers")
    classrooms = relationship(
        "ClassroomModel",
        secondary=teacher_classroom,
        back_populates="teachers",
    )


class StudentModel(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(1))

    classroom = relationship("ClassroomModel", back_populates="students")
```

## B.6 `src/domain/entities.py`

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class School:
    id: Optional[int]
    name: str
    abbreviation: str
    address: str
```

## B.7 `src/domain/repositories.py`

```python
from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities import School


class SchoolRepository(ABC):
    @abstractmethod
    def add(self, school: School) -> School:
        ...

    @abstractmethod
    def get(self, school_id: int) -> Optional[School]:
        ...

    @abstractmethod
    def list(self, name: Optional[str] = None) -> list[School]:
        ...

    @abstractmethod
    def update(self, school: School) -> School:
        ...

    @abstractmethod
    def delete(self, school_id: int) -> None:
        ...

    @abstractmethod
    def counts(self, school_id: int) -> dict:
        ...
```

## B.8 `src/infrastructure/repositories/school_repository.py`

```python
from typing import Optional

from sqlalchemy.orm import Session

from src.domain.entities import School
from src.domain.repositories import SchoolRepository
from src.infrastructure.models import (
    ClassroomModel,
    SchoolModel,
    StudentModel,
    TeacherModel,
)


class SQLAlchemySchoolRepository(SchoolRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: SchoolModel) -> School:
        return School(
            id=model.id,
            name=model.name,
            abbreviation=model.abbreviation,
            address=model.address,
        )

    def add(self, school: School) -> School:
        model = SchoolModel(
            name=school.name,
            abbreviation=school.abbreviation,
            address=school.address,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def get(self, school_id: int) -> Optional[School]:
        model = self.db.get(SchoolModel, school_id)
        return self._to_entity(model) if model else None

    def list(self, name: Optional[str] = None) -> list[School]:
        query = self.db.query(SchoolModel)
        if name:
            query = query.filter(SchoolModel.name.ilike(f"%{name}%"))
        return [self._to_entity(model) for model in query.all()]

    def update(self, school: School) -> School:
        model = self.db.get(SchoolModel, school.id)
        if not model:
            raise ValueError("School not found")

        model.name = school.name
        model.abbreviation = school.abbreviation
        model.address = school.address
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def delete(self, school_id: int) -> None:
        model = self.db.get(SchoolModel, school_id)
        if not model:
            raise ValueError("School not found")
        self.db.delete(model)
        self.db.commit()

    def counts(self, school_id: int) -> dict:
        return {
            "classroom_count": self.db.query(ClassroomModel)
            .filter(ClassroomModel.school_id == school_id)
            .count(),
            "teacher_count": self.db.query(TeacherModel)
            .filter(TeacherModel.school_id == school_id)
            .count(),
            "student_count": self.db.query(StudentModel)
            .join(ClassroomModel)
            .filter(ClassroomModel.school_id == school_id)
            .count(),
        }
```

## B.9 `src/application/use_cases/school.py`

```python
from dataclasses import dataclass

from src.domain.entities import School
from src.domain.repositories import SchoolRepository


@dataclass
class CreateSchoolInput:
    name: str
    abbreviation: str
    address: str


@dataclass
class UpdateSchoolInput:
    school_id: int
    name: str
    abbreviation: str
    address: str


class CreateSchool:
    def __init__(self, repository: SchoolRepository):
        self.repository = repository

    def execute(self, data: CreateSchoolInput) -> School:
        school = School(
            id=None,
            name=data.name,
            abbreviation=data.abbreviation,
            address=data.address,
        )
        return self.repository.add(school)


class ListSchools:
    def __init__(self, repository: SchoolRepository):
        self.repository = repository

    def execute(self, name: str | None = None) -> list[School]:
        return self.repository.list(name=name)


class GetSchool:
    def __init__(self, repository: SchoolRepository):
        self.repository = repository

    def execute(self, school_id: int) -> School | None:
        return self.repository.get(school_id)


class UpdateSchool:
    def __init__(self, repository: SchoolRepository):
        self.repository = repository

    def execute(self, data: UpdateSchoolInput) -> School:
        school = School(
            id=data.school_id,
            name=data.name,
            abbreviation=data.abbreviation,
            address=data.address,
        )
        return self.repository.update(school)


class DeleteSchool:
    def __init__(self, repository: SchoolRepository):
        self.repository = repository

    def execute(self, school_id: int) -> None:
        self.repository.delete(school_id)
```

## B.10 `src/presentation/schemas/school.py`

```python
from pydantic import BaseModel, ConfigDict


class SchoolCreate(BaseModel):
    name: str
    abbreviation: str
    address: str


class SchoolUpdate(BaseModel):
    name: str
    abbreviation: str
    address: str


class SchoolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    abbreviation: str
    address: str


class SchoolDetailOut(SchoolOut):
    classroom_count: int
    teacher_count: int
    student_count: int
```

## B.11 `src/presentation/api/v1/schools.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.application.use_cases.school import (
    CreateSchool,
    CreateSchoolInput,
    DeleteSchool,
    GetSchool,
    ListSchools,
    UpdateSchool,
    UpdateSchoolInput,
)
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


def get_repository(db: Session = Depends(get_db)) -> SQLAlchemySchoolRepository:
    return SQLAlchemySchoolRepository(db)


@router.post("/", response_model=SchoolOut, status_code=status.HTTP_201_CREATED)
def create_school(
    payload: SchoolCreate,
    repository: SQLAlchemySchoolRepository = Depends(get_repository),
):
    use_case = CreateSchool(repository)
    return use_case.execute(
        CreateSchoolInput(
            name=payload.name,
            abbreviation=payload.abbreviation,
            address=payload.address,
        )
    )


@router.get("/", response_model=list[SchoolOut])
def list_schools(
    name: str | None = Query(default=None),
    repository: SQLAlchemySchoolRepository = Depends(get_repository),
):
    use_case = ListSchools(repository)
    return use_case.execute(name=name)


@router.get("/{school_id}/", response_model=SchoolDetailOut)
def get_school_detail(
    school_id: int,
    repository: SQLAlchemySchoolRepository = Depends(get_repository),
):
    use_case = GetSchool(repository)
    school = use_case.execute(school_id)
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found",
        )

    counts = repository.counts(school_id)
    return SchoolDetailOut(
        id=school.id,
        name=school.name,
        abbreviation=school.abbreviation,
        address=school.address,
        classroom_count=counts["classroom_count"],
        teacher_count=counts["teacher_count"],
        student_count=counts["student_count"],
    )


@router.put("/{school_id}/", response_model=SchoolOut)
def update_school(
    school_id: int,
    payload: SchoolUpdate,
    repository: SQLAlchemySchoolRepository = Depends(get_repository),
):
    use_case = UpdateSchool(repository)
    return use_case.execute(
        UpdateSchoolInput(
            school_id=school_id,
            name=payload.name,
            abbreviation=payload.abbreviation,
            address=payload.address,
        )
    )


@router.delete("/{school_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_school(
    school_id: int,
    repository: SQLAlchemySchoolRepository = Depends(get_repository),
):
    use_case = DeleteSchool(repository)
    use_case.execute(school_id)
```

## B.12 `src/main.py`

```python
from fastapi import FastAPI

from src.infrastructure.db.session import Base, engine
from src.presentation.api.v1.schools import router as schools_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="School API DDD")

app.include_router(schools_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
```

## B.13 คำสั่งรัน FastAPI

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

เปิด Swagger: `http://127.0.0.1:8000/docs`

---
 