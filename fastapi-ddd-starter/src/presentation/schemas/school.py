from pydantic import BaseModel, ConfigDict, Field


class SchoolCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    abbreviation: str = Field(min_length=1, max_length=50)
    address: str = Field(min_length=1)


class SchoolUpdate(SchoolCreate):
    pass


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
