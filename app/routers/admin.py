from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.user import User
from app.schemas.user import UserPublic, UserRoleUpdate
from app.core.deps import sessionDep, adminDep

router = APIRouter(prefix="/admin", tags=["admin"])



@router.get(
    "/users",
    response_model=List[UserPublic],
    summary="Listar todos los usuarios",
    description="Devuelve una lista de todos los usuarios registrados. Solo accesible para administradores."
)
async def list_all_users(
    db: sessionDep,
    admin_user: adminDep,
    skip: int = 0,
    limit: int = 100,
):
    users = await User.get_all(db, skip=skip, limit=limit)
    return users



@router.get(
    "/users/{user_id}",
    response_model=UserPublic,
    summary="Obtener usuario por ID",
    description="Devuelve la información de un usuario específico por su ID. Solo accesible para administradores."
)
async def get_user_by_id(
    user_id: int,
    db: sessionDep,
    admin_user: adminDep,
):
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user



@router.put(
    "/users/{user_id}/role",
    response_model=UserPublic,
    summary="Actualizar el rol de un usuario",
    description="Permite a un administrador cambiar el rol de un usuario. No puedes cambiar tu propio rol."
)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: sessionDep,
    admin_user: adminDep,
):
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes cambiar tu propio rol"
        )
    
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    updated_user = await User.update(db, user_id, role=role_update.role)
    return updated_user



@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un usuario",
    description="Elimina un usuario por su ID. No puedes eliminar tu propia cuenta. Solo accesible para administradores."
)
async def delete_user(
    user_id: int,
    db: sessionDep,
    admin_user: adminDep,
):
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta"
        )
    
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    await User.delete(db, user_id)
