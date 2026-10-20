import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ExplorerPage } from './pages/ExplorerPage';
import { LoginPage } from './pages/LoginPage';
import { useAppStore } from './hooks/useAppStore';
import { authApi } from './api/client';

function AppRoutes() {
  const { user, setUser, isAuthenticated } = useAppStore();

  // Check auth on mount
  React.useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await authApi.me();
        setUser(res.data);
      } catch {
        setUser(null);
      }
    };
    checkAuth();
  }, [setUser]);

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/explorer/:domainId?"
        element={
          isAuthenticated ? <ExplorerPage /> : <Navigate to="/login" replace />
        }
      />
      <Route path="/" element={<Navigate to="/explorer" replace />} />
      <Route path="*" element={<Navigate to="/explorer" replace />} />
    </Routes>
  );
}

export default function App() {
  return <AppRoutes />;
}