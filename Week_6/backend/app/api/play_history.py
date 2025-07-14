from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.play_history import PlayHistoryCreate, PlayHistoryOut, PlayHistoryWithSong
from app.models.play_history import PlayHistory
from app.models.song import Song
from app.models.artist import Artist
from app.db.session import get_db
from app.api.user import get_current_user
from typing import List

router = APIRouter(prefix="/me/history", tags=["play-history"])

@router.get("/", response_model=List[PlayHistoryWithSong])
def list_play_history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    play_history = db.query(PlayHistory).filter(PlayHistory.user_id == current_user.id).order_by(PlayHistory.played_at.desc()).limit(50).all()
    result = []
    for ph in play_history:
        song = db.query(Song).filter(Song.id == ph.song_id).first()
        artist = db.query(Artist).filter(Artist.id == song.artist_id).first() if song else None
        result.append({
            "id": ph.id,
            "song_id": ph.song_id,
            "played_at": ph.played_at.isoformat() if ph.played_at else None,
            "device": ph.device,
            "song_title": song.title if song else "",
            "artist_name": artist.name if artist else ""
        })
    return result

@router.post("/", response_model=PlayHistoryOut)
def add_play_history(play_history_in: PlayHistoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Check if song exists
    song = db.query(Song).filter(Song.id == play_history_in.song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    play_history = PlayHistory(
        user_id=current_user.id,
        song_id=play_history_in.song_id,
        device=play_history_in.device
    )
    db.add(play_history)
    db.commit()
    db.refresh(play_history)
    return play_history 