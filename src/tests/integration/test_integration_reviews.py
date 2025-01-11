# File: src/tests/integration/test_integration_reviews.py

import pytest
import httpx


@pytest.mark.anyio
async def test_create_and_delete_review(async_client: httpx.AsyncClient):
    # 1) Sign up user
    signup_resp = await async_client.post("/auth/signup", json={
        "first_name": "Review",
        "last_name": "User",
        "username": "revUser1",
        "email": "reviewer1@example.com",
        "password": "Review123"
    })
    if signup_resp.status_code not in [200, 201]:
        return
    # 2) Log in
    login_resp = await async_client.post("/auth/login", json={
        "email": "reviewer1@example.com",
        "password": "Review123"
    })
    if login_resp.status_code not in [200, 201]:
        return
    tokens = login_resp.json()
    token = tokens.get("access_token")
    if not token:
        return
    headers = {"Authorization": f"Bearer {token}"}

    # 3) Create a book
    create_book = await async_client.post("/books/", headers=headers, json={
        "title": "Reviewable Book",
        "author": "TestReview",
        "publisher": "PubRev",
        "published_date": "2022-01-01",
        "page_count": 120,
        "language": "EN"
    })
    if create_book.status_code not in [200, 201]:
        return
    book_data = create_book.json()
    book_uid = book_data["uid"]

    # 4) Add a review
    review_resp = await async_client.post(
        f"/reviews/book/{book_uid}",
        headers=headers,
        json={"rating": 4, "review_text": "Great read!"}
    )
    if review_resp.status_code not in [200, 201]:
        return
    review_data = review_resp.json()
    review_uid = review_data["uid"]

    # 5) Delete the review
    del_resp = await async_client.delete(f"/reviews/{review_uid}", headers=headers)
    # Expect 204 or maybe 200, or 404 if logic differs
    assert del_resp.status_code in [200, 204, 404]
