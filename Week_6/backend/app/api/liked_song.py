from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.liked_song import LikedSongCreate, LikedSongOut, LikedSongWithSong
from app.models.liked_song import LikedSong
from app.models.song import Song
from app.models.artist import Artist
from app.db.session import get_db
from app.api.user import get_current_user
from typing import List

router = APIRouter(prefix="/me/liked-songs", tags=["liked-songs"])

@router.get("/", response_model=List[LikedSongWithSong])
def list_liked_songs(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    liked_songs = db.query(LikedSong).filter(LikedSong.user_id == current_user.id).all()
    result = []
    for ls in liked_songs:
        song = db.query(Song).filter(Song.id == ls.song_id).first()
        artist = db.query(Artist).filter(Artist.id == song.artist_id).first() if song else None
        result.append({
            "id": ls.id,
            "song_id": ls.song_id,
            "liked_at": ls.liked_at.isoformat() if ls.liked_at else None,
            "song_title": song.title if song else "",
            "artist_name": artist.name if artist else ""
        })
    return result

@router.post("/", response_model=LikedSongOut)
def like_song(liked_song_in: LikedSongCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Check if song exists
    song = db.query(Song).filter(Song.id == liked_song_in.song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    # Check if already liked
    existing = db.query(LikedSong).filter(LikedSong.user_id == current_user.id, LikedSong.song_id == liked_song_in.song_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Song already liked")
    liked_song = LikedSong(user_id=current_user.id, song_id=liked_song_in.song_id)
    db.add(liked_song)
    db.commit()
    db.refresh(liked_song)
    return liked_song

@router.delete("/{song_id}")
def unlike_song(song_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    liked_song = db.query(LikedSong).filter(LikedSong.user_id == current_user.id, LikedSong.song_id == song_id).first()
    if not liked_song:
        raise HTTPException(status_code=404, detail="Song not liked")
    db.delete(liked_song)
    db.commit()
    return {"message": "Song unliked"} 