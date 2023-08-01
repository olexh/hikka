from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_user_by_username
from app.database import get_session
from datetime import datetime
from app.errors import Abort
from fastapi import Depends
from app.models import User
from .utils import checkpwd

from .service import (
    get_user_by_activation,
    get_user_by_email,
    get_user_by_reset,
)

from .schemas import (
    ComfirmResetArgs,
    SignupArgs,
    LoginArgs,
    EmailArgs,
    TokenArgs,
)


async def body_email_user(
    args: EmailArgs,
    session: AsyncSession = Depends(get_session),
) -> User:
    # Get user by email
    if not (user := await get_user_by_email(session, args.email)):
        raise Abort("auth", "user-not-found")

    return user


async def validate_signup(
    signup: SignupArgs, session: AsyncSession = Depends(get_session)
) -> SignupArgs:
    # Check if username is availaible
    if await get_user_by_username(session, signup.username):
        raise Abort("auth", "username-taken")

    # Check if email has been used
    if await get_user_by_email(session, signup.email):
        raise Abort("auth", "email-exists")

    # if signup.email not in test_emails:
    #     raise Abort("auth", "banned")

    return signup


async def validate_login(
    login: LoginArgs, session: AsyncSession = Depends(get_session)
) -> User:
    # Find user by email
    if not (user := await get_user_by_email(session, login.email)):
        raise Abort("auth", "user-not-found")

    # Check password hash
    if not checkpwd(login.password, user.password_hash):
        raise Abort("auth", "invalid-password")

    # Make sure user is activated
    if not user.activated:
        raise Abort("auth", "not-activated")

    return user


async def validate_provider(provider: str) -> str:
    if provider not in ["google"]:
        raise Abort("auth", "invalid-provider")

    return provider


async def validate_activation(
    args: TokenArgs,
    session: AsyncSession = Depends(get_session),
) -> User:
    # Find user by activation token
    if not (user := await get_user_by_activation(session, args.token)):
        raise Abort("auth", "activation-invalid")

    # Let's have it here just in case
    if not user.activation_expire:
        raise Abort("auth", "activation-expired")

    # Check if activation token still valid
    if user.activation_expire < datetime.utcnow():
        raise Abort("auth", "activation-expired")

    return user


async def validate_activation_resend(
    user: User = Depends(body_email_user),
) -> User:
    # Make sure user not yet activated
    if user.activated:
        raise Abort("auth", "already-activated")

    # Prevent sending new activation email if previous token still valid
    if user.activation_expire:
        if datetime.utcnow() < user.activation_expire:
            raise Abort("auth", "activation-valid")

    return user


async def validate_password_reset(
    user: User = Depends(body_email_user),
) -> User:
    # Make sure user is activated
    if not user.activated:
        raise Abort("auth", "not-activated")

    # Prevent sending new password reset email if previous token still valid
    if user.password_reset_expire:
        if datetime.utcnow() < user.password_reset_expire:
            raise Abort("auth", "reset-valid")

    return user


async def validate_password_confirm(
    confirm: ComfirmResetArgs, session: AsyncSession = Depends(get_session)
):
    # Get user by reset token
    if not (user := await get_user_by_reset(session, confirm.token)):
        raise Abort("auth", "reset-invalid")

    # Just in case
    if not user.password_reset_expire:
        raise Abort("auth", "reset-expired")

    # Make sure reset token is valid
    if datetime.utcnow() > user.password_reset_expire:
        raise Abort("auth", "reset-expired")

    return user, confirm.password
