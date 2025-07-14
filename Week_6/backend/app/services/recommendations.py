"""
AI Recommendations service for personalized music recommendations.
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import uuid

from app.models.song import Song
from app.models.artist import Artist
from app.models.album import Album
from app.models.user import User
from app.models.liked_song import LikedSong
from app.models.play_history import PlayHistory
from app.models.embedding import Embedding
from app.services.embeddings import embeddings_service
from app.core.cache import Cache
from app.models.playlist import Playlist


class RecommendationsService:
    """Service for generating personalized music recommendations."""
    
    def __init__(self):
        self.embedding_dim = 128
    
    def get_user_preferences(self, db: Session, user_id: str) -> Dict:
        """Extract user preferences from their behavior."""
        preferences = {
            'liked_genres': [],
            'liked_artists': [],
            'listening_patterns': [],
            'preferred_duration': 0,
            'active_hours': [],
            'total_listening_time': 0
        }
        
        # Get liked songs and their genres
        liked_songs = db.query(LikedSong).filter(LikedSong.user_id == user_id).all()
        for liked in liked_songs:
            song = db.query(Song).filter(Song.id == liked.song_id).first()
            if song and song.genre:
                preferences['liked_genres'].append(song.genre)
        
        # Get play history for listening patterns
        play_history = db.query(PlayHistory).filter(
            PlayHistory.user_id == user_id
        ).order_by(desc(PlayHistory.played_at)).limit(100).all()
        
        total_duration = 0
        for play in play_history:
            song = db.query(Song).filter(Song.id == play.song_id).first()
            if song:
                total_duration += song.duration
                hour = play.played_at.hour
                preferences['active_hours'].append(hour)
        
        preferences['total_listening_time'] = total_duration
        if play_history:
            preferences['preferred_duration'] = total_duration / len(play_history)
        
        # Get most listened artists
        artist_plays = db.query(
            Song.artist_id,
            func.count(PlayHistory.id).label('play_count')
        ).join(PlayHistory).filter(
            PlayHistory.user_id == user_id
        ).group_by(Song.artist_id).order_by(desc('play_count')).limit(10).all()
        
        for artist_id, play_count in artist_plays:
            artist = db.query(Artist).filter(Artist.id == artist_id).first()
            if artist:
                preferences['liked_artists'].append(artist.name)
        
        return preferences
    
    def content_based_recommendations(self, db: Session, user_id: str, limit: int = 10) -> List[Dict]:
        """Generate content-based recommendations based on user's liked content."""
        # Get user's liked songs
        liked_songs = db.query(LikedSong).filter(LikedSong.user_id == user_id).all()
        
        if not liked_songs:
            return self._get_popular_songs(db, limit)
        
        # Get embeddings for liked songs
        liked_embeddings = []
        for liked in liked_songs:
            embedding = db.query(Embedding).filter(
                Embedding.entity_type == "song",
                Embedding.entity_id == liked.song_id
            ).first()
            if embedding and embedding.embedding:
                liked_embeddings.append(embedding.embedding)
        
        if not liked_embeddings:
            return self._get_popular_songs(db, limit)
        
        # Calculate average embedding of liked songs
        avg_embedding = np.mean(liked_embeddings, axis=0)
        
        # Find similar songs
        all_song_embeddings = db.query(Embedding).filter(
            Embedding.entity_type == "song"
        ).all()
        
        similarities = []
        for embedding in all_song_embeddings:
            if embedding.embedding and embedding.entity_id not in [str(ls.song_id) for ls in liked_songs]:
                similarity = embeddings_service.calculate_similarity(avg_embedding, embedding.embedding)
                similarities.append((embedding.entity_id, similarity))
        
        # Sort by similarity and get top recommendations
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for song_id, similarity in similarities[:limit]:
            song = db.query(Song).filter(Song.id == song_id).first()
            if song:
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
                    'similarity_score': similarity,
                    'recommendation_type': 'content_based'
                })
        
        return recommendations
    
    def collaborative_filtering_recommendations(self, db: Session, user_id: str, limit: int = 10) -> List[Dict]:
        """Generate collaborative filtering recommendations based on similar users."""
        # Find users with similar taste
        user_liked_songs = set()
        liked_songs = db.query(LikedSong).filter(LikedSong.user_id == user_id).all()
        for liked in liked_songs:
            user_liked_songs.add(str(liked.song_id))
        
        if not user_liked_songs:
            return self._get_popular_songs(db, limit)
        
        # Find users with overlapping liked songs
        similar_users = []
        all_users = db.query(User).filter(User.id != user_id).all()
        
        for user in all_users:
            user_likes = db.query(LikedSong).filter(LikedSong.user_id == user.id).all()
            user_liked_set = {str(like.song_id) for like in user_likes}
            
            # Calculate similarity based on overlapping liked songs
            overlap = len(user_liked_songs.intersection(user_liked_set))
            if overlap > 0:
                similarity = overlap / len(user_liked_songs.union(user_liked_set))
                similar_users.append((user.id, similarity))
        
        # Sort by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        
        # Get recommendations from similar users
        recommended_songs = set()
        for similar_user_id, similarity in similar_users[:5]:  # Top 5 similar users
            user_likes = db.query(LikedSong).filter(
                LikedSong.user_id == similar_user_id,
                ~LikedSong.song_id.in_(user_liked_songs)  # Not already liked
            ).all()
            
            for like in user_likes:
                recommended_songs.add(str(like.song_id))
        
        # Get song details
        recommendations = []
        for song_id in list(recommended_songs)[:limit]:
            song = db.query(Song).filter(Song.id == song_id).first()
            if song:
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
                    'similarity_score': 0.5,  # Placeholder
                    'recommendation_type': 'collaborative'
                })
        
        return recommendations
    
    def hybrid_recommendations(self, db: Session, user_id: str, limit: int = 10) -> List[Dict]:
        """Generate hybrid recommendations combining multiple approaches."""
        content_based = self.content_based_recommendations(db, user_id, limit // 2)
        collaborative = self.collaborative_filtering_recommendations(db, user_id, limit // 2)
        
        # Combine and deduplicate
        seen_ids = set()
        hybrid_recommendations = []
        
        # Add content-based recommendations first
        for rec in content_based:
            if rec['id'] not in seen_ids:
                hybrid_recommendations.append(rec)
                seen_ids.add(rec['id'])
        
        # Add collaborative recommendations
        for rec in collaborative:
            if rec['id'] not in seen_ids and len(hybrid_recommendations) < limit:
                hybrid_recommendations.append(rec)
                seen_ids.add(rec['id'])
        
        return hybrid_recommendations
    
    def context_based_recommendations(self, db: Session, user_id: str, context: Dict, limit: int = 10) -> List[Dict]:
        """Generate context-based recommendations (time of day, mood, etc.)."""
        current_hour = datetime.now().hour
        
        # Get user's listening patterns by hour
        preferences = self.get_user_preferences(db, user_id)
        active_hours = preferences.get('active_hours', [])
        
        if not active_hours:
            return self._get_popular_songs(db, limit)
        
        # Find most common active hour
        from collections import Counter
        hour_counts = Counter(active_hours)
        most_active_hour = hour_counts.most_common(1)[0][0]
        
        # Get songs that user listens to during this hour
        hour_songs = db.query(PlayHistory).filter(
            PlayHistory.user_id == user_id,
            func.extract('hour', PlayHistory.played_at) == most_active_hour
        ).limit(50).all()
        
        if not hour_songs:
            return self._get_popular_songs(db, limit)
        
        # Get genres and artists from this time period
        song_ids = [play.song_id for play in hour_songs]
        songs = db.query(Song).filter(Song.id.in_(song_ids)).all()
        
        genres = [song.genre for song in songs if song.genre]
        artist_ids = [song.artist_id for song in songs]
        
        # Find similar songs based on time-based preferences
        similar_songs = db.query(Song).filter(
            Song.genre.in_(genres) if genres else True,
            Song.artist_id.in_(artist_ids) if artist_ids else True,
            ~Song.id.in_(song_ids)  # Not already in user's history
        ).limit(limit).all()
        
        recommendations = []
        for song in similar_songs:
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
                'similarity_score': 0.6,  # Context-based score
                'recommendation_type': 'context_based'
            })
        
        return recommendations
    
    def _get_popular_songs(self, db: Session, limit: int) -> List[Dict]:
        """Get popular songs as fallback recommendations."""
        # Get songs with most plays
        popular_songs = db.query(
            Song.id,
            func.count(PlayHistory.id).label('play_count')
        ).join(PlayHistory).group_by(Song.id).order_by(
            desc('play_count')
        ).limit(limit).all()
        
        recommendations = []
        for song_id, play_count in popular_songs:
            song = db.query(Song).filter(Song.id == song_id).first()
            if song:
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
                    'similarity_score': 0.3,  # Popular score
                    'recommendation_type': 'popular'
                })
        
        return recommendations
    
    def get_recommendations_summary(self, db: Session, user_id: str) -> Dict:
        """Get a summary of recommendation insights for a user."""
        preferences = self.get_user_preferences(db, user_id)
        
        # Get recent listening activity
        recent_plays = db.query(PlayHistory).filter(
            PlayHistory.user_id == user_id,
            PlayHistory.played_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Get favorite genres
        genre_counts = {}
        liked_songs = db.query(LikedSong).filter(LikedSong.user_id == user_id).all()
        for liked in liked_songs:
            song = db.query(Song).filter(Song.id == liked.song_id).first()
            if song and song.genre:
                genre_counts[song.genre] = genre_counts.get(song.genre, 0) + 1
        
        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'total_liked_songs': len(liked_songs),
            'recent_plays_7_days': recent_plays,
            'favorite_genres': [genre for genre, count in top_genres],
            'total_listening_time_minutes': preferences['total_listening_time'] // 60,
            'most_active_hour': max(preferences['active_hours']) if preferences['active_hours'] else None,
            'preferred_duration_seconds': int(preferences['preferred_duration'])
        }

    def get_cached_recommendations(self, db: Session, user_id: str, rec_type: str, limit: int = 10):
        key = f"recommendations:{user_id}:{rec_type}:{limit}"
        def fetch():
            if rec_type == "content_based":
                return self.content_based_recommendations(db, user_id, limit)
            elif rec_type == "collaborative":
                return self.collaborative_filtering_recommendations(db, user_id, limit)
            elif rec_type == "context_based":
                return self.context_based_recommendations(db, user_id, {}, limit)
            elif rec_type == "popular":
                return self._get_popular_songs(db, limit)
            else:
                return self.hybrid_recommendations(db, user_id, limit)
        return Cache.get_or_set(key, fetch, ttl=1800)

    def invalidate_recommendations_cache(self, user_id: str):
        # Invalidate all recommendation types for this user
        for rec_type in ["content_based", "collaborative", "context_based", "popular", "hybrid"]:
            for limit in [10, 20, 50]:
                Cache.invalidate(f"recommendations:{user_id}:{rec_type}:{limit}")

    def get_cached_playlist(self, db: Session, playlist_id: str):
        key = f"playlist:{playlist_id}"
        def fetch():
            # ... fetch playlist from DB ...
            playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
            if not playlist:
                return None
            # ... serialize playlist ...
            return {"id": str(playlist.id), "name": playlist.name, "songs": [str(s.id) for s in playlist.songs]}
        return Cache.get_or_set(key, fetch, ttl=1800)

    def invalidate_playlist_cache(self, playlist_id: str):
        Cache.invalidate(f"playlist:{playlist_id}")

    def cache_warm_popular_recommendations(self, db: Session):
        # Preload cache for popular recommendations
        for rec_type in ["popular", "hybrid"]:
            for limit in [10, 20, 50]:
                Cache.warm(f"recommendations:popular:{rec_type}:{limit}", lambda: self._get_popular_songs(db, limit), ttl=1800)

    def cache_metrics(self):
        return Cache.metrics()


# Global instance
recommendations_service = RecommendationsService() 