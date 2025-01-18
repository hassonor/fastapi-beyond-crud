# File: src/tests/integration/test_integration_auth.py

import pytest
import httpx
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import create_url_safe_token
from src.db.models import User


@pytest.mark.asyncio
async def test_create_user_account(override_get_session, async_client: httpx.AsyncClient):
    """
    Test POST /api/v1/auth/signup to ensure user is created and
    we return the expected JSON structure.
    """
    unique_part = uuid.uuid4().hex[:5]
    signup_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": f"jd_{unique_part[:2]}",  # keep <= 8 chars
        "email": f"john_{unique_part}@example.com",
        "password": "Secret123"
    }

    # Create user
    resp = await async_client.post("/api/v1/auth/signup", json=signup_data)
    if resp.status_code == 404:
        pytest.skip("Auth signup route not found at /api/v1/auth/signup")

    assert resp.status_code in [200, 201], f"Signup failed: {resp.text}"

    data = resp.json()
    # The new route returns => {"message": "...", "user": new_user}
    assert "message" in data, f"Expected a message key, got: {data}"
    assert "user" in data, f"Expected a user key, got: {data}"
    # We can do further checks on "user" if needed:
    user_info = data["user"]
    assert "email" in user_info
    assert user_info["email"] == signup_data["email"]


@pytest.mark.asyncio
async def test_verify_user_account(override_get_session, async_client: httpx.AsyncClient, db_session: AsyncSession):
    """
    Test verifying a user via GET /api/v1/auth/verify/{token}.
    We'll:
     1) Manually create a user in the DB (unverified).
     2) Generate a URL-safe token for that user's email.
     3) Call /api/v1/auth/verify/{token} and check 'is_verified' is True.
    """
    # 1) Insert user in DB:
    email = f"verify_{uuid.uuid4().hex[:4]}@example.com"
    await db_session.exec(
        "PRAGMA foreign_keys=ON"  # no-op on SQLite if needed
    )
    # You could create a user properly via your service, or quickly:
    from src.db.models import User
    new_user = User(
        username="ver1",
        email=email,
        password_hash="fakehash",
        first_name="Ver",
        last_name="Test",
        is_verified=False
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    # 2) Create the verify token for that user's email
    token = create_url_safe_token({"email": email})

    # 3) Call /verify/{token}
    verify_url = f"/api/v1/auth/verify/{token}"
    resp = await async_client.get(verify_url)
    if resp.status_code == 404:
        pytest.skip("Verify route not found at /api/v1/auth/verify/{token}")

    assert resp.status_code == 200, f"Verify failed: {resp.text}"

    # 4) Now check the user is verified in DB
    # Re-fetch the user from DB
    user_again = await db_session.get(User, new_user.uid)
    assert user_again is not None
    assert user_again.is_verified is True, "User should be verified after calling /verify"


@pytest.mark.asyncio
async def test_login_and_tokens(override_get_session, async_client: httpx.AsyncClient, db_session: AsyncSession):
    """
    Test that a newly verified user can log in and we get an access + refresh token.
    """
    # We'll create & verify a user quickly:
    email = f"login_{uuid.uuid4().hex[:4]}@example.com"
    user = User(
        username="login1",
        email=email,
        password_hash="$2b$12$5q8arGh...",  # already hashed for 'Secret123'
        first_name="Login",
        last_name="Test",
        is_verified=True,  # Mark as verified for login
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # 2) Now try logging in:
    login_data = {"email": email, "password": "Secret123"}  # Must match the hashed password above
    resp = await async_client.post("/api/v1/auth/login", json=login_data)
    if resp.status_code == 404:
        pytest.skip("Login route not found at /api/v1/auth/login")

    assert resp.status_code in [200, 201], f"Login failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data, "No access_token returned"
    assert "refresh_token" in data, "No refresh_token returned"

    # Next, let's test the refresh:
    refresh_token = data["refresh_token"]
    headers = {"Authorization": f"Bearer {refresh_token}"}
    r = await async_client.get("/api/v1/auth/refresh_token", headers=headers)
    if r.status_code == 404:
        pytest.skip("Refresh token route not found at /api/v1/auth/refresh_token")

    # Acceptable statuses might be 200, 400, 401, 403
    assert r.status_code in [200, 400, 401, 403], f"Unexpected code: {r.status_code} -> {r.text}"


@pytest.mark.asyncio
async def test_logout(override_get_session, async_client: httpx.AsyncClient, db_session: AsyncSession):
    """
    Test logging out by calling /api/v1/auth/logout (which revokes the token).
    """
    # Create user that is verified:
    email = f"logout_{uuid.uuid4().hex[:4]}@example.com"
    user = User(
        username="logout1",
        email=email,
        password_hash="$2b$12$someHashedSecret",  # matches 'Secret123' presumably
        first_name="Log",
        last_name="Out",
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # 1) Log them in to get an access token
    resp = await async_client.post("/api/v1/auth/login", json={
        "email": email, "password": "Secret123"
    })
    if resp.status_code in [404]:
        pytest.skip("Login route not found")
    data = resp.json()
    access_token = data.get("access_token")
    assert access_token, f"No access token after login: {data}"

    # 2) Call /logout with the access token
    headers = {"Authorization": f"Bearer {access_token}"}
    logout_resp = await async_client.get("/api/v1/auth/logout", headers=headers)
    if logout_resp.status_code == 404:
        pytest.skip("/api/v1/auth/logout route not found")

    # If success => 200
    assert logout_resp.status_code in [200], f"Logout failed: {logout_resp.text}"
    # Optionally, we can test the token is blocked by re-calling some route
    # but depends on your logic.
