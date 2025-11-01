from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.user import User
from app.schemas.user import UserPublic, UserRoleUpdate
from app.core.deps import sessionDep, adminDep

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserPublic])
async def list_all_users(
    db: sessionDep,
    admin_user: adminDep,
    skip: int = 0,
    limit: int = 100,
):
    users = await User.get_all(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserPublic)
async def get_user_by_id(
    user_id: int,
    db: sessionDep,
    admin_user: adminDep,
):
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/users/{user_id}/role", response_model=UserPublic)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: sessionDep,
    admin_user: adminDep,
):
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = await User.update(db, user_id, role=role_update.role)
    return updated_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: sessionDep,
    admin_user: adminDep,
):
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await User.delete(db, user_id)
