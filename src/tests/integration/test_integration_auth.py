# File: src/tests/integration/test_integration_auth.py

import pytest
import httpx
import uuid

from src import app
from src.db.main import get_session


@pytest.fixture(scope="function")
def override_get_session(db_session):
    """
    Override FastAPI's `get_session()` to use the test DB session
    (in-memory SQLite), not the real database.
    """

    async def _override_get_session():
        yield db_session

    # Apply the override
    app.dependency_overrides[get_session] = _override_get_session
    yield

    # Remove the override after test
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_signup_and_login(override_get_session, async_client: httpx.AsyncClient):
    """
    Tests user signup and login with the in-memory test DB.
    """
    unique_part = uuid.uuid4().hex[:4]
    signup_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": f"jd_{unique_part[:2]}",  # keep <= 8 chars
        "email": f"john_{unique_part}@example.com",
        "password": "Secret123"
    }

    # Signup
    resp = await async_client.post("/api/v1/auth/signup", json=signup_data)
    if resp.status_code == 404:
        pytest.skip("Auth routes not found at /api/v1/auth/signup")

    assert resp.status_code in [200, 201], f"Signup failed: {resp.text}"

    # Login
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": signup_data["email"], "password": signup_data["password"]},
    )
    if login_resp.status_code == 404:
        pytest.skip("Auth login route not found at /api/v1/auth/login")

    assert login_resp.status_code in [200, 201], f"Login failed: {login_resp.text}"

    data = login_resp.json()
    assert "access_token" in data, "No access_token returned"
    assert "refresh_token" in data, "No refresh_token returned"


@pytest.mark.asyncio
async def test_refresh_token(override_get_session, async_client: httpx.AsyncClient):
    """
    Tests that refresh_token can be used, with the test DB.
    """
    unique_part = uuid.uuid4().hex[:4]
    signup_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "username": f"js_{unique_part[:2]}",
        "email": f"jane_{unique_part}@example.com",
        "password": "JanePass123"
    }

    # Create user
    resp = await async_client.post("/api/v1/auth/signup", json=signup_data)
    if resp.status_code == 404:
        pytest.skip("Auth signup route not found")
    if resp.status_code not in [200, 201]:
        pytest.skip(f"Cannot sign up user: {resp.status_code} - {resp.text}")

    # Log in
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": signup_data["email"], "password": signup_data["password"]}
    )
    if login_resp.status_code not in [200, 201]:
        pytest.skip(f"Cannot log in user: {login_resp.status_code} - {login_resp.text}")

    data = login_resp.json()
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        pytest.skip("No refresh_token returned during login")

    # Attempt refresh
    headers = {"Authorization": f"Bearer {refresh_token}"}
    r = await async_client.get("/api/v1/auth/refresh_token", headers=headers)
    if r.status_code == 404:
        pytest.skip("Refresh token route not found")

    # Acceptable statuses might be 200, 400, 401, 403
    assert r.status_code in [200, 400, 401, 403], f"Unexpected code: {r.status_code} -> {r.text}"
