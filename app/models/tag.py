from sqlalchemy import Column, String, Integer,select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from app.db.services import Base
from app.models.crud import CRUDBase
from app.models.timestampmixin import TimestampMixin
from app.models.visibilitymixin import VisibilityMixin

class Tag(Base, CRUDBase, TimestampMixin, VisibilityMixin):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    
    posts = relationship("Post",secondary="posts_tags", back_populates="tags", uselist=True)
    @classmethod
    async def search_by_title(cls, db: AsyncSession, title: str):

        query = select(cls).where(cls.title.ilike(f"%{title}%"))
        result = await db.execute(query)
        return result.scalars().all()