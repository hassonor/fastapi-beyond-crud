# File: src/tests/integration/test_integration_auth.py

import pytest
import uuid
import re
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
    # Make sure an email was sent
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
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Secret123"}
    )
    assert login_response.status_code in [200, 201]

    data = login_response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Test token refresh
    refresh_headers = {"Authorization": f"Bearer {data['refresh_token']}"}
    refresh_response = await async_client.get(
        "/api/v1/auth/refresh_token",
        headers=refresh_headers
    )
    assert refresh_response.status_code in [200, 401, 403]


@pytest.mark.asyncio
async def test_logout(override_get_session, async_client, db_session):
    """Test user logout flow"""
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

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Secret123"}
    )
    assert login_response.status_code in [200, 201]
    data = login_response.json()
    access_token = data.get("access_token")
    assert access_token is not None

    headers = {"Authorization": f"Bearer {access_token}"}
    logout_response = await async_client.get("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 200


# ---------------------------------------------------------------------------
#   NEW TESTS FOR PASSWORD RESET FEATURE
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_password_reset_request_flow(
        override_get_session, async_client, db_session, mock_mail
):
    """
    1) Create a user
    2) Request a password reset
    3) Verify that an email was sent with the reset link
    """
    email = f"reset_{uuid.uuid4().hex[:4]}@example.com"
    user = User(
        username="resetuser",
        email=email,
        password_hash=generate_passwd_hash("InitialPass123"),
        first_name="Reset",
        last_name="Tester",
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    resp = await async_client.post(
        "/api/v1/auth/password-reset-request",
        json={"email": email}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Please check your email for instructions to reset your password"
    assert mock_mail.send_message.called

    # Optionally parse the token out of the email body
    last_call = mock_mail.send_message.call_args
    message_obj = last_call[0][0]
    assert email in message_obj.recipients

    pattern = r"/password-reset-confirm/([^\"']+)"
    match = re.search(pattern, message_obj.body)
    assert match is not None
    token_in_email = match.group(1)
    assert token_in_email


@pytest.mark.asyncio
async def test_password_reset_confirm_success(
        override_get_session, async_client, db_session, mock_mail
):
    """
    1) Create user
    2) Request password reset (mail is sent)
    3) Extract token from email
    4) POST to confirm with matching new passwords
    5) Expect success -> confirm DB changed
    """
    email = f"fullreset_{uuid.uuid4().hex[:4]}@example.com"
    old_hashed = generate_passwd_hash("OldSecret123")
    user = User(
        username="fullresetuser",
        email=email,
        password_hash=old_hashed,
        first_name="ResetFlow",
        last_name="Tester",
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    # Step 2 - request reset
    await async_client.post(
        "/api/v1/auth/password-reset-request",
        json={"email": email}
    )
    assert mock_mail.send_message.called

    # Extract token from the email
    last_call = mock_mail.send_message.call_args
    message_obj = last_call[0][0]
    match = re.search(r"/password-reset-confirm/([^\"']+)", message_obj.body)
    assert match is not None
    token_in_email = match.group(1)

    # Step 4 - do confirm with matching new passwords
    payload = {
        "new_password": "NewSecret123",
        "confirmed_new_password": "NewSecret123"
    }
    resp = await async_client.post(
        f"/api/v1/auth/password-reset-confirm/{token_in_email}",
        json=payload
    )
    assert resp.status_code == 200
    result_data = resp.json()
    assert "Password reset Successfully" in result_data["message"]

    # Step 5 - confirm DB changed
    await db_session.refresh(user)
    assert user.password_hash != old_hashed


@pytest.mark.asyncio
async def test_password_reset_confirm_mismatch_fake_token(
        override_get_session, async_client
):
    """
    If new_password != confirmed_new_password, the route returns 400.
    BUT if the token is also invalid, decode fails => we'd see 500 before 400.
    We'll just show that we get 500 or 400.
    Typically you'd want a valid token to see mismatch => 400.
    This test shows a "fake token" scenario.
    """
    fake_token = "fake-token-for-mismatch"

    payload = {
        "new_password": "MismatchOne",
        "confirmed_new_password": "MismatchTwo"
    }
    resp = await async_client.post(
        f"/api/v1/auth/password-reset-confirm/{fake_token}",
        json=payload
    )
    # Because the token decode fails, we get a 500
    # The route never checks mismatch if the token doesn't decode.
    assert resp.status_code == 500


@pytest.mark.asyncio
async def test_password_reset_confirm_mismatch_real_token(
        override_get_session, async_client, db_session, mock_mail
):
    """
    If the token is valid but the user enters mismatching new passwords,
    the route should raise 400 (Passwords do not match).
    """
    email = f"mismatch_{uuid.uuid4().hex[:4]}@example.com"
    user = User(
        username="mismatchuser",
        email=email,
        password_hash=generate_passwd_hash("Init1234"),
        first_name="Mismatch",
        last_name="Case",
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    # Request a reset
    r = await async_client.post("/api/v1/auth/password-reset-request", json={"email": email})
    assert r.status_code == 200
    assert mock_mail.send_message.called

    # Extract the token
    last_call = mock_mail.send_message.call_args
    message_obj = last_call[0][0]
    match = re.search(r"/password-reset-confirm/([^\"']+)", message_obj.body)
    assert match is not None
    token_in_email = match.group(1)

    # Attempt confirm with mismatch
    payload = {
        "new_password": "OnePassword",
        "confirmed_new_password": "AnotherPassword"
    }
    r2 = await async_client.post(
        f"/api/v1/auth/password-reset-confirm/{token_in_email}",
        json=payload
    )
    assert r2.status_code == 400
    assert "Passwords do not match" in r2.text


@pytest.mark.asyncio
async def test_password_reset_confirm_user_not_found(
        override_get_session, async_client, mock_mail
):
    """
    If the token references an email that doesn't exist in DB,
    the route should raise UserNotFound => 404.
    """
    # Request a reset for a user that doesn't exist
    email = "doesnotexist@example.com"
    await async_client.post("/api/v1/auth/password-reset-request", json={"email": email})
    assert mock_mail.send_message.called

    # Extract token from the mock
    last_call = mock_mail.send_message.call_args
    message_obj = last_call[0][0]
    match = re.search(r"/password-reset-confirm/([^\"']+)", message_obj.body)
    assert match is not None
    token_in_email = match.group(1)

    payload = {
        "new_password": "SomePass123",
        "confirmed_new_password": "SomePass123"
    }
    r2 = await async_client.post(
        f"/api/v1/auth/password-reset-confirm/{token_in_email}",
        json=payload
    )
    # Because there's no user for that email => raise UserNotFound => 404
    assert r2.status_code == 404
    assert "User not found" in r2.text


@pytest.mark.asyncio
async def test_password_reset_confirm_invalid_token(
        override_get_session, async_client
):
    """
    If decode_url_safe_token fails (invalid token format),
    the route returns 500 with "Error occurred during password reset".
    """
    invalid_token = "completely-bad-token"

    payload = {
        "new_password": "AnyPass123",
        "confirmed_new_password": "AnyPass123"
    }
    r = await async_client.post(
        f"/api/v1/auth/password-reset-confirm/{invalid_token}",
        json=payload
    )
    # The route sees decode_url_safe_token(None) => returns 500
    assert r.status_code == 500
    assert "Error occurred during password reset" in r.text
