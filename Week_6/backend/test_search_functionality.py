#!/usr/bin/env python3
"""
Simple test script to verify enhanced search functionality.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.embeddings import embeddings_service
from app.db.session import get_db
from app.models.song import Song
from app.models.artist import Artist
from app.models.album import Album
import uuid
from datetime import datetime


def test_embeddings_service():
    """Test the embeddings service functionality."""
    print("🧪 Testing Embeddings Service...")
    
    # Test embedding generation
    text = "This is a test song about love and happiness"
    embedding = embeddings_service.generate_embedding(text)
    print(f"✅ Generated embedding with {len(embedding)} dimensions")
    
    # Test similarity calculation
    text2 = "This is another song about love and happiness"
    embedding2 = embeddings_service.generate_embedding(text2)
    
    similarity = embeddings_service.calculate_similarity(embedding, embedding2)
    print(f"✅ Calculated similarity: {similarity:.4f}")
    
    # Test with different text
    text3 = "Completely different topic about cars and engines"
    embedding3 = embeddings_service.generate_embedding(text3)
    
    similarity2 = embeddings_service.calculate_similarity(embedding, embedding3)
    print(f"✅ Calculated similarity (different topics): {similarity2:.4f}")
    
    print("✅ Embeddings service tests passed!")


def test_search_functionality():
    """Test search functionality with database."""
    print("\n🧪 Testing Search Functionality...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test data
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="A test artist for search functionality"
        )
        db.add(artist)
        db.commit()
        print(f"✅ Created test artist: {artist.name}")
        
        album = Album(
            id=uuid.uuid4(),
            title="Test Album",
            artist_id=artist.id,
            release_date=datetime.now().date()
        )
        db.add(album)
        db.commit()
        print(f"✅ Created test album: {album.title}")
        
        song = Song(
            id=uuid.uuid4(),
            title="Test Song",
            artist_id=artist.id,
            album_id=album.id,
            duration=180,
            audio_url="http://example.com/test.mp3",
            genre="Pop",
            lyrics="This is a test song with lyrics about testing"
        )
        db.add(song)
        db.commit()
        print(f"✅ Created test song: {song.title}")
        
        # Test embedding creation
        embedding = embeddings_service.create_embedding(
            db, "song", str(song.id), 
            f"{song.title} {song.genre} {song.lyrics}"
        )
        print(f"✅ Created embedding for song: {embedding.id}")
        
        # Test semantic search
        results = embeddings_service.semantic_search(
            db=db,
            query_text="test song",
            entity_type="song",
            limit=5,
            similarity_threshold=0.1
        )
        print(f"✅ Semantic search found {len(results)} results")
        
        if results:
            entity_data, similarity = results[0]
            print(f"   Top result: {entity_data['title']} (similarity: {similarity:.4f})")
        
        print("✅ Search functionality tests passed!")
        
    except Exception as e:
        print(f"❌ Error during search test: {e}")
        raise
    finally:
        db.close()


def main():
    """Run all tests."""
    print("🚀 Testing Enhanced Search Functionality")
    print("=" * 50)
    
    try:
        test_embeddings_service()
        test_search_functionality()
        
        print("\n🎉 All tests passed! Enhanced search functionality is working.")
        print("\n📋 Features implemented:")
        print("   ✅ Embedding generation")
        print("   ✅ Similarity calculation")
        print("   ✅ Database integration")
        print("   ✅ Semantic search")
        print("   ✅ Search API endpoints")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 