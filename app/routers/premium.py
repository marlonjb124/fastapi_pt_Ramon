from typing import List, Literal, Union
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.future import select

from app.models.post import Post
from app.schemas.post import PostPublic, PostPublicExtended
from app.core.deps import sessionDep, currentUserDep, premiumDep

router = APIRouter(prefix="/premium", tags=["premium"])


@router.get("/posts", response_model=List[Union[PostPublic, PostPublicExtended]])
async def list_paid_posts(
    db: sessionDep,
    current_user: premiumDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    load_type: Literal["lazy", "selectin", "joined"] = Query(default="selectin"),
):
    query = select(Post).where(Post.is_paid == True, Post.is_deleted == False)
    query = query.offset(skip).limit(limit)
    
    posts = await Post.execute_query(db, query, load_type=load_type)
    
    if load_type == "lazy":
        return [PostPublic.model_validate(p, from_attributes=True) for p in posts]
    return [PostPublicExtended.model_validate(p, from_attributes=True) for p in posts]


@router.get("/posts/{post_id}", response_model=Union[PostPublic, PostPublicExtended])
async def get_paid_post(
    post_id: int,
    db: sessionDep,
    current_user: premiumDep,
    load_type: Literal["lazy", "selectin", "joined"] = Query(default="selectin"),
):
    post = await Post.get_by_id(db, post_id, load_type=load_type)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if not post.is_paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This post is not a paid post"
        )
    
    if load_type == "lazy":
        return PostPublic.model_validate(post, from_attributes=True)
    return PostPublicExtended.model_validate(post, from_attributes=True)


@router.put("/posts/{post_id}/toggle-paid", response_model=Union[PostPublic, PostPublicExtended])
async def toggle_post_paid_status(
    post_id: int,
    db: sessionDep,
    current_user: currentUserDep,
    is_paid: bool = Query(...),
    load_type: Literal["lazy", "selectin", "joined"] = Query(default="selectin"),
):
    post = await Post.get_by_id(db, post_id, load_type="lazy")
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can change payment status"
        )
    
    updated_post = await Post.update(db, post_id, is_paid=is_paid)
    db_post_loaded = await Post.get_by_id(db, updated_post.id, load_type=load_type)
    
    if load_type == "lazy":
        return PostPublic.model_validate(db_post_loaded, from_attributes=True)
    return PostPublicExtended.model_validate(db_post_loaded, from_attributes=True)


@router.get("/my-posts", response_model=List[Union[PostPublic, PostPublicExtended]])
async def my_paid_posts(
    db: sessionDep,
    current_user: currentUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    load_type: Literal["lazy", "selectin", "joined"] = Query(default="selectin"),
):
    query = select(Post).where(
        Post.owner_id == current_user.id,
        Post.is_paid == True,
        Post.is_deleted == False
    )
    query = query.offset(skip).limit(limit)
    
    posts = await Post.execute_query(db, query, load_type=load_type)
    
    if load_type == "lazy":
        return [PostPublic.model_validate(p, from_attributes=True) for p in posts]
    return [PostPublicExtended.model_validate(p, from_attributes=True) for p in posts]
