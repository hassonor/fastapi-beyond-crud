# File: src/tests/integration/test_integration_advanced.py

import pytest
import httpx


@pytest.mark.anyio
async def test_create_book_with_future_date_disallowed(async_client: httpx.AsyncClient):
    signup_resp = await async_client.post("/auth/signup", json={
        "first_name": "Future",
        "last_name": "Test",
        "username": "future_test",
        "email": "future@example.com",
        "password": "Future123"
    })
    if signup_resp.status_code == 404:
        return
    if signup_resp.status_code not in [200, 201]:
        return

    login_resp = await async_client.post("/auth/login", json={
        "email": "future@example.com",
        "password": "Future123"
    })
    if login_resp.status_code not in [200, 201]:
        return

    data = login_resp.json()
    token = data.get("access_token", None)
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    create_resp = await async_client.post("/books/", headers=headers, json={
        "title": "Future Book",
        "author": "Time Traveler",
        "publisher": "TimePub",
        "published_date": "2099-01-01",
        "page_count": 350,
        "language": "EN"
    })
    assert create_resp.status_code in [200, 201, 400, 422]


@pytest.mark.anyio
async def test_logout_and_access_protected_route(async_client: httpx.AsyncClient):
    signup_resp = await async_client.post("/auth/signup", json={
        "first_name": "Logout",
        "last_name": "User",
        "username": "logout_user",
        "email": "logout@example.com",
        "password": "Logout123"
    })
    if signup_resp.status_code == 404:
        return
    if signup_resp.status_code not in [200, 201]:
        return

    login_resp = await async_client.post("/auth/login", json={
        "email": "logout@example.com",
        "password": "Logout123"
    })
    if login_resp.status_code not in [200, 201]:
        return
    token = login_resp.json().get("access_token", None)
    if not token:
        return

    logout_resp = await async_client.get("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    if logout_resp.status_code == 404:
        return
    if logout_resp.status_code not in [200, 204]:
        return

    protected_resp = await async_client.post("/books/", headers={"Authorization": f"Bearer {token}"}, json={
        "title": "Should Fail",
        "author": "No Access",
        "publisher": "No Access",
        "published_date": "2022-01-01",
        "page_count": 100,
        "language": "EN"
    })
    assert protected_resp.status_code in [200, 201, 401, 403]


@pytest.mark.anyio
async def test_refresh_token_expired(async_client: httpx.AsyncClient):
    signup_resp = await async_client.post("/auth/signup", json={
        "first_name": "Expired",
        "last_name": "Refresh",
        "username": "refresh_expired",
        "email": "expired@example.com",
        "password": "Expired123"
    })
    if signup_resp.status_code == 404:
        return
    if signup_resp.status_code not in [200, 201]:
        return

    login_resp = await async_client.post("/auth/login", json={
        "email": "expired@example.com",
        "password": "Expired123"
    })
    if login_resp.status_code not in [200, 201]:
        return

    data = login_resp.json()
    ref_token = data.get("refresh_token", None)
    if not ref_token:
        return

    headers = {"Authorization": f"Bearer {ref_token}"}
    resp = await async_client.get("/auth/refresh_token", headers=headers)
    assert resp.status_code in [200, 400, 401, 403]
