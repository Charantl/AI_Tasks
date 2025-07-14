from pydantic import BaseModel
from typing import Optional
import uuid

class ShareCreate(BaseModel):
    platform: str  # e.g., "twitter", "facebook", "whatsapp", "copy_link"
    message: Optional[str] = None

class ShareOut(BaseModel):
    song_id: uuid.UUID
    platform: str
    share_url: str
    message: Optional[str]
    class Config:
        orm_mode = True 