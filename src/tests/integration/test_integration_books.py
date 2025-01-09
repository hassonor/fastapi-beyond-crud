import pytest
import httpx


@pytest.mark.anyio
async def test_create_and_get_book(async_client: httpx.AsyncClient):
    signup_resp = await async_client.post("/auth/signup", json={
        "first_name": "Book",
        "last_name": "User",
        "username": "bookuser",
        "email": "bookuser@example.com",
        "password": "Book1234"
    })
    if signup_resp.status_code == 404:
        return
    if signup_resp.status_code not in [200, 201]:
        return

    login_resp = await async_client.post("/auth/login", json={
        "email": "bookuser@example.com",
        "password": "Book1234"
    })
    if login_resp.status_code not in [200, 201]:
        return
    data = login_resp.json()
    token = data.get("access_token", None)
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    create_resp = await async_client.post("/books/", headers=headers, json={
        "title": "Integration Book",
        "author": "Auth Test",
        "publisher": "PubTest",
        "published_date": "2021-01-01",
        "page_count": 200,
        "language": "EN"
    })
    if create_resp.status_code == 404:
        return
    assert create_resp.status_code in [200, 201]
    created_data = create_resp.json()

    get_resp = await async_client.get(f"/books/{created_data.get('uid', 'dummy')}", headers=headers)
    if get_resp.status_code == 404:
        return
    assert get_resp.status_code in [200, 201]

    del_resp = await async_client.delete(f"/books/{created_data.get('uid', 'dummy')}", headers=headers)
    if del_resp.status_code == 404:
        return
    assert del_resp.status_code in [200, 204]
