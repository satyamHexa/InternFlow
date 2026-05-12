// ──────────────────────────────────────────────────────────────
//  Page: Settings.tsx
//  Route: /settings  (protected)
// ──────────────────────────────────────────────────────────────

import React, { useState } from 'react';
import useAuthStore from '../store/authStore';
import authApi from '../api/authApi';
import { useAuth } from '../hooks/useAuth';

export default function Settings() {
  const user = useAuthStore((s) => s.user);
  const { logout } = useAuth();

  const [currentPwd, setCurrentPwd] = useState('');
  const [newPwd, setNewPwd] = useState('');
  const [pwdMsg, setPwdMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [saving, setSaving] = useState(false);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setPwdMsg(null);
    try {
      await authApi.changePassword(currentPwd, newPwd);
      setPwdMsg({ ok: true, text: 'Password updated successfully.' });
      setCurrentPwd('');
      setNewPwd('');
    } catch (err: unknown) {
      setPwdMsg({ ok: false, text: err instanceof Error ? err.message : 'Failed to update password.' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

      {/* Profile */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Profile</h2>
        <div className="space-y-1 text-sm">
          <p><span className="text-gray-500">Name:</span> <span className="font-medium">{user?.name}</span></p>
          <p><span className="text-gray-500">Email:</span> <span className="font-medium">{user?.email}</span></p>
          <p><span className="text-gray-500">Role:</span> <span className="font-medium">{user?.role}</span></p>
          {user?.department && (
            <p><span className="text-gray-500">Department:</span> <span className="font-medium">{user.department}</span></p>
          )}
        </div>
      </div>

      {/* Change Password */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Change Password</h2>
        <form onSubmit={handlePasswordChange} className="space-y-3">
          <input
            type="password"
            value={currentPwd}
            onChange={(e) => setCurrentPwd(e.target.value)}
            placeholder="Current password"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="password"
            value={newPwd}
            onChange={(e) => setNewPwd(e.target.value)}
            placeholder="New password (min 8 chars)"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {pwdMsg && (
            <div className={`text-sm px-3 py-2 rounded-lg border ${
              pwdMsg.ok
                ? 'bg-green-50 border-green-200 text-green-700'
                : 'bg-red-50 border-red-200 text-red-700'
            }`}>
              {pwdMsg.text}
            </div>
          )}
          <button
            type="submit"
            disabled={saving || !currentPwd || !newPwd}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-lg px-4 py-2 text-sm"
          >
            {saving ? 'Updating…' : 'Update Password'}
          </button>
        </form>
      </div>

      {/* Sign out */}
      <button
        onClick={logout}
        className="w-full border border-red-300 text-red-600 hover:bg-red-50 font-semibold rounded-lg px-4 py-2 text-sm"
      >
        Sign Out
      </button>
    </div>
  );
}
