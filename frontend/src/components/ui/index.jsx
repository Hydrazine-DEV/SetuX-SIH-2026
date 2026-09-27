/**
 * SetuX — Reusable UI Components System
 */
import { ShieldCheck, AlertTriangle, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { STATUS_COLORS, RISK_COLORS, SCHEDULE_STATUS_COLORS } from '../../data/demoProjects';

// ─── Status Badge ────────────────────────────────────────────────
export function StatusBadge({ status }) {
  const colors = STATUS_COLORS[status] || STATUS_COLORS['Under Review'];
  return (
    <span className={`badge ${colors.bg} ${colors.text} border border-current/10`}>
      <span className={`w-1.5 h-1.5 rounded-full ${colors.dot}`} />
      {status}
    </span>
  );
}

// ─── Risk Badge ──────────────────────────────────────────────────
export function RiskBadge({ risk }) {
  const riskKey = (risk || 'LOW').toUpperCase();
  const config = {
    LOW: {
      bg: 'bg-green-100 dark:bg-green-950/60',
      text: 'text-green-800 dark:text-green-300',
      border: 'border-green-300/50 dark:border-green-800/60',
      icon: CheckCircle2,
      dot: 'bg-green-600',
    },
    MEDIUM: {
      bg: 'bg-amber-100 dark:bg-amber-950/60',
      text: 'text-amber-800 dark:text-amber-300',
      border: 'border-amber-300/50 dark:border-amber-800/60',
      icon: AlertTriangle,
      dot: 'bg-amber-600',
    },
    HIGH: {
      bg: 'bg-red-100 dark:bg-red-950/60',
      text: 'text-red-800 dark:text-red-300',
      border: 'border-red-300/50 dark:border-red-800/60',
      icon: ShieldAlert,
      dot: 'bg-red-600',
    },
    CRITICAL: {
      bg: 'bg-red-900/20 dark:bg-red-950/90',
      text: 'text-red-900 dark:text-red-200 font-bold',
      border: 'border-red-700/60 dark:border-red-600',
      icon: ShieldAlert,
      dot: 'bg-red-800',
    },
  };

  const current = config[riskKey] || config.LOW;
  const Icon = current.icon;

  return (
    <span className={`badge ${current.bg} ${current.text} border ${current.border} shadow-2xs`}>
      <Icon size={12} className="shrink-0" />
      <span>{riskKey} RISK</span>
    </span>
  );
}

// ─── Delay Badge ─────────────────────────────────────────────────
export function DelayBadge({ days }) {
  if (days <= 0) return null;
  return (
    <span className="badge bg-red-100 dark:bg-red-950/60 text-red-800 dark:text-red-300 border border-red-200 dark:border-red-800/60">
      <AlertTriangle size={12} className="shrink-0 text-red-600 dark:text-red-400" />
      <span>Delayed {days} days</span>
    </span>
  );
}

// ─── Schedule Status Badge ───────────────────────────────────────
export function ScheduleStatusBadge({ status }) {
  const colorClass = SCHEDULE_STATUS_COLORS[status] || "text-gray-700 dark:text-slate-300 bg-gray-100 dark:bg-slate-800";
  return (
    <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${colorClass} border border-current/10`}>
      {status}
    </span>
  );
}

// ─── Progress Bar ────────────────────────────────────────────────
export function ProgressBar({ value, color = 'blue', className = '' }) {
  const colors = {
    green: 'bg-[#16A34A]',
    amber: 'bg-[#D97706]',
    red: 'bg-[#DC2626]',
    blue: 'bg-[#1769D2]',
    saffron: 'bg-[#f97316]',
  };
  return (
    <div className={`progress-bar ${className}`}>
      <div
        className={`h-full rounded-full transition-all duration-700 ${colors[color] || 'bg-[#1769D2]'}`}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  );
}

// ─── KPI Card ────────────────────────────────────────────────────
export function KPICard({ title, value, subtitle, icon: Icon, color = 'blue', trend }) {
  const colorMap = {
    blue:    'bg-blue-50 dark:bg-blue-950/50 text-[#1769D2] dark:text-blue-400 border border-blue-200/50 dark:border-blue-800/40',
    green:   'bg-green-50 dark:bg-green-950/50 text-green-600 dark:text-green-400 border border-green-200/50 dark:border-green-800/40',
    amber:   'bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 border border-amber-200/50 dark:border-amber-800/40',
    red:     'bg-red-50 dark:bg-red-950/50 text-red-600 dark:text-red-400 border border-red-200/50 dark:border-red-800/40',
    saffron: 'bg-orange-50 dark:bg-orange-950/50 text-orange-600 dark:text-orange-400 border border-orange-200/50 dark:border-orange-800/40',
  };
  return (
    <div className="card p-5 flex items-start gap-4 transition-all">
      {Icon && (
        <div className={`p-3 rounded-2xl flex-shrink-0 ${colorMap[color] || colorMap.blue}`}>
          <Icon size={22} />
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className="text-2xl sm:text-3xl font-extrabold text-[#14213D] dark:text-slate-100 tabular-nums tracking-tight">
          {typeof value === 'number' ? value.toLocaleString('en-IN') : value}
        </div>
        <div className="text-sm font-semibold text-[#14213D] dark:text-slate-200 mt-0.5">{title}</div>
        {subtitle && <div className="text-xs text-[#64748B] dark:text-slate-400 mt-0.5">{subtitle}</div>}
        {trend && (
          <div className={`text-xs font-semibold mt-1.5 ${trend > 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
            {trend > 0 ? '▲' : '▼'} {Math.abs(trend)}% this month
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Empty State ─────────────────────────────────────────────────
export function EmptyState({ icon: Icon, title, description }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center px-4">
      {Icon && <Icon size={44} className="text-gray-300 dark:text-slate-600 mb-4 stroke-1" />}
      <div className="text-base font-bold text-[#14213D] dark:text-slate-200">{title}</div>
      {description && <div className="text-xs sm:text-sm text-[#64748B] dark:text-slate-400 mt-1 max-w-sm">{description}</div>}
    </div>
  );
}

// ─── Loading Spinner ─────────────────────────────────────────────
export function Spinner({ size = 'md' }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' };
  return (
    <div className={`animate-spin rounded-full border-2 border-gray-200 dark:border-slate-700 border-t-[#1769D2] ${sizes[size]}`} />
  );
}

// ─── Section Header ──────────────────────────────────────────────
export function SectionHeader({ title, subtitle, actions }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-6">
      <div>
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="text-sm text-[#64748B] dark:text-slate-400 mt-1">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2 flex-shrink-0">{actions}</div>}
    </div>
  );
}

// ─── Anomaly Gauge ──────────────────────────────────────────────
export function AnomalyGauge({ score }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color =
    score >= 75 ? '#dc2626' :
    score >= 50 ? '#d97706' :
    score >= 25 ? '#1769d2' : '#16a34a';
  const label =
    score >= 75 ? 'HIGH' :
    score >= 50 ? 'MEDIUM' :
    score >= 25 ? 'LOW' : 'MINIMAL';

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        <svg viewBox="0 0 130 130" className="w-36 h-36" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx="65" cy="65" r={radius} fill="none" className="stroke-gray-100 dark:stroke-slate-800" strokeWidth="14" />
          <circle
            cx="65" cy="65" r={radius}
            fill="none" stroke={color} strokeWidth="14"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1.2s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold text-[#14213D] dark:text-slate-100">{score}</span>
          <span className="text-xs text-[#64748B] dark:text-slate-400 font-medium">/100</span>
        </div>
      </div>
      <span
        className="text-xs font-extrabold px-3 py-1 rounded-full border border-current/20"
        style={{ background: `${color}18`, color }}
      >
        {label} RISK
      </span>
    </div>
  );
}

// ─── Project Health Score Gauge ──────────────────────────────────
export function HealthScoreGauge({ score }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color =
    score >= 80 ? '#16a34a' :
    score >= 50 ? '#d97706' : '#dc2626';
  const label =
    score >= 80 ? 'HEALTHY' :
    score >= 50 ? 'AT RISK' : 'CRITICAL';

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        <svg viewBox="0 0 130 130" className="w-36 h-36" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx="65" cy="65" r={radius} fill="none" className="stroke-gray-100 dark:stroke-slate-800" strokeWidth="14" />
          <circle
            cx="65" cy="65" r={radius}
            fill="none" stroke={color} strokeWidth="14"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1.2s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold text-[#14213D] dark:text-slate-100">{score}</span>
          <span className="text-xs text-[#64748B] dark:text-slate-400 font-medium">/100</span>
        </div>
      </div>
      <span
        className="text-xs font-extrabold px-3 py-1 rounded-full border border-current/20"
        style={{ background: `${color}18`, color }}
      >
        {label}
      </span>
    </div>
  );
}

// ─── Check Row ───────────────────────────────────────────────────
export function CheckRow({ label, value, status }) {
  const statusConfig = {
    ok:      { icon: '✓', color: 'text-green-700 dark:text-green-300', bg: 'bg-green-50 dark:bg-green-950/40 border-green-200 dark:border-green-900/40' },
    warning: { icon: '⚠', color: 'text-amber-700 dark:text-amber-300', bg: 'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-900/40' },
    error:   { icon: '✗', color: 'text-red-700 dark:text-red-300',   bg: 'bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-900/40' },
    info:    { icon: 'ℹ', color: 'text-blue-700 dark:text-blue-300',  bg: 'bg-blue-50 dark:bg-blue-950/40 border-blue-200 dark:border-blue-900/40' },
  };
  const cfg = statusConfig[status] || statusConfig.info;
  return (
    <div className={`flex items-center justify-between px-4 py-3 rounded-xl border ${cfg.bg}`}>
      <span className="text-xs sm:text-sm font-semibold text-[#14213D] dark:text-slate-200">{label}</span>
      <div className={`flex items-center gap-2 text-xs sm:text-sm font-bold ${cfg.color}`}>
        <span>{cfg.icon}</span>
        <span>{value}</span>
      </div>
    </div>
  );
}

