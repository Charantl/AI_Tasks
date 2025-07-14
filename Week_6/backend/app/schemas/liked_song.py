from pydantic import BaseModel
from typing import Optional, List
import uuid

class LikedSongCreate(BaseModel):
    song_id: uuid.UUID

class LikedSongOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    song_id: uuid.UUID
    liked_at: Optional[str]
    class Config:
        orm_mode = True

class LikedSongWithSong(BaseModel):
    id: uuid.UUID
    song_id: uuid.UUID
    liked_at: Optional[str]
    song_title: str
    artist_name: str
    class Config:
        orm_mode = True 