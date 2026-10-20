import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/client';
import { useAppStore } from '../hooks/useAppStore';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setUser } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await authApi.login();
      if (res.data.url === '/demo-login') {
        // Demo mode
        setUser({ sub: 'demo-user', email: 'demo@example.com', name: 'Demo User', roles: ['viewer', 'operator'] });
        navigate('/explorer');
      } else {
        window.location.href = res.data.url;
      }
    } catch (err) {
      setError('Failed to initiate login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f8f9fa' }}>
      <div style={{ background: '#fff', padding: '40px', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', width: '100%', maxWidth: '400px' }}>
        <h1 style={{ margin: '0 0 8px', fontSize: '28px', textAlign: 'center' }}>Orbit Engine</h1>
        <p style={{ margin: '0 0 32px', textAlign: 'center', color: '#6c757d' }}>Sign in to explore learning taxonomies</p>

        {error && (
          <div style={{ background: '#f8d7da', color: '#721c24', padding: '12px', borderRadius: '6px', marginBottom: '16px', fontSize: '14px' }}>
            {error}
          </div>
        )}

        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            background: '#4a90d9',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            fontWeight: 500,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading ? 'Signing in...' : 'Sign in with Keycloak'}
        </button>

        <p style={{ margin: '24px 0 0', textAlign: 'center', fontSize: '13px', color: '#6c757d' }}>
          Demo mode available when Keycloak is not configured
        </p>
      </div>
    </div>
  );
};