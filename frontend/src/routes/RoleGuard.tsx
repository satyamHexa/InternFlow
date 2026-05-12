// ──────────────────────────────────────────────────────────────
//  Module: src/routes/RoleGuard.tsx
//  Responsibility: Render children only if user role is permitted.
// ──────────────────────────────────────────────────────────────

import React from 'react';
import { Navigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import type { UserRole } from '../types/auth.types';

interface RoleGuardProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
  redirectTo?: string;
}

export default function RoleGuard({
  allowedRoles,
  children,
  redirectTo = '/',
}: RoleGuardProps) {
  const user = useAuthStore((s) => s.user);

  if (!user || !allowedRoles.includes(user.role)) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
}
