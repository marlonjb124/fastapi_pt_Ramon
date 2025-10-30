from pydantic import BaseModel

class UserSchemaBase(BaseModel):
    email: str | None = None
    full_name: str | None = None

class UserSchemaCreate(UserSchemaBase):
    password: str
    


class UserSchema(UserSchemaBase):
    id: int
    class Config:
        from_attributes = True
    