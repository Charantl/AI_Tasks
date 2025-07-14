from pydantic import BaseModel
from typing import Optional, List
import uuid

class AnalyticsCreate(BaseModel):
    song_id: uuid.UUID
    event_type: str
    device: Optional[str] = None

class AnalyticsOut(BaseModel):
    id: uuid.UUID
    song_id: uuid.UUID
    user_id: Optional[uuid.UUID]
    event_type: str
    event_time: Optional[str]
    device: Optional[str]
    class Config:
        orm_mode = True

class SongAnalytics(BaseModel):
    song_id: uuid.UUID
    song_title: str
    total_plays: int
    unique_listeners: int
    total_likes: int
    total_shares: int
    class Config:
        orm_mode = True

class UserAnalytics(BaseModel):
    user_id: uuid.UUID
    username: str
    total_songs_played: int
    total_time_listened: int
    favorite_genre: str
    class Config:
        orm_mode = True 