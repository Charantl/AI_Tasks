"""
Enhanced AI Recommendations API with multiple recommendation algorithms.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import time
from datetime import datetime
import uuid

from app.db.session import get_db
from app.models.user import User
from app.models.song import Song
from app.models.artist import Artist
from app.models.album import Album
from app.models.liked_song import LikedSong
from app.services.recommendations import recommendations_service
from app.schemas.recommendations import (
    RecommendationRequest, RecommendationResponse, RecommendationItem,
    UserPreferences, RecommendationInsights, BatchRecommendationRequest,
    BatchRecommendationResponse, RecommendationFeedback, RecommendationMetrics,
    PersonalizedPlaylistRequest, PersonalizedPlaylistResponse
)

router = APIRouter()


@router.post("/recommendations", response_model=RecommendationResponse, tags=["Recommendations"], summary="Get personalized music recommendations", description="Get personalized music recommendations for a user using content-based, collaborative, hybrid, context-based, or popular algorithms.")
async def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get personalized music recommendations for a user.
    - **recommendation_type**: 'content_based', 'collaborative', 'hybrid', 'context_based', or 'popular'
    - **limit**: Number of recommendations to return
    - **context**: Optional context (e.g., time, mood)
    """
    start_time = time.time()
    
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recommendations based on type
    if request.recommendation_type == "content_based":
        recommendations = recommendations_service.content_based_recommendations(
            db, str(request.user_id), request.limit
        )
    elif request.recommendation_type == "collaborative":
        recommendations = recommendations_service.collaborative_filtering_recommendations(
            db, str(request.user_id), request.limit
        )
    elif request.recommendation_type == "context_based":
        recommendations = recommendations_service.context_based_recommendations(
            db, str(request.user_id), request.context or {}, request.limit
        )
    elif request.recommendation_type == "popular":
        recommendations = recommendations_service._get_popular_songs(db, request.limit)
    else:  # hybrid
        recommendations = recommendations_service.hybrid_recommendations(
            db, str(request.user_id), request.limit
        )
    
    processing_time = (time.time() - start_time) * 1000
    
    return RecommendationResponse(
        user_id=str(request.user_id),
        recommendation_type=request.recommendation_type,
        recommendations=recommendations,
        total_count=len(recommendations),
        generated_at=datetime.utcnow(),
        processing_time_ms=processing_time
    )


@router.get("/recommendations/{user_id}", response_model=RecommendationResponse, tags=["Recommendations"], summary="Get recommendations for a user", description="Get recommendations for a user by user_id and algorithm type.")
async def get_user_recommendations(
    user_id: str,
    recommendation_type: str = Query("hybrid", description="Type of recommendation algorithm: content_based, collaborative, hybrid, context_based, popular"),
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    db: Session = Depends(get_db)
):
    """
    Get recommendations for a user by user_id and algorithm type.
    """
    start_time = time.time()
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recommendations
    if recommendation_type == "content_based":
        recommendations = recommendations_service.content_based_recommendations(
            db, user_id, limit
        )
    elif recommendation_type == "collaborative":
        recommendations = recommendations_service.collaborative_filtering_recommendations(
            db, user_id, limit
        )
    elif recommendation_type == "context_based":
        recommendations = recommendations_service.context_based_recommendations(
            db, user_id, {}, limit
        )
    elif recommendation_type == "popular":
        recommendations = recommendations_service._get_popular_songs(db, limit)
    else:  # hybrid
        recommendations = recommendations_service.hybrid_recommendations(
            db, user_id, limit
        )
    
    processing_time = (time.time() - start_time) * 1000
    
    return RecommendationResponse(
        user_id=user_id,
        recommendation_type=recommendation_type,
        recommendations=recommendations,
        total_count=len(recommendations),
        generated_at=datetime.utcnow(),
        processing_time_ms=processing_time
    )


