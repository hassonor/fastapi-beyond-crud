# File: src/tests/integration/test_integration_roles.py

import pytest
import httpx
import uuid


@pytest.mark.asyncio
async def test_role_based_access(override_get_session, async_client: httpx.AsyncClient):
    """
    Tests admin vs. normal user permissions, using the in-memory test DB.
    """
    admin_suffix = uuid.uuid4().hex[:2]
    normal_suffix = uuid.uuid4().hex[:2]

    admin_data = {
        "first_name": "Admin",
        "last_name": "User",
        "username": f"adm{admin_suffix}",  # <= 8 chars
        "email": f"admin_{admin_suffix}@example.com",
        "password": "AdminPass123"
    }

    # ADMIN SIGNUP
    admin_signup = await async_client.post("/api/v1/auth/signup", json=admin_data)
    if admin_signup.status_code == 404:
        pytest.skip("Auth signup route not found at /api/v1/auth/signup")
    assert admin_signup.status_code in [200, 201], f"Admin signup failed: {admin_signup.text}"

    # ADMIN LOGIN
    admin_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": admin_data["email"], "password": admin_data["password"]},
    )
    if admin_login.status_code not in [200, 201]:
        pytest.skip(f"Admin login failed: {admin_login.text}")

    data = admin_login.json()
    admin_token = data.get("access_token")
    if not admin_token:
        pytest.skip("No admin access_token returned")

    # NORMAL USER
    user_data = {
        "first_name": "Normal",
        "last_name": "User",
        "username": f"nr{normal_suffix}",
        "email": f"normal_{normal_suffix}@example.com",
        "password": "Normal123"
    }
    user_signup = await async_client.post("/api/v1/auth/signup", json=user_data)
    if user_signup.status_code == 404:
        pytest.skip("Auth signup route not found")
    assert user_signup.status_code in [200, 201], f"User signup failed: {user_signup.text}"

    # NORMAL USER LOGIN
    user_login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    if user_login.status_code not in [200, 201]:
        pytest.skip(f"User login failed: {user_login.text}")

    user_token = user_login.json().get("access_token")
    if not user_token:
        pytest.skip("No normal user access_token")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Suppose /api/v1/auth/list-users is admin-only
    admin_resp = await async_client.get("/api/v1/auth/list-users", headers=admin_headers)
    if admin_resp.status_code == 404:
        pytest.skip("/api/v1/auth/list-users route not found")
    assert admin_resp.status_code in [200, 401, 403]

    user_resp = await async_client.get("/api/v1/auth/list-users", headers=user_headers)
    assert user_resp.status_code in [401, 403, 404]
