from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.share import ShareCreate, ShareOut
from app.models.song import Song
from app.db.session import get_db
from app.api.user import get_current_user
from typing import Dict
import uuid

router = APIRouter(tags=["share"])

def generate_share_url(song_id: str, platform: str) -> str:
    """Generate share URL for different platforms"""
    base_url = "https://yourmusicapp.com/songs"
    song_url = f"{base_url}/{song_id}"
    
    if platform == "twitter":
        return f"https://twitter.com/intent/tweet?url={song_url}&text=Check%20out%20this%20song!"
    elif platform == "facebook":
        return f"https://www.facebook.com/sharer/sharer.php?u={song_url}"
    elif platform == "whatsapp":
        return f"https://wa.me/?text=Check%20out%20this%20song!%20{song_url}"
    elif platform == "copy_link":
        return song_url
    else:
        return song_url

@router.post("/songs/{song_id}/share", response_model=ShareOut)
def share_song(song_id: str, share_in: ShareCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Check if song exists
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Validate platform
    valid_platforms = ["twitter", "facebook", "whatsapp", "copy_link"]
    if share_in.platform not in valid_platforms:
        raise HTTPException(status_code=400, detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}")
    
    # Generate share URL
    share_url = generate_share_url(song_id, share_in.platform)
    
    return ShareOut(
        song_id=uuid.UUID(song_id),
        platform=share_in.platform,
        share_url=share_url,
        message=share_in.message
    )

@router.get("/songs/{song_id}/share")
def get_share_options(song_id: str, db: Session = Depends(get_db)):
    # Check if song exists
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Return available sharing platforms
    platforms = [
        {"name": "Twitter", "value": "twitter"},
        {"name": "Facebook", "value": "facebook"},
        {"name": "WhatsApp", "value": "whatsapp"},
        {"name": "Copy Link", "value": "copy_link"}
    ]
    
    return {
        "song_id": song_id,
        "song_title": song.title,
        "available_platforms": platforms
    } 