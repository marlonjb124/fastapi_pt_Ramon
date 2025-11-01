from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.db.services import get_db
from app.models.user import User as UserModel
from app.schemas.user import Role, TokenData

oauth2_scheme = settings.OAUTH2_SCHEME

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
  
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract user data from token
        email: str = payload.get("sub")
        role: str = payload.get("role")
        
        if email is None or role is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(UserModel).filter(UserModel.email == email))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
        
    # Verify user is active
    if hasattr(user, 'is_deleted') and user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if hasattr(current_user, 'is_deleted') and current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
def require_role(required_roles: List[Role]):
    """
    Dependency factory to check if the current user has any of the required roles.
    
    Usage:
        @router.get("/admin")
        async def admin_route(
            current_user: UserModel = Depends(require_role([Role.ADMIN]))
        ):
            ...
    """
    def role_checker(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this resource",
            )
        return current_user
    
    return role_checker

# Common role-based dependencies
async def get_role(current_user: UserModel = Depends(get_current_user)) -> Role:
    """
    Dependency to get the current user's role.
    """
    return current_user.role

currentUserDep = Annotated[UserModel, Depends(get_current_user)]
sessionDep = Annotated[AsyncSession, Depends(get_db)]