from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.db.session import get_db
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db), request: Request = None):
    # Only allow admin creation by an authenticated admin
    role = user_in.role if hasattr(user_in, 'role') else 'user'
    if role == 'admin':
        # Check for admin token in Authorization header
        auth_header = request.headers.get('Authorization') if request else None
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=403, detail="Admin creation requires admin authentication")
        from app.api.user import get_current_user
        try:
            current_admin = get_current_user(token=auth_header.split(' ')[1], db=db)
        except Exception:
            raise HTTPException(status_code=403, detail="Invalid admin token")
        if not current_admin or current_admin.role != 'admin':
            raise HTTPException(status_code=403, detail="Only admins can create other admins")
    else:
        role = 'user'
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role=role,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return user

@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    # Stateless JWT: logout is handled client-side
    return {"message": "Logged out"} 