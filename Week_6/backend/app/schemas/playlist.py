from pydantic import BaseModel
from typing import Optional, List
import uuid

class PlaylistCreate(BaseModel):
    name: str
    is_public: bool = False

class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    is_public: Optional[bool] = None

class PlaylistOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    is_public: bool
    created_at: Optional[str]
    class Config:
        orm_mode = True

class PlaylistSongAdd(BaseModel):
    song_id: uuid.UUID
    position: int

class PlaylistSongOut(BaseModel):
    id: uuid.UUID
    playlist_id: uuid.UUID
    song_id: uuid.UUID
    position: int
    class Config:
        orm_mode = True 