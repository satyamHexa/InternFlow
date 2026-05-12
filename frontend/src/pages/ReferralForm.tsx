// ──────────────────────────────────────────────────────────────
//  Page: ReferralForm.tsx
//  Route: /referrals/new  (protected — employee)
// ──────────────────────────────────────────────────────────────

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { useCreateReferral } from '../hooks/useReferral';

const schema = z.object({
  candidateName: z.string().min(2, 'Name must be at least 2 characters'),
  candidateEmail: z.string().email('Enter a valid email'),
  candidatePhone: z.string().optional(),
  department: z.string().min(2, 'Department is required'),
});
type FormData = z.infer<typeof schema>;

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      {children}
      {error && <p className="text-red-600 text-xs mt-1">{error}</p>}
    </div>
  );
}

export default function ReferralForm() {
  const navigate = useNavigate();
  const createReferral = useCreateReferral();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormData) => {
    const referral = await createReferral.mutateAsync(values);
    navigate(`/referrals/${referral.id}`);
  };

  const inputCls =
    'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500';

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">New Referral</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-2xl shadow p-6 space-y-4">
        <Field label="Candidate Name" error={errors.candidateName?.message}>
          <input {...register('candidateName')} className={inputCls} placeholder="Jane Smith" />
        </Field>
        <Field label="Candidate Email" error={errors.candidateEmail?.message}>
          <input {...register('candidateEmail')} type="email" className={inputCls} placeholder="jane@example.com" />
        </Field>
        <Field label="Phone (optional)" error={errors.candidatePhone?.message}>
          <input {...register('candidatePhone')} className={inputCls} placeholder="+1 555 000 0000" />
        </Field>
        <Field label="Department" error={errors.department?.message}>
          <input {...register('department')} className={inputCls} placeholder="Engineering" />
        </Field>

        {createReferral.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-sm text-red-700">
            {(createReferral.error as Error).message}
          </div>
        )}

        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting || createReferral.isPending}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-lg px-4 py-2 text-sm transition-colors"
          >
            {createReferral.isPending ? 'Submitting…' : 'Submit Referral'}
          </button>
        </div>
      </form>
    </div>
  );
}
