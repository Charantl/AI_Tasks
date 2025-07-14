# AI Recommendations API Documentation

This document describes the AI-powered recommendations endpoints for the Spotify-like music streaming platform.

## Endpoints

### 1. Get Personalized Recommendations
- **POST** `/recommendations`
- **Description:** Get personalized music recommendations for a user using content-based, collaborative, hybrid, context-based, or popular algorithms.
- **Request Body:**
```json
{
  "user_id": "<user-uuid>",
  "recommendation_type": "hybrid", // or content_based, collaborative, context_based, popular
  "limit": 10,
  "context": {"mood": "energetic"}
}
```
- **Response:**
```json
{
  "user_id": "<user-uuid>",
  "recommendation_type": "hybrid",
  "recommendations": [
    {
      "id": "<song-uuid>",
      "title": "Song Title",
      "artist_name": "Artist Name",
      "album_title": "Album Title",
      "duration": 180,
      "genre": "Pop",
      "audio_url": "http://...",
      "similarity_score": 0.82,
      "recommendation_type": "content_based"
    }
  ],
  "total_count": 10,
  "generated_at": "2024-07-10T12:00:00Z",
  "processing_time_ms": 42.5
}
```

### 2. Get Recommendations by User ID
- **GET** `/recommendations/{user_id}`
- **Query Params:** `recommendation_type`, `limit`
- **Description:** Get recommendations for a user by user_id and algorithm type.

### 3. Batch Recommendations
- **POST** `/recommendations/batch`
- **Description:** Get recommendations for multiple users in a single request.

### 4. User Insights
- **GET** `/recommendations/{user_id}/insights`
- **Description:** Get insights about a user's music preferences, favorite genres, and listening patterns.

### 5. Submit Feedback
- **POST** `/recommendations/feedback`
- **Description:** Submit feedback (like, dislike, skip, play) on a recommendation to improve future suggestions.
- **Request Body:**
```json
{
  "user_id": "<user-uuid>",
  "recommendation_id": "<rec-id>",
  "feedback_type": "like",
  "feedback_value": 1.0
}
```

### 6. Recommendation Metrics
- **GET** `/recommendations/metrics`
- **Description:** Get overall metrics for recommendation system performance (click-through rate, satisfaction, diversity, etc.).

### 7. Personalized Playlist
- **POST** `/recommendations/playlist`
- **Description:** Create a personalized playlist for a user based on preferences, mood, and target duration.

### 8. Similar Users
- **GET** `/recommendations/{user_id}/similar-users`
- **Description:** Find users with similar music taste based on liked songs.

### 9. Discovery Recommendations
- **GET** `/recommendations/{user_id}/discover`
- **Description:** Get recommendations for songs outside the user's usual preferences (genre exploration).

---

## Recommendation Types
- **content_based**: Recommends songs similar to those the user has liked.
- **collaborative**: Recommends songs liked by users with similar taste.
- **hybrid**: Combines content-based and collaborative approaches.
- **context_based**: Uses context (time, mood, etc.) for recommendations.
- **popular**: Returns currently popular songs.
- **discovery**: Suggests songs outside the user's usual genres.

---

## Example Usage

### Get Hybrid Recommendations
```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<user-uuid>",
    "recommendation_type": "hybrid",
    "limit": 10
  }'
```

### Get User Insights
```bash
curl http://localhost:8000/recommendations/<user-uuid>/insights
```

---

## Feedback
- Use the feedback endpoint to help improve future recommendations.
- Feedback types: `like`, `dislike`, `skip`, `play`

---

## See Also
- [Search API Documentation](./search_api.md)
- [System Architecture](./system_architecture.md) 