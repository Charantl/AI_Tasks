import React, { useEffect, useState } from 'react';
import axios from 'axios';

export const SubscriptionTier: React.FC = () => {
  const [tier, setTier] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTier = async () => {
      setLoading(true);
      try {
        const res = await axios.get('/subscription');
        setTier(res.data.tier || res.data.subscription || 'Free');
      } catch {
        setTier(null);
      } finally {
        setLoading(false);
      }
    };
    fetchTier();
  }, []);

  if (loading) return null;
  if (!tier) return null;
  return <span style={{ marginLeft: 8 }}>[{tier} tier]</span>;
}; 