"""
Embeddings service for semantic search functionality.
"""
import numpy as np
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.embedding import Embedding
from app.models.song import Song
from app.models.artist import Artist
from app.models.album import Album
import uuid
from datetime import datetime


class EmbeddingsService:
    """Service for managing embeddings and semantic search."""
    
    def __init__(self):
        # For now, we'll use a simple TF-IDF like approach
        # In production, you'd use a proper embedding model like sentence-transformers
        self.embedding_dim = 128  # Placeholder dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for given text.
        In production, this would use a proper embedding model.
        """
        # Simple hash-based embedding for demo purposes
        # In production, use sentence-transformers or similar
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 128-dimensional vector
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            value = int.from_bytes(chunk, byteorder='big')
            embedding.append((value % 1000) / 1000.0)  # Normalize to [0,1]
        
        # Pad or truncate to embedding_dim
        while len(embedding) < self.embedding_dim:
            embedding.extend(embedding[:min(len(embedding), self.embedding_dim - len(embedding))])
        
        return embedding[:self.embedding_dim]
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def create_embedding(self, db: Session, entity_type: str, entity_id: str, text: str) -> Embedding:
        """Create and store embedding for an entity."""
        embedding_vector = self.generate_embedding(text)
        
        embedding = Embedding(
            id=uuid.uuid4(),
            entity_type=entity_type,
            entity_id=entity_id,
            embedding=embedding_vector
        )
        
        db.add(embedding)
        db.commit()
        db.refresh(embedding)
        
        return embedding
    
    def update_embedding(self, db: Session, entity_type: str, entity_id: str, text: str) -> Embedding:
        """Update existing embedding or create new one."""
        # Check if embedding exists
        existing = db.query(Embedding).filter(
            Embedding.entity_type == entity_type,
            Embedding.entity_id == entity_id
        ).first()
        
        if existing:
            # Update existing embedding
            existing.embedding = self.generate_embedding(text)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new embedding
            return self.create_embedding(db, entity_type, entity_id, text)
    
    def semantic_search(self, db: Session, query_text: str, entity_type: str = "all", 
                       limit: int = 10, similarity_threshold: float = 0.7) -> List[Tuple[dict, float]]:
        """
        Perform semantic search using embeddings.
        Returns list of (entity_data, similarity_score) tuples.
        """
        query_embedding = self.generate_embedding(query_text)
        results = []
        
        # Get embeddings for the specified entity type
        if entity_type == "all":
            embeddings = db.query(Embedding).all()
        else:
            embeddings = db.query(Embedding).filter(Embedding.entity_type == entity_type).all()
        
        for embedding in embeddings:
            similarity = self.calculate_similarity(query_embedding, embedding.embedding)
            
            if similarity >= similarity_threshold:
                # Get the actual entity data
                entity_data = self._get_entity_data(db, embedding.entity_type, embedding.entity_id)
                if entity_data:
                    results.append((entity_data, similarity))
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    def _get_entity_data(self, db: Session, entity_type: str, entity_id: str) -> Optional[dict]:
        """Get entity data based on type and ID."""
        if entity_type == "song":
            song = db.query(Song).filter(Song.id == entity_id).first()
            if song:
                artist = db.query(Artist).filter(Artist.id == song.artist_id).first()
                return {
                    "id": str(song.id),
                    "type": "song",
                    "title": song.title,
                    "artist_name": artist.name if artist else "Unknown",
                    "duration": song.duration,
                    "genre": song.genre,
                    "audio_url": song.audio_url
                }
        
        elif entity_type == "artist":
            artist = db.query(Artist).filter(Artist.id == entity_id).first()
            if artist:
                return {
                    "id": str(artist.id),
                    "type": "artist",
                    "name": artist.name,
                    "bio": artist.bio,
                    "image_url": artist.image_url
                }
        
        elif entity_type == "album":
            album = db.query(Album).filter(Album.id == entity_id).first()
            if album:
                artist = db.query(Artist).filter(Artist.id == album.artist_id).first()
                return {
                    "id": str(album.id),
                    "type": "album",
                    "title": album.title,
                    "artist_name": artist.name if artist else "Unknown",
                    "release_date": album.release_date,
                    "cover_url": album.cover_url
                }
        
        return None
    
    def generate_song_embedding(self, db: Session, song: Song) -> Embedding:
        """Generate embedding for a song using its metadata."""
        text_content = f"{song.title} {song.genre or ''} {song.lyrics or ''}"
        
        # Get artist name
        artist = db.query(Artist).filter(Artist.id == song.artist_id).first()
        if artist:
            text_content += f" {artist.name}"
        
        # Get album title
        if song.album_id:
            album = db.query(Album).filter(Album.id == song.album_id).first()
            if album:
                text_content += f" {album.title}"
        
        return self.update_embedding(db, "song", str(song.id), text_content)
    
    def generate_artist_embedding(self, db: Session, artist: Artist) -> Embedding:
        """Generate embedding for an artist using their metadata."""
        text_content = f"{artist.name} {artist.bio or ''}"
        return self.update_embedding(db, "artist", str(artist.id), text_content)
    
    def generate_album_embedding(self, db: Session, album: Album) -> Embedding:
        """Generate embedding for an album using its metadata."""
        text_content = f"{album.title}"
        
        # Get artist name
        artist = db.query(Artist).filter(Artist.id == album.artist_id).first()
        if artist:
            text_content += f" {artist.name}"
        
        return self.update_embedding(db, "album", str(album.id), text_content)


# Global instance
embeddings_service = EmbeddingsService() 