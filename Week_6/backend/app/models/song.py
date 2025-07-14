from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.models.base import Base

class Song(Base):
    __tablename__ = "songs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    album_id = Column(UUID(as_uuid=True), ForeignKey("albums.id", ondelete="SET NULL"))
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    audio_url = Column(String, nullable=False)
    lyrics = Column(Text)
    genre = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False) 