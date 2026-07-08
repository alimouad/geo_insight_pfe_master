from datetime import datetime

from pydantic import BaseModel


class NotificationBase(BaseModel):
    user_id: int
    title: str
    message: str
    is_read: bool = False


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True