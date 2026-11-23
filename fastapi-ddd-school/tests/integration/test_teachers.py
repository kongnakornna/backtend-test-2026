from tests.integration.conftest import ids

URL = "/api/v1/teachers"


def payload(seed, **overrides) -> dict:
    data = {
        "school_id": seed.school_a,
        "first_name": "Wichai",
        "last_name": "Sukjai",
        "gender": "M",
        "classroom_ids": [seed.room_a1],
    }
    data.update(overrides)
    return data


async def test_create(client, seed):
    response = await client.post(URL, json=payload(seed))
    assert response.status_code == 201
    assert response.json()["classroom_ids"] == [seed.room_a1]


async def test_create_without_classrooms(client, seed):
    response = await client.post(URL, json=payload(seed, classroom_ids=[]))
    assert response.status_code == 201


async def test_rejects_classroom_from_other_school(client, seed):
    response = await client.post(URL, json=payload(seed, classroom_ids=[seed.room_b1]))
    assert response.status_code == 422
    assert "do not belong to school" in response.json()["detail"]


async def test_rejects_unknown_classroom(client, seed):
    response = await client.post(URL, json=payload(seed, classroom_ids=[999]))
    assert response.status_code == 422
    assert "do not exist" in response.json()["detail"]


async def test_rejects_invalid_gender(client, seed):
    response = await client.post(URL, json=payload(seed, gender="X"))
    assert response.status_code == 422


async def test_filter_school(client, seed):
    assert ids(await client.get(URL, params={"school": seed.school_b})) == [seed.teacher_b]


async def test_filter_classroom(client, seed):
    assert ids(await client.get(URL, params={"classroom": seed.room_a2})) == [seed.teacher_a]


async def test_filter_firstname(client, seed):
    assert ids(await client.get(URL, params={"firstname": "SOM"})) == [seed.teacher_a]


async def test_filter_lastname(client, seed):
    assert ids(await client.get(URL, params={"lastname": "rak"})) == [seed.teacher_b]


async def test_filter_gender(client, seed):
    assert ids(await client.get(URL, params={"gender": "F"})) == [seed.teacher_b]


async def test_filter_gender_invalid_value(client, seed):
    assert (await client.get(URL, params={"gender": "X"})).status_code == 422


async def test_detail_lists_classrooms(client, seed):
    body = (await client.get(f"{URL}/{seed.teacher_a}")).json()
    assert [c["id"] for c in body["classrooms"]] == [seed.room_a1, seed.room_a2]
    assert body["classrooms"][0]["year_level"] == 1


async def test_put_replaces_classrooms(client, seed):
    response = await client.put(
        f"{URL}/{seed.teacher_a}", json=payload(seed, first_name="Somsak", classroom_ids=[seed.room_a2])
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Somsak"
    assert response.json()["classroom_ids"] == [seed.room_a2]


async def test_patch_name_keeps_classrooms(client, seed):
    response = await client.patch(f"{URL}/{seed.teacher_a}", json={"last_name": "Dee"})
    assert response.status_code == 200
    assert response.json()["classroom_ids"] == [seed.room_a1, seed.room_a2]


async def test_change_school_with_old_classrooms_rejected(client, seed):
    response = await client.patch(f"{URL}/{seed.teacher_a}", json={"school_id": seed.school_b})
    assert response.status_code == 422


async def test_change_school_with_new_classrooms(client, seed):
    response = await client.patch(
        f"{URL}/{seed.teacher_a}", json={"school_id": seed.school_b, "classroom_ids": [seed.room_b1]}
    )
    assert response.status_code == 200
    assert response.json()["classroom_ids"] == [seed.room_b1]


async def test_delete(client, seed):
    assert (await client.delete(f"{URL}/{seed.teacher_b}")).status_code == 204
    assert (await client.get(f"{URL}/{seed.teacher_b}")).status_code == 404
    room = (await client.get(f"/api/v1/classrooms/{seed.room_b1}")).json()
    assert room["teachers"] == []
