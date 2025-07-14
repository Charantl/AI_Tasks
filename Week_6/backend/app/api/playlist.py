from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate, PlaylistOut, PlaylistSongAdd, PlaylistSongOut
from app.models.playlist import Playlist
from app.models.playlist_song import PlaylistSong
from app.models.song import Song
from app.db.session import get_db
from app.api.user import get_current_user
from typing import List
import uuid

router = APIRouter(prefix="/playlists", tags=["playlists"])

@router.post("/", response_model=PlaylistOut)
def create_playlist(playlist_in: PlaylistCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    playlist = Playlist(user_id=current_user.id, **playlist_in.dict())
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist

@router.get("/", response_model=List[PlaylistOut])
def list_playlists(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Playlist).filter(Playlist.user_id == current_user.id).all()

@router.get("/{playlist_id}", response_model=PlaylistOut)
def get_playlist(playlist_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id, Playlist.user_id == current_user.id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist

@router.patch("/{playlist_id}", response_model=PlaylistOut)
def update_playlist(playlist_id: str, playlist_in: PlaylistUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id, Playlist.user_id == current_user.id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    for field, value in playlist_in.dict(exclude_unset=True).items():
        setattr(playlist, field, value)
    db.commit()
    db.refresh(playlist)
    return playlist

@router.delete("/{playlist_id}")
def delete_playlist(playlist_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id, Playlist.user_id == current_user.id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    db.delete(playlist)
    db.commit()
    return {"message": "Playlist deleted"}

@router.post("/{playlist_id}/songs", response_model=PlaylistSongOut)
def add_song_to_playlist(playlist_id: str, song_in: PlaylistSongAdd, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id, Playlist.user_id == current_user.id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    song = db.query(Song).filter(Song.id == song_in.song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    ps = PlaylistSong(playlist_id=playlist.id, song_id=song.id, position=song_in.position)
    db.add(ps)
    db.commit()
    db.refresh(ps)
    return ps

@router.delete("/{playlist_id}/songs/{song_id}")
def remove_song_from_playlist(playlist_id: str, song_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    ps = db.query(PlaylistSong).join(Playlist).filter(PlaylistSong.playlist_id == playlist_id, PlaylistSong.song_id == song_id, Playlist.user_id == current_user.id).first()
    if not ps:
        raise HTTPException(status_code=404, detail="Song not in playlist or playlist not found")
    db.delete(ps)
    db.commit()
    return {"message": "Song removed from playlist"}

@router.get("/{playlist_id}/songs", response_model=List[PlaylistSongOut])
def list_playlist_songs(playlist_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id, Playlist.user_id == current_user.id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return db.query(PlaylistSong).filter(PlaylistSong.playlist_id == playlist_id).all() 