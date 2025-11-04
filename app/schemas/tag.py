from pydantic import BaseModel
from app.schemas.timestampmixin import TimestampMixin
from typing import Optional


class TagBase(BaseModel):
    title: str
    description: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class TagPublic(TagBase, TimestampMixin):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
