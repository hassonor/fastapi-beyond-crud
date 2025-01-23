from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Config
from src.celery_tasks import send_email_task
from src.db.main import get_session
from src.db.redis import token_blocklist_client
from src.errors import InvalidCredentials, InvalidToken, UserAlreadyExists, UserNotFound
from .dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker, get_current_user
from .schemas import (
    EmailModel,
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
    UserBooksModel,
    UserCreateModel,
    UserLoginModel,
)
from .service import UserService
from .utils import (
    create_access_token,
    create_url_safe_token,
    decode_url_safe_token,
    generate_passwd_hash,
    verify_password,
)

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])
REFRESH_TOKEN_EXPIRY = 2


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    """
    Example endpoint to send an email via Celery.
    """
    recipients = emails.addresses
    subject = "Welcome to our app"
    html_content = "<h1>Welcome to the app</h1>"

    send_email_task.delay(recipients, subject, html_content)
    return {"message": "Email sent successfully."}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_account(
        user_data: UserCreateModel,
        session: AsyncSession = Depends(get_session),
):
    """
    Create a user account, queue up a verification email, and return user info.
    """
    email = user_data.email
    if await user_service.user_exists(email, session):
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)
    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    subject = "Verify your email"
    html = f"""
    <h1>Verify your email</h1>
    <p>Please click the <a href="{link}">link</a> below to verify your email</p>
    """

    send_email_task.delay([email], subject, html)

    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user,
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    """
    Use a URL-safe token to verify a user's account (set is_verified=True).
    """
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email") if token_data else None

    if not user_email:
        return JSONResponse(
            content={"message": "Error occurred during verification"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise UserNotFound()

    await user_service.update_user(user, {"is_verified": True}, session)
    return JSONResponse(
        content={"message": "Account verified successfully"},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/login")
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    """
    Log a user in by validating credentials, then return an access + refresh token pair.
    """
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    if user and verify_password(password, user.password_hash):
        access_token = create_access_token(
            user_data={
                "email": user.email,
                "user_uid": str(user.uid),
                "role": user.role,
            }
        )
        refresh_token = create_access_token(
            user_data={
                "email": user.email,
                "user_uid": str(user.uid),
            },
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
        )
        return JSONResponse(
            content={
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "email": user.email,
                    "uid": str(user.uid),
                },
            }
        )

    raise InvalidCredentials()


@auth_router.get("/refresh_token")
async def get_refreshed_token(token_details: dict = Depends(RefreshTokenBearer())):
    """
    Exchange a valid refresh token for a new access token.
    """
    expiry_dt = datetime.fromtimestamp(token_details["exp"], tz=timezone.utc)
    if expiry_dt <= datetime.now(timezone.utc):
        raise InvalidToken()

    new_access_token = create_access_token(user_data=token_details["user"])
    return JSONResponse(content={"access_token": new_access_token})


@auth_router.get("/current-user", response_model=UserBooksModel)
async def get_current_user_route(
        user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    """
    Return the currently logged-in user's data (including books, reviews).
    """
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    """
    Revoke an access token by adding its jti to the blocklist.
    """
    jti = token_details["jti"]
    await token_blocklist_client.add_jti_to_blocklist(jti)
    return JSONResponse(content={"message": "Logged out successfully"}, status_code=status.HTTP_200_OK)


# -------------------------------------------
# Password Reset Flow
# -------------------------------------------
# 1. Provide email -> queue password reset email
# 2. User clicks link -> /password-reset-confirm
# 3. Reset password
# -------------------------------------------

@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    """
    Queue a password-reset email with a token link for the user to confirm.
    """
    email = email_data.email
    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    subject = "Reset Your Password"
    html_message = f"""
    <h1>Reset your Password</h1>
    <p>Please click the <a href="{link}">link</a> below to Reset Your Password</p>
    """

    send_email_task.delay([email], subject, html_message)
    return JSONResponse(
        content={"message": "Please check your email for instructions to reset your password"},
        status_code=status.HTTP_200_OK
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
        token: str,
        passwords: PasswordResetConfirmModel,
        session: AsyncSession = Depends(get_session)
):
    """
    Confirm a user's password reset using the token from their email.
    """
    if passwords.new_password != passwords.confirmed_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    token_data = decode_url_safe_token(token)
    if not token_data:
        return JSONResponse(
            content={"message": "Error occurred during password reset"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    user_email = token_data.get("email")
    if not user_email:
        return JSONResponse(
            content={"message": "Error occurred during password reset"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise UserNotFound()

    hashed_password = generate_passwd_hash(passwords.new_password)
    await user_service.update_user(user, {"password_hash": hashed_password}, session)

    return JSONResponse(
        content={"message": "Password reset Successfully"},
        status_code=status.HTTP_200_OK,
    )
