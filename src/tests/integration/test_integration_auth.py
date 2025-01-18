# src/tests/integration/test_integration_auth.py
import pytest
import uuid
from src.db.models import User
from src.auth.utils import generate_passwd_hash, create_url_safe_token


@pytest.mark.asyncio
async def test_create_user_account(override_get_session, async_client, mock_mail):
    """Test user creation and email verification"""
    unique_id = uuid.uuid4().hex[:5]
    signup_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": f"jd_{unique_id[:2]}",
        "email": f"john_{unique_id}@example.com",
        "password": "Secret123"
    }

    response = await async_client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "message" in data
    assert "user" in data
    assert mock_mail.send_message.called


@pytest.mark.asyncio
async def test_verify_user_account(override_get_session, async_client, db_session):
    """Test user email verification"""
    email = f"verify_{uuid.uuid4().hex[:4]}@example.com"
    user = User(
        username="ver_tester",
        email=email,
        password_hash=generate_passwd_hash("test123"),
        first_name="Verif",
        last_name="Tester",
        is_verified=False
    )
    db_session.add(user)
    await db_session.commit()

    token = create_url_safe_token({"email": email})
    response = await async_client.get(f"/api/v1/auth/verify/{token}")
    assert response.status_code == 200

    await db_session.refresh(user)
    assert user.is_verified is True


@pytest.mark.asyncio
async def test_login_and_tokens(override_get_session, async_client, db_session):
    """Test login and token refresh flow"""
    email = f"login_{uuid.uuid4().hex[:4]}@example.com"
    user = User(
        username="login1",
        email=email,
        password_hash=generate_passwd_hash("Secret123"),
        first_name="Login",
        last_name="Test",
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    # Test login
    login_response = await async_client.post("/api/v1/auth/login",
                                             json={"email": email, "password": "Secret123"})

    assert login_response.status_code in [200, 201]
    data = login_response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Test token refresh
    refresh_headers = {"Authorization": f"Bearer {data['refresh_token']}"}
    refresh_response = await async_client.get("/api/v1/auth/refresh_token",
                                              headers=refresh_headers)
    assert refresh_response.status_code in [200, 401, 403]


@pytest.mark.asyncio
async def test_logout(override_get_session, async_client, db_session):
    """Test user logout flow"""
    # Create test user
    email = f"logout_{uuid.uuid4().hex[:4]}@example.com"
    user = User(
        username="logout1",
        email=email,
        password_hash=generate_passwd_hash("Secret123"),
        first_name="Logout",
        last_name="Test",
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    # Login
    login_response = await async_client.post("/api/v1/auth/login",
                                             json={"email": email, "password": "Secret123"})

    assert login_response.status_code in [200, 201]
    data = login_response.json()
    access_token = data.get("access_token")
    assert access_token is not None

    # Test logout
    headers = {"Authorization": f"Bearer {access_token}"}
    logout_response = await async_client.get("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 200
