from dataclasses import dataclass

from src.domain.entities import School, SchoolCounts
from src.domain.exceptions import SchoolNotFoundError
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


@dataclass(frozen=True)
class SchoolDetail:
    school: School
    counts: SchoolCounts


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


class GetSchoolDetail:
    def __init__(self, repository: SchoolRepository):
        self.repository = repository

    def execute(self, school_id: int) -> SchoolDetail:
        school = self.repository.get(school_id)
        if school is None:
            raise SchoolNotFoundError(school_id)
        return SchoolDetail(school=school, counts=self.repository.counts(school_id))


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
