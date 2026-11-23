from tests.integration.conftest import ids

URL = "/api/v1/classrooms"


async def test_create_requires_existing_school(client):
    response = await client.post(URL, json={"school_id": 99, "year_level": 1, "section": "1"})
    assert response.status_code == 422
    assert response.json()["code"] == "business_rule_violation"


async def test_create_rejects_year_level_zero(client, seed):
    response = await client.post(URL, json={"school_id": seed.school_a, "year_level": 0, "section": "9"})
    assert response.status_code == 422


async def test_duplicate_in_same_school_conflicts(client, seed):
    response = await client.post(URL, json={"school_id": seed.school_a, "year_level": 1, "section": "1"})
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


async def test_same_room_name_in_other_school_is_allowed(client, seed):
    response = await client.post(URL, json={"school_id": seed.school_b, "year_level": 1, "section": "1"})
    assert response.status_code == 201


async def test_filter_by_school(client, seed):
    assert ids(await client.get(URL, params={"school": seed.school_a})) == [seed.room_a1, seed.room_a2]


async def test_detail_lists_teachers_and_students(client, seed):
    body = (await client.get(f"{URL}/{seed.room_a1}")).json()
    assert [t["id"] for t in body["teachers"]] == [seed.teacher_a]
    assert [s["id"] for s in body["students"]] == [seed.student_a1]
    assert body["students"][0]["gender"] == "M"


async def test_patch_section(client, seed):
    response = await client.patch(f"{URL}/{seed.room_a2}", json={"section": "3"})
    assert response.status_code == 200
    assert response.json()["section"] == "3"


async def test_patch_into_duplicate_conflicts(client, seed):
    response = await client.patch(f"{URL}/{seed.room_a2}", json={"section": "1"})
    assert response.status_code == 409


async def test_cannot_move_room_with_teachers_to_other_school(client, seed):
    response = await client.patch(f"{URL}/{seed.room_a1}", json={"school_id": seed.school_b})
    assert response.status_code == 422


async def test_can_move_room_without_teachers(client, seed):
    room = (await client.post(URL, json={"school_id": seed.school_a, "year_level": 6, "section": "1"})).json()
    response = await client.patch(f"{URL}/{room['id']}", json={"school_id": seed.school_b})
    assert response.status_code == 200
    assert response.json()["school_id"] == seed.school_b


async def test_delete_removes_students_and_assignments(client, seed):
    assert (await client.delete(f"{URL}/{seed.room_a1}")).status_code == 204
    assert (await client.get(f"/api/v1/students/{seed.student_a1}")).status_code == 404
    teacher = (await client.get(f"/api/v1/teachers/{seed.teacher_a}")).json()
    assert [c["id"] for c in teacher["classrooms"]] == [seed.room_a2]
