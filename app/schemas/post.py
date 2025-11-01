from pydantic import BaseModel
from typing import Optional, List
from app.schemas.tag import TagPublic
from app.schemas.user import UserPublic
from app.schemas.timestampmixin import TimestampMixin
from app.schemas.visibilitymixin import VisibilitySchema
# Assuming a TagPublic schema exists in app.schemas.tag
# from .tag import TagPublic 
# Assuming a UserPublic schema exists in app.schemas.user
# from .user import UserPublic

# For now, let's use placeholder schemas to avoid import errors


class TagPublic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel, TimestampMixin):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    
class PostPublic(PostBase, TimestampMixin):
    id: int
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True
class PostPublicExtended(PostBase, TimestampMixin):
    id: int
    owner_id: Optional[int] = None
    user: Optional[UserPublic] = None
    tags: List[TagPublic] = []

    class Config:
        from_attributes = True



