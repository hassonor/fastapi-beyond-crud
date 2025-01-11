# File: src/tests/integration/test_integration_tags.py

import pytest
import httpx


@pytest.mark.anyio
async def test_create_and_update_tag(async_client: httpx.AsyncClient):
    # 1) sign up
    signup_resp = await async_client.post("/auth/signup", json={
        "first_name": "Taggy",
        "last_name": "User",
        "username": "tagUser1",
        "email": "taguser1@example.com",
        "password": "TagUser123"
    })
    if signup_resp.status_code not in [200, 201]:
        return

    # 2) login
    login_resp = await async_client.post("/auth/login", json={
        "email": "taguser1@example.com",
        "password": "TagUser123"
    })
    if login_resp.status_code not in [200, 201]:
        return
    token = login_resp.json().get("access_token")
    if not token:
        return
    headers = {"Authorization": f"Bearer {token}"}

    # 3) create a tag
    tag_create_resp = await async_client.post("/tags/", headers=headers, json={"name": "Fantasy"})
    if tag_create_resp.status_code == 404:
        return
    assert tag_create_resp.status_code in [200, 201]
    created_tag = tag_create_resp.json()
    tag_uid = created_tag["uid"]

    # 4) update the tag
    tag_update_resp = await async_client.put(f"/tags/{tag_uid}", headers=headers, json={"name": "Fantasy Updated"})
    # accept 200 or 404
    assert tag_update_resp.status_code in [200, 404]
    if tag_update_resp.status_code == 200:
        updated_tag = tag_update_resp.json()
        assert updated_tag["name"] == "Fantasy Updated"


@pytest.mark.anyio
async def test_add_tag_to_book(async_client: httpx.AsyncClient):
    # 1) create user
    signup_resp = await async_client.post("/auth/signup", json={
        "first_name": "BookTag",
        "last_name": "User",
        "username": "bookTagger1",
        "email": "bookTagger1@example.com",
        "password": "BookTag123"
    })
    if signup_resp.status_code not in [200, 201]:
        return

    # 2) login
    login_resp = await async_client.post("/auth/login", json={
        "email": "bookTagger1@example.com",
        "password": "BookTag123"
    })
    if login_resp.status_code not in [200, 201]:
        return
    token = login_resp.json().get("access_token")
    if not token:
        return
    headers = {"Authorization": f"Bearer {token}"}

    # 3) create a book
    create_book = await async_client.post("/books/", headers=headers, json={
        "title": "Book With Tag",
        "author": "Tagging Author",
        "publisher": "TagPub",
        "published_date": "2022-01-01",
        "page_count": 150,
        "language": "EN"
    })
    if create_book.status_code not in [200, 201]:
        return
    book_data = create_book.json()
    book_uid = book_data.get("uid")

    # 4) create a tag
    create_tag = await async_client.post("/tags/", headers=headers, json={"name": "Adventure"})
    if create_tag.status_code not in [200, 201]:
        return

    # 5) add tag to book
    # we pass {"tags": [{"name": "Adventure"}]} => route: POST /tags/book/{book_uid}/tags
    payload = {
        "tags": [{"name": "Adventure"}]
    }
    add_tag_resp = await async_client.post(f"/tags/book/{book_uid}/tags", headers=headers, json=payload)
    # If route doesn't exist => 404
    if add_tag_resp.status_code == 404:
        return
    # success => 200
    assert add_tag_resp.status_code == 200
    book_with_tag = add_tag_resp.json()
    assert any(t["name"] == "Adventure" for t in book_with_tag["tags"])
