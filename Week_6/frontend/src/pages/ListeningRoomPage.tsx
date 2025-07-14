import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';

interface User {
  id: string;
  name: string;
}

export const ListeningRoomPage: React.FC = () => {
  const { roomId } = useParams<{ roomId: string }>();
  const [users, setUsers] = useState<User[]>([]);
  const [progress, setProgress] = useState(0);
  const [song, setSong] = useState<string>('');
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!roomId) return;
    const ws = new WebSocket(`ws://localhost:8000/ws/listening-room/${roomId}`);
    wsRef.current = ws;
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'users') setUsers(data.users);
      if (data.type === 'progress') setProgress(data.progress);
      if (data.type === 'song') setSong(data.song);
    };
    return () => ws.close();
  }, [roomId]);

  if (!roomId) return <div>Missing room ID</div>;

  return (
    <div>
      <h2>Listening Room: {roomId}</h2>
      <div>Now playing: {song}</div>
      <div>Progress: <progress value={progress} max={100} style={{ width: 200 }} /> {progress}%</div>
      <div>Users in room:</div>
      <ul>
        {users.map(u => <li key={u.id}>{u.name}</li>)}
      </ul>
    </div>
  );
}; 