// ──────────────────────────────────────────────────────────────
//  Module: src/types/auth.types.ts
//  Responsibility: TypeScript interfaces for Auth domain.
// ──────────────────────────────────────────────────────────────

export type UserRole =
  | 'employee'
  | 'hr'
  | 'mentor'
  | 'it_admin'
  | 'compliance_officer'
  | 'program_owner';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  department?: string;
  avatarUrl?: string;
  createdAt: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
}
