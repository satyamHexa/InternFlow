// ──────────────────────────────────────────────────────────────
//  Hook: hooks/useAuth.ts
//  Responsibility: Auth actions (login, logout, refreshToken).
//  Wraps authApi calls + updates authStore.
// ──────────────────────────────────────────────────────────────

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import authApi from '../api/authApi';
import useAuthStore from '../store/authStore';
import type { LoginPayload } from '../types/auth.types';

export function useAuth() {
  const { user, tokens, isAuthenticated, setAuth, clearAuth } = useAuthStore();
  const navigate = useNavigate();

  const login = useCallback(
    async (payload: LoginPayload) => {
      const { user: loggedInUser, tokens: newTokens } = await authApi.login(payload);
      setAuth(loggedInUser, newTokens);
      navigate('/');
    },
    [setAuth, navigate]
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } finally {
      clearAuth();
      navigate('/login', { replace: true });
    }
  }, [clearAuth, navigate]);

  const refreshProfile = useCallback(async () => {
    const profile = await authApi.getProfile();
    useAuthStore.getState().setUser(profile);
    return profile;
  }, []);

  return { user, tokens, isAuthenticated, login, logout, refreshProfile };
}

