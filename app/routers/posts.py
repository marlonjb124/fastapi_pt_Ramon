from typing import List, Literal, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.post import Post
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostPublic,
    PostPublicExtended
)
from app.schemas.user import Role
from app.core.deps import sessionDep, currentUserDep
from app.models.visibilitymixin import VisibilityMixin

router = APIRouter(prefix="/posts", tags=["posts"])



@router.post(
    "/",
    response_model=Union[PostPublic, PostPublicExtended],
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo post",
    description=(
        "Crea un nuevo post asociado al usuario autenticado. "
        "Si el título ya existe, devuelve un error 400. "
        "Puedes definir el tipo de carga (`lazy`, `selectin`, `joined`)."
    ),
)
async def create_post(
    post_in: PostCreate,
    db: sessionDep,
    current_user: currentUserDep,
    load_type: Literal["lazy", "selectin", "joined"] = Query(
        default="selectin",
        description="Define cómo se cargan las relaciones (lazy, selectin, joined)."
    )
):
    existing = await Post.get_by_title(db, post_in.title)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A post with this title already exists"
        )

    db_post = await Post.create(db, **post_in.model_dump(), owner_id=current_user.id)
    db_post_loaded = await Post.get_by_id(db, db_post.id, load_type=load_type)

    if load_type == "lazy":
        return PostPublic.model_validate(db_post_loaded, from_attributes=True)
    return PostPublicExtended.model_validate(db_post_loaded, from_attributes=True)



@router.get(
    "/{post_id}",
    response_model=Union[PostPublic, PostPublicExtended],
    summary="Get post by ID",
)
async def read_post(
    post_id: int,
    db: sessionDep,
    current_user: currentUserDep,
    load_type: Literal["lazy", "selectin", "joined"] = Query(default="selectin"),
):
    db_post = await Post.get_by_id(db, post_id, load_type=load_type)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not db_post.has_permission(
        current_user_role=current_user.role,
        user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access this resource"
        )

    if load_type == "lazy":
        return PostPublic.model_validate(db_post, from_attributes=True)
    return PostPublicExtended.model_validate(db_post, from_attributes=True)



@router.get(
    "/search/",
    response_model=List[Union[PostPublic, PostPublicExtended]],
    summary="Buscar posts por título",
    description=(
        "Permite buscar posts por coincidencia parcial o total en el título. "
        "Aplica automáticamente las restricciones de visibilidad definidas "
        "por el rol del usuario actual."
    ),
)
async def search_posts(
    db: sessionDep,
    current_user: currentUserDep,
    title: str = Query(..., description="Texto parcial o completo del título a buscar."),
    skip: int = Query(0, ge=0, description="Resultados a omitir."),
    limit: int = Query(50, le=100, description="Resultados máximos a devolver."),
    load_type: Literal["lazy", "selectin", "joined"] = Query(
        default="selectin",
        description="Tipo de carga de relaciones."
    ),
):
    query = select(Post).where(Post.title.ilike(f"%{title}%"))
    query = VisibilityMixin.apply_visibility_filters(
        query,
        model_cls=Post,
        current_user_role=current_user.role,
        user_id=current_user.id
    )
    query = query.offset(skip).limit(limit)

    posts = await Post.execute_query(db, query, load_type=load_type)

    if load_type == "lazy":
        return [PostPublic.model_validate(p, from_attributes=True) for p in posts]
    return [PostPublicExtended.model_validate(p, from_attributes=True) for p in posts]


@router.get(
    "/",
    response_model=List[Union[PostPublic, PostPublicExtended]],
    summary="Listar posts visibles",
    description=(
        "Lista los posts visibles según el rol del usuario y las reglas de visibilidad. "
        "Soporta paginación y distintos tipos de carga de relaciones."
    ),
)
async def list_posts(
    db: sessionDep,
    current_user: currentUserDep,
    skip: int = Query(0, ge=0, description="Número de posts a omitir (paginación)."),
    limit: int = Query(100, le=100, description="Cantidad máxima de posts."),
    load_type: Literal["lazy", "selectin", "joined"] = Query(
        default="selectin",
        description="Tipo de carga de relaciones (lazy, selectin, joined)."
    ),
):
    query = select(Post)
    query = VisibilityMixin.apply_visibility_filters(
        query,
        model_cls=Post,
        current_user_role=current_user.role,
        user_id=current_user.id
    )
    query = query.offset(skip).limit(limit)

    posts = await Post.execute_query(db, query, load_type=load_type)
    if load_type == "lazy":
        return [PostPublic.model_validate(p, from_attributes=True) for p in posts]
    return [PostPublicExtended.model_validate(p, from_attributes=True) for p in posts]



@router.put(
    "/{post_id}",
    response_model=Union[PostPublic, PostPublicExtended],
    summary="Actualizar un post existente",
    description=(
        "Permite actualizar un post existente. "
        "Solo el propietario puede modificarlo (incluyendo campos de visibilidad)."
    ),
)
async def update_post(
    post_id: int,
    post_in: PostUpdate,
    db: sessionDep,
    current_user: currentUserDep,
    load_type: Literal["lazy", "selectin", "joined"] = Query(
        default="selectin",
        description="Tipo de carga de relaciones."
    ),
):
    try:
        updated_post = await Post.update_with_ownership(
            db=db,
            resource_id=post_id,
            current_user_id=current_user.id,
            update_data=post_in.model_dump(exclude_unset=True)
        )
        
        if not updated_post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        db_post_loaded = await Post.get_by_id(db, updated_post.id, load_type=load_type)
        
        if load_type == "lazy":
            return PostPublic.model_validate(db_post_loaded, from_attributes=True)
        return PostPublicExtended.model_validate(db_post_loaded, from_attributes=True)
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )



@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete post",
)
async def delete_post(
    post_id: int,
    db: sessionDep,
    current_user: currentUserDep,
):
    try:
        deleted_post = await Post.soft_delete_with_ownership(
            db=db,
            resource_id=post_id,
            current_user_id=current_user.id
        )
        
        if not deleted_post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return {"ok": True, "message": "Post deleted successfully"}
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.post(
    "/{post_id}/restore",
    response_model=Union[PostPublic, PostPublicExtended],
    summary="Restore deleted post",
)
async def restore_post(
    post_id: int,
    db: sessionDep,
    current_user: currentUserDep,
    load_type: Literal["lazy", "selectin", "joined"] = Query(default="selectin"),
):
    try:
        restored_post = await Post.restore_with_ownership(
            db=db,
            resource_id=post_id,
            current_user_id=current_user.id
        )
        
        if not restored_post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        db_post_loaded = await Post.get_by_id(db, restored_post.id, load_type=load_type)
        
        if load_type == "lazy":
            return PostPublic.model_validate(db_post_loaded, from_attributes=True)
        return PostPublicExtended.model_validate(db_post_loaded, from_attributes=True)
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
