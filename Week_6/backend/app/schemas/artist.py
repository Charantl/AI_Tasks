from pydantic import BaseModel
from typing import Optional
import uuid

class ArtistCreate(BaseModel):
    name: str
    bio: Optional[str] = None
    image_url: Optional[str] = None

class ArtistUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None

class ArtistOut(BaseModel):
    id: uuid.UUID
    name: str
    bio: Optional[str]
    image_url: Optional[str]
    created_at: Optional[str]

    class Config:
        orm_mode = True 