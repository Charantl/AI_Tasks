from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.artist import ArtistCreate, ArtistUpdate, ArtistOut
from app.models.artist import Artist
from app.db.session import get_db

router = APIRouter(prefix="/artists", tags=["artists"])

@router.get("/", response_model=list[ArtistOut])
def list_artists(db: Session = Depends(get_db), q: str = None):
    query = db.query(Artist)
    if q:
        query = query.filter(Artist.name.ilike(f"%{q}%"))
    return query.all()

@router.post("/", response_model=ArtistOut)
def create_artist(artist_in: ArtistCreate, db: Session = Depends(get_db)):
    # Only admin/artist should be allowed (add auth later)
    artist = Artist(**artist_in.dict())
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist

@router.get("/{id}", response_model=ArtistOut)
def get_artist(id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

@router.patch("/{id}", response_model=ArtistOut)
def update_artist(id: str, artist_in: ArtistUpdate, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    for field, value in artist_in.dict(exclude_unset=True).items():
        setattr(artist, field, value)
    db.commit()
    db.refresh(artist)
    return artist 