from typing import List, Literal, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate, TagPublic
from app.schemas.user import Role
from app.core.deps import sessionDep, currentUserDep
from app.models.visibilitymixin import VisibilityMixin

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post(
    "/",
    response_model=TagPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo tag",
    description="Crea un nuevo tag asociado al usuario autenticado.",
)
async def create_tag(
    tag_in: TagCreate,
    db: sessionDep,
    current_user: currentUserDep,
):
    existing = await Tag.get_by_title(db, tag_in.title)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un tag con este título."
        )

    db_tag = await Tag.create(db, **tag_in.model_dump(), owner_id=current_user.id)
    return TagPublic.model_validate(db_tag, from_attributes=True)


@router.get(
    "/{tag_id}",
    response_model=TagPublic,
    summary="Obtener un tag por ID",
    description="Devuelve la información del tag según su visibilidad y el rol del usuario.",
)
async def read_tag(
    tag_id: int,
    db: sessionDep,
    current_user: currentUserDep,
):
    db_tag = await Tag.get_by_id(db, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado.")

    if not db_tag.has_permission(
        current_user_role=current_user.role,
        user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a este recurso."
        )

    return TagPublic.model_validate(db_tag, from_attributes=True)


@router.get(
    "/search/",
    response_model=List[TagPublic],
    summary="Buscar tags por título",
    description="Permite buscar tags por coincidencia parcial o total en el título.",
)
async def search_tags(
    db: sessionDep,
    current_user: currentUserDep,
    title: str = Query(..., description="Texto parcial o completo del título a buscar."),
    skip: int = Query(0, ge=0, description="Resultados a omitir."),
    limit: int = Query(50, le=100, description="Resultados máximos a devolver."),
):
    query = select(Tag).where(Tag.title.ilike(f"%{title}%"))
    query = VisibilityMixin.apply_visibility_filters(
        query,
        model_cls=Tag,
        current_user_role=current_user.role,
        user_id=current_user.id
    )
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    tags = result.scalars().all()

    return [TagPublic.model_validate(t, from_attributes=True) for t in tags]


@router.get(
    "/",
    response_model=List[TagPublic],
    summary="Listar tags visibles",
    description="Lista los tags visibles según el rol del usuario y las reglas de visibilidad.",
)
async def list_tags(
    db: sessionDep,
    current_user: currentUserDep,
    skip: int = Query(0, ge=0, description="Número de tags a omitir."),
    limit: int = Query(100, le=100, description="Cantidad máxima de tags."),
):
    query = select(Tag)
    query = VisibilityMixin.apply_visibility_filters(
        query,
        model_cls=Tag,
        current_user_role=current_user.role,
        user_id=current_user.id
    )
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    tags = result.scalars().all()

    return [TagPublic.model_validate(t, from_attributes=True) for t in tags]


@router.put(
    "/{tag_id}",
    response_model=TagPublic,
    summary="Actualizar un tag existente",
    description=(
        "Permite actualizar un tag existente. "
        "Solo el propietario puede modificarlo (incluyendo campos de visibilidad)."
    ),
)
async def update_tag(
    tag_id: int,
    tag_in: TagUpdate,
    db: sessionDep,
    current_user: currentUserDep,
):
    try:
        # Usa el método heredado del VisibilityMixin que verifica propiedad
        updated_tag = await Tag.update_with_ownership(
            db=db,
            resource_id=tag_id,
            current_user_id=current_user.id,
            update_data=tag_in.model_dump(exclude_unset=True)
        )
        
        if not updated_tag:
            raise HTTPException(status_code=404, detail="Tag no encontrado.")
        
        return TagPublic.model_validate(updated_tag, from_attributes=True)
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Realizar soft delete de un tag",
    description="Marca un tag como eliminado. Solo el propietario puede eliminarlo.",
)
async def delete_tag(
    tag_id: int,
    db: sessionDep,
    current_user: currentUserDep,
):
    try:
        # Usa el método heredado del VisibilityMixin
        deleted_tag = await Tag.soft_delete_with_ownership(
            db=db,
            resource_id=tag_id,
            current_user_id=current_user.id
        )
        
        if not deleted_tag:
            raise HTTPException(status_code=404, detail="Tag no encontrado.")
        
        return {"ok": True, "message": "Tag eliminado exitosamente"}
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.post(
    "/{tag_id}/restore",
    response_model=TagPublic,
    summary="Restaurar un tag eliminado",
    description="Restaura un tag que fue marcado como eliminado. Solo el propietario puede restaurarlo.",
)
async def restore_tag(
    tag_id: int,
    db: sessionDep,
    current_user: currentUserDep,
):
    try:
        # Usa el método heredado del VisibilityMixin
        restored_tag = await Tag.restore_with_ownership(
            db=db,
            resource_id=tag_id,
            current_user_id=current_user.id
        )
        
        if not restored_tag:
            raise HTTPException(status_code=404, detail="Tag no encontrado.")
        
        return TagPublic.model_validate(restored_tag, from_attributes=True)
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
