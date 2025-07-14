from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response, Request
from sqlalchemy.orm import Session
from app.schemas.song import SongCreate, SongUpdate, SongOut
from app.models.song import Song
from app.db.session import get_db
from typing import List
from app.core.security import get_s3_client, S3_BUCKET
import uuid
from fastapi.responses import StreamingResponse
import requests
from app.api.user import get_current_user
from app.core.cache import Cache

router = APIRouter(prefix="/songs", tags=["songs"])

@router.get("/", response_model=List[SongOut])
def list_songs(db: Session = Depends(get_db), q: str = None):
    query = db.query(Song)
    if q:
        query = query.filter(Song.title.ilike(f"%{q}%"))
    return query.all()

@router.post("/", response_model=SongOut)
def create_song(song_in: SongCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "artist":
        raise HTTPException(status_code=403, detail="Only artists can create songs")
    song = Song(**song_in.dict())
    db.add(song)
    db.commit()
    db.refresh(song)
    return song

@router.get("/{song_id}")
def get_song(song_id: str, db: Session = Depends(get_db)):
    key = f"song:{song_id}"
    def fetch():
        song = db.query(Song).filter(Song.id == song_id).first()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        return {"id": str(song.id), "title": song.title, "artist_id": str(song.artist_id), "duration": song.duration, "audio_url": song.audio_url, "genre": song.genre}
    return Cache.get_or_set(key, fetch, ttl=1800)

@router.patch("/{song_id}", response_model=SongOut)
def update_song(song_id: str, song_update: SongUpdate, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    for field, value in song_update.dict(exclude_unset=True).items():
        setattr(song, field, value)
    db.commit()
    db.refresh(song)
    # Invalidate cache
    Cache.invalidate(f"song:{song_id}")
    return song

@router.delete("/{song_id}")
def delete_song(song_id: str, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.delete(song)
    db.commit()
    # Invalidate cache
    Cache.invalidate(f"song:{song_id}")
    return {"message": "Song deleted"}

@router.post("/upload/audio")
def upload_audio(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    if current_user.role != "artist":
        raise HTTPException(status_code=403, detail="Only artists can upload audio")
    s3 = get_s3_client()
    ext = file.filename.split(".")[-1]
    key = f"audio/{uuid.uuid4()}.{ext}"
    s3.upload_fileobj(file.file, S3_BUCKET, key, ExtraArgs={"ContentType": file.content_type})
    url = f"https://{S3_BUCKET}.s3.amazonaws.com/{key}"
    return {"audio_url": url}

@router.get("/{id}/stream")
def stream_audio(id: str, request: Request, db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    audio_url = song.audio_url
    range_header = request.headers.get("range")
    headers = {"Range": range_header} if range_header else {}
    resp = requests.get(audio_url, headers=headers, stream=True)
    if resp.status_code not in (200, 206):
        raise HTTPException(status_code=resp.status_code, detail="Failed to fetch audio")
    return StreamingResponse(resp.raw, status_code=resp.status_code, media_type="audio/mpeg", headers={k: v for k, v in resp.headers.items() if k.lower().startswith("content-")})

@router.get("/trending")
def get_trending_songs(db: Session = Depends(get_db)):
    # Return the 10 most recent songs as trending (customize as needed)
    trending = db.query(Song).order_by(Song.created_at.desc()).limit(10).all()
    return {"songs": [s for s in trending]}

# Cache warming for trending songs
def warm_trending_songs_cache(db: Session):
    trending_song_ids = [s.id for s in db.query(Song).order_by(Song.play_count.desc()).limit(10).all()]
    for song_id in trending_song_ids:
        Cache.warm(f"song:{song_id}", lambda: db.query(Song).filter(Song.id == song_id).first(), ttl=1800) 