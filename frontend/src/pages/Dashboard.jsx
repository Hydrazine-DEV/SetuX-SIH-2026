import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  FolderKanban,
  ShieldAlert,
  AlertTriangle,
  BarChart3,
  Map,
  FileSpreadsheet,
  FileCheck2,
  Building2,
  ShieldCheck,
  ArrowRight,
  UserCheck,
  RefreshCw,
  Loader2,
  FileWarning,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import PageHeader from '../components/common/PageHeader';
import { analyticsApi, alertsApi } from '../services/api';
import { StatusBadge, RiskBadge } from '../components/ui';

export default function Dashboard() {
  const { user } = useAuth();

  const [summary, setSummary] = useState(null);
  const [priorityProjects, setPriorityProjects] = useState([]);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const officerName = user?.full_name || 'Department Officer';
  const officerDepartment = user?.department_name || user?.department?.name || 'Public Works Department';
  const officerDesignation = user?.designation || 'Department Official';
  const officerDistrict = user?.district || 'State Level';
  const officerId = user?.employee_id || `OFF-${user?.id || '2026'}`;

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const [summaryRes, priorityRes, alertsRes] = await Promise.allSettled([
        analyticsApi.getSummary(),
        analyticsApi.getPriority(),
        alertsApi.list({ limit: 5 }),
      ]);

      if (summaryRes.status === 'fulfilled') {
        setSummary(summaryRes.value.data);
      }
      if (priorityRes.status === 'fulfilled') {
        setPriorityProjects(Array.isArray(priorityRes.value.data) ? priorityRes.value.data.slice(0, 5) : []);
      }
      if (alertsRes.status === 'fulfilled') {
        const data = alertsRes.value.data;
        const alertsList = Array.isArray(data) ? data : data?.alerts || data?.items || [];
        setRecentAlerts(alertsList.slice(0, 4));
      }
    } catch {
      // Graceful fallback to structural UI
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const MODULE_CARDS = [
    {
      title: 'Infrastructure Projects',
      description: 'Explore the complete directory of state infrastructure projects with multi-criteria filtering and status tracking.',
      to: '/projects',
      icon: FolderKanban,
      actionText: 'View Projects',
      badge: 'Portfolio',
    },
    {
      title: 'Risk Intelligence',
      description: 'Predictive risk scoring, schedule and cost overrun machine learning classifiers, and anomaly evaluations.',
      to: '/risk',
      icon: ShieldAlert,
      actionText: 'Open Risk Models',
      badge: 'AI Detection',
    },
    {
      title: 'Early Warnings',
      description: 'Actionable early warning indicators and automated delay signals flagged for executive intervention.',
      to: '/warnings',
      icon: AlertTriangle,
      actionText: 'Inspect Warnings',
      badge: 'Alerts',
    },
    {
      title: 'Analytics & Intelligence',
      description: 'Comprehensive financial utilization, department-level comparisons, and milestone completion trends.',
      to: '/analytics',
      icon: BarChart3,
      actionText: 'Open Analytics',
      badge: 'Metrics',
    },
    {
      title: 'Geospatial Project Map',
      description: 'Interactive GIS mapping displaying project distribution, geo-tagged site evidence, and regional clustering.',
      to: '/map',
      icon: Map,
      actionText: 'Launch Map',
      badge: 'GIS Layer',
    },
    {
      title: 'Executive Reports & Audit',
      description: 'Deterministic executive PDF summaries, state audit trails, and immutable progress logs for official review.',
      to: '/reports',
      icon: FileSpreadsheet,
      actionText: 'Generate Reports',
      badge: 'Audit Trail',
    },
  ];

  return (
    <div className="min-h-full pb-12">
      {/* Page Header */}
      <PageHeader
        title="Officer Command Center"
        subtitle="Authorized departmental workspace for state infrastructure oversight, AI anomaly detection, and verification governance."
        badge="Official Portal"
        breadcrumbs={['SetuX', 'Command Center']}
      />

      {/* Main Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6 sm:space-y-8">
        
        {/* Officer Active Session Overview Card */}
        <div className="bg-[#0B2A4A] dark:bg-[#050E1A] text-white rounded-2xl p-6 sm:p-8 shadow-sm border border-navy-800 dark:border-slate-800 relative overflow-hidden transition-colors">
          <div className="absolute inset-0 bg-gradient-to-r from-[#0B2A4A] via-[#103761] to-[#1769D2]/30 dark:from-[#050E1A] dark:via-[#0B1B2D] dark:to-[#1769D2]/20 opacity-90 z-0"></div>

          <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            
            {/* Left Info */}
            <div className="space-y-2 max-w-2xl">
              <div className="inline-flex items-center space-x-2 bg-blue-500/20 text-blue-200 border border-blue-400/30 px-3 py-1 rounded-full text-xs font-semibold">
                <ShieldCheck size={14} className="text-blue-400" />
                <span>Authenticated Officer Workspace</span>
              </div>

              <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                Welcome back, {officerName}
              </h2>

              <p className="text-xs sm:text-sm text-gray-300 dark:text-slate-300 leading-relaxed">
                You are authenticated as an authorized department officer. Real-time project records, AI visual verification models, early warnings, and executive reporting are accessible through the command modules below.
              </p>
            </div>

            {/* Right Officer Metadata Grid */}
            <div className="grid grid-cols-2 gap-3 sm:gap-4 bg-white/10 dark:bg-black/40 backdrop-blur-xs p-4 rounded-xl border border-white/10 dark:border-slate-800 shrink-0 text-xs">
              <div className="space-y-0.5">
                <span className="text-[10px] text-gray-300 dark:text-slate-400 uppercase tracking-wider block">Department</span>
                <span className="font-semibold text-white truncate block">{officerDepartment}</span>
              </div>

              <div className="space-y-0.5">
                <span className="text-[10px] text-gray-300 dark:text-slate-400 uppercase tracking-wider block">Designation</span>
                <span className="font-semibold text-white truncate block">{officerDesignation}</span>
              </div>

              <div className="space-y-0.5">
                <span className="text-[10px] text-gray-300 dark:text-slate-400 uppercase tracking-wider block">Jurisdiction</span>
                <span className="font-semibold text-white truncate block">{officerDistrict}, Maharashtra</span>
              </div>

              <div className="space-y-0.5">
                <span className="text-[10px] text-gray-300 dark:text-slate-400 uppercase tracking-wider block">Officer ID</span>
                <span className="font-mono text-blue-200 dark:text-blue-400 truncate block">{officerId}</span>
              </div>
            </div>

          </div>
        </div>

        {/* Real Backend Portfolio Metrics Overview (if available) */}
        {summary && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-[#64748B] dark:text-slate-400">
                Portfolio Overview Metrics
              </h3>
              <button
                type="button"
                onClick={fetchDashboardData}
                disabled={loading}
                className="text-xs text-[#1769D2] hover:underline flex items-center space-x-1 font-semibold"
              >
                <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                <span>Sync Live Data</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="card p-5">
                <div className="flex items-center justify-between text-[#64748B] dark:text-slate-400">
                  <span className="text-xs font-bold uppercase tracking-wider">Total Projects</span>
                  <Building2 size={16} className="text-[#1769D2] dark:text-blue-400" />
                </div>
                <div className="mt-2 flex items-baseline justify-between">
                  <span className="text-2xl font-extrabold font-mono text-[#14213D] dark:text-slate-100">{summary.total_projects}</span>
                  <span className="text-xs text-[#64748B] dark:text-slate-400">monitored assets</span>
                </div>
              </div>

              <div className="card p-5">
                <div className="flex items-center justify-between text-[#64748B] dark:text-slate-400">
                  <span className="text-xs font-bold uppercase tracking-wider">High Risk / Delayed</span>
                  <ShieldAlert size={16} className="text-red-500" />
                </div>
                <div className="mt-2 flex items-baseline justify-between">
                  <span className="text-2xl font-extrabold font-mono text-red-600 dark:text-red-400">
                    {(summary.high_risk || 0) + (summary.delayed || 0)}
                  </span>
                  <span className="text-xs text-[#64748B] dark:text-slate-400">
                    ({summary.high_risk || 0} risk, {summary.delayed || 0} delayed)
                  </span>
                </div>
              </div>

              <div className="card p-5">
                <div className="flex items-center justify-between text-[#64748B] dark:text-slate-400">
                  <span className="text-xs font-bold uppercase tracking-wider">Reported vs AI Gap</span>
                  <AlertTriangle size={16} className="text-amber-500" />
                </div>
                <div className="mt-2 flex items-baseline justify-between">
                  <span className="text-2xl font-extrabold font-mono text-[#14213D] dark:text-slate-100">
                    {Math.abs((summary.avg_reported_progress || 0) - (summary.avg_ai_estimated_progress || 0)).toFixed(1)}%
                  </span>
                  <span className="text-xs text-[#64748B] dark:text-slate-400">
                    {summary.avg_reported_progress}% rep / {summary.avg_ai_estimated_progress}% est
                  </span>
                </div>
              </div>

              <div className="card p-5">
                <div className="flex items-center justify-between text-[#64748B] dark:text-slate-400">
                  <span className="text-xs font-bold uppercase tracking-wider">Inspection Rate</span>
                  <FileCheck2 size={16} className="text-purple-600 dark:text-purple-400" />
                </div>
                <div className="mt-2 flex items-baseline justify-between">
                  <span className="text-2xl font-extrabold font-mono text-[#14213D] dark:text-slate-100">{summary.inspection_rate}%</span>
                  <span className="text-xs text-[#64748B] dark:text-slate-400">review required</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Priority Projects & Early Warnings Callout Section */}
        {(priorityProjects.length > 0 || recentAlerts.length > 0) && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Priority Inspection Projects */}
            {priorityProjects.length > 0 && (
              <div className={`${recentAlerts.length > 0 ? 'lg:col-span-7' : 'lg:col-span-12'} card p-6 space-y-4`}>
                <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
                  <div className="flex items-center space-x-2">
                    <FileWarning size={16} className="text-red-500" />
                    <h3 className="card-title">Projects Requiring Immediate Oversight</h3>
                  </div>
                  <Link to="/projects" className="text-xs font-bold text-[#1769D2] hover:underline">
                    View Portfolio →
                  </Link>
                </div>

                <div className="divide-y divide-gray-100 dark:divide-slate-800">
                  {priorityProjects.map((p) => (
                    <div key={p.project_id} className="py-3 flex items-center justify-between gap-3 hover:bg-gray-50/50 dark:hover:bg-slate-800/40 rounded-xl px-2 transition-colors">
                      <div className="min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono font-bold text-xs text-[#1769D2] dark:text-blue-400">{p.project_id}</span>
                          <span className="text-xs font-bold text-[#14213D] dark:text-slate-100 truncate">{p.name}</span>
                        </div>
                        <p className="text-[11px] text-[#64748B] dark:text-slate-400 truncate mt-0.5">{p.district} • {p.reason}</p>
                      </div>

                      <div className="flex items-center space-x-3 shrink-0">
                        <span className="text-xs font-mono font-bold text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/60 px-2 py-0.5 rounded-lg border border-red-200 dark:border-red-900/60">
                          {p.risk_score}/100
                        </span>
                        <Link to={`/projects/${p.project_id}`} className="text-xs font-semibold text-[#1769D2] hover:underline">
                          Inspect
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Early Warning Alerts */}
            {recentAlerts.length > 0 && (
              <div className={`${priorityProjects.length > 0 ? 'lg:col-span-5' : 'lg:col-span-12'} card p-6 space-y-4`}>
                <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle size={16} className="text-amber-500" />
                    <h3 className="card-title">Recent Early Warnings</h3>
                  </div>
                  <Link to="/warnings" className="text-xs font-bold text-[#1769D2] hover:underline">
                    All Warnings →
                  </Link>
                </div>

                <div className="space-y-2.5">
                  {recentAlerts.map((alert) => (
                    <div key={alert.id} className="p-3 bg-gray-50/80 dark:bg-[#10243A] rounded-xl border border-gray-200/60 dark:border-slate-700/60 space-y-1">
                      <div className="flex items-center justify-between">
                        <RiskBadge risk={alert.severity || 'MEDIUM'} />
                        <span className="text-[10px] text-[#64748B] dark:text-slate-400 font-mono">
                          {alert.created_at ? new Date(alert.created_at).toLocaleDateString('en-IN') : 'Recent'}
                        </span>
                      </div>
                      <p className="text-xs font-bold text-[#14213D] dark:text-slate-200 truncate">{alert.title || alert.alert_type}</p>
                      <p className="text-[11px] text-[#64748B] dark:text-slate-400 line-clamp-1">{alert.description || alert.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}

        {/* Command Center Modules Header */}
        <div className="flex items-center justify-between pt-2">
          <div>
            <h3 className="section-title">
              Department Command Modules
            </h3>
            <p className="text-xs text-[#64748B] dark:text-slate-400 mt-0.5">
              Select a specialized monitoring workspace to proceed.
            </p>
          </div>

          <Link
            to="/issues"
            className="hidden sm:inline-flex items-center space-x-1.5 text-xs font-semibold text-[#1769D2] hover:text-[#1459b8] bg-[#EAF3FF] dark:bg-blue-950/60 hover:bg-blue-100 dark:hover:bg-blue-900/60 px-3.5 py-2 rounded-xl border border-blue-200 dark:border-blue-800/60 transition"
          >
            <FileCheck2 size={14} />
            <span>Field Evidence Log</span>
          </Link>
        </div>

        {/* 6 Grid Cards for Navigation */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {MODULE_CARDS.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.to}
                className="card p-5 sm:p-6 card-hover flex flex-col justify-between space-y-4 group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="w-10 h-10 rounded-xl bg-[#EAF3FF] dark:bg-blue-950/60 text-[#1769D2] dark:text-blue-400 flex items-center justify-center group-hover:scale-105 transition-transform">
                      <Icon size={20} />
                    </div>
                    <span className="text-[10px] font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-gray-100 dark:bg-slate-800 text-gray-600 dark:text-slate-300 border border-gray-200 dark:border-slate-700">
                      {card.badge}
                    </span>
                  </div>

                  <div className="space-y-1">
                    <h4 className="card-title group-hover:text-[#1769D2] dark:group-hover:text-blue-400 transition-colors">
                      {card.title}
                    </h4>
                    <p className="text-xs text-[#64748B] dark:text-slate-400 leading-relaxed">
                      {card.description}
                    </p>
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-100 dark:border-slate-800">
                  <Link
                    to={card.to}
                    className="inline-flex items-center space-x-1.5 text-xs font-bold text-[#1769D2] dark:text-blue-400 group-hover:text-[#1459b8] transition-colors"
                  >
                    <span>{card.actionText}</span>
                    <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom Governance Notice */}
        <div className="card p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 flex items-center justify-center shrink-0 mt-0.5 border border-emerald-200/60 dark:border-emerald-900/60">
              <UserCheck size={16} />
            </div>
            <div>
              <p className="text-xs font-bold text-[#14213D] dark:text-slate-200">
                Official Audit Trail Active
              </p>
              <p className="text-[11px] text-[#64748B] dark:text-slate-400 mt-0.5">
                All officer interactions, inspection records, and verification decisions are logged under official state audit parameters.
              </p>
            </div>
          </div>

          <Link
            to="/settings"
            className="text-xs font-semibold text-[#64748B] dark:text-slate-400 hover:text-[#14213D] dark:hover:text-slate-100 shrink-0 hover:underline"
          >
            Officer Settings →
          </Link>
        </div>

      </div>
    </div>
  );
}

