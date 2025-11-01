from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.core.deps import sessionDep, currentUserDep, get_current_active_user
from app.models.user import User as UserModel
from app.schemas.user import Role, UserCreate, UserPublic, Token, TokenData
from app.core.security import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])



def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta 
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )

# Authentication dependencies



# API endpoints

@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: sessionDep,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    # Get user from database
    result = await db.execute(select(UserModel).filter(UserModel.email == form_data.username))
    user = result.scalars().first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: currentUserDep
) -> UserModel:
    return current_user