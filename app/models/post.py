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
    
    @classmethod
    async def add_tags(cls, db: AsyncSession, post_id: int, tag_ids: list[int]):
        from app.models.tag import Tag
        
        post = await cls.get_by_id(db, post_id, load_type="selectin")
        if not post:
            return None
        
        if not tag_ids:
            return post
        
        query = select(Tag).where(Tag.id.in_(tag_ids))
        result = await db.execute(query)
        tags = result.scalars().all()
        
        existing_tag_ids = {tag.id for tag in post.tags}
        new_tags = [tag for tag in tags if tag.id not in existing_tag_ids]
        
        if new_tags:
            post.tags.extend(new_tags)
            await db.commit()
            await db.refresh(post)
        
        return post

    @classmethod
    async def remove_tags(cls, db: AsyncSession, post_id: int, tag_ids: list[int]):
        post = await cls.get_by_id(db, post_id, load_type="selectin")
        if not post:
            return None
        
        if not tag_ids:
            return post
        
        tag_ids_set = set(tag_ids)
        post.tags = [tag for tag in post.tags if tag.id not in tag_ids_set]
        
        await db.commit()
        await db.refresh(post)
        return post

    @classmethod
    async def set_tags(cls, db: AsyncSession, post_id: int, tag_ids: list[int]):
        from app.models.tag import Tag
        
        post = await cls.get_by_id(db, post_id, load_type="selectin")
        if not post:
            return None
        
        if not tag_ids:
            post.tags = []
        else:
            query = select(Tag).where(Tag.id.in_(tag_ids))
            result = await db.execute(query)
            post.tags = result.scalars().all()
        
        await db.commit()
        await db.refresh(post)
        return post