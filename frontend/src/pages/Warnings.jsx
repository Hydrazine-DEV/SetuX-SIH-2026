import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  RefreshCw,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  Eye,
  Clock,
  ShieldAlert,
  Loader2,
  ArrowUpRight,
  Zap,
  Info,
  CheckCheck,
  Building2,
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import { alertsApi } from '../services/api';
import { formatDate } from '../utils/formatters';

/* ─── Severity Badges & Colors ────────────────────────────────────── */
const SEVERITY_STYLE = {
  CRITICAL: {
    bg: 'bg-red-100',
    border: 'border-red-300',
    text: 'text-red-900',
    dot: 'bg-red-700',
    badge: 'bg-red-100 text-red-900 border-red-300',
  },
  HIGH: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-700',
    dot: 'bg-red-500',
    badge: 'bg-red-50 text-red-700 border-red-200',
  },
  MEDIUM: {
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-700',
    dot: 'bg-amber-500',
    badge: 'bg-amber-50 text-amber-700 border-amber-200',
  },
  LOW: {
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    text: 'text-emerald-700',
    dot: 'bg-emerald-500',
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
};

/* ─── Status Badges ────────────────────────────────────────────────── */
const STATUS_STYLE = {
  UNREAD: 'bg-blue-50 dark:bg-blue-950/40 text-blue-700 border-blue-200',
  READ: 'bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-slate-300 border-gray-200 dark:border-slate-700',
  RESOLVED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  DISMISSED: 'bg-gray-50 dark:bg-slate-800/50 text-gray-500 dark:text-slate-400 border-gray-200 dark:border-slate-700',
};

/* ─── Source Badges ────────────────────────────────────────────────── */
const SOURCE_STYLE = {
  RULE_ENGINE: 'bg-blue-50 dark:bg-blue-950/40 text-blue-800 border-blue-200',
  COST_PREDICTOR: 'bg-purple-50 text-purple-800 border-purple-200',
  TIME_PREDICTOR: 'bg-purple-50 text-purple-800 border-purple-200',
  SYSTEM: 'bg-gray-50 dark:bg-slate-800/50 text-gray-700 dark:text-slate-300 border-gray-200 dark:border-slate-700',
};

function formatAlertTypeName(type) {
  if (!type) return 'ALERT';
  return type
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function Warnings() {
  const [alerts, setAlerts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null);

  // Filters
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [alertTypeFilter, setAlertTypeFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Pagination
  const [page, setPage] = useState(1);
  const limit = 50;

  // ─── Fetch Alerts ─────────────────────────────────────────────────
  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page, limit };
      if (severityFilter) params.severity = severityFilter;
      if (statusFilter) params.status = statusFilter;
      if (alertTypeFilter) params.alert_type = alertTypeFilter;

      const res = await alertsApi.list(params);
      const data = res.data;
      if (data && Array.isArray(data.items)) {
        setAlerts(data.items);
        setTotal(data.total || data.items.length);
      } else if (Array.isArray(data)) {
        setAlerts(data);
        setTotal(data.length);
      } else {
        setAlerts([]);
        setTotal(0);
      }
    } catch (err) {
      setError(
        err.response?.status === 401
          ? 'Authentication required to view early warning alerts.'
          : 'Unable to load early warning alerts from backend.'
      );
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  }, [page, limit, severityFilter, statusFilter, alertTypeFilter]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  // ─── Trigger Bulk Alert Generation ───────────────────────────────
  const handleBulkGenerate = async () => {
    setGenerating(true);
    setNotification(null);
    try {
      const res = await alertsApi.generateAll();
      const count = res.data?.total_generated_alerts || res.data?.generated_count || 0;
      setNotification({
        type: 'success',
        message: `Alert evaluation complete! Generated/refreshed ${count} alert(s) across monitored projects.`,
      });
      fetchAlerts();
    } catch (err) {
      setNotification({
        type: 'error',
        message: 'Failed to trigger bulk alert generation. Officer privileges required.',
      });
    } finally {
      setGenerating(false);
    }
  };

  // ─── Alert Actions ────────────────────────────────────────────────
  const handleMarkRead = async (alertId) => {
    try {
      await alertsApi.markRead(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, status: 'READ', is_read: true } : a))
      );
    } catch (err) {
      // silent fallback
    }
  };

  const handleResolve = async (alertId) => {
    try {
      await alertsApi.markResolved(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, status: 'RESOLVED' } : a))
      );
      setNotification({ type: 'success', message: `Alert #${alertId} marked as RESOLVED.` });
    } catch (err) {
      setNotification({ type: 'error', message: `Failed to resolve alert #${alertId}.` });
    }
  };

  const handleDismiss = async (alertId) => {
    try {
      await alertsApi.markDismissed(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, status: 'DISMISSED' } : a))
      );
      setNotification({ type: 'success', message: `Alert #${alertId} marked as DISMISSED.` });
    } catch (err) {
      setNotification({ type: 'error', message: `Failed to dismiss alert #${alertId}.` });
    }
  };

  // ─── Filtered Alerts (Client Search) ──────────────────────────────
  const filteredAlerts = alerts.filter((a) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const title = (a.title || '').toLowerCase();
    const msg = (a.message || '').toLowerCase();
    const pCode = (a.project_code || `id-${a.project_id}`).toLowerCase();
    const type = (a.alert_type || '').toLowerCase();
    return title.includes(q) || msg.includes(q) || pCode.includes(q) || type.includes(q);
  });

  return (
    <div className="min-h-full pb-12">
      <PageHeader
        title="Early Warning Intelligence Center"
        subtitle="Automated threshold monitoring, ML risk signals, and executive bottleneck alerts."
        badge="Early Warnings"
        breadcrumbs={['SetuX', 'Early Warnings']}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        
        {/* Top Control Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 p-4 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-[#EAF3FF] dark:bg-blue-950/40 text-[#1769D2] rounded-xl flex items-center justify-center border border-blue-100">
              <Zap size={20} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-[#14213D] dark:text-slate-100">Project Bottleneck & Risk Warnings</h2>
              <p className="text-xs text-[#64748B] dark:text-slate-400">Real-time database and ML model alert notifications</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleBulkGenerate}
              disabled={generating}
              className="inline-flex items-center space-x-1.5 bg-[#1769D2] hover:bg-[#1459b8] text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-60"
            >
              {generating ? (
                <Loader2 size={13} className="animate-spin" />
              ) : (
                <Zap size={13} />
              )}
              <span>{generating ? 'Evaluating Risks...' : 'Run All Alert Models'}</span>
            </button>

            <button
              type="button"
              onClick={fetchAlerts}
              disabled={loading}
              className="p-2 rounded-lg text-gray-500 dark:text-slate-400 hover:text-gray-900 bg-gray-50 dark:bg-slate-800/50 hover:bg-gray-100 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 transition"
              title="Refresh alert list"
            >
              <RefreshCw size={14} className={loading ? 'animate-spin text-[#1769D2]' : ''} />
            </button>
          </div>
        </div>

        {/* Notification Toast */}
        {notification && (
          <div className={`p-4 rounded-xl border flex items-center justify-between text-xs ${
            notification.type === 'success' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-red-50 text-red-800 border-red-200'
          }`}>
            <div className="flex items-center space-x-2">
              {notification.type === 'success' ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
              <span className="font-semibold">{notification.message}</span>
            </div>
            <button type="button" onClick={() => setNotification(null)} className="font-bold underline ml-4">
              Dismiss
            </button>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-4 shadow-sm grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search title, code, message..."
              className="w-full pl-9 pr-3 py-2 text-xs border border-gray-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1769D2] text-[#14213D] dark:text-slate-100"
            />
          </div>

          <div>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-gray-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1769D2] text-[#14213D] dark:text-slate-100 bg-white dark:bg-slate-900"
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical Severity</option>
              <option value="HIGH">High Severity</option>
              <option value="MEDIUM">Medium Severity</option>
              <option value="LOW">Low Severity</option>
            </select>
          </div>

          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-gray-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1769D2] text-[#14213D] dark:text-slate-100 bg-white dark:bg-slate-900"
            >
              <option value="">All Statuses</option>
              <option value="UNREAD">Unread</option>
              <option value="READ">Read</option>
              <option value="RESOLVED">Resolved</option>
              <option value="DISMISSED">Dismissed</option>
            </select>
          </div>

          <div>
            <select
              value={alertTypeFilter}
              onChange={(e) => setAlertTypeFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-gray-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1769D2] text-[#14213D] dark:text-slate-100 bg-white dark:bg-slate-900"
            >
              <option value="">All Alert Types</option>
              <option value="SCHEDULE_DELAY">Schedule Delay</option>
              <option value="COST_OVERRUN">Cost Overrun</option>
              <option value="LOW_PROGRESS">Low Progress</option>
              <option value="MILESTONE_DELAY">Milestone Delay</option>
              <option value="CRITICAL_ISSUE">Critical Issue</option>
              <option value="PREDICTIVE_COST_OVERRUN">Predictive Cost ML</option>
              <option value="PREDICTIVE_TIME_OVERRUN">Predictive Time ML</option>
            </select>
          </div>
        </div>

        {/* Alerts Content */}
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-5 space-y-3 animate-pulse">
                <div className="flex justify-between items-center">
                  <div className="h-4 bg-gray-100 dark:bg-slate-800 rounded w-48" />
                  <div className="h-4 bg-gray-100 dark:bg-slate-800 rounded w-20" />
                </div>
                <div className="h-3 bg-gray-100 dark:bg-slate-800 rounded w-full" />
                <div className="h-3 bg-gray-100 dark:bg-slate-800 rounded w-3/4" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-8 text-center space-y-4">
            <div className="w-12 h-12 bg-red-50 text-red-500 rounded-xl flex items-center justify-center mx-auto border border-red-200">
              <AlertTriangle size={24} />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#14213D] dark:text-slate-100">Unable to Load Early Warnings</h3>
              <p className="text-xs text-red-600 mt-1 max-w-md mx-auto">{error}</p>
            </div>
            <button
              type="button"
              onClick={fetchAlerts}
              className="inline-flex items-center space-x-1.5 bg-[#1769D2] text-white px-4 py-2 rounded-lg text-xs font-semibold hover:bg-[#1459b8] transition"
            >
              <RefreshCw size={13} />
              <span>Retry</span>
            </button>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-10 text-center space-y-4">
            <div className="w-14 h-14 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center mx-auto border border-emerald-100">
              <CheckCheck size={28} />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#14213D] dark:text-slate-100">No Early Warnings Found</h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400 mt-1 max-w-md mx-auto">
                No active bottleneck alerts match your current filter parameters. You can trigger a new risk evaluation scan anytime.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredAlerts.map((alert) => {
              const sev = SEVERITY_STYLE[alert.severity] || SEVERITY_STYLE.LOW;
              const statusBadge = STATUS_STYLE[alert.status] || STATUS_STYLE.UNREAD;
              const sourceBadge = SOURCE_STYLE[alert.source] || SOURCE_STYLE.SYSTEM;
              const meta = alert.metadata || {};

              return (
                <div
                  key={alert.id}
                  className={`bg-white dark:bg-slate-900 rounded-2xl border transition-all duration-200 shadow-sm hover:shadow-sm p-5 space-y-3 ${
                    alert.status === 'UNREAD' ? 'border-l-4 border-l-[#1769D2] border-gray-200 dark:border-slate-700' : 'border-gray-200 dark:border-slate-700 opacity-90'
                  }`}
                >
                  {/* Top Bar */}
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${sev.badge}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${sev.dot}`} />
                        <span>{alert.severity}</span>
                      </span>

                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${statusBadge}`}>
                        {alert.status}
                      </span>

                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${sourceBadge}`}>
                        {alert.source}
                      </span>

                      <span className="text-xs font-mono font-bold text-[#1769D2]">
                        Project ID #{alert.project_id}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 text-[11px] text-[#64748B] dark:text-slate-400">
                      <Clock size={12} />
                      <span>{formatDate(alert.created_at)}</span>
                    </div>
                  </div>

                  {/* Body */}
                  <div>
                    <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2">
                      <span>{alert.title}</span>
                      {alert.risk_score > 0 && (
                        <span className="text-[10px] font-mono font-bold text-red-600 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                          +{alert.risk_score} Risk Impact
                        </span>
                      )}
                    </h3>
                    <p className="text-xs text-[#64748B] dark:text-slate-400 mt-1 leading-relaxed">{alert.message}</p>
                  </div>

                  {/* Metadata / Explanation / Recommendation */}
                  {(meta.explanation || meta.recommendation || meta.reasons) && (
                    <div className="bg-[#F5F7FA] dark:bg-slate-800 p-3 rounded-xl border border-gray-200 dark:border-slate-700 space-y-1.5 text-xs">
                      {meta.explanation && (
                        <div className="flex items-start space-x-2 text-[#14213D] dark:text-slate-100">
                          <Info size={14} className="text-[#1769D2] shrink-0 mt-0.5" />
                          <span><strong className="font-semibold">Details:</strong> {meta.explanation}</span>
                        </div>
                      )}
                      {meta.recommendation && (
                        <div className="flex items-start space-x-2 text-emerald-800">
                          <CheckCircle2 size={14} className="text-emerald-600 shrink-0 mt-0.5" />
                          <span><strong className="font-semibold">Action:</strong> {meta.recommendation}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Actions Bar */}
                  <div className="flex flex-wrap items-center justify-between pt-2 border-t border-gray-100 dark:border-slate-800 gap-2">
                    <div className="flex items-center space-x-2">
                      {alert.status === 'UNREAD' && (
                        <button
                          type="button"
                          onClick={() => handleMarkRead(alert.id)}
                          className="inline-flex items-center space-x-1 text-xs text-[#1769D2] font-semibold hover:underline"
                        >
                          <Eye size={12} />
                          <span>Mark Read</span>
                        </button>
                      )}

                      {alert.status !== 'RESOLVED' && (
                        <button
                          type="button"
                          onClick={() => handleResolve(alert.id)}
                          className="inline-flex items-center space-x-1 text-xs text-emerald-700 font-semibold hover:underline bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200"
                        >
                          <CheckCircle2 size={12} />
                          <span>Resolve</span>
                        </button>
                      )}

                      {alert.status !== 'DISMISSED' && alert.status !== 'RESOLVED' && (
                        <button
                          type="button"
                          onClick={() => handleDismiss(alert.id)}
                          className="inline-flex items-center space-x-1 text-xs text-gray-600 hover:text-gray-900 font-semibold hover:underline"
                        >
                          <XCircle size={12} />
                          <span>Dismiss</span>
                        </button>
                      )}
                    </div>

                    <Link
                      to={`/projects/${alert.project_id}`}
                      onClick={() => handleMarkRead(alert.id)}
                      className="inline-flex items-center space-x-1 text-xs font-semibold text-[#1769D2] bg-white dark:bg-slate-900 hover:bg-[#EAF3FF] dark:bg-blue-950/40 px-3 py-1 rounded-lg border border-blue-200 transition"
                    >
                      <span>View Project Details</span>
                      <ArrowUpRight size={12} />
                    </Link>
                  </div>

                </div>
              );
            })}
          </div>
        )}

      </div>
    </div>
  );
}
