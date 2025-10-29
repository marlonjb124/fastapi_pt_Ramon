from app.db.services import Base

# para autogenerar migraciones facilmente
from app.models.user import User


__all__ = ["Base", "User"]