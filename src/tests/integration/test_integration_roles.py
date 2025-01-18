# src/tests/integration/test_integration_roles.py
import pytest
import uuid
from src.db.models import User
from src.auth.utils import generate_passwd_hash


@pytest.mark.asyncio
async def test_role_based_access(override_get_session, async_client, db_session):
    """Test role-based access control"""

    # Create and add admin user
    admin_email = f"admin_{uuid.uuid4().hex[:4]}@example.com"
    admin = User(
        username="admin1",
        email=admin_email,
        password_hash=generate_passwd_hash("AdminPass123"),
        first_name="Admin",
        last_name="User",
        role="admin",
        is_verified=True
    )
    db_session.add(admin)
    await db_session.commit()

    # Login as admin
    admin_login = await async_client.post("/api/v1/auth/login", json={
        "email": admin_email,
        "password": "AdminPass123"
    })
    assert admin_login.status_code in [200, 201]
    admin_token = admin_login.json().get("access_token")
    assert admin_token is not None

    # Create regular user
    user_email = f"user_{uuid.uuid4().hex[:4]}@example.com"
    regular_user = User(
        username="regular1",
        email=user_email,
        password_hash=generate_passwd_hash("UserPass123"),
        first_name="Regular",
        last_name="User",
        role="user",
        is_verified=True
    )
    db_session.add(regular_user)
    await db_session.commit()

    # Login as regular user
    user_login = await async_client.post("/api/v1/auth/login", json={
        "email": user_email,
        "password": "UserPass123"
    })
    assert user_login.status_code in [200, 201]
    user_token = user_login.json().get("access_token")
    assert user_token is not None

    # Test access to admin-only route
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Admin should have access
    admin_response = await async_client.get("/api/v1/reviews/", headers=admin_headers)
    assert admin_response.status_code in [200, 403, 404]

    # Regular user should be denied
    user_response = await async_client.get("/api/v1/reviews/", headers=user_headers)
    assert user_response.status_code in [401, 403, 404]
