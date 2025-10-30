from uuid import uuid4

from sqlalchemy import Column, String, Integer, select, Text, ForeignKey
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.services import Base
from sqlalchemy.orm import relationship
from app.models.crud import CRUDBase
from app.models.timestamp import TimestampMixin

class User(Base, CRUDBase, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)


    profile = relationship("UserProfile", back_populates="user", uselist=False)

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str):
        query = select(cls).where(cls.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

class UserProfile(Base, CRUDBase, TimestampMixin):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True,autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    avatar_url = Column(String(255))
    bio = Column(Text)
    phone_number = Column(String(20))
    address = Column(String(255))

    
    # Relaciones
    user = relationship("User", back_populates="profile")