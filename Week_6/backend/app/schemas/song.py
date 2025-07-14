from pydantic import BaseModel
from typing import Optional
import uuid

class SongCreate(BaseModel):
    album_id: Optional[uuid.UUID] = None
    artist_id: uuid.UUID
    title: str
    duration: int
    audio_url: str
    lyrics: Optional[str] = None
    genre: Optional[str] = None

class SongUpdate(BaseModel):
    album_id: Optional[uuid.UUID] = None
    title: Optional[str] = None
    duration: Optional[int] = None
    audio_url: Optional[str] = None
    lyrics: Optional[str] = None
    genre: Optional[str] = None

class SongOut(BaseModel):
    id: uuid.UUID
    album_id: Optional[uuid.UUID]
    artist_id: uuid.UUID
    title: str
    duration: int
    audio_url: str
    lyrics: Optional[str]
    genre: Optional[str]
    created_at: Optional[str]

    class Config:
        orm_mode = True 