from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import UUID
from datetime import datetime


class SearchResult(BaseModel):
    """Base search result model."""
    id: UUID
    type: Literal["song", "artist", "album"]
    title: str
    score: Optional[float] = None


class SongSearchResult(SearchResult):
    """Song search result."""
    type: Literal["song"] = "song"
    artist_name: str
    album_title: Optional[str] = None
    duration: int
    genre: Optional[str] = None
    audio_url: str


class ArtistSearchResult(SearchResult):
    """Artist search result."""
    type: Literal["artist"] = "artist"
    name: str
    bio: Optional[str] = None
    image_url: Optional[str] = None


class AlbumSearchResult(SearchResult):
    """Album search result."""
    type: Literal["album"] = "album"
    title: str
    artist_name: str
    release_date: Optional[datetime] = None
    cover_url: Optional[str] = None


class SearchFilters(BaseModel):
    """Search filters for advanced search."""
    entity_type: Optional[Literal["song", "artist", "album", "all"]] = "all"
    genre: Optional[str] = None
    duration_min: Optional[int] = Field(None, ge=0, description="Minimum duration in seconds")
    duration_max: Optional[int] = Field(None, ge=0, description="Maximum duration in seconds")
    artist_id: Optional[UUID] = None
    album_id: Optional[UUID] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    search_type: Literal["keyword", "semantic", "hybrid"] = "keyword"
    filters: Optional[SearchFilters] = None
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    search_type: str
    total_results: int
    results: List[SearchResult]
    processing_time_ms: float


class SemanticSearchRequest(BaseModel):
    """Semantic search request model."""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to find similar content for")
    entity_type: Optional[Literal["song", "artist", "album", "all"]] = "all"
    limit: int = Field(10, ge=1, le=50, description="Maximum number of similar results")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum similarity score")


class EmbeddingRequest(BaseModel):
    """Request to generate embeddings for content."""
    entity_type: Literal["song", "artist", "album"]
    entity_id: UUID
    text: str = Field(..., description="Text content to embed")


class EmbeddingResponse(BaseModel):
    """Response for embedding generation."""
    entity_type: str
    entity_id: UUID
    embedding_id: UUID
    embedding_size: int
    created_at: datetime 