from dataclasses import dataclass

import pytest
from httpx import AsyncClient


async def create(client: AsyncClient, path: str, payload: dict) -> dict:
    response = await client.post(f"/api/v1/{path}", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


@dataclass
class Seed:
    school_a: int
    school_b: int
    room_a1: int
    room_a2: int
    room_b1: int
    teacher_a: int
    teacher_b: int
    student_a1: int
    student_a2: int
    student_b: int


@pytest.fixture
async def seed(client: AsyncClient) -> Seed:
    """Two schools: A has rooms 1/1, 1/2 with teacher Somchai and 2 students; B has room 4/1."""
    school_a = (await create(client, "schools", {"name": "Satit Demo", "abbreviation": "SD", "address": "Bangkok"}))["id"]
    school_b = (await create(client, "schools", {"name": "Triam Udom", "abbreviation": "TU", "address": "Bangkok"}))["id"]

    room_a1 = (await create(client, "classrooms", {"school_id": school_a, "year_level": 1, "section": "1"}))["id"]
    room_a2 = (await create(client, "classrooms", {"school_id": school_a, "year_level": 1, "section": "2"}))["id"]
    room_b1 = (await create(client, "classrooms", {"school_id": school_b, "year_level": 4, "section": "1"}))["id"]

    teacher_a = (await create(client, "teachers", {
        "school_id": school_a, "first_name": "Somchai", "last_name": "Jaidee", "gender": "M",
        "classroom_ids": [room_a1, room_a2],
    }))["id"]
    teacher_b = (await create(client, "teachers", {
        "school_id": school_b, "first_name": "Suda", "last_name": "Rakdee", "gender": "F",
        "classroom_ids": [room_b1],
    }))["id"]

    student_a1 = (await create(client, "students", {
        "classroom_id": room_a1, "first_name": "Mana", "last_name": "Dekdee", "gender": "M",
    }))["id"]
    student_a2 = (await create(client, "students", {
        "classroom_id": room_a2, "first_name": "Manee", "last_name": "Meejai", "gender": "F",
    }))["id"]
    student_b = (await create(client, "students", {
        "classroom_id": room_b1, "first_name": "Piti", "last_name": "Yindee", "gender": "M",
    }))["id"]

    return Seed(school_a, school_b, room_a1, room_a2, room_b1, teacher_a, teacher_b,
                student_a1, student_a2, student_b)


def ids(response) -> list[int]:
    assert response.status_code == 200, response.text
    return [item["id"] for item in response.json()["items"]]
