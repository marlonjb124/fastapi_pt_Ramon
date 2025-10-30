from sqlalchemy import Column, String, Integer, ForeignKey, Uuid, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from app.db.services import Base
from app.models.crud import CRUDBase
from app.models.timestamp import TimestampMixin


class Post(Base, CRUDBase, TimestampMixin):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # hago posible nulo al autor pq puede ser un post anonimo
    title = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    content = Column(String, nullable=True)
    category = Column(String, nullable=True)

    user = relationship("User", back_populates="posts",uselist=False)
    tags= relationship("Tag", secondary="posts_tags", back_populates="posts", uselist=True)
    @classmethod
    async def get_by_title(cls, db: AsyncSession, title: str):

        query = select(cls).where(cls.title.ilike(f"%{title}%"))
        result = await db.execute(query)
        return result.scalars().all()