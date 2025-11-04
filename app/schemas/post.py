from pydantic import BaseModel, Field
from typing import Optional, List
from app.schemas.tag import TagPublic
from app.schemas.user import UserPublic
from app.schemas.timestampmixin import TimestampMixin
from app.schemas.visibilitymixin import VisibilitySchema


class PostBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None


class PostCreate(PostBase):
    tag_ids: List[int] = Field(default_factory=list, description="List of tag IDs to associate")


class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    is_visible: Optional[bool] = None
    is_paid: Optional[bool] = None


class PostTagsUpdate(BaseModel):
    tag_ids: List[int] = Field(..., description="New list of tag IDs")
    
class PostPublic(PostBase, TimestampMixin, VisibilitySchema):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class PostPublicExtended(PostPublic):
    user: Optional[UserPublic] = None
    tags: List[TagPublic] = []

    class Config:
        from_attributes = True



