from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from app.schemas.user import UserOut, UserUpdate
from app.models.user import User
from app.db.session import get_db
from app.core.security import decode_access_token, hash_password
from fastapi.security import OAuth2PasswordBearer
from app.core.cache import Cache
from app.schemas.user import UserLogin
from app.core.security import verify_password
from app.core.security import create_access_token
from typing import List

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Admin access required')
    return current_user

@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user.id)})
    # Cache session data
    Cache.set(f"session:{user.id}", {"user_id": str(user.id), "email": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # Invalidate session cache
    Cache.invalidate(f"session:{current_user.id}")
    return {"message": "Logged out"}

@router.patch("/profile")
def update_profile(profile_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if profile_update.username:
        current_user.username = profile_update.username
    if profile_update.email:
        current_user.email = profile_update.email
    if hasattr(profile_update, 'avatar') and profile_update.avatar is not None:
        current_user.avatar = profile_update.avatar
    if profile_update.password:
        current_user.password_hash = hash_password(profile_update.password)
    db.commit()
    db.refresh(current_user)
    # Invalidate session cache
    Cache.invalidate(f"session:{current_user.id}")
    return current_user

@router.get("/all", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Security(admin_required)):
    return db.query(User).all() 