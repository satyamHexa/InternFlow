// ──────────────────────────────────────────────────────────────
//  Module: src/api/authApi.ts
//  Responsibility: All authentication HTTP calls.
//  Endpoints consumed:
//    POST /api/auth/login
//    POST /api/auth/register
//    POST /api/auth/refresh
//    GET  /api/auth/profile
//    POST /api/auth/logout
// ──────────────────────────────────────────────────────────────

import axiosClient from './axiosClient';
import type { AuthTokens, LoginPayload, User } from '../types/auth.types';

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  role?: string;
  department?: string;
}

export interface TokenApiResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

function mapTokens(raw: TokenApiResponse): AuthTokens {
  return {
    accessToken: raw.access_token,
    refreshToken: raw.refresh_token,
    expiresIn: raw.expires_in,
  };
}

function mapUser(raw: Record<string, unknown>): User {
  return {
    id: raw.id as string,
    name: raw.name as string,
    email: raw.email as string,
    role: raw.role as User['role'],
    department: raw.department as string | undefined,
    createdAt: raw.created_at as string,
  };
}

const authApi = {
  async login(payload: LoginPayload): Promise<{ user: User; tokens: AuthTokens }> {
    const { data } = await axiosClient.post<TokenApiResponse>('/auth/login', {
      email: payload.email,
      password: payload.password,
    });
    const tokens = mapTokens(data);
    const profile = await authApi.getProfile();
    return { user: profile, tokens };
  },

  async register(payload: RegisterPayload): Promise<User> {
    const { data } = await axiosClient.post<Record<string, unknown>>('/auth/register', payload);
    return mapUser(data);
  },

  async refresh(refreshToken: string): Promise<AuthTokens> {
    const { data } = await axiosClient.post<TokenApiResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return mapTokens(data);
  },

  async getProfile(): Promise<User> {
    const { data } = await axiosClient.get<Record<string, unknown>>('/auth/profile');
    return mapUser(data);
  },

  async logout(): Promise<void> {
    await axiosClient.post('/auth/logout');
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await axiosClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};

export default authApi;

