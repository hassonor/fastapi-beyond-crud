from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime, timezone

from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from .schemas import UserCreateModel, UserLoginModel, UserBooksModel, EmailModel, PasswordResetRequestModel, \
    PasswordResetConfirmModel
from .service import UserService
from .utils import create_access_token, verify_password, create_url_safe_token, \
    decode_url_safe_token, generate_passwd_hash
from src.db.main import get_session
from src.db.redis import token_blocklist_client
from src.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from src.mail import mail, create_message
from src.config import Config

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin', 'user'])

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post('/send_mail')
async def send_mail(emails: EmailModel):
    emails = emails.addresses

    html = "<h1>Welcome to the app</h1>"

    message = create_message(recipients=emails, subject="Welcome", body=html)

    await mail.send_message(message)

    return {"message": "Email sent successfully."}


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise UserAlreadyExists()
    else:
        new_user = await user_service.create_user(user_data, session)

        token = create_url_safe_token({"email": email})

        link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

        html_message = f"""
        <h1>Verify your email</h1>
        <p>Please click the <a href="{link}">link</a> below to verify your email</p>
        """
        message = create_message(recipients=[email], subject="Verify your email", body=html_message)
        await mail.send_message(message)

        return {"message": "Account Created! Check email to verify your account", "user": new_user}


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occurred during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.post('/login')
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    "role": user.role,
                }
            )

            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )

    raise InvalidCredentials()


@auth_router.get('/refresh_token')
async def get_refreshed_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_dt = datetime.fromtimestamp(token_details['exp'], tz=timezone.utc)
    current_dt = datetime.now(timezone.utc)

    if expiry_dt > current_dt:
        new_access_token = create_access_token(
            user_data=token_details['user']
        )

        return JSONResponse(content={
            "access_token": new_access_token
        })

    raise InvalidToken()


@auth_router.get('/current-user', response_model=UserBooksModel)
async def get_current_user(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    return user


@auth_router.get('/logout')
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]
    await token_blocklist_client.add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message": "Logged out successfully"
        },
        status_code=status.HTTP_200_OK
    )


"""
1. PROVIDE THE EMAIL -> password reset request
2. SEND PASSWORD RESET LINK
3. RESET PASSWORD -> password reset confirm
"""


@auth_router.post('/password-reset-request')
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
      <h1>Reset your Password</h1>
      <p>Please click the <a href="{link}">link</a> below to Reset Your Password</p>
      """
    message = create_message(recipients=[email], subject="Reset Your Password", body=html_message)
    await mail.send_message(message)

    return JSONResponse(
        content={"message": "Please check your email for instructions to reset your password"},
        status_code=status.HTTP_200_OK
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(token: str, passwords: PasswordResetConfirmModel,
                                 session: AsyncSession = Depends(get_session)):
    new_password = passwords.new_password
    confirmed_new_password = passwords.confirmed_new_password
    if new_password != confirmed_new_password:
        raise HTTPException(detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST)

    token_data = decode_url_safe_token(token)
    if not token_data:
        # If decode returned None, we can't proceed
        return JSONResponse(
            content={"message": "Error occurred during password reset"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()

        hashed_password = generate_passwd_hash(new_password)
        await user_service.update_user(user, {"password_hash": hashed_password}, session)

        return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occurred during password reset"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
