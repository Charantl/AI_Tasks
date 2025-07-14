"""
Tests for AI recommendations functionality.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime, timedelta

from app.main import app
from app.models.song import Song
from app.models.artist import Artist
from app.models.album import Album
from app.models.user import User
from app.models.liked_song import LikedSong
from app.models.play_history import PlayHistory
from app.services.recommendations import recommendations_service

client = TestClient(app)


class TestRecommendationsAPI:
    """Test cases for recommendations API endpoints."""
    
    def test_content_based_recommendations(self, db_session: Session):
        """Test content-based recommendations."""
        # Create test data
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Test bio"
        )
        db_session.add(artist)
        
        song1 = Song(
            id=uuid.uuid4(),
            title="Liked Song 1",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/song1.mp3",
            genre="Rock"
        )
        song2 = Song(
            id=uuid.uuid4(),
            title="Liked Song 2",
            artist_id=artist.id,
            duration=200,
            audio_url="http://example.com/song2.mp3",
            genre="Rock"
        )
        db_session.add_all([song1, song2])
        db_session.commit()
        
        # Create liked songs
        liked1 = LikedSong(
            id=uuid.uuid4(),
            user_id=user.id,
            song_id=song1.id
        )
        liked2 = LikedSong(
            id=uuid.uuid4(),
            user_id=user.id,
            song_id=song2.id
        )
        db_session.add_all([liked1, liked2])
        db_session.commit()
        
        # Test content-based recommendations
        response = client.post("/recommendations", json={
            "user_id": str(user.id),
            "recommendation_type": "content_based",
            "limit": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(user.id)
        assert data["recommendation_type"] == "content_based"
        assert "recommendations" in data
    
    def test_collaborative_filtering_recommendations(self, db_session: Session):
        """Test collaborative filtering recommendations."""
        # Create test users
        user1 = User(
            id=uuid.uuid4(),
            username="user1",
            email="user1@example.com",
            password_hash="hashed_password"
        )
        user2 = User(
            id=uuid.uuid4(),
            username="user2",
            email="user2@example.com",
            password_hash="hashed_password"
        )
        db_session.add_all([user1, user2])
        
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Test bio"
        )
        db_session.add(artist)
        
        song = Song(
            id=uuid.uuid4(),
            title="Shared Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/shared.mp3",
            genre="Pop"
        )
        db_session.add(song)
        db_session.commit()
        
        # Both users like the same song
        liked1 = LikedSong(
            id=uuid.uuid4(),
            user_id=user1.id,
            song_id=song.id
        )
        liked2 = LikedSong(
            id=uuid.uuid4(),
            user_id=user2.id,
            song_id=song.id
        )
        db_session.add_all([liked1, liked2])
        db_session.commit()
        
        # Test collaborative filtering
        response = client.post("/recommendations", json={
            "user_id": str(user1.id),
            "recommendation_type": "collaborative",
            "limit": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["recommendation_type"] == "collaborative"
    
    def test_hybrid_recommendations(self, db_session: Session):
        """Test hybrid recommendations."""
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post("/recommendations", json={
            "user_id": str(user.id),
            "recommendation_type": "hybrid",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["recommendation_type"] == "hybrid"
        assert len(data["recommendations"]) >= 0  # May have results from popular songs
    
    def test_context_based_recommendations(self, db_session: Session):
        """Test context-based recommendations."""
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Test bio"
        )
        db_session.add(artist)
        
        song = Song(
            id=uuid.uuid4(),
            title="Context Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/context.mp3",
            genre="Jazz"
        )
        db_session.add(song)
        db_session.commit()
        
        # Add play history
        play_history = PlayHistory(
            id=uuid.uuid4(),
            user_id=user.id,
            song_id=song.id,
            played_at=datetime.now(),
            device="mobile"
        )
        db_session.add(play_history)
        db_session.commit()
        
        response = client.post("/recommendations", json={
            "user_id": str(user.id),
            "recommendation_type": "context_based",
            "context": {"time_of_day": "morning"},
            "limit": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["recommendation_type"] == "context_based"
    
    def test_popular_recommendations(self, db_session: Session):
        """Test popular recommendations."""
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Test bio"
        )
        db_session.add(artist)
        
        song = Song(
            id=uuid.uuid4(),
            title="Popular Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/popular.mp3",
            genre="Pop"
        )
        db_session.add(song)
        db_session.commit()
        
        # Add play history to make it popular
        for i in range(10):
            play_history = PlayHistory(
                id=uuid.uuid4(),
                user_id=user.id,
                song_id=song.id,
                played_at=datetime.now() - timedelta(hours=i),
                device="mobile"
            )
            db_session.add(play_history)
        db_session.commit()
        
        response = client.post("/recommendations", json={
            "user_id": str(user.id),
            "recommendation_type": "popular",
            "limit": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["recommendation_type"] == "popular"
    
    def test_get_user_insights(self, db_session: Session):
        """Test getting user insights."""
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Test bio"
        )
        db_session.add(artist)
        
        song = Song(
            id=uuid.uuid4(),
            title="Insight Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/insight.mp3",
            genre="Rock"
        )
        db_session.add(song)
        db_session.commit()
        
        # Add liked song
        liked = LikedSong(
            id=uuid.uuid4(),
            user_id=user.id,
            song_id=song.id
        )
        db_session.add(liked)
        db_session.commit()
        
        response = client.get(f"/recommendations/{user.id}/insights")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(user.id)
        assert "preferences" in data
        assert "top_artists" in data
        assert "top_genres" in data
    
    def test_submit_feedback(self, db_session: Session):
        """Test submitting recommendation feedback."""
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post("/recommendations/feedback", json={
            "user_id": str(user.id),
            "recommendation_id": str(uuid.uuid4()),
            "feedback_type": "like",
            "feedback_value": 0.8
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Feedback received"
        assert data["user_id"] == str(user.id)
    
    def test_get_metrics(self, db_session: Session):
        """Test getting recommendation metrics."""
        response = client.get("/recommendations/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_recommendations_generated" in data
        assert "average_click_through_rate" in data
        assert "user_satisfaction_score" in data
    
    def test_create_personalized_playlist(self, db_session: Session):
        """Test creating personalized playlist."""
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Test bio"
        )
        db_session.add(artist)
        
        song = Song(
            id=uuid.uuid4(),
            title="Playlist Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/playlist.mp3",
            genre="Pop"
        )
        db_session.add(song)
        db_session.commit()
        
        response = client.post("/recommendations/playlist", json={
            "user_id": str(user.id),
            "playlist_name": "My Personalized Playlist",
            "target_duration_minutes": 60,
            "mood": "energetic",
            "include_liked_songs": True,
            "include_discoveries": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["playlist_name"] == "My Personalized Playlist"
        assert data["user_id"] == str(user.id)
        assert "songs" in data
    
    def test_get_similar_users(self, db_session: Session):
        """Test finding similar users."""
        user1 = User(
            id=uuid.uuid4(),
            username="user1",
            email="user1@example.com",
            password_hash="hashed_password"
        )
        user2 = User(
            id=uuid.uuid4(),
            username="user2",
            email="user2@example.com",
            password_hash="hashed_password"
        )
        db_session.add_all([user1, user2])
        
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Test bio"
        )
        db_session.add(artist)
        
        song = Song(
            id=uuid.uuid4(),
            title="Shared Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/shared.mp3",
            genre="Pop"
        )
        db_session.add(song)
        db_session.commit()
        
        # Both users like the same song
        liked1 = LikedSong(
            id=uuid.uuid4(),
            user_id=user1.id,
            song_id=song.id
        )
        liked2 = LikedSong(
            id=uuid.uuid4(),
            user_id=user2.id,
            song_id=song.id
        )
        db_session.add_all([liked1, liked2])
        db_session.commit()
        
        response = client.get(f"/recommendations/{user1.id}/similar-users?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert "similar_users" in data
        assert "total_similar_users" in data
    
    def test_get_discovery_recommendations(self, db_session: Session):
        """Test discovery recommendations."""
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Test bio"
        )
        db_session.add(artist)
        
        song = Song(
            id=uuid.uuid4(),
            title="Discovery Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/discovery.mp3",
            genre="Jazz"
        )
        db_session.add(song)
        db_session.commit()
        
        response = client.get(f"/recommendations/{user.id}/discover?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(user.id)
        assert "recommendations" in data
        assert data["discovery_type"] == "genre_exploration"
    
    def test_invalid_user_id(self, db_session: Session):
        """Test recommendations with invalid user ID."""
        invalid_user_id = str(uuid.uuid4())
        
        response = client.post("/recommendations", json={
            "user_id": invalid_user_id,
            "recommendation_type": "content_based",
            "limit": 5
        })
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_invalid_recommendation_type(self, db_session: Session):
        """Test recommendations with invalid recommendation type."""
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post("/recommendations", json={
            "user_id": str(user.id),
            "recommendation_type": "invalid_type",
            "limit": 5
        })
        
        assert response.status_code == 422  # Validation error


class TestRecommendationsService:
    """Test cases for recommendations service."""
    
    def test_get_user_preferences(self, db_session: Session):
        """Test extracting user preferences."""
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Test bio"
        )
        db_session.add(artist)
        
        song = Song(
            id=uuid.uuid4(),
            title="Test Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/test.mp3",
            genre="Rock"
        )
        db_session.add(song)
        db_session.commit()
        
        # Add liked song
        liked = LikedSong(
            id=uuid.uuid4(),
            user_id=user.id,
            song_id=song.id
        )
        db_session.add(liked)
        
        # Add play history
        play_history = PlayHistory(
            id=uuid.uuid4(),
            user_id=user.id,
            song_id=song.id,
            played_at=datetime.now(),
            device="mobile"
        )
        db_session.add(play_history)
        db_session.commit()
        
        preferences = recommendations_service.get_user_preferences(db_session, str(user.id))
        
        assert "liked_genres" in preferences
        assert "liked_artists" in preferences
        assert "listening_patterns" in preferences
        assert "preferred_duration" in preferences
        assert "active_hours" in preferences
        assert "total_listening_time" in preferences
    
    def test_get_recommendations_summary(self, db_session: Session):
        """Test getting recommendations summary."""
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        summary = recommendations_service.get_recommendations_summary(db_session, str(user.id))
        
        assert "total_liked_songs" in summary
        assert "recent_plays_7_days" in summary
        assert "favorite_genres" in summary
        assert "total_listening_time_minutes" in summary
        assert "preferred_duration_seconds" in summary 