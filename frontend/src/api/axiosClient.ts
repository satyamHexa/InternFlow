// ──────────────────────────────────────────────────────────────
//  Module: src/api/axiosClient.ts
//  Responsibility: Shared Axios instance.
//  Concerns:
//    - Base URL from env
//    - JWT Bearer token injection via request interceptor
//    - 401 handling → token refresh → retry
//    - Error normalisation
// ──────────────────────────────────────────────────────────────

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

const axiosClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
});

// ── Request interceptor: attach access token ──────────────────
axiosClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const raw = localStorage.getItem('auth-storage');
  if (raw) {
    try {
      const state = JSON.parse(raw) as { state?: { tokens?: { accessToken?: string } } };
      const token = state?.state?.tokens?.accessToken;
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch {
      // malformed storage — ignore
    }
  }
  return config;
});

// ── Response interceptor: 401 → refresh → retry ───────────────
let _isRefreshing = false;
let _refreshQueue: Array<(token: string) => void> = [];

axiosClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(normaliseError(error));
    }

    if (_isRefreshing) {
      return new Promise((resolve) => {
        _refreshQueue.push((token: string) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          resolve(axiosClient(originalRequest));
        });
      });
    }

    originalRequest._retry = true;
    _isRefreshing = true;

    try {
      const raw = localStorage.getItem('auth-storage');
      const state = raw ? (JSON.parse(raw) as { state?: { tokens?: { refreshToken?: string } } }) : null;
      const refreshToken = state?.state?.tokens?.refreshToken;
      if (!refreshToken) throw new Error('No refresh token');

      const { data } = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refreshToken });
      const newAccessToken: string = data.access_token;

      // Persist the new token into Zustand's persisted store
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed?.state?.tokens) {
          parsed.state.tokens.accessToken = newAccessToken;
          localStorage.setItem('auth-storage', JSON.stringify(parsed));
        }
      }

      _refreshQueue.forEach((cb) => cb(newAccessToken));
      _refreshQueue = [];
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return axiosClient(originalRequest);
    } catch {
      _refreshQueue = [];
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
      return Promise.reject(normaliseError(error));
    } finally {
      _isRefreshing = false;
    }
  }
);

// ── Error normalisation ───────────────────────────────────────
function normaliseError(error: AxiosError): Error {
  const detail = (error.response?.data as { detail?: string })?.detail;
  return new Error(detail ?? error.message ?? 'An unexpected error occurred');
}

export default axiosClient;

