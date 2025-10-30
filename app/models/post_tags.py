from sqlalchemy import Column, ForeignKey, Integer
from app.db.services import Base

class PostsTags(Base):
    __tablename__ = "posts_tags"

    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)