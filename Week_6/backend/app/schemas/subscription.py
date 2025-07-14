from pydantic import BaseModel
from typing import Optional
import uuid

class SubscriptionOut(BaseModel):
    id: uuid.UUID
    name: str
    price: float
    features: Optional[dict]

    class Config:
        orm_mode = True

class SubscriptionUpgrade(BaseModel):
    subscription_id: uuid.UUID 