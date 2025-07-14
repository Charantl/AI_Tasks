import React, { useEffect, useState } from 'react';
import axios from 'axios';

export const SubscriptionPage: React.FC = () => {
  const [subscription, setSubscription] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchSubscription = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get('/subscription');
        setSubscription(res.data.tier || res.data.subscription || 'Free');
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch subscription');
      } finally {
        setLoading(false);
      }
    };
    fetchSubscription();
  }, []);

  const handleUpgrade = async () => {
    setError(null);
    setSuccess(false);
    try {
      await axios.post('/subscription/upgrade');
      setSuccess(true);
      setSubscription('Premium');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upgrade failed');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h2>Subscription</h2>
      <div>Current tier: <b>{subscription}</b></div>
      {subscription !== 'Premium' && (
        <button onClick={handleUpgrade}>Upgrade to Premium</button>
      )}
      {success && <div style={{ color: 'green' }}>Upgrade successful!</div>}
    </div>
  );
}; 