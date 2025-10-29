from fastapi import APIRouter, Depends
from app.schemas.user import UserSchema, UserSchemaCreate
from app.db.services import SessionDep
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User as UserModel
from app.core.security import get_password_hash
router = APIRouter(prefix="/user", tags=["user"])




@router.get("/get-user", response_model=UserSchema)
async def get_user(id: str, db:SessionDep):
    user = await UserModel.get(db, id)
    return user


@router.get("/get-users", response_model=list[UserSchema])
async def get_users(db: SessionDep):
    users = await UserModel.get_all(db)
    return users


@router.post("/create-user", response_model=UserSchema)
async def create_user(user: UserSchemaCreate, db:SessionDep):
    password_hash = get_password_hash(user.password)
    print("ASDSADSADSADasadasdasdasdsadsadsa")
    print(password_hash)
    user_model = await UserModel.create(db, password_hash=password_hash, **user.model_dump(exclude={"password"}))
    return user_model