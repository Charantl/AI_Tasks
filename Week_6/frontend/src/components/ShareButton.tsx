import React, { useState } from 'react';
import axios from 'axios';

interface ShareLinks {
  url: string;
  twitter?: string;
  facebook?: string;
  whatsapp?: string;
}

export const ShareButton: React.FC<{ songId: string }> = ({ songId }) => {
  const [open, setOpen] = useState(false);
  const [links, setLinks] = useState<ShareLinks | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchLinks = async () => {
    try {
      const res = await axios.get(`/songs/${songId}/share`, { withCredentials: true });
      setLinks(res.data);
      setOpen(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch share links');
    }
  };

  const handleClick = () => {
    if (!links) fetchLinks();
    else setOpen(o => !o);
  };

  return (
    <span style={{ marginLeft: 8, position: 'relative' }}>
      <button onClick={handleClick}>Share</button>
      {open && links && (
        <div style={{ position: 'absolute', background: '#fff', border: '1px solid #ccc', padding: 8, zIndex: 10 }}>
          <div><a href={links.url} target="_blank" rel="noopener noreferrer">Copy Link</a></div>
          {links.twitter && <div><a href={links.twitter} target="_blank" rel="noopener noreferrer">Share on Twitter</a></div>}
          {links.facebook && <div><a href={links.facebook} target="_blank" rel="noopener noreferrer">Share on Facebook</a></div>}
          {links.whatsapp && <div><a href={links.whatsapp} target="_blank" rel="noopener noreferrer">Share on WhatsApp</a></div>}
        </div>
      )}
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </span>
  );
}; 