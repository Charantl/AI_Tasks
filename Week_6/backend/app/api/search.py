"""
Enhanced search API with keyword and semantic search capabilities.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
import time
from datetime import datetime

from app.db.session import get_db
from app.models.song import Song
from app.models.artist import Artist
from app.models.album import Album
from app.models.embedding import Embedding
from app.schemas.search import (
    SearchRequest, SearchResponse, SearchResult, SongSearchResult,
    ArtistSearchResult, AlbumSearchResult, SearchFilters,
    SemanticSearchRequest, EmbeddingRequest, EmbeddingResponse
)
from app.services.embeddings import embeddings_service

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_content(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Enhanced search endpoint supporting keyword, semantic, and hybrid search.
    """
    start_time = time.time()
    
    if request.search_type == "semantic":
        results = await _semantic_search(db, request)
    elif request.search_type == "hybrid":
        results = await _hybrid_search(db, request)
    else:  # keyword search
        results = await _keyword_search(db, request)
    
    processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    return SearchResponse(
        query=request.query,
        search_type=request.search_type,
        total_results=len(results),
        results=results,
        processing_time_ms=processing_time
    )


@router.post("/search/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Semantic search using embeddings.
    """
    start_time = time.time()
    
    # Perform semantic search
    semantic_results = embeddings_service.semantic_search(
        db=db,
        query_text=request.text,
        entity_type=request.entity_type,
        limit=request.limit,
        similarity_threshold=request.similarity_threshold
    )
    
    # Convert to search results
    results = []
    for entity_data, similarity in semantic_results:
        if entity_data["type"] == "song":
            result = SongSearchResult(
                id=entity_data["id"],
                type="song",
                title=entity_data["title"],
                artist_name=entity_data["artist_name"],
                album_title=entity_data.get("album_title"),
                duration=entity_data["duration"],
                genre=entity_data.get("genre"),
                audio_url=entity_data["audio_url"],
                score=similarity
            )
        elif entity_data["type"] == "artist":
            result = ArtistSearchResult(
                id=entity_data["id"],
                type="artist",
                title=entity_data["name"],
                name=entity_data["name"],
                bio=entity_data.get("bio"),
                image_url=entity_data.get("image_url"),
                score=similarity
            )
        elif entity_data["type"] == "album":
            result = AlbumSearchResult(
                id=entity_data["id"],
                type="album",
                title=entity_data["title"],
                artist_name=entity_data["artist_name"],
                release_date=entity_data.get("release_date"),
                cover_url=entity_data.get("cover_url"),
                score=similarity
            )
        else:
            continue
        
        results.append(result)
    
    processing_time = (time.time() - start_time) * 1000
    
    return SearchResponse(
        query=request.text,
        search_type="semantic",
        total_results=len(results),
        results=results,
        processing_time_ms=processing_time
    )


@router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embedding(
    request: EmbeddingRequest,
    db: Session = Depends(get_db)
):
    """
    Create or update embedding for an entity.
    """
    embedding = embeddings_service.update_embedding(
        db=db,
        entity_type=request.entity_type,
        entity_id=str(request.entity_id),
        text=request.text
    )
    
    return EmbeddingResponse(
        entity_type=embedding.entity_type,
        entity_id=embedding.entity_id,
        embedding_id=embedding.id,
        embedding_size=len(embedding.embedding) if embedding.embedding else 0,
        created_at=datetime.utcnow()
    )


async def _keyword_search(db: Session, request: SearchRequest) -> List[SearchResult]:
    """Perform keyword-based search."""
    query = request.query.lower()
    filters = request.filters or SearchFilters()
    
    results = []
    
    # Search songs
    if filters.entity_type in ["song", "all"]:
        song_query = db.query(Song).join(Artist)
        
        # Apply filters
        if filters.genre:
            song_query = song_query.filter(Song.genre.ilike(f"%{filters.genre}%"))
        if filters.duration_min is not None:
            song_query = song_query.filter(Song.duration >= filters.duration_min)
        if filters.duration_max is not None:
            song_query = song_query.filter(Song.duration <= filters.duration_max)
        if filters.artist_id:
            song_query = song_query.filter(Song.artist_id == filters.artist_id)
        if filters.album_id:
            song_query = song_query.filter(Song.album_id == filters.album_id)
        
        # Apply text search
        song_query = song_query.filter(
            or_(
                Song.title.ilike(f"%{query}%"),
                Artist.name.ilike(f"%{query}%"),
                Song.genre.ilike(f"%{query}%"),
                Song.lyrics.ilike(f"%{query}%")
            )
        )
        
        songs = song_query.limit(request.limit).offset(request.offset).all()
        
        for song in songs:
            artist = db.query(Artist).filter(Artist.id == song.artist_id).first()
            album = None
            if song.album_id:
                album = db.query(Album).filter(Album.id == song.album_id).first()
            
            result = SongSearchResult(
                id=song.id,
                type="song",
                title=song.title,
                artist_name=artist.name if artist else "Unknown",
                album_title=album.title if album else None,
                duration=song.duration,
                genre=song.genre,
                audio_url=song.audio_url
            )
            results.append(result)
    
    # Search artists
    if filters.entity_type in ["artist", "all"]:
        artist_query = db.query(Artist).filter(
            or_(
                Artist.name.ilike(f"%{query}%"),
                Artist.bio.ilike(f"%{query}%")
            )
        )
        
        artists = artist_query.limit(request.limit).offset(request.offset).all()
        
        for artist in artists:
            result = ArtistSearchResult(
                id=artist.id,
                type="artist",
                title=artist.name,
                name=artist.name,
                bio=artist.bio,
                image_url=artist.image_url
            )
            results.append(result)
    
    # Search albums
    if filters.entity_type in ["album", "all"]:
        album_query = db.query(Album).join(Artist).filter(
            or_(
                Album.title.ilike(f"%{query}%"),
                Artist.name.ilike(f"%{query}%")
            )
        )
        
        albums = album_query.limit(request.limit).offset(request.offset).all()
        
        for album in albums:
            artist = db.query(Artist).filter(Artist.id == album.artist_id).first()
            result = AlbumSearchResult(
                id=album.id,
                type="album",
                title=album.title,
                artist_name=artist.name if artist else "Unknown",
                release_date=album.release_date,
                cover_url=album.cover_url
            )
            results.append(result)
    
    return results


async def _semantic_search(db: Session, request: SearchRequest) -> List[SearchResult]:
    """Perform semantic search using embeddings."""
    semantic_results = embeddings_service.semantic_search(
        db=db,
        query_text=request.query,
        entity_type=request.filters.entity_type if request.filters else "all",
        limit=request.limit,
        similarity_threshold=0.5
    )
    
    results = []
    for entity_data, similarity in semantic_results:
        if entity_data["type"] == "song":
            result = SongSearchResult(
                id=entity_data["id"],
                type="song",
                title=entity_data["title"],
                artist_name=entity_data["artist_name"],
                album_title=entity_data.get("album_title"),
                duration=entity_data["duration"],
                genre=entity_data.get("genre"),
                audio_url=entity_data["audio_url"],
                score=similarity
            )
        elif entity_data["type"] == "artist":
            result = ArtistSearchResult(
                id=entity_data["id"],
                type="artist",
                title=entity_data["name"],
                name=entity_data["name"],
                bio=entity_data.get("bio"),
                image_url=entity_data.get("image_url"),
                score=similarity
            )
        elif entity_data["type"] == "album":
            result = AlbumSearchResult(
                id=entity_data["id"],
                type="album",
                title=entity_data["title"],
                artist_name=entity_data["artist_name"],
                release_date=entity_data.get("release_date"),
                cover_url=entity_data.get("cover_url"),
                score=similarity
            )
        else:
            continue
        
        results.append(result)
    
    return results


async def _hybrid_search(db: Session, request: SearchRequest) -> List[SearchResult]:
    """Perform hybrid search combining keyword and semantic results."""
    # Get keyword results
    keyword_results = await _keyword_search(db, request)
    
    # Get semantic results
    semantic_results = await _semantic_search(db, request)
    
    # Combine and deduplicate results
    seen_ids = set()
    combined_results = []
    
    # Add keyword results first (higher priority)
    for result in keyword_results:
        if result.id not in seen_ids:
            combined_results.append(result)
            seen_ids.add(result.id)
    
    # Add semantic results
    for result in semantic_results:
        if result.id not in seen_ids:
            combined_results.append(result)
            seen_ids.add(result.id)
    
    return combined_results[:request.limit]


@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial query.
    """
    query = query.lower()
    suggestions = []
    
    # Get song title suggestions
    songs = db.query(Song).filter(
        Song.title.ilike(f"%{query}%")
    ).limit(limit).all()
    
    for song in songs:
        suggestions.append({
            "type": "song",
            "text": song.title,
            "id": str(song.id)
        })
    
    # Get artist name suggestions
    artists = db.query(Artist).filter(
        Artist.name.ilike(f"%{query}%")
    ).limit(limit).all()
    
    for artist in artists:
        suggestions.append({
            "type": "artist",
            "text": artist.name,
            "id": str(artist.id)
        })
    
    # Get album title suggestions
    albums = db.query(Album).filter(
        Album.title.ilike(f"%{query}%")
    ).limit(limit).all()
    
    for album in albums:
        suggestions.append({
            "type": "album",
            "text": album.title,
            "id": str(album.id)
        })
    
    return {"suggestions": suggestions[:limit]} 