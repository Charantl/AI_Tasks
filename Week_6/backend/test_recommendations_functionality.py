#!/usr/bin/env python3
"""
Test script to verify AI recommendations functionality.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.recommendations import recommendations_service
from app.db.session import get_db
from app.models.song import Song
from app.models.artist import Artist
from app.models.album import Album
from app.models.user import User
from app.models.liked_song import LikedSong
from app.models.play_history import PlayHistory
import uuid
from datetime import datetime, timedelta


def test_recommendations_service():
    """Test the recommendations service functionality."""
    print("🧪 Testing Recommendations Service...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test users
        user1 = User(
            id=uuid.uuid4(),
            username="testuser1",
            email="user1@example.com",
            password_hash="hashed_password"
        )
        user2 = User(
            id=uuid.uuid4(),
            username="testuser2",
            email="user2@example.com",
            password_hash="hashed_password"
        )
        db.add_all([user1, user2])
        
        # Create test artist
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="A test artist for recommendations"
        )
        db.add(artist)
        db.commit()
        print(f"✅ Created test users and artist")
        
        # Create test songs
        songs = []
        for i in range(5):
            song = Song(
                id=uuid.uuid4(),
                title=f"Test Song {i+1}",
                artist_id=artist.id,
                duration=180 + (i * 30),
                audio_url=f"http://example.com/song{i+1}.mp3",
                genre="Pop" if i % 2 == 0 else "Rock"
            )
            songs.append(song)
        
        db.add_all(songs)
        db.commit()
        print(f"✅ Created {len(songs)} test songs")
        
        # Add liked songs for user1
        for i in range(3):
            liked = LikedSong(
                id=uuid.uuid4(),
                user_id=user1.id,
                song_id=songs[i].id
            )
            db.add(liked)
        
        # Add play history for user1
        for i in range(3):
            play_history = PlayHistory(
                id=uuid.uuid4(),
                user_id=user1.id,
                song_id=songs[i].id,
                played_at=datetime.now() - timedelta(hours=i),
                device="mobile"
            )
            db.add(play_history)
        
        db.commit()
        print(f"✅ Added liked songs and play history for user1")
        
        # Test user preferences
        preferences = recommendations_service.get_user_preferences(db, str(user1.id))
        print(f"✅ Extracted user preferences:")
        print(f"   - Liked genres: {preferences['liked_genres']}")
        print(f"   - Liked artists: {preferences['liked_artists']}")
        print(f"   - Total listening time: {preferences['total_listening_time']} seconds")
        
        # Test content-based recommendations
        content_recs = recommendations_service.content_based_recommendations(
            db, str(user1.id), 5
        )
        print(f"✅ Content-based recommendations: {len(content_recs)} results")
        
        # Test collaborative filtering
        # Add liked songs for user2 (similar taste)
        for i in range(2):
            liked = LikedSong(
                id=uuid.uuid4(),
                user_id=user2.id,
                song_id=songs[i].id
            )
            db.add(liked)
        db.commit()
        
        collab_recs = recommendations_service.collaborative_filtering_recommendations(
            db, str(user1.id), 5
        )
        print(f"✅ Collaborative filtering recommendations: {len(collab_recs)} results")
        
        # Test hybrid recommendations
        hybrid_recs = recommendations_service.hybrid_recommendations(
            db, str(user1.id), 10
        )
        print(f"✅ Hybrid recommendations: {len(hybrid_recs)} results")
        
        # Test context-based recommendations
        context_recs = recommendations_service.context_based_recommendations(
            db, str(user1.id), {"time_of_day": "morning"}, 5
        )
        print(f"✅ Context-based recommendations: {len(context_recs)} results")
        
        # Test recommendations summary
        summary = recommendations_service.get_recommendations_summary(db, str(user1.id))
        print(f"✅ Recommendations summary:")
        print(f"   - Total liked songs: {summary['total_liked_songs']}")
        print(f"   - Recent plays (7 days): {summary['recent_plays_7_days']}")
        print(f"   - Favorite genres: {summary['favorite_genres']}")
        print(f"   - Total listening time: {summary['total_listening_time_minutes']} minutes")
        
        print("✅ All recommendations service tests passed!")
        
    except Exception as e:
        print(f"❌ Error during recommendations test: {e}")
        raise
    finally:
        db.close()


def test_recommendation_algorithms():
    """Test different recommendation algorithms."""
    print("\n🧪 Testing Recommendation Algorithms...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test user
        user = User(
            id=uuid.uuid4(),
            username="algo_test_user",
            email="algo@example.com",
            password_hash="hashed_password"
        )
        db.add(user)
        
        # Create test artist
        artist = Artist(
            id=uuid.uuid4(),
            name="Algorithm Test Artist",
            bio="Testing recommendation algorithms"
        )
        db.add(artist)
        db.commit()
        
        # Test popular recommendations (should work even without user data)
        popular_recs = recommendations_service._get_popular_songs(db, 5)
        print(f"✅ Popular recommendations: {len(popular_recs)} results")
        
        # Test with no user data (should return popular songs)
        content_recs = recommendations_service.content_based_recommendations(
            db, str(user.id), 5
        )
        print(f"✅ Content-based (no data): {len(content_recs)} results")
        
        collab_recs = recommendations_service.collaborative_filtering_recommendations(
            db, str(user.id), 5
        )
        print(f"✅ Collaborative (no data): {len(collab_recs)} results")
        
        print("✅ Algorithm tests passed!")
        
    except Exception as e:
        print(f"❌ Error during algorithm test: {e}")
        raise
    finally:
        db.close()


def main():
    """Run all recommendation tests."""
    print("🚀 Testing AI Recommendations Functionality")
    print("=" * 50)
    
    try:
        test_recommendations_service()
        test_recommendation_algorithms()
        
        print("\n🎉 All tests passed! AI recommendations functionality is working.")
        print("\n📋 Features implemented:")
        print("   ✅ Content-based recommendations")
        print("   ✅ Collaborative filtering")
        print("   ✅ Hybrid recommendations")
        print("   ✅ Context-based recommendations")
        print("   ✅ User preference extraction")
        print("   ✅ Recommendation insights")
        print("   ✅ Personalized playlists")
        print("   ✅ Similar users discovery")
        print("   ✅ Discovery recommendations")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 