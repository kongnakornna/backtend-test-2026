import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.infrastructure.db.session import Base, get_db
from src.infrastructure.models import (
    ClassroomModel,
    SchoolModel,
    StudentModel,
    TeacherModel,
)
from src.main import app

URL = "/api/v1/schools/"
PAYLOAD = {"name": "Demo School", "abbreviation": "DS", "address": "Bangkok"}


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False)
    engine.dispose()


@pytest.fixture
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # No `with` block: skip lifespan so tests never touch the real school.db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def school_with_members(session_factory):
    with session_factory() as db:
        school = SchoolModel(**PAYLOAD)
        classroom = ClassroomModel(school=school, year_level=1, section="A")
        db.add_all(
            [
                school,
                TeacherModel(
                    school=school,
                    first_name="Somchai",
                    last_name="Jaidee",
                    gender="M",
                    classrooms=[classroom],
                ),
                StudentModel(
                    classroom=classroom,
                    first_name="Somsri",
                    last_name="Dee",
                    gender="F",
                ),
            ]
        )
        db.commit()
        return school.id


def test_create_school(client):
    response = client.post(URL, json=PAYLOAD)
    assert response.status_code == 201
    assert response.json() == {"id": 1, **PAYLOAD}


@pytest.mark.parametrize("field", ["name", "abbreviation", "address"])
def test_create_school_rejects_empty_fields(client, field):
    response = client.post(URL, json={**PAYLOAD, field: ""})
    assert response.status_code == 422


def test_list_filters_by_name_case_insensitive(client):
    client.post(URL, json=PAYLOAD)
    client.post(URL, json={**PAYLOAD, "name": "Other"})

    assert len(client.get(URL).json()) == 2
    results = client.get(URL, params={"name": "demo"}).json()
    assert [s["name"] for s in results] == ["Demo School"]


def test_detail_includes_counts(client, school_with_members):
    response = client.get(f"{URL}{school_with_members}/")
    assert response.status_code == 200
    body = response.json()
    assert body["classroom_count"] == 1
    assert body["teacher_count"] == 1
    assert body["student_count"] == 1


def test_update_school(client):
    school_id = client.post(URL, json=PAYLOAD).json()["id"]
    response = client.put(f"{URL}{school_id}/", json={**PAYLOAD, "name": "Renamed"})
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"


@pytest.mark.parametrize(
    ("method", "kwargs"),
    [("get", {}), ("put", {"json": PAYLOAD}), ("delete", {})],
)
def test_missing_school_returns_404(client, method, kwargs):
    response = getattr(client, method)(f"{URL}999/", **kwargs)
    assert response.status_code == 404
    assert response.json() == {"detail": "School 999 not found"}


def test_delete_school_cascades_to_members(
    client, session_factory, school_with_members
):
    response = client.delete(f"{URL}{school_with_members}/")
    assert response.status_code == 204

    with session_factory() as db:
        for model in (ClassroomModel, TeacherModel, StudentModel):
            assert db.query(model).count() == 0
