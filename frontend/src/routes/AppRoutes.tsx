// ──────────────────────────────────────────────────────────────
//  Module: src/routes/AppRoutes.tsx
//  Responsibility: Top-level route tree.
// ──────────────────────────────────────────────────────────────

import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import AppLayout from '../layouts/AppLayout';

// Lazy-load pages for code splitting
const Login = lazy(() => import('../pages/Login'));
const Dashboard = lazy(() => import('../pages/Dashboard'));
const ReferralForm = lazy(() => import('../pages/ReferralForm'));
const CandidateProfile = lazy(() => import('../pages/CandidateProfile'));
const WorkflowTracker = lazy(() => import('../pages/WorkflowTracker'));
const Certificates = lazy(() => import('../pages/Certificates'));
const AuditLogs = lazy(() => import('../pages/AuditLogs'));
const Settings = lazy(() => import('../pages/Settings'));

const Loading = () => (
  <div className="flex items-center justify-center h-full min-h-screen">
    <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
  </div>
);

export default function AppRoutes() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<Login />} />

        {/* Protected — any authenticated user, wrapped in app shell */}
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/referrals/new" element={<ReferralForm />} />
            <Route path="/referrals/:id" element={<CandidateProfile />} />
            <Route path="/workflow/:id" element={<WorkflowTracker />} />
            <Route path="/certificates" element={<Certificates />} />
            <Route path="/audit" element={<AuditLogs />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}

