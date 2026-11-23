from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.domain.entities import School, SchoolCounts
from src.domain.exceptions import SchoolNotFoundError
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

    @staticmethod
    def _to_entity(model: SchoolModel) -> School:
        return School(
            id=model.id,
            name=model.name,
            abbreviation=model.abbreviation,
            address=model.address,
        )

    def _get_model(self, school_id: int) -> SchoolModel:
        model = self.db.get(SchoolModel, school_id)
        if model is None:
            raise SchoolNotFoundError(school_id)
        return model

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
        stmt = select(SchoolModel).order_by(SchoolModel.id)
        if name:
            stmt = stmt.where(SchoolModel.name.ilike(f"%{name}%"))
        return [self._to_entity(model) for model in self.db.scalars(stmt)]

    def update(self, school: School) -> School:
        model = self._get_model(school.id)
        model.name = school.name
        model.abbreviation = school.abbreviation
        model.address = school.address
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def delete(self, school_id: int) -> None:
        self.db.delete(self._get_model(school_id))
        self.db.commit()

    def counts(self, school_id: int) -> SchoolCounts:
        def count(stmt) -> int:
            return self.db.scalar(stmt) or 0

        return SchoolCounts(
            classroom_count=count(
                select(func.count(ClassroomModel.id)).where(
                    ClassroomModel.school_id == school_id
                )
            ),
            teacher_count=count(
                select(func.count(TeacherModel.id)).where(
                    TeacherModel.school_id == school_id
                )
            ),
            student_count=count(
                select(func.count(StudentModel.id))
                .join(ClassroomModel)
                .where(ClassroomModel.school_id == school_id)
            ),
        )
