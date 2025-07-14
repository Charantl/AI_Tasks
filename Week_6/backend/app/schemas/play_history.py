from pydantic import BaseModel
from typing import Optional, List
import uuid

class PlayHistoryCreate(BaseModel):
    song_id: uuid.UUID
    device: Optional[str] = None

class PlayHistoryOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    song_id: uuid.UUID
    played_at: Optional[str]
    device: Optional[str]
    class Config:
        orm_mode = True

class PlayHistoryWithSong(BaseModel):
    id: uuid.UUID
    song_id: uuid.UUID
    played_at: Optional[str]
    device: Optional[str]
    song_title: str
    artist_name: str
    class Config:
        orm_mode = True 