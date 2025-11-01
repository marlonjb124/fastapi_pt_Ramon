from datetime import datetime
from pydantic import BaseModel

class TimestampMixin():
    created_at: datetime
    updated_at: datetime 