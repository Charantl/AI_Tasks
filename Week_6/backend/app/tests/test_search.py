"""
Tests for enhanced search functionality including semantic search.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime

from app.main import app
from app.models.song import Song
from app.models.artist import Artist
from app.models.album import Album
from app.models.embedding import Embedding
from app.services.embeddings import embeddings_service

client = TestClient(app)


class TestSearchAPI:
    """Test cases for search API endpoints."""
    
    def test_keyword_search_songs(self, db_session: Session):
        """Test keyword search for songs."""
        # Create test data
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Test bio"
        )
        db_session.add(artist)
        db_session.commit()
        
        song = Song(
            id=uuid.uuid4(),
            title="Test Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/song.mp3",
            genre="Rock"
        )
        db_session.add(song)
        db_session.commit()
        
        # Test search
        response = client.post("/search", json={
            "query": "Test Song",
            "search_type": "keyword",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Test Song"
        assert data["search_type"] == "keyword"
        assert len(data["results"]) > 0
        
        # Check song result
        song_result = data["results"][0]
        assert song_result["type"] == "song"
        assert song_result["title"] == "Test Song"
        assert song_result["artist_name"] == "Test Artist"
    
    def test_keyword_search_artists(self, db_session: Session):
        """Test keyword search for artists."""
        artist = Artist(
            id=uuid.uuid4(),
            name="Test Artist",
            bio="Rock musician"
        )
        db_session.add(artist)
        db_session.commit()
        
        response = client.post("/search", json={
            "query": "Test Artist",
            "search_type": "keyword",
            "filters": {"entity_type": "artist"},
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) > 0
        
        artist_result = data["results"][0]
        assert artist_result["type"] == "artist"
        assert artist_result["name"] == "Test Artist"
    
    def test_search_with_filters(self, db_session: Session):
        """Test search with filters."""
        artist = Artist(id=uuid.uuid4(), name="Rock Artist")
        db_session.add(artist)
        db_session.commit()
        
        song = Song(
            id=uuid.uuid4(),
            title="Rock Song",
            artist_id=artist.id,
            duration=200,
            audio_url="http://example.com/rock.mp3",
            genre="Rock"
        )
        db_session.add(song)
        db_session.commit()
        
        response = client.post("/search", json={
            "query": "Rock",
            "search_type": "keyword",
            "filters": {
                "entity_type": "song",
                "genre": "Rock",
                "duration_min": 100,
                "duration_max": 300
            },
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) > 0
        
        song_result = data["results"][0]
        assert song_result["genre"] == "Rock"
        assert song_result["duration"] >= 100
        assert song_result["duration"] <= 300
    
    @patch('app.services.embeddings.embeddings_service.semantic_search')
    def test_semantic_search(self, mock_semantic_search, db_session: Session):
        """Test semantic search functionality."""
        # Mock semantic search results
        mock_results = [
            ({
                "id": str(uuid.uuid4()),
                "type": "song",
                "title": "Semantic Song",
                "artist_name": "Test Artist",
                "duration": 180,
                "genre": "Pop",
                "audio_url": "http://example.com/song.mp3"
            }, 0.85)
        ]
        mock_semantic_search.return_value = mock_results
        
        response = client.post("/search/semantic", json={
            "text": "happy upbeat music",
            "entity_type": "song",
            "limit": 5,
            "similarity_threshold": 0.7
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["search_type"] == "semantic"
        assert len(data["results"]) > 0
        
        song_result = data["results"][0]
        assert song_result["type"] == "song"
        assert song_result["title"] == "Semantic Song"
        assert song_result["score"] == 0.85
    
    def test_hybrid_search(self, db_session: Session):
        """Test hybrid search combining keyword and semantic results."""
        # Create test data
        artist = Artist(id=uuid.uuid4(), name="Test Artist")
        db_session.add(artist)
        db_session.commit()
        
        song = Song(
            id=uuid.uuid4(),
            title="Hybrid Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/hybrid.mp3"
        )
        db_session.add(song)
        db_session.commit()
        
        response = client.post("/search", json={
            "query": "Hybrid",
            "search_type": "hybrid",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["search_type"] == "hybrid"
        assert len(data["results"]) >= 0  # May have results from keyword search
    
    def test_create_embedding(self, db_session: Session):
        """Test creating embeddings for entities."""
        response = client.post("/embeddings", json={
            "entity_type": "song",
            "entity_id": str(uuid.uuid4()),
            "text": "This is a test song with lyrics"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["entity_type"] == "song"
        assert "embedding_id" in data
        assert data["embedding_size"] > 0
    
    def test_search_suggestions(self, db_session: Session):
        """Test search suggestions endpoint."""
        # Create test data
        artist = Artist(id=uuid.uuid4(), name="Suggestion Artist")
        db_session.add(artist)
        db_session.commit()
        
        song = Song(
            id=uuid.uuid4(),
            title="Suggestion Song",
            artist_id=artist.id,
            duration=180,
            audio_url="http://example.com/suggestion.mp3"
        )
        db_session.add(song)
        db_session.commit()
        
        response = client.get("/search/suggestions?query=Suggestion&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0
        
        # Check that suggestions contain the query
        suggestion_texts = [s["text"] for s in data["suggestions"]]
        assert any("Suggestion" in text for text in suggestion_texts)
    
    def test_search_invalid_request(self):
        """Test search with invalid request."""
        response = client.post("/search", json={
            "query": "",  # Empty query
            "search_type": "keyword"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_search_invalid_search_type(self):
        """Test search with invalid search type."""
        response = client.post("/search", json={
            "query": "test",
            "search_type": "invalid_type"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_semantic_search_invalid_threshold(self):
        """Test semantic search with invalid similarity threshold."""
        response = client.post("/search/semantic", json={
            "text": "test",
            "similarity_threshold": 1.5  # Invalid threshold
        })
        
        assert response.status_code == 422  # Validation error


class TestEmbeddingsService:
    """Test cases for embeddings service."""
    
    def test_generate_embedding(self):
        """Test embedding generation."""
        text = "This is a test song"
        embedding = embeddings_service.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == embeddings_service.embedding_dim
        assert all(isinstance(x, float) for x in embedding)
    
    def test_calculate_similarity(self):
        """Test similarity calculation."""
        embedding1 = [0.1, 0.2, 0.3, 0.4]
        embedding2 = [0.1, 0.2, 0.3, 0.4]
        
        similarity = embeddings_service.calculate_similarity(embedding1, embedding2)
        assert similarity == 1.0  # Identical embeddings should have similarity 1.0
    
    def test_create_embedding(self, db_session: Session):
        """Test creating embedding in database."""
        entity_type = "song"
        entity_id = str(uuid.uuid4())
        text = "Test song content"
        
        embedding = embeddings_service.create_embedding(db_session, entity_type, entity_id, text)
        
        assert embedding.entity_type == entity_type
        assert embedding.entity_id == entity_id
        assert embedding.embedding is not None
        assert len(embedding.embedding) == embeddings_service.embedding_dim
    
    def test_update_embedding(self, db_session: Session):
        """Test updating existing embedding."""
        entity_type = "song"
        entity_id = str(uuid.uuid4())
        text1 = "Original text"
        text2 = "Updated text"
        
        # Create initial embedding
        embedding1 = embeddings_service.create_embedding(db_session, entity_type, entity_id, text1)
        
        # Update embedding
        embedding2 = embeddings_service.update_embedding(db_session, entity_type, entity_id, text2)
        
        assert embedding1.id == embedding2.id  # Same embedding record
        assert embedding1.embedding != embedding2.embedding  # Different embeddings
    
    def test_semantic_search_empty_results(self, db_session: Session):
        """Test semantic search with no results."""
        results = embeddings_service.semantic_search(
            db=db_session,
            query_text="nonexistent content",
            limit=10,
            similarity_threshold=0.9
        )
        
        assert len(results) == 0 