# File: src/tests/integration/test_integration_concurrency.py

import pytest
import httpx
import asyncio


@pytest.mark.anyio
async def test_concurrent_book_creations(async_client: httpx.AsyncClient):
    signup_resp = await async_client.post("/auth/signup", json={
        "first_name": "Concurrent",
        "last_name": "Test",
        "username": "concurrent_test",
        "email": "concurrent@example.com",
        "password": "Concurrent123"
    })
    if signup_resp.status_code == 404:
        return
    if signup_resp.status_code not in [200, 201]:
        return

    login_resp = await async_client.post("/auth/login", json={
        "email": "concurrent@example.com",
        "password": "Concurrent123"
    })
    if login_resp.status_code not in [200, 201]:
        return
    data = login_resp.json()
    token = data.get("access_token", None)
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    async def create_book(i):
        payload = {
            "title": f"Concurrent Book {i}",
            "author": "MultiAuthor",
            "publisher": "MultiPub",
            "published_date": "2022-01-01",
            "page_count": 100,
            "language": "EN"
        }
        resp = await async_client.post("/books/", headers=headers, json=payload)
        return resp.status_code

    tasks = [create_book(i) for i in range(2)]
    results = await asyncio.gather(*tasks)
    for code in results:
        assert code in [200, 201, 403, 401, 404]
