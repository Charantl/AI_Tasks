import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Comment {
  id: string;
  user_id: string;
  content: string;
  created_at: string;
}

export const CommentsSection: React.FC<{ songId: string; currentUserId?: string }> = ({ songId, currentUserId }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchComments = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`/songs/${songId}/comments`, { withCredentials: true });
      setComments(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load comments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchComments(); }, [songId]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    try {
      await axios.post(`/songs/${songId}/comments`, { content: newComment }, { withCredentials: true });
      setNewComment('');
      fetchComments();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add comment');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await axios.delete(`/comments/${id}`, { withCredentials: true });
      fetchComments();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete comment');
    }
  };

  return (
    <div style={{ marginTop: 24 }}>
      <h4>Comments</h4>
      <form onSubmit={handleAdd}>
        <input value={newComment} onChange={e => setNewComment(e.target.value)} placeholder="Add a comment..." />
        <button type="submit">Post</button>
      </form>
      {loading ? <div>Loading...</div> : (
        <ul>
          {comments.map(c => (
            <li key={c.id}>
              {c.content} <span style={{ color: '#888', marginLeft: 8 }}>{new Date(c.created_at).toLocaleString()}</span>
              {currentUserId && c.user_id === currentUserId && (
                <button style={{ marginLeft: 8 }} onClick={() => handleDelete(c.id)}>Delete</button>
              )}
            </li>
          ))}
        </ul>
      )}
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </div>
  );
}; 