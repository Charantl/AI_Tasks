from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from app.models.base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    features = Column(JSONB) 