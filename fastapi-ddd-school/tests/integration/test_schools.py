from tests.integration.conftest import ids

URL = "/api/v1/schools"


async def test_create_school(client):
    response = await client.post(URL, json={"name": " New ", "abbreviation": "NW", "address": "CNX"})
    assert response.status_code == 201
    assert response.json()["name"] == "New"  # whitespace stripped


async def test_create_school_validation_error_format(client):
    response = await client.post(URL, json={"name": ""})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "validation_error"
    fields = {tuple(e["loc"]) for e in body["errors"]}
    assert ("body", "abbreviation") in fields and ("body", "name") in fields


async def test_list_is_paginated(client, seed):
    response = await client.get(URL, params={"page": 1, "page_size": 1})
    body = response.json()
    assert body["total"] == 2
    assert body["page_size"] == 1
    assert [s["id"] for s in body["items"]] == [seed.school_a]


async def test_filter_by_name(client, seed):
    assert ids(await client.get(URL, params={"name": "triam"})) == [seed.school_b]


async def test_filter_name_treats_wildcards_literally(client, seed):
    assert ids(await client.get(URL, params={"name": "%"})) == []


async def test_detail_counts(client, seed):
    body = (await client.get(f"{URL}/{seed.school_a}")).json()
    assert (body["classroom_count"], body["teacher_count"], body["student_count"]) == (2, 1, 2)


async def test_detail_counts_empty_school(client):
    school = (await client.post(URL, json={"name": "E", "abbreviation": "E", "address": "-"})).json()
    body = (await client.get(f"{URL}/{school['id']}")).json()
    assert (body["classroom_count"], body["teacher_count"], body["student_count"]) == (0, 0, 0)


async def test_not_found(client):
    response = await client.get(f"{URL}/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "School 999 not found", "code": "not_found"}


async def test_put_replaces(client, seed):
    response = await client.put(
        f"{URL}/{seed.school_a}", json={"name": "Renamed", "abbreviation": "RN", "address": "BKK"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"


async def test_patch_updates_only_given_fields(client, seed):
    response = await client.patch(f"{URL}/{seed.school_a}", json={"address": "Nonthaburi"})
    assert response.status_code == 200
    assert response.json()["address"] == "Nonthaburi"
    assert response.json()["name"] == "Satit Demo"


async def test_patch_rejects_null(client, seed):
    response = await client.patch(f"{URL}/{seed.school_a}", json={"name": None})
    assert response.status_code == 422


async def test_delete_cascades(client, seed):
    assert (await client.delete(f"{URL}/{seed.school_a}")).status_code == 204
    assert (await client.get(f"{URL}/{seed.school_a}")).status_code == 404
    assert (await client.get(f"/api/v1/classrooms/{seed.room_a1}")).status_code == 404
    assert (await client.get(f"/api/v1/teachers/{seed.teacher_a}")).status_code == 404
    assert (await client.get(f"/api/v1/students/{seed.student_a1}")).status_code == 404
    # other school untouched
    assert (await client.get(f"/api/v1/students/{seed.student_b}")).status_code == 200
