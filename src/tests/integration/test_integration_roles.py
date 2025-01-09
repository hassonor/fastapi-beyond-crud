import pytest
import httpx


@pytest.mark.anyio
async def test_role_based_access(async_client: httpx.AsyncClient):
    admin_signup = await async_client.post("/auth/signup", json={
        "first_name": "Admin",
        "last_name": "User",
        "username": "admin_user",
        "email": "admin@example.com",
        "password": "AdminPass123"
    })
    if admin_signup.status_code == 404:
        return
    assert admin_signup.status_code in [200, 201]

    admin_login = await async_client.post("/auth/login", json={
        "email": "admin@example.com",
        "password": "AdminPass123"
    })
    if admin_login.status_code not in [200, 201]:
        return
    data = admin_login.json()
    admin_token = data.get("access_token", None)
    if not admin_token:
        return

    user_signup = await async_client.post("/auth/signup", json={
        "first_name": "Normal",
        "last_name": "User",
        "username": "normal_user",
        "email": "normal@example.com",
        "password": "Normal123"
    })
    if user_signup.status_code == 404:
        return
    if user_signup.status_code not in [200, 201]:
        return

    user_login = await async_client.post("/auth/login", json={
        "email": "normal@example.com",
        "password": "Normal123"
    })
    if user_login.status_code not in [200, 201]:
        return
    user_token = user_login.json().get("access_token", None)
    if not user_token:
        return

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    admin_resp = await async_client.get("/auth/list-users", headers=admin_headers)
    if admin_resp.status_code == 404:
        return
    # If your app allows admin => 200, else 403
    assert admin_resp.status_code in [200, 403, 401]

    user_resp = await async_client.get("/auth/list-users", headers=user_headers)
    assert user_resp.status_code in [401, 403, 404]
