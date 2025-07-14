from sqlalchemy import Column, String, UUID, ARRAY, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from app.models.base import Base
import uuid


class Embedding(Base):
    """Model for storing vector embeddings for semantic search."""
    __tablename__ = "embeddings"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False)  # 'song', 'artist', 'album'
    entity_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    embedding = Column(ARRAY(Float), nullable=True)  # Vector embedding

    # Ensure unique embeddings per entity
    __table_args__ = (
        UniqueConstraint('entity_type', 'entity_id', name='uix_entity_embedding'),
    )

    def __repr__(self):
        return f"<Embedding(entity_type='{self.entity_type}', entity_id='{self.entity_id}')>" 