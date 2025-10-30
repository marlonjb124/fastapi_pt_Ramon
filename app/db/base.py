from app.db.services import Base

# para autogenerar migraciones facilmente
from app.models.user import User, UserProfile
from app.models.post_tags import PostsTags
from app.models.tags import Tag
from app.models.posts import Post


__all__ = ["Base", "User", "PostsTags", "Tag", "Post", "UserProfile"]