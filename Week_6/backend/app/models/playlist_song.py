from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base

class PlaylistSong(Base):
    __tablename__ = "playlist_songs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    playlist_id = Column(UUID(as_uuid=True), ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint("playlist_id", "song_id", name="uix_playlist_song"),) 