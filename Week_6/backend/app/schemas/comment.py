from pydantic import BaseModel
from typing import Optional, List
import uuid

class CommentCreate(BaseModel):
    content: str

class CommentUpdate(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    song_id: uuid.UUID
    content: str
    created_at: Optional[str]
    class Config:
        orm_mode = True

class CommentWithUser(BaseModel):
    id: uuid.UUID
    song_id: uuid.UUID
    content: str
    created_at: Optional[str]
    username: str
    class Config:
        orm_mode = True 