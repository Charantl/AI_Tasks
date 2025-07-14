import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_websocket_room_broadcast():
    room_id = "testroom"
    with client.websocket_connect(f"/ws/rooms/{room_id}") as ws1, \
         client.websocket_connect(f"/ws/rooms/{room_id}") as ws2:
        # ws1 sends a chat message
        msg = {"type": "chat", "user": "alice", "text": "Hello!"}
        ws1.send_json(msg)
        # Both ws1 and ws2 should receive the message
        data1 = ws1.receive_json()
        data2 = ws2.receive_json()
        assert data1 == msg
        assert data2 == msg
        # ws2 sends a play progress update
        progress = {"type": "progress", "user": "bob", "position": 42}
        ws2.send_json(progress)
        data1 = ws1.receive_json()
        data2 = ws2.receive_json()
        assert data1 == progress
        assert data2 == progress
        # ws1 disconnects
    # ws2 should receive a leave message
    with client.websocket_connect(f"/ws/rooms/{room_id}") as ws3:
        ws3.send_json({"type": "chat", "user": "carol", "text": "Bye!"})
        ws3.receive_json()  # echo 