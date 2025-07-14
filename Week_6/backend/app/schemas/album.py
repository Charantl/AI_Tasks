from pydantic import BaseModel
from typing import Optional
import uuid

class AlbumCreate(BaseModel):
    artist_id: uuid.UUID
    title: str
    release_date: Optional[str] = None
    cover_url: Optional[str] = None

class AlbumUpdate(BaseModel):
    title: Optional[str] = None
    release_date: Optional[str] = None
    cover_url: Optional[str] = None

class AlbumOut(BaseModel):
    id: uuid.UUID
    artist_id: uuid.UUID
    title: str
    release_date: Optional[str]
    cover_url: Optional[str]

    class Config:
        orm_mode = True 