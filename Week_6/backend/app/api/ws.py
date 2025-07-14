"""
WebSocket endpoints for real-time features: listening rooms, play progress, user presence.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Set
import asyncio
import uuid
import json

# Optional: import aioredis for Redis pub/sub
# import aioredis

router = APIRouter()

# In-memory room/user management
class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}
        self.usernames: Dict[WebSocket, str] = {}

    async def connect(self, room_id: str, websocket: WebSocket, username: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(websocket)
        self.usernames[websocket] = username
        await self.broadcast(room_id, {"event": "join", "username": username, "room_id": room_id})

    def disconnect(self, room_id: str, websocket: WebSocket):
        self.rooms[room_id].remove(websocket)
        username = self.usernames.pop(websocket, None)
        if not self.rooms[room_id]:
            del self.rooms[room_id]
        return username

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.rooms:
            for ws in list(self.rooms[room_id]):
                try:
                    await ws.send_text(json.dumps(message))
                except Exception:
                    pass

    def get_users(self, room_id: str) -> List[str]:
        return [self.usernames[ws] for ws in self.rooms.get(room_id, set())]

room_manager = RoomManager()

@router.websocket("/ws/listening-room/{room_id}")
async def websocket_listening_room(websocket: WebSocket, room_id: str, username: str = "guest"):
    """
    WebSocket endpoint for joining a listening room.
    - Receives and broadcasts play progress, user join/leave, and custom events.
    - Query param: username (optional)
    """
    await room_manager.connect(room_id, websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            # Broadcast play progress or chat to room
            await room_manager.broadcast(room_id, {"event": "message", "from": username, **message})
    except WebSocketDisconnect:
        left_user = room_manager.disconnect(room_id, websocket)
        await room_manager.broadcast(room_id, {"event": "leave", "username": left_user, "room_id": room_id})

@router.websocket("/ws/play-progress")
async def websocket_play_progress(websocket: WebSocket, user_id: str = "guest"):
    """
    WebSocket endpoint for real-time play progress updates (single user or group).
    - Query param: user_id (optional)
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process play progress
            await websocket.send_text(data)
    except WebSocketDisconnect:
        pass

# (Optional) Redis pub/sub integration for production
# async def redis_broadcast(room_id: str, message: dict):
#     # Use aioredis to publish to a channel
#     pass 