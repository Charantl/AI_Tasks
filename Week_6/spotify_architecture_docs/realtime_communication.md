# Real-Time Communication Strategy

## WebSocket Usage
- **Play Progress Updates:**
  - Endpoint: `/ws/play-progress`
  - Clients send/receive current playback position, buffering status, and scrubbing events.
  - Used for synchronizing UI and analytics.

- **Real-Time Song Status:**
  - Endpoint: `/ws/song-status/{song_id}`
  - Broadcasts when a song is played, paused, skipped, or finished.
  - Enables live stats (e.g., "X people listening now").

- **Shared Listening Rooms:**
  - Endpoint: `/ws/listening-room/{room_id}`
  - Multiple users join a room to listen together in sync.
  - Host controls playback; all clients receive real-time updates.

## Implementation Details
- **Backend:** FastAPI with `websockets` or `starlette.websockets` for async, scalable connections.
- **Frontend:** React with WebSocket client (native or library like `socket.io-client`).
- **State Sync:**
  - Server maintains room/user state in Redis for fast access and recovery.
  - Events: play, pause, seek, join/leave, chat messages.
- **Scalability:**
  - Use Redis Pub/Sub for cross-instance event propagation.
  - Horizontal scaling with sticky sessions or distributed session management.
- **Security:**
  - JWT or session token required for connection.
  - Room access control for private/public rooms. 