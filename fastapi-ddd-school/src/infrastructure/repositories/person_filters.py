from typing import Any

from sqlalchemy import Select

from src.domain.repositories.criteria import PersonCriteria


def apply_name_gender_filters(stmt: Select[Any], model: Any, criteria: PersonCriteria) -> Select[Any]:
    """Filters shared by teachers and students (first/last name contains, gender)."""
    if criteria.first_name:
        stmt = stmt.where(model.first_name.icontains(criteria.first_name, autoescape=True))
    if criteria.last_name:
        stmt = stmt.where(model.last_name.icontains(criteria.last_name, autoescape=True))
    if criteria.gender is not None:
        stmt = stmt.where(model.gender == criteria.gender.value)
    return stmt
