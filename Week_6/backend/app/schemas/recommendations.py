from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from uuid import UUID
from datetime import datetime


class RecommendationItem(BaseModel):
    """Individual recommendation item."""
    id: str
    title: str
    artist_name: str
    album_title: Optional[str] = None
    duration: int
    genre: Optional[str] = None
    audio_url: str
    similarity_score: float
    recommendation_type: Literal["content_based", "collaborative", "context_based", "popular", "hybrid"]


class RecommendationRequest(BaseModel):
    """Request for recommendations."""
    user_id: UUID
    recommendation_type: Literal["content_based", "collaborative", "hybrid", "context_based", "popular"] = "hybrid"
    limit: int = Field(10, ge=1, le=50, description="Number of recommendations to return")
    context: Optional[Dict[str, Any]] = Field(None, description="Context information (time, mood, etc.)")


class RecommendationResponse(BaseModel):
    """Response with recommendations."""
    user_id: str
    recommendation_type: str
    recommendations: List[RecommendationItem]
    total_count: int
    generated_at: datetime
    processing_time_ms: float


class UserPreferences(BaseModel):
    """User preferences and behavior insights."""
    total_liked_songs: int
    recent_plays_7_days: int
    favorite_genres: List[str]
    total_listening_time_minutes: int
    most_active_hour: Optional[int] = None
    preferred_duration_seconds: int


class RecommendationInsights(BaseModel):
    """Insights about user's music preferences."""
    user_id: str
    preferences: UserPreferences
    top_artists: List[str]
    top_genres: List[str]
    listening_patterns: Dict[str, Any]
    recommendation_confidence: float


class BatchRecommendationRequest(BaseModel):
    """Request for batch recommendations for multiple users."""
    user_ids: List[UUID]
    recommendation_type: Literal["content_based", "collaborative", "hybrid", "context_based", "popular"] = "hybrid"
    limit_per_user: int = Field(10, ge=1, le=20)
    context: Optional[Dict[str, Any]] = None


class BatchRecommendationResponse(BaseModel):
    """Response with batch recommendations."""
    recommendations: Dict[str, List[RecommendationItem]]
    total_users: int
    total_recommendations: int
    generated_at: datetime
    processing_time_ms: float


class RecommendationFeedback(BaseModel):
    """Feedback on recommendations."""
    user_id: UUID
    recommendation_id: str
    feedback_type: Literal["like", "dislike", "skip", "play"]
    feedback_value: Optional[float] = Field(None, ge=0.0, le=1.0, description="Rating value if applicable")
    context: Optional[Dict[str, Any]] = None


class RecommendationMetrics(BaseModel):
    """Metrics for recommendation performance."""
    total_recommendations_generated: int
    average_click_through_rate: float
    average_play_time: float
    user_satisfaction_score: float
    diversity_score: float
    novelty_score: float


class PersonalizedPlaylistRequest(BaseModel):
    """Request for personalized playlist generation."""
    user_id: UUID
    playlist_name: str
    target_duration_minutes: int = Field(60, ge=15, le=180)
    mood: Optional[Literal["energetic", "chill", "focused", "party", "workout"]] = None
    include_liked_songs: bool = True
    include_discoveries: bool = True


class PersonalizedPlaylistResponse(BaseModel):
    """Response with personalized playlist."""
    playlist_id: str
    playlist_name: str
    user_id: str
    songs: List[RecommendationItem]
    total_duration_minutes: int
    mood: Optional[str] = None
    generated_at: datetime 