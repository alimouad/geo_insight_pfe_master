from datetime import datetime

from pydantic import BaseModel


class FavoriteBase(BaseModel):
    user_id: int
    analysis_id: int


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True