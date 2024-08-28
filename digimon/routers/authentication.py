from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from typing import Annotated
import datetime

from .. import config
from .. import models
from .. import security

router = APIRouter(tags=["authentication"])

settings = config.get_settings()

@router.post("/token")
async def authenticate_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[models.AsyncSession, Depends(models.get_session)],
) -> models.Token:
    # Retrieve user by username
    user = await get_user_by_username_or_email(form_data.username, session)
    
    if not user or not await user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Update the last login date
    user.last_login_date = datetime.datetime.now()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    # Create tokens
    access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return models.Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.datetime.now() + access_token_expires,
        issued_at=user.last_login_date,
        user_id=user.id
    )

async def get_user_by_username_or_email(username_or_email: str, session: models.AsyncSession):
    # Attempt to find the user by username
    result = await session.exec(
        select(models.DBUser).where(models.DBUser.username == username_or_email)
    )
    user = result.one_or_none()
    
    # If not found by username, attempt to find by email
    if not user:
        result = await session.exec(
            select(models.DBUser).where(models.DBUser.email == username_or_email)
        )
        user = result.one_or_none()
    
    return user
