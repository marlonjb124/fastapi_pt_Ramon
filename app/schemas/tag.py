from pydantic import BaseModel
from app.schemas.timestampmixin import TimestampMixin
from app.schemas.visibilitymixin import VisibilitySchema
from typing import Optional
class TagBase(BaseModel,TimestampMixin,VisibilitySchema):
    title: str
    description: str
    
class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class TagPublic(TagBase):
    id: int
    class Config:
        from_attributes = True
