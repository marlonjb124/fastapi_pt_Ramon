from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from app.schemas.visibilitymixin import VisibilitySchema
from app.schemas.timestampmixin import TimestampMixin
class Role(str, Enum):
    FREE_USER = "FREE_USER"
    PAID_USER = "PAID_USER"
    ADMIN = "ADMIN"
class UserBase(BaseModel):
    email: str
    full_name:str
    role: Optional[Role] = Role.FREE_USER  
class UserCreate(BaseModel):
    email:EmailStr
    password: str 
    full_name:str
    

class UserPublic(UserBase,TimestampMixin):
    id:int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[Role] = None

class UserRoleUpdate(BaseModel):
    role: Role   