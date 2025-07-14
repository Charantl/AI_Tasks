from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.schemas.analytics import AnalyticsCreate, AnalyticsOut, SongAnalytics, UserAnalytics
from app.models.analytics import Analytics
from app.models.song import Song
from app.models.user import User
from app.models.play_history import PlayHistory
from app.models.liked_song import LikedSong
from app.db.session import get_db
from app.api.user import get_current_user
from typing import List
import uuid
from app.core.cache import Cache
import psutil
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/song/{song_id}", response_model=SongAnalytics)
def get_song_analytics(song_id: str, db: Session = Depends(get_db)):
    # Check if song exists
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Get play count
    total_plays = db.query(PlayHistory).filter(PlayHistory.song_id == song_id).count()
    
    # Get unique listeners
    unique_listeners = db.query(PlayHistory.user_id).filter(PlayHistory.song_id == song_id).distinct().count()
    
    # Get like count
    total_likes = db.query(LikedSong).filter(LikedSong.song_id == song_id).count()
    
    # Get share count (from analytics events)
    total_shares = db.query(Analytics).filter(
        Analytics.song_id == song_id,
        Analytics.event_type == "share"
    ).count()
    
    return SongAnalytics(
        song_id=uuid.UUID(song_id),
        song_title=song.title,
        total_plays=total_plays,
        unique_listeners=unique_listeners,
        total_likes=total_likes,
        total_shares=total_shares
    )

@router.get("/user/{user_id}", response_model=UserAnalytics)
def get_user_analytics(user_id: str, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get total songs played
    total_songs_played = db.query(PlayHistory).filter(PlayHistory.user_id == user_id).count()
    
    # Get total time listened (estimated from play count * average song duration)
    total_time_listened = total_songs_played * 180  # Assuming 3 minutes per song
    
    # Get favorite genre (most played songs' genre)
    favorite_genre = db.query(Song.genre).join(PlayHistory).filter(
        PlayHistory.user_id == user_id
    ).group_by(Song.genre).order_by(func.count(PlayHistory.id).desc()).first()
    
    return UserAnalytics(
        user_id=uuid.UUID(user_id),
        username=user.username,
        total_songs_played=total_songs_played,
        total_time_listened=total_time_listened,
        favorite_genre=favorite_genre[0] if favorite_genre else "Unknown"
    )

@router.post("/track", response_model=AnalyticsOut)
def track_event(analytics_in: AnalyticsCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Check if song exists
    song = db.query(Song).filter(Song.id == analytics_in.song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    analytics = Analytics(
        song_id=analytics_in.song_id,
        user_id=current_user.id,
        event_type=analytics_in.event_type,
        device=analytics_in.device
    )
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    return analytics

# --- Dashboard Analytics Caching ---
@router.get("/dashboard/{user_id}")
def get_dashboard_analytics(user_id: str, db: Session = Depends(get_db)):
    key = f"analytics:dashboard:{user_id}"
    def fetch():
        # Compute analytics (example: play counts, top songs, recent activity)
        total_plays = db.query(PlayHistory).filter(PlayHistory.user_id == user_id).count()
        top_songs = db.query(Song).join(PlayHistory).filter(
            PlayHistory.user_id == user_id
        ).group_by(Song.id).order_by(func.count(PlayHistory.id).desc()).limit(5).all()
        recent_activity = db.query(PlayHistory).filter(PlayHistory.user_id == user_id).order_by(PlayHistory.played_at.desc()).limit(10).all()
        return {
            "total_plays": total_plays,
            "top_songs": [{"id": str(s.id), "title": s.title} for s in top_songs],
            "recent_activity": [{"song_id": str(a.song_id), "played_at": a.played_at.isoformat()} for a in recent_activity]
        }
    return Cache.get_or_set(key, fetch, ttl=900)

@router.post("/dashboard/{user_id}/invalidate")
def invalidate_dashboard_analytics(user_id: str):
    Cache.invalidate(f"analytics:dashboard:{user_id}")
    return {"message": "Dashboard analytics cache invalidated"}

@router.get("/cache/metrics")
def cache_metrics():
    return Cache.metrics() 

@router.get("/monitoring/active_users")
def get_active_user_count(db: Session = Depends(get_db)):
    # Example: count users with recent activity in the last 10 minutes
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    active_users = db.execute(text("""
        SELECT COUNT(DISTINCT user_id) FROM play_history WHERE played_at > :since
    """), {"since": ten_minutes_ago}).scalar()
    return {"active_users_last_10min": active_users}

@router.get("/monitoring/db_performance")
def get_db_performance(db: Session = Depends(get_db)):
    # Example: get row counts for key tables (simulate DB stats)
    song_count = db.execute(text("SELECT COUNT(*) FROM song")).scalar()
    user_count = db.execute(text("SELECT COUNT(*) FROM user")).scalar()
    play_count = db.execute(text("SELECT COUNT(*) FROM play_history")).scalar()
    return {
        "song_count": song_count,
        "user_count": user_count,
        "play_count": play_count
    }

@router.get("/monitoring/system")
def get_system_resource_usage():
    # Use psutil to get system resource usage
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    return {
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "memory_used_mb": mem.used // (1024 * 1024),
        "memory_total_mb": mem.total // (1024 * 1024)
    }

@router.get("/monitoring/cache")
def get_cache_metrics():
    return Cache.metrics() 