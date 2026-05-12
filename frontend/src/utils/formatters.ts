// ──────────────────────────────────────────────────────────────
//  Module: src/utils/formatters.ts
//  Responsibility: Display formatting helpers.
// ──────────────────────────────────────────────────────────────

/** Format ISO timestamp → "May 11, 2026 at 2:30 PM" */
export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

/** Format ISO date only → "May 11, 2026" */
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/** Format status enum slug → human-readable label */
export function formatStatus(status: string): string {
  return status
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/** Format confidence score → percentage string, e.g. "87%" */
export function formatConfidence(score: number): string {
  return `${Math.round(score * 100)}%`;
}

/** Format byte count → "4.2 MB" */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** Truncate long strings with ellipsis */
export function truncate(text: string, maxLen = 80): string {
  return text.length <= maxLen ? text : `${text.slice(0, maxLen)}…`;
}