@router.post("/recommendations/batch", response_model=BatchRecommendationResponse, tags=["Recommendations"], summary="Batch recommendations for multiple users", description="Get recommendations for multiple users in a single request.")
async def get_batch_recommendations(
    request: BatchRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get recommendations for multiple users in a single request.
    """
    start_time = time.time()
    
    batch_recommendations = {}
    total_recommendations = 0
    
    for user_id in request.user_ids:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue
        
        # Get recommendations for this user
        if request.recommendation_type == "content_based":
            recommendations = recommendations_service.content_based_recommendations(
                db, str(user_id), request.limit_per_user
            )
        elif request.recommendation_type == "collaborative":
            recommendations = recommendations_service.collaborative_filtering_recommendations(
                db, str(user_id), request.limit_per_user
            )
        elif request.recommendation_type == "context_based":
            recommendations = recommendations_service.context_based_recommendations(
                db, str(user_id), request.context or {}, request.limit_per_user
            )
        elif request.recommendation_type == "popular":
            recommendations = recommendations_service._get_popular_songs(db, request.limit_per_user)
        else:  # hybrid
            recommendations = recommendations_service.hybrid_recommendations(
                db, str(user_id), request.limit_per_user
            )
        
        batch_recommendations[str(user_id)] = recommendations
        total_recommendations += len(recommendations)
    
    processing_time = (time.time() - start_time) * 1000
    
    return BatchRecommendationResponse(
        recommendations=batch_recommendations,
        total_users=len(batch_recommendations),
        total_recommendations=total_recommendations,
        generated_at=datetime.utcnow(),
        processing_time_ms=processing_time
    )


@router.get("/recommendations/{user_id}/insights", response_model=RecommendationInsights, tags=["Recommendations"], summary="Get user music preference insights", description="Get insights about a user's music preferences, favorite genres, and listening patterns.")
async def get_user_insights(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get insights about a user's music preferences, favorite genres, and listening patterns.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user preferences
    preferences = recommendations_service.get_user_preferences(db, user_id)
    
    # Get insights summary
    insights_summary = recommendations_service.get_recommendations_summary(db, user_id)
    
    # Calculate recommendation confidence based on user activity
    total_activity = insights_summary['total_liked_songs'] + insights_summary['recent_plays_7_days']
    confidence = min(1.0, total_activity / 50.0)  # Normalize to 0-1
    
    return RecommendationInsights(
        user_id=user_id,
        preferences=UserPreferences(
            total_liked_songs=insights_summary['total_liked_songs'],
            recent_plays_7_days=insights_summary['recent_plays_7_days'],
            favorite_genres=insights_summary['favorite_genres'],
            total_listening_time_minutes=insights_summary['total_listening_time_minutes'],
            most_active_hour=insights_summary['most_active_hour'],
            preferred_duration_seconds=insights_summary['preferred_duration_seconds']
        ),
        top_artists=preferences['liked_artists'][:5],
        top_genres=preferences['liked_genres'][:5],
        listening_patterns={
            'active_hours': preferences['active_hours'],
            'preferred_duration': preferences['preferred_duration'],
            'total_listening_time': preferences['total_listening_time']
        },
        recommendation_confidence=confidence
    )


@router.post("/recommendations/feedback", tags=["Recommendations"], summary="Submit feedback on recommendations", description="Submit feedback (like, dislike, skip, play) on a recommendation to improve future suggestions.")
async def submit_recommendation_feedback(
    feedback: RecommendationFeedback,
    db: Session = Depends(get_db)
):
    """
    Submit feedback (like, dislike, skip, play) on a recommendation to improve future suggestions.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == feedback.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # In a real implementation, you would store this feedback
    # and use it to improve recommendations
    # For now, we'll just acknowledge the feedback
    
    return {
        "message": "Feedback received",
        "user_id": str(feedback.user_id),
        "recommendation_id": feedback.recommendation_id,
        "feedback_type": feedback.feedback_type,
        "timestamp": datetime.utcnow()
    }


@router.get("/recommendations/metrics", response_model=RecommendationMetrics, tags=["Recommendations"], summary="Get recommendation system metrics", description="Get overall metrics for recommendation system performance (click-through rate, satisfaction, diversity, etc.).")
async def get_recommendation_metrics(
    db: Session = Depends(get_db)
):
    """
    Get overall metrics for recommendation system performance (click-through rate, satisfaction, diversity, etc.).
    """
    # In a real implementation, you would calculate these metrics
    # from actual usage data and feedback
    # For now, we'll return placeholder metrics
    
    return RecommendationMetrics(
        total_recommendations_generated=1000,
        average_click_through_rate=0.15,
        average_play_time=180.5,
        user_satisfaction_score=0.78,
        diversity_score=0.65,
        novelty_score=0.42
    )


@router.post("/recommendations/playlist", response_model=PersonalizedPlaylistResponse, tags=["Recommendations"], summary="Create personalized playlist", description="Create a personalized playlist for a user based on preferences, mood, and target duration.")
async def create_personalized_playlist(
    request: PersonalizedPlaylistRequest,
    db: Session = Depends(get_db)
):
    """
    Create a personalized playlist for a user based on preferences, mood, and target duration.
    """
    start_time = time.time()
    
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recommendations for playlist
    recommendations = recommendations_service.hybrid_recommendations(
        db, str(request.user_id), request.target_duration_minutes * 2  # Get more songs to filter by duration
    )
    
    # Filter songs to match target duration
    selected_songs = []
    total_duration = 0
    target_duration_seconds = request.target_duration_minutes * 60
    
    for rec in recommendations:
        if total_duration + rec['duration'] <= target_duration_seconds:
            selected_songs.append(rec)
            total_duration += rec['duration']
        if len(selected_songs) >= 20:  # Limit playlist size
            break
    
    processing_time = (time.time() - start_time) * 1000
    
    return PersonalizedPlaylistResponse(
        playlist_id=str(uuid.uuid4()),
        playlist_name=request.playlist_name,
        user_id=str(request.user_id),
        songs=selected_songs,
        total_duration_minutes=total_duration // 60,
        mood=request.mood,
        generated_at=datetime.utcnow()
    )


@router.get("/recommendations/{user_id}/similar-users", tags=["Recommendations"], summary="Find similar users", description="Find users with similar music taste based on liked songs.")
async def get_similar_users(
    user_id: str,
    limit: int = Query(5, ge=1, le=20, description="Number of similar users to return"),
    db: Session = Depends(get_db)
):
    """
    Find users with similar music taste based on liked songs.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's liked songs
    user_liked_songs = set()
    liked_songs = db.query(LikedSong).filter(LikedSong.user_id == user_id).all()
    for liked in liked_songs:
        user_liked_songs.add(str(liked.song_id))
    
    if not user_liked_songs:
        return {"similar_users": [], "message": "No music preferences found"}
    
    # Find similar users
    similar_users = []
    all_users = db.query(User).filter(User.id != user_id).all()
    
    for other_user in all_users:
        other_likes = db.query(LikedSong).filter(LikedSong.user_id == other_user.id).all()
        other_liked_set = {str(like.song_id) for like in other_likes}
        
        if other_liked_set:
            # Calculate Jaccard similarity
            intersection = len(user_liked_songs.intersection(other_liked_set))
            union = len(user_liked_songs.union(other_liked_set))
            similarity = intersection / union if union > 0 else 0
            
            if similarity > 0:
                similar_users.append({
                    "user_id": str(other_user.id),
                    "username": other_user.username,
                    "similarity_score": similarity,
                    "common_likes": intersection
                })
    
    # Sort by similarity and return top users
    similar_users.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return {
        "similar_users": similar_users[:limit],
        "total_similar_users": len(similar_users)
    }


@router.get("/recommendations/{user_id}/discover", tags=["Recommendations"], summary="Get discovery recommendations", description="Get recommendations for songs outside the user's usual preferences (genre exploration).")
async def get_discovery_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=20, description="Number of discovery recommendations"),
    db: Session = Depends(get_db)
):
    """
    Get recommendations for songs outside the user's usual preferences (genre exploration).
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's preferences
    preferences = recommendations_service.get_user_preferences(db, user_id)
    
    # Get songs from genres the user doesn't usually listen to
    user_genres = set(preferences['liked_genres'])
    all_songs = db.query(Song).filter(
        ~Song.genre.in_(user_genres) if user_genres else True
    ).limit(limit * 2).all()
    
    # Randomly select songs for discovery
    import random
    discovery_songs = random.sample(all_songs, min(limit, len(all_songs)))
    
    recommendations = []
    for song in discovery_songs:
        artist = db.query(Artist).filter(Artist.id == song.artist_id).first()
        album = None
        if song.album_id:
            album = db.query(Album).filter(Album.id == song.album_id).first()
        
        recommendations.append({
            'id': str(song.id),
            'title': song.title,
            'artist_name': artist.name if artist else "Unknown",
            'album_title': album.title if album else None,
            'duration': song.duration,
            'genre': song.genre,
            'audio_url': song.audio_url,
            'similarity_score': 0.1,  # Low score for discovery
            'recommendation_type': 'discovery'
        })
    
    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "total_count": len(recommendations),
        "discovery_type": "genre_exploration"
    } 