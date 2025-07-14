from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.subscription import SubscriptionOut, SubscriptionUpgrade
from app.models.subscription import Subscription
from app.models.user import User
from app.db.session import get_db
from app.api.user import get_current_user

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.get("/", response_model=list[SubscriptionOut])
def list_subscriptions(db: Session = Depends(get_db)):
    return db.query(Subscription).all()

@router.post("/upgrade", response_model=SubscriptionOut)
def upgrade_subscription(upgrade: SubscriptionUpgrade, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subscription = db.query(Subscription).filter(Subscription.id == upgrade.subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if current_user.subscription_id == subscription.id:
        raise HTTPException(status_code=400, detail="Already on this subscription tier")
    current_user.subscription_id = subscription.id
    db.commit()
    db.refresh(current_user)
    return subscription 