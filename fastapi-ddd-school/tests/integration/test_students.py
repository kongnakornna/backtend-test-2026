from tests.integration.conftest import ids

URL = "/api/v1/students"


async def test_create(client, seed):
    response = await client.post(
        URL, json={"classroom_id": seed.room_b1, "first_name": "Chujai", "last_name": "Jaidee", "gender": "F"}
    )
    assert response.status_code == 201


async def test_create_requires_classroom(client):
    response = await client.post(URL, json={"first_name": "Chujai", "last_name": "Jaidee", "gender": "F"})
    assert response.status_code == 422


async def test_create_with_unknown_classroom(client, seed):
    response = await client.post(
        URL, json={"classroom_id": 999, "first_name": "A", "last_name": "B", "gender": "F"}
    )
    assert response.status_code == 422


async def test_filter_school(client, seed):
    assert ids(await client.get(URL, params={"school": seed.school_a})) == [seed.student_a1, seed.student_a2]


async def test_filter_classroom(client, seed):
    assert ids(await client.get(URL, params={"classroom": seed.room_b1})) == [seed.student_b]


async def test_filter_firstname(client, seed):
    assert ids(await client.get(URL, params={"firstname": "manee"})) == [seed.student_a2]


async def test_filter_lastname(client, seed):
    assert ids(await client.get(URL, params={"lastname": "yin"})) == [seed.student_b]


async def test_filter_gender(client, seed):
    assert ids(await client.get(URL, params={"gender": "F"})) == [seed.student_a2]


async def test_filters_combine(client, seed):
    assert ids(await client.get(URL, params={"school": seed.school_a, "gender": "M"})) == [seed.student_a1]


async def test_detail_shows_classroom(client, seed):
    body = (await client.get(f"{URL}/{seed.student_a1}")).json()
    assert body["classroom"] == {"id": seed.room_a1, "school_id": seed.school_a, "year_level": 1, "section": "1"}


async def test_move_classroom(client, seed):
    response = await client.patch(f"{URL}/{seed.student_a1}", json={"classroom_id": seed.room_b1})
    assert response.status_code == 200
    assert ids(await client.get(URL, params={"classroom": seed.room_b1})) == [seed.student_a1, seed.student_b]


async def test_move_to_unknown_classroom(client, seed):
    response = await client.patch(f"{URL}/{seed.student_a1}", json={"classroom_id": 999})
    assert response.status_code == 422


async def test_delete(client, seed):
    assert (await client.delete(f"{URL}/{seed.student_b}")).status_code == 204
    assert (await client.get(f"{URL}/{seed.student_b}")).status_code == 404
