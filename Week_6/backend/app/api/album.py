from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.album import AlbumCreate, AlbumUpdate, AlbumOut
from app.models.album import Album
from app.db.session import get_db

router = APIRouter(prefix="/albums", tags=["albums"])

@router.get("/", response_model=list[AlbumOut])
def list_albums(db: Session = Depends(get_db), q: str = None):
    query = db.query(Album)
    if q:
        query = query.filter(Album.title.ilike(f"%{q}%"))
    return query.all()

@router.post("/", response_model=AlbumOut)
def create_album(album_in: AlbumCreate, db: Session = Depends(get_db)):
    album = Album(**album_in.dict())
    db.add(album)
    db.commit()
    db.refresh(album)
    return album

@router.get("/{id}", response_model=AlbumOut)
def get_album(id: str, db: Session = Depends(get_db)):
    album = db.query(Album).filter(Album.id == id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

@router.patch("/{id}", response_model=AlbumOut)
def update_album(id: str, album_in: AlbumUpdate, db: Session = Depends(get_db)):
    album = db.query(Album).filter(Album.id == id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    for field, value in album_in.dict(exclude_unset=True).items():
        setattr(album, field, value)
    db.commit()
    db.refresh(album)
    return album 