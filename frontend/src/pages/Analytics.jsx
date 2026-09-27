import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  Building2,
  MapPin,
  RefreshCw,
  Loader2,
  ShieldAlert,
  ArrowUpRight,
  PieChart as PieChartIcon,
  Layers,
  FileWarning,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from 'recharts';
import PageHeader from '../components/common/PageHeader';
import { analyticsApi } from '../services/api';

/* ─── Color Palette for Charts (SetuX Theme) ──────────────────────── */
const SETUX_COLORS = {
  navy: '#0B2A4A',
  blue: '#1769D2',
  lightBlue: '#3B82F6',
  emerald: '#10B981',
  amber: '#F59E0B',
  red: '#EF4444',
  purple: '#8B5CF6',
  gray: '#64748B',
};

const STATUS_PIE_COLORS = [
  '#10B981', // Verified / Completed - Emerald
  '#1769D2', // Review Required - Government Blue
  '#F59E0B', // Delayed - Amber
  '#EF4444', // High Risk - Red
  '#8B5CF6', // Completed / Other - Purple
];

/* ─── Custom Tooltip Component ──────────────────────────────────────── */
function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#0B2A4A] text-white p-3 rounded-xl shadow-lg text-xs space-y-1 border border-navy-800">
        <p className="font-bold border-b border-gray-700 pb-1">{label}</p>
        {payload.map((entry, index) => (
          <div key={`item-${index}`} className="flex items-center justify-between space-x-4">
            <span style={{ color: entry.color || '#fff' }} className="font-semibold">
              {entry.name}:
            </span>
            <span className="font-mono font-bold">{entry.value}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [districts, setDistricts] = useState([]);
  const [trends, setTrends] = useState(null);
  const [priority, setPriority] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ─── Fetch Analytics Data ─────────────────────────────────────────
  const fetchAnalyticsData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryRes, districtsRes, trendsRes, priorityRes] = await Promise.allSettled([
        analyticsApi.getSummary(),
        analyticsApi.getDistricts(),
        analyticsApi.getTrends(),
        analyticsApi.getPriority(),
      ]);

      if (summaryRes.status === 'fulfilled') {
        setSummary(summaryRes.value.data);
      }
      if (districtsRes.status === 'fulfilled') {
        setDistricts(Array.isArray(districtsRes.value.data) ? districtsRes.value.data : []);
      }
      if (trendsRes.status === 'fulfilled') {
        setTrends(trendsRes.value.data);
      }
      if (priorityRes.status === 'fulfilled') {
        setPriority(Array.isArray(priorityRes.value.data) ? priorityRes.value.data : []);
      }

      if (
        summaryRes.status === 'rejected' &&
        districtsRes.status === 'rejected'
      ) {
        setError('Unable to load backend analytics endpoints. Please verify server connection.');
      }
    } catch (err) {
      setError('An unexpected error occurred while fetching analytics data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalyticsData();
  }, [fetchAnalyticsData]);

  // ─── Derived Status Data for Chart ────────────────────────────────
  const statusPieData = summary
    ? [
        { name: 'Verified', value: summary.verified || 0 },
        { name: 'Review Required', value: summary.review_required || 0 },
        { name: 'Delayed', value: summary.delayed || 0 },
        { name: 'High Risk', value: summary.high_risk || 0 },
        { name: 'Completed', value: summary.completed || 0 },
      ].filter((d) => d.value > 0)
    : [];

  return (
    <div className="min-h-full pb-12">
      <PageHeader
        title="Analytics & Project Intelligence"
        subtitle="Cross-departmental budget utilization, district performance, and risk metrics derived from live backend databases."
        badge="Phase 7"
        breadcrumbs={['SetuX', 'Analytics']}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        
        {/* Controls Bar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <BarChart3 size={18} className="text-[#1769D2]" />
            <h2 className="text-base font-bold text-[#14213D] dark:text-slate-100">Infrastructure Command Analytics</h2>
          </div>
          <button
            type="button"
            onClick={fetchAnalyticsData}
            disabled={loading}
            className="inline-flex items-center space-x-1.5 bg-white dark:bg-slate-900 hover:bg-gray-50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700 text-[#14213D] dark:text-slate-100 px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-sm transition"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin text-[#1769D2]' : 'text-gray-500 dark:text-slate-400'} />
            <span>Refresh Analytics</span>
          </button>
        </div>

        {/* Loading State */}
        {loading ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-5 animate-pulse space-y-3">
                  <div className="h-4 bg-gray-100 dark:bg-slate-800 rounded w-24" />
                  <div className="h-8 bg-gray-100 dark:bg-slate-800 rounded w-16" />
                </div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 h-80 animate-pulse flex items-center justify-center">
                <Loader2 size={24} className="text-[#1769D2] animate-spin" />
              </div>
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 h-80 animate-pulse flex items-center justify-center">
                <Loader2 size={24} className="text-[#1769D2] animate-spin" />
              </div>
            </div>
          </div>
        ) : error ? (
          /* Error State */
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-8 text-center space-y-4">
            <div className="w-12 h-12 bg-red-50 text-red-500 rounded-xl flex items-center justify-center mx-auto border border-red-200">
              <AlertTriangle size={24} />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#14213D] dark:text-slate-100">Analytics Unavailable</h3>
              <p className="text-xs text-red-600 mt-1 max-w-md mx-auto">{error}</p>
            </div>
            <button
              type="button"
              onClick={fetchAnalyticsData}
              className="inline-flex items-center space-x-1.5 bg-[#1769D2] text-white px-4 py-2 rounded-lg text-xs font-semibold hover:bg-[#1459b8] transition"
            >
              <RefreshCw size={13} />
              <span>Retry Connection</span>
            </button>
          </div>
        ) : !summary && districts.length === 0 ? (
          /* Empty State */
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-10 text-center space-y-4">
            <div className="w-14 h-14 bg-[#EAF3FF] dark:bg-blue-950/40 text-[#1769D2] rounded-2xl flex items-center justify-center mx-auto border border-blue-100">
              <BarChart3 size={28} />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#14213D] dark:text-slate-100">No Infrastructure Analytics Data</h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400 mt-1 max-w-md mx-auto">
                No active projects or district metrics are available in the backend database.
              </p>
            </div>
          </div>
        ) : (
          /* ─── REAL BACKEND ANALYTICS CONTENT ───────────────────────────── */
          <div className="space-y-6">

            {/* Top KPI Cards */}
            {summary && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-5 shadow-sm">
                  <div className="flex items-center justify-between text-[#64748B] dark:text-slate-400">
                    <span className="text-xs font-bold uppercase tracking-wider">Total Projects</span>
                    <Building2 size={16} className="text-[#1769D2]" />
                  </div>
                  <div className="mt-3 flex items-baseline justify-between">
                    <span className="text-2xl font-bold font-mono text-[#14213D] dark:text-slate-100">{summary.total_projects}</span>
                    <span className="text-[11px] text-[#64748B] dark:text-slate-400">monitored state assets</span>
                  </div>
                </div>

                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-5 shadow-sm">
                  <div className="flex items-center justify-between text-[#64748B] dark:text-slate-400">
                    <span className="text-xs font-bold uppercase tracking-wider">High Risk / Delayed</span>
                    <ShieldAlert size={16} className="text-red-500" />
                  </div>
                  <div className="mt-3 flex items-baseline justify-between">
                    <div className="flex items-baseline space-x-2">
                      <span className="text-2xl font-bold font-mono text-red-600">
                        {(summary.high_risk || 0) + (summary.delayed || 0)}
                      </span>
                      <span className="text-xs text-[#64748B] dark:text-slate-400">
                        ({summary.high_risk || 0} high risk, {summary.delayed || 0} delayed)
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-5 shadow-sm">
                  <div className="flex items-center justify-between text-[#64748B] dark:text-slate-400">
                    <span className="text-xs font-bold uppercase tracking-wider">Reported vs AI Gap</span>
                    <TrendingUp size={16} className="text-amber-500" />
                  </div>
                  <div className="mt-3 flex items-baseline justify-between">
                    <span className="text-2xl font-bold font-mono text-[#14213D] dark:text-slate-100">
                      {Math.abs((summary.avg_reported_progress || 0) - (summary.avg_ai_estimated_progress || 0)).toFixed(1)}%
                    </span>
                    <span className="text-[11px] text-[#64748B] dark:text-slate-400">
                      {summary.avg_reported_progress}% rep / {summary.avg_ai_estimated_progress}% est
                    </span>
                  </div>
                </div>

                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-5 shadow-sm">
                  <div className="flex items-center justify-between text-[#64748B] dark:text-slate-400">
                    <span className="text-xs font-bold uppercase tracking-wider">Inspection Rate</span>
                    <AlertTriangle size={16} className="text-purple-600" />
                  </div>
                  <div className="mt-3 flex items-baseline justify-between">
                    <span className="text-2xl font-bold font-mono text-[#14213D] dark:text-slate-100">{summary.inspection_rate}%</span>
                    <span className="text-[11px] text-[#64748B] dark:text-slate-400">flagged for review</span>
                  </div>
                </div>
              </div>
            )}

            {/* Row 1: Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              
              {/* Project Status Distribution */}
              {statusPieData.length > 0 && (
                <div className="lg:col-span-5 bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 p-6 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
                    <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2">
                      <PieChartIcon size={16} className="text-[#1769D2]" />
                      <span>Project Status Distribution</span>
                    </h3>
                  </div>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={statusPieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={90}
                          paddingAngle={3}
                          dataKey="value"
                        >
                          {statusPieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={STATUS_PIE_COLORS[index % STATUS_PIE_COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* District Infrastructure & Risk Breakdown */}
              {districts.length > 0 && (
                <div className={`${statusPieData.length > 0 ? 'lg:col-span-7' : 'lg:col-span-12'} bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 p-6 shadow-sm space-y-4`}>
                  <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
                    <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2">
                      <MapPin size={16} className="text-[#1769D2]" />
                      <span>District Infrastructure & Risk Distribution</span>
                    </h3>
                  </div>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={districts} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <XAxis dataKey="district" tick={{ fontSize: 11, fill: '#64748B' }} />
                        <YAxis tick={{ fontSize: 11, fill: '#64748B' }} allowDecimals={false} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend verticalAlign="top" wrapperStyle={{ fontSize: '11px' }} />
                        <Bar dataKey="total" name="Total Projects" fill={SETUX_COLORS.blue} radius={[4, 4, 0, 0]} />
                        <Bar dataKey="high_risk" name="High Risk Projects" fill={SETUX_COLORS.red} radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>

            {/* Row 2: District Progress Gap & Sector/Trend Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              
              {/* District Progress Gap Chart */}
              {districts.length > 0 && (
                <div className="lg:col-span-6 bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 p-6 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
                    <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2">
                      <TrendingUp size={16} className="text-amber-500" />
                      <span>Average Progress Discrepancy by District (%)</span>
                    </h3>
                  </div>
                  <div className="h-60">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={districts} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <XAxis dataKey="district" tick={{ fontSize: 11, fill: '#64748B' }} />
                        <YAxis tick={{ fontSize: 11, fill: '#64748B' }} unit="%" />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar dataKey="avg_progress_gap" name="Avg Reported vs AI Gap (%)" fill={SETUX_COLORS.amber} radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Monthly Trend or Sector Distribution */}
              {trends && (trends.monthly_trend || trends.type_distribution) && (
                <div className="lg:col-span-6 bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 p-6 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
                    <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2">
                      <Layers size={16} className="text-[#1769D2]" />
                      <span>{trends.monthly_trend ? 'Completion Trend (Reported vs AI)' : 'Sector Project Breakdown'}</span>
                    </h3>
                  </div>
                  <div className="h-60">
                    <ResponsiveContainer width="100%" height="100%">
                      {trends.monthly_trend ? (
                        <AreaChart data={trends.monthly_trend} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                          <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748B' }} />
                          <YAxis tick={{ fontSize: 11, fill: '#64748B' }} unit="%" />
                          <Tooltip content={<CustomTooltip />} />
                          <Legend verticalAlign="top" wrapperStyle={{ fontSize: '11px' }} />
                          <Area type="monotone" dataKey="reported" name="Reported Progress %" stroke={SETUX_COLORS.blue} fill={SETUX_COLORS.blue} fillOpacity={0.15} />
                          <Area type="monotone" dataKey="ai_estimated" name="AI Estimated %" stroke={SETUX_COLORS.emerald} fill={SETUX_COLORS.emerald} fillOpacity={0.15} />
                        </AreaChart>
                      ) : (
                        <BarChart data={trends.type_distribution} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                          <XAxis dataKey="type" tick={{ fontSize: 10, fill: '#64748B' }} />
                          <YAxis tick={{ fontSize: 11, fill: '#64748B' }} />
                          <Tooltip content={<CustomTooltip />} />
                          <Bar dataKey="count" name="Project Count" fill={SETUX_COLORS.purple} radius={[4, 4, 0, 0]} />
                        </BarChart>
                      )}
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>

            {/* High Anomaly / Priority Inspection Callout Table */}
            {priority.length > 0 && (
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
                  <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2">
                    <FileWarning size={16} className="text-red-500" />
                    <span>Inspection Priority Callouts</span>
                  </h3>
                  <span className="text-[10px] font-bold text-[#64748B] dark:text-slate-400 bg-gray-50 dark:bg-slate-800/50 px-2 py-0.5 rounded border border-gray-200 dark:border-slate-700">
                    Top {priority.length} Flagged
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="bg-[#F5F7FA] dark:bg-slate-800 text-[#64748B] dark:text-slate-400 font-bold border-b border-gray-200 dark:border-slate-700">
                        <th className="py-2.5 px-3">Project Code</th>
                        <th className="py-2.5 px-3">Project Name</th>
                        <th className="py-2.5 px-3">District</th>
                        <th className="py-2.5 px-3 text-center">Reported vs AI</th>
                        <th className="py-2.5 px-3 text-center">Anomaly Score</th>
                        <th className="py-2.5 px-3">Inspection Reason</th>
                        <th className="py-2.5 px-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
                      {priority.map((p) => (
                        <tr key={p.project_id} className="hover:bg-[#EAF3FF] dark:bg-blue-950/40/40 transition-colors">
                          <td className="py-3 px-3 font-mono font-bold text-[#1769D2]">{p.project_id}</td>
                          <td className="py-3 px-3 font-semibold text-[#14213D] dark:text-slate-100 truncate max-w-[200px]">{p.name}</td>
                          <td className="py-3 px-3 text-[#64748B] dark:text-slate-400">{p.district || '—'}</td>
                          <td className="py-3 px-3 text-center font-mono">
                            <span className="text-[#14213D] dark:text-slate-100 font-bold">{p.reported_progress}%</span>
                            <span className="text-[#64748B] dark:text-slate-400 text-[10px] ml-1">/ {p.ai_estimated_progress}%</span>
                          </td>
                          <td className="py-3 px-3 text-center">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                              p.risk_score >= 75 ? 'bg-red-100 text-red-900 border-red-300' :
                              p.risk_score >= 50 ? 'bg-red-50 text-red-700 border-red-200' :
                              'bg-amber-50 text-amber-700 border-amber-200'
                            }`}>
                              {p.risk_score} / 100
                            </span>
                          </td>
                          <td className="py-3 px-3 text-[#64748B] dark:text-slate-400 text-[11px] max-w-[250px] truncate">{p.reason}</td>
                          <td className="py-3 px-3 text-right">
                            <Link
                              to="/risk"
                              className="inline-flex items-center space-x-1 text-[11px] font-bold text-[#1769D2] hover:underline"
                            >
                              <span>Risk Intel</span>
                              <ArrowUpRight size={12} />
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

          </div>
        )}
      </div>
    </div>
  );
}
