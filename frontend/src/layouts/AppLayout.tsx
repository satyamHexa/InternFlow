// ──────────────────────────────────────────────────────────────
//  Layout: layouts/AppLayout.tsx
//  Responsibility: Main authenticated shell with sidebar + topnav.
// ──────────────────────────────────────────────────────────────

import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import authApi from '../api/authApi';

interface NavItem {
  to: string;
  label: string;
  roles?: string[];
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Dashboard', roles: ['hr', 'program_owner'] },
  { to: '/referrals/new', label: 'New Referral', roles: ['employee'] },
  { to: '/certificates', label: 'Certificates', roles: ['hr', 'program_owner'] },
  { to: '/audit', label: 'Audit Logs', roles: ['compliance_officer', 'hr'] },
  { to: '/settings', label: 'Settings' },
];

export default function AppLayout() {
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const navigate = useNavigate();

  const handleLogout = async () => {
    try { await authApi.logout(); } finally {
      clearAuth();
      navigate('/login', { replace: true });
    }
  };

  const visibleLinks = NAV_ITEMS.filter(
    (item) => !item.roles || (user && item.roles.includes(user.role))
  );

  const linkCls = ({ isActive }: { isActive: boolean }) =>
    `block px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'
    }`;

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r flex flex-col">
        <div className="px-4 py-5 border-b">
          <span className="text-lg font-bold text-blue-600">InternFlow</span>
        </div>
        <nav className="flex-1 px-2 py-4 space-y-1">
          {visibleLinks.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === '/'} className={linkCls}>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-4 py-4 border-t">
          <p className="text-xs text-gray-500 truncate">{user?.name}</p>
          <p className="text-xs text-gray-400 truncate">{user?.role}</p>
          <button
            onClick={handleLogout}
            className="mt-2 w-full text-xs text-red-600 hover:text-red-700 text-left"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
