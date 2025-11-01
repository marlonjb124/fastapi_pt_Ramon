from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserPublic, UserCreate
from app.core.deps import sessionDep
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User as UserModel
from app.core.security import get_password_hash
router = APIRouter(prefix="/user", tags=["user"])




@router.get("/get-user", response_model=UserPublic)
async def get_user(id: str, db:sessionDep):
    user = await UserModel.get(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/get-users", response_model=list[UserPublic])
async def get_users(db: sessionDep):
    users = await UserModel.get_all(db)
    return users


# @router.post("/create-user", response_model=UserPublic)
# async def create_user(user: UserCreate, db:sessionDep):
#     password_hash = get_password_hash(user.password)
#     verify_user = await UserModel.get_by_email(db, user.email)
 
#     if verify_user:
#         raise HTTPException(status_code=400, detail="User already exists")
#     user_model = await UserModel.create(db, password_hash=password_hash, **user.model_dump(exclude={"password"}))
#     return user_model
