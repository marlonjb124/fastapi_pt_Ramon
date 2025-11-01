from app.db.services import Base

# para autogenerar migraciones facilmente
from app.models.user import User, UserProfile
from app.models.post_tag import PostsTags
from app.models.tag import Tag
from app.models.post import Post
# from app.models.timestampmixin import TimestampMixin
# from app.models.visibilitymixin import VisibilityMixin



__all__ = ["Base", "User", "PostsTags", "Tag", "Post", "UserProfile"]