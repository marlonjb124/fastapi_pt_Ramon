from sqlalchemy import Column, String, Integer, ForeignKey, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload , joinedload
from app.db.services import Base
from app.models.crud import CRUDBase
from app.models.timestampmixin import TimestampMixin
from app.models.visibilitymixin import VisibilityMixin

class Post(Base, CRUDBase, TimestampMixin, VisibilityMixin):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, unique=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    content = Column(String, nullable=True)
    category = Column(String, nullable=True)
    

    user = relationship("User", back_populates="posts",uselist=False)
    tags= relationship("Tag", secondary="posts_tags", back_populates="posts", uselist=True)
    @classmethod
    async def search_by_title(cls, db: AsyncSession, title: str):
        query = select(cls).where(cls.title.ilike(f"%{title}%"))
        result = await db.execute(query)
        return result.scalars().all()
    @classmethod
    async def get_by_title(cls, db: AsyncSession, title: str):
        query = select(cls).where(cls.title == title)
        result = await db.execute(query)
        return result.scalars().first()
    @classmethod
    async def execute_query(cls, db: AsyncSession, query, load_type: str = "selectin"):
        if load_type == "selectin":
            query = query.options(selectinload(cls.user), selectinload(cls.tags))
        elif load_type == "joined":
            query = query.options(joinedload(cls.user), joinedload(cls.tags))

        result = await db.execute(query)
        return result.scalars().all()