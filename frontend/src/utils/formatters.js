/**
 * SetuX — Official Data Formatters
 * Formats currencies, dates, progress metrics, and status badges.
 */

/**
 * Formats a budget value provided in Lakhs into appropriate Indian denomination.
 * e.g., 1500.0 Lakhs -> ₹15.00 Cr, 45.5 Lakhs -> ₹45.50 Lakh
 */
export function formatLakhs(valueInLakhs) {
  if (valueInLakhs === null || valueInLakhs === undefined || isNaN(valueInLakhs)) {
    return '—';
  }
  const num = Number(valueInLakhs);
  if (num === 0) return '₹0.00 Lakh';

  if (num >= 100) {
    const cr = num / 100;
    return `₹${cr.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} Cr`;
  }
  return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} Lakh`;
}

/**
 * Formats ISO / YYYY-MM-DD date strings into human-readable Indian format.
 * e.g., "2026-03-15" -> "15 Mar 2026"
 */
export function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return String(dateStr);
    return d.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return String(dateStr);
  }
}

/**
 * Formats progress percentage between 0% and 100%.
 */
export function formatProgress(val) {
  if (val === null || val === undefined || isNaN(val)) return '0%';
  const num = Math.min(100, Math.max(0, Number(val)));
  return `${Math.round(num)}%`;
}

/**
 * Returns restrained semantic badge styling based on project status.
 */
export function getStatusBadgeStyle(status) {
  const s = (status || '').toLowerCase().trim();
  switch (s) {
    case 'completed':
    case 'verified':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    case 'in progress':
    case 'ongoing':
    case 'active':
      return 'bg-blue-50 text-[#1769D2] border-blue-200';
    case 'review required':
    case 'under review':
    case 'pending':
      return 'bg-amber-50 text-amber-800 border-amber-200';
    case 'delayed':
    case 'high risk':
    case 'critical':
      return 'bg-red-50 text-red-700 border-red-200';
    default:
      return 'bg-gray-50 text-gray-700 border-gray-200';
  }
}

/**
 * Returns restrained semantic badge styling for milestones.
 */
export function getMilestoneStatusStyle(status) {
  const s = (status || '').toUpperCase().trim();
  switch (s) {
    case 'COMPLETED':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    case 'IN_PROGRESS':
      return 'bg-blue-50 text-[#1769D2] border-blue-200';
    case 'DELAYED':
      return 'bg-red-50 text-red-700 border-red-200';
    case 'PENDING':
    case 'NOT_STARTED':
    default:
      return 'bg-gray-100 text-gray-700 border-gray-200';
  }
}
