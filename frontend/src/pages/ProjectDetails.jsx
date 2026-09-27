import { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Building2,
  MapPin,
  Calendar,
  Briefcase,
  Layers,
  FileCheck2,
  Clock,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
  IndianRupee,
  Activity,
  Edit3,
  PlusCircle,
  X,
  Loader2,
  History,
  TrendingUp,
  ShieldAlert,
  FileSpreadsheet,
  Download,
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import { useAuth } from '../context/AuthContext';
import { projectsApi, authApi, alertsApi, reportApi } from '../services/api';
import {
  formatLakhs,
  formatDate,
  formatProgress,
  getStatusBadgeStyle,
  getMilestoneStatusStyle,
} from '../utils/formatters';

/* ─── Compact Early Warnings Section (Phase 8) ─────────────────────────── */
function ProjectEarlyWarningsSection({ projectId }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const fetchAlerts = useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const res = await alertsApi.getByProject(projectId);
      setAlerts(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await alertsApi.generateForProject(projectId);
      await fetchAlerts();
    } catch (err) {
      // silent
    } finally {
      setGenerating(false);
    }
  };

  const handleResolve = async (alertId) => {
    try {
      await alertsApi.markResolved(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, status: 'RESOLVED' } : a))
      );
    } catch (err) {}
  };

  if (loading && alerts.length === 0) return null;

  const activeAlerts = alerts.filter((a) => a.status !== 'RESOLVED' && a.status !== 'DISMISSED');

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-slate-800">
        <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2">
          <AlertCircle size={16} className="text-amber-500" />
          <span>Early Warnings & Alerts</span>
          <span className="text-[10px] bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full font-bold border border-amber-200">
            {activeAlerts.length} Active
          </span>
        </h3>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={generating}
          className="text-xs font-semibold text-[#1769D2] hover:underline inline-flex items-center space-x-1"
        >
          <RefreshCw size={12} className={generating ? 'animate-spin' : ''} />
          <span>{generating ? 'Evaluating...' : 'Refresh Alerts'}</span>
        </button>
      </div>

      {alerts.length === 0 ? (
        <p className="text-xs text-[#64748B] dark:text-slate-400">No early warning alerts active for this project.</p>
      ) : (
        <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
          {alerts.map((a) => {
            const isResolved = a.status === 'RESOLVED' || a.status === 'DISMISSED';
            return (
              <div
                key={a.id}
                className={`p-3 rounded-xl border text-xs space-y-1 ${
                  isResolved ? 'bg-gray-50 dark:bg-slate-800/50 border-gray-200 dark:border-slate-700 text-gray-500 dark:text-slate-400' : 'bg-amber-50/60 border-amber-200 text-[#14213D] dark:text-slate-100'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold border ${
                        a.severity === 'CRITICAL' ? 'bg-red-100 text-red-900 border-red-300' :
                        a.severity === 'HIGH' ? 'bg-red-50 text-red-700 border-red-200' :
                        a.severity === 'MEDIUM' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                        'bg-emerald-50 text-emerald-700 border-emerald-200'
                      }`}
                    >
                      {a.severity}
                    </span>
                    <span className="font-bold text-[#14213D] dark:text-slate-100">{a.title}</span>
                  </div>
                  {!isResolved && (
                    <button
                      type="button"
                      onClick={() => handleResolve(a.id)}
                      className="text-[10px] font-bold text-emerald-700 hover:underline"
                    >
                      Resolve
                    </button>
                  )}
                </div>
                <p className="text-[11px] leading-relaxed text-[#64748B] dark:text-slate-400">{a.message}</p>
              </div>
            );
          })}
        </div>
      )}

      <div className="pt-2 border-t border-gray-100 dark:border-slate-800">
        <Link to="/warnings" className="text-xs font-semibold text-[#1769D2] hover:underline flex items-center space-x-1">
          <span>View All Early Warning Center Alerts</span>
          <TrendingUp size={12} />
        </Link>
      </div>
    </div>
  );
}

/* ─── Compact Executive Reports Section (Phase 10) ───────────────────────── */
function ProjectReportsSection({ projectId }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [downloadingId, setDownloadingId] = useState(null);

  const fetchReports = useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const res = await reportApi.getByProject(projectId);
      setReports(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setReports([]);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await reportApi.generate(projectId, 'PROJECT_SUMMARY');
      await fetchReports();
    } catch (err) {
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async (reportId, fileName) => {
    setDownloadingId(reportId);
    try {
      const res = await reportApi.download(reportId);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName || `SetuX_Report_${reportId}.pdf`;
      document.body.appendChild(link);
      link.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (err) {
    } finally {
      setDownloadingId(null);
    }
  };

  if (loading && reports.length === 0) return null;

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-slate-800">
        <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2">
          <FileSpreadsheet size={16} className="text-[#1769D2]" />
          <span>Executive PDF Reports & Audit</span>
          <span className="text-[10px] bg-blue-50 dark:bg-blue-950/40 text-[#1769D2] px-2 py-0.5 rounded-full font-bold border border-blue-200">
            {reports.length} Available
          </span>
        </h3>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={generating}
          className="text-xs font-semibold text-[#1769D2] hover:underline inline-flex items-center space-x-1"
        >
          {generating ? <Loader2 size={12} className="animate-spin" /> : <PlusCircle size={12} />}
          <span>{generating ? 'Generating...' : 'Generate PDF'}</span>
        </button>
      </div>

      {reports.length === 0 ? (
        <p className="text-xs text-[#64748B] dark:text-slate-400">No PDF reports currently generated for this project.</p>
      ) : (
        <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
          {reports.slice(0, 4).map((r) => (
            <div key={r.id} className="p-3 rounded-xl border border-gray-200 dark:border-slate-700 bg-[#F5F7FA] dark:bg-slate-800 flex items-center justify-between text-xs">
              <div className="min-w-0">
                <span className="font-bold text-[#14213D] dark:text-slate-100 block truncate">{r.file_name || r.report_type}</span>
                <span className="text-[10px] text-[#64748B] dark:text-slate-400">{formatDate(r.created_at)} • {r.report_type}</span>
              </div>
              <button
                type="button"
                onClick={() => handleDownload(r.id, r.file_name)}
                disabled={downloadingId === r.id}
                className="ml-3 inline-flex items-center space-x-1 text-xs font-bold text-[#1769D2] hover:underline shrink-0"
              >
                {downloadingId === r.id ? <Loader2 size={12} className="animate-spin" /> : <Download size={12} />}
                <span>Download</span>
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="pt-2 border-t border-gray-100 dark:border-slate-800">
        <Link to="/reports" className="text-xs font-semibold text-[#1769D2] hover:underline flex items-center space-x-1">
          <span>Open Full Executive Report Center</span>
          <TrendingUp size={12} />
        </Link>
      </div>
    </div>
  );
}

const STATUS_OPTIONS = [
  'Verified',
  'Review Required',
  'Under Review',
  'Ongoing',
  'Delayed',
  'Completed',
];

const SECTOR_OPTIONS = [
  'Roads & Highways',
  'Water Resources',
  'Energy & Power',
  'Urban Transport',
  'Healthcare Infrastructure',
  'Education & Schools',
  'Rural Development',
  'Bridges & Flyovers',
];

/* ─── Risk Intelligence Inline Section (Phase 6) ─────────────────────────── */
const RISK_LEVEL_STYLE = {
  LOW: { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  MEDIUM: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', dot: 'bg-amber-500' },
  HIGH: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', dot: 'bg-red-500' },
  CRITICAL: { bg: 'bg-red-100', border: 'border-red-300', text: 'text-red-900', dot: 'bg-red-700' },
};

const SEVERITY_BADGE_STYLE = {
  LOW: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  MEDIUM: 'bg-amber-50 text-amber-700 border-amber-200',
  HIGH: 'bg-red-50 text-red-700 border-red-200',
  CRITICAL: 'bg-red-100 text-red-900 border-red-300',
};

function RiskIntelligenceSection({ projectId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRisk = useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await projectsApi.getRiskIntelligence(projectId);
      setData(res.data);
    } catch (err) {
      const status = err.response?.status;
      if (status === 404) {
        setError('Risk intelligence data is not available for this project.');
      } else if (status === 401 || status === 403) {
        setError('Access denied for risk intelligence.');
      } else {
        setError('Unable to load risk intelligence. Please try again.');
      }
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => { fetchRisk(); }, [fetchRisk]);

  const riskStyle = (level) => RISK_LEVEL_STYLE[level] || RISK_LEVEL_STYLE.LOW;

  // Loading skeleton
  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 shadow-sm space-y-4 animate-pulse">
        <div className="flex items-center space-x-2 pb-3 border-b border-gray-100 dark:border-slate-800">
          <div className="w-4 h-4 bg-gray-200 dark:bg-slate-700 rounded" />
          <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-40" />
        </div>
        <div className="h-8 bg-gray-100 dark:bg-slate-800 rounded w-24" />
        <div className="h-2 bg-gray-100 dark:bg-slate-800 rounded w-full" />
        <div className="grid grid-cols-2 gap-3">
          <div className="h-16 bg-gray-50 dark:bg-slate-800/50 rounded-xl" />
          <div className="h-16 bg-gray-50 dark:bg-slate-800/50 rounded-xl" />
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 shadow-sm">
        <div className="flex items-center space-x-2 pb-3 border-b border-gray-100 dark:border-slate-800 mb-4">
          <ShieldAlert size={16} className="text-[#1769D2]" />
          <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100">Risk Intelligence</h3>
        </div>
        <div className="flex items-center space-x-2 text-xs text-amber-700 bg-amber-50 p-3.5 rounded-xl border border-amber-200">
          <AlertCircle size={14} className="shrink-0" />
          <span>{error}</span>
          <button type="button" onClick={fetchRisk} className="ml-auto shrink-0 text-[#1769D2] font-bold hover:underline">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data || !data.is_available) return null;

  const overall = data.overall_risk || {};
  const rs = riskStyle(overall.level);
  const costPred = data.cost_overrun_prediction;
  const timePred = data.time_overrun_prediction;

  const renderPredMini = (pred, label) => {
    if (!pred) return null;
    if (!pred.is_available) {
      return (
        <div className="bg-gray-50 dark:bg-slate-800/50 rounded-xl p-3 border border-gray-200 dark:border-slate-700 space-y-1">
          <span className="text-[10px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider block">{label}</span>
          <span className="text-xs text-[#64748B] dark:text-slate-400">Prediction unavailable</span>
          {pred.error && <span className="text-[10px] text-[#64748B] dark:text-slate-400 block">{pred.error}</span>}
        </div>
      );
    }
    const hasRisk = pred.prediction && pred.prediction.includes('OVERRUN') && !pred.prediction.includes('NO_');
    return (
      <div className="bg-[#F5F7FA] dark:bg-slate-800 rounded-xl p-3 border border-gray-200 dark:border-slate-700 space-y-1">
        <span className="text-[10px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider block">{label}</span>
        <div className="flex items-center space-x-2">
          <span className={`text-lg font-bold font-mono ${hasRisk ? 'text-red-700' : 'text-emerald-700'}`}>
            {(pred.probability * 100).toFixed(1)}%
          </span>
          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${
            hasRisk ? 'bg-red-50 text-red-700 border-red-200' : 'bg-emerald-50 text-emerald-700 border-emerald-200'
          }`}>
            {hasRisk ? 'Risk Detected' : 'No Risk'}
          </span>
        </div>
        {pred.model_name && <span className="text-[10px] text-[#64748B] dark:text-slate-400">{pred.model_name}</span>}
      </div>
    );
  };

  const topFactors = (data.prioritized_risk_factors || []).filter(f => f.severity === 'HIGH' || f.severity === 'CRITICAL').slice(0, 4);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 shadow-sm space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-slate-800">
        <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 tracking-tight flex items-center space-x-2">
          <ShieldAlert size={16} className="text-[#1769D2]" />
          <span>Risk Intelligence</span>
        </h3>
        <div className="flex items-center space-x-2">
          {overall.version && (
            <span className="text-[10px] text-[#64748B] dark:text-slate-400 bg-gray-50 dark:bg-slate-800/50 px-2 py-0.5 rounded border border-gray-200 dark:border-slate-700">
              {overall.version}
            </span>
          )}
          <button type="button" onClick={fetchRisk} className="p-1.5 rounded-lg text-gray-400 dark:text-slate-500 hover:text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:bg-slate-800 transition" title="Refresh risk data">
            <RefreshCw size={13} />
          </button>
        </div>
      </div>

      {/* Overall Risk */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="flex items-center space-x-4">
          <div className={`w-16 h-16 rounded-xl ${rs.bg} ${rs.border} border flex items-center justify-center`}>
            <span className="text-xl font-bold font-mono text-[#14213D] dark:text-slate-100">{overall.score?.toFixed(0) ?? '—'}</span>
          </div>
          <div>
            <span className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold border ${rs.bg} ${rs.border} ${rs.text}`}>
              <span className={`w-2 h-2 rounded-full ${rs.dot}`} />
              <span>{overall.level || 'UNKNOWN'}</span>
            </span>
            <div className="text-[10px] text-[#64748B] dark:text-slate-400 mt-1">
              Overall Risk Score: <span className="font-mono font-bold text-[#14213D] dark:text-slate-100">{overall.score?.toFixed(1) ?? '—'}</span> / 100
            </div>
          </div>
        </div>
        {data.summary && (
          <p className="text-xs text-[#64748B] dark:text-slate-400 leading-relaxed flex-1 sm:pl-4 sm:border-l sm:border-gray-200 dark:border-slate-700">{data.summary}</p>
        )}
      </div>

      {/* Model Signals */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {renderPredMini(costPred, 'Cost Overrun Prediction')}
        {renderPredMini(timePred, 'Time Overrun Prediction')}
      </div>

      {/* Key Risk Drivers */}
      {topFactors.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-gray-100 dark:border-slate-800">
          <span className="text-[10px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider">Key Risk Drivers</span>
          {topFactors.map((f, i) => {
            const badge = SEVERITY_BADGE_STYLE[f.severity] || SEVERITY_BADGE_STYLE.LOW;
            return (
              <div key={i} className="flex items-start gap-2 text-xs">
                <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold border shrink-0 mt-0.5 ${badge}`}>
                  {f.severity}
                </span>
                <div className="min-w-0">
                  <span className="font-semibold text-[#14213D] dark:text-slate-100">
                    {(f.factor || '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                  </span>
                  {f.explanation && (
                    <span className="text-[#64748B] dark:text-slate-400 ml-1 text-[11px]">— {f.explanation}</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Rule-based & Model Details */}
      {overall.rule_based_baseline_score !== undefined && (
        <div className="flex items-center justify-between text-xs bg-gray-50 dark:bg-slate-800/50 px-3 py-2 rounded-xl border border-gray-200 dark:border-slate-700">
          <span className="text-[#64748B] dark:text-slate-400 font-medium">Rule-Based Assessment Baseline:</span>
          <span className="font-mono font-bold text-[#14213D] dark:text-slate-100">{overall.rule_based_baseline_score?.toFixed(1) ?? '—'} / 100</span>
        </div>
      )}

      {/* Recommended Actions */}
      {((data.recommendations && data.recommendations.length > 0) || (data.recommended_actions && data.recommended_actions.length > 0)) && (
        <div className="pt-2 border-t border-gray-100 dark:border-slate-800">
          <span className="text-[10px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider block mb-2">Recommended Actions</span>
          <ul className="space-y-1.5">
            {(data.recommendations || data.recommended_actions).slice(0, 3).map((action, i) => (
              <li key={i} className="flex items-start space-x-2 text-xs text-[#14213D] dark:text-slate-100">
                <span className="w-4 h-4 bg-[#EAF3FF] dark:bg-blue-950/40 text-[#1769D2] rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 mt-0.5">{i + 1}</span>
                <span className="leading-relaxed">{action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* View Full Intelligence Link */}
      <div className="pt-2 border-t border-gray-100 dark:border-slate-800">
        <Link
          to="/risk"
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-[#1769D2] hover:underline"
        >
          <span>View Full Risk Intelligence</span>
          <TrendingUp size={12} />
        </Link>
      </div>
    </div>
  );
}

export default function ProjectDetails() {
  const { id } = useParams();
  const { user } = useAuth();

  // Core Data State
  const [project, setProject] = useState(null);
  const [milestones, setMilestones] = useState([]);
  const [latestProgress, setLatestProgress] = useState(null);
  const [progressHistory, setProgressHistory] = useState([]);
  const [departments, setDepartments] = useState([]);

  // UI State
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const [notification, setNotification] = useState(null); // { type: 'success' | 'error', message: '' }

  // Modal / Form States
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isProgressModalOpen, setIsProgressModalOpen] = useState(false);

  // Edit Project Form State
  const [editFormData, setEditFormData] = useState({});
  const [editFormErrors, setEditFormErrors] = useState({});
  const [isSavingProject, setIsSavingProject] = useState(false);

  // Progress Update Form State
  const [progressFormData, setProgressFormData] = useState({
    report_date: new Date().toISOString().split('T')[0],
    physical_progress: '',
    financial_progress: '',
    expenditure: '',
    remarks: '',
  });
  const [progressFormErrors, setProgressFormErrors] = useState({});
  const [isSubmittingProgress, setIsSubmittingProgress] = useState(false);

  // ─── Data Fetching ────────────────────────────────────────────────────────
  const fetchProjectDetails = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    setNotFound(false);

    try {
      // 1. Fetch main project
      const projRes = await projectsApi.getById(id);
      setProject(projRes.data);

      // 2. Fetch milestones
      try {
        const milesRes = await projectsApi.getMilestones(id);
        setMilestones(Array.isArray(milesRes.data) ? milesRes.data : []);
      } catch (err) {
        console.warn('Milestones fetch note:', err?.message);
        setMilestones([]);
      }

      // 3. Fetch latest progress
      try {
        const progRes = await projectsApi.getLatestProgress(id);
        setLatestProgress(progRes.data);
      } catch {
        setLatestProgress(null);
      }

      // 4. Fetch full progress history
      try {
        const histRes = await projectsApi.getProgress(id);
        setProgressHistory(Array.isArray(histRes.data) ? histRes.data : []);
      } catch {
        setProgressHistory([]);
      }

    } catch (err) {
      console.warn('Project fetch error:', err);
      if (err.response?.status === 404) {
        setNotFound(true);
      } else {
        setError('Unable to load project details. Please check connection to the SetuX service.');
      }
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchProjectDetails();
  }, [fetchProjectDetails]);

  // Fetch departments list for edit dropdown
  useEffect(() => {
    async function loadDepts() {
      try {
        const res = await authApi.getDepartments();
        if (Array.isArray(res.data)) {
          setDepartments(res.data);
        }
      } catch {
        // Non-fatal if departments API is unavailable
      }
    }
    loadDepts();
  }, []);

  // ─── Auto-Dismiss Notifications ──────────────────────────────────────────
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 6000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // ─── Edit Project Handlers ────────────────────────────────────────────────
  const handleOpenEditModal = () => {
    if (!project) return;
    setEditFormData({
      name: project.name || '',
      description: project.description || '',
      sector: project.sector || project.project_type || 'Roads & Highways',
      ministry: project.ministry || '',
      department_name: project.department_name || project.department || '',
      contractor_name: project.contractor_name || project.contractor || '',
      location: project.location || project.location_name || '',
      district: project.district || '',
      taluka: project.taluka || '',
      state: project.state || 'Maharashtra',
      original_cost: project.original_cost ?? project.budget_lakh ?? 0,
      revised_cost: project.revised_cost ?? '',
      start_date: project.start_date || '',
      planned_completion_date: project.planned_completion_date || project.expected_completion || '',
      revised_completion_date: project.revised_completion_date || '',
      actual_completion_date: project.actual_completion_date || '',
      status: project.status || 'Under Review',
    });
    setEditFormErrors({});
    setIsEditModalOpen(true);
  };

  const handleSaveProject = async (e) => {
    e.preventDefault();
    setEditFormErrors({});

    // Client-side Validation
    const errors = {};
    if (!editFormData.name || editFormData.name.trim().length < 2) {
      errors.name = 'Project name must be at least 2 characters.';
    }
    if (editFormData.original_cost !== '' && Number(editFormData.original_cost) < 0) {
      errors.original_cost = 'Sanctioned budget must be positive.';
    }
    if (editFormData.revised_cost !== '' && Number(editFormData.revised_cost) < 0) {
      errors.revised_cost = 'Revised budget must be positive.';
    }

    if (Object.keys(errors).length > 0) {
      setEditFormErrors(errors);
      return;
    }

    setIsSavingProject(true);

    try {
      const pIdentifier = project.project_code || project.id;
      const payload = {
        name: editFormData.name.trim(),
        description: editFormData.description ? editFormData.description.trim() : null,
        sector: editFormData.sector ? editFormData.sector.trim() : undefined,
        ministry: editFormData.ministry ? editFormData.ministry.trim() : null,
        department_name: editFormData.department_name ? editFormData.department_name.trim() : null,
        contractor_name: editFormData.contractor_name ? editFormData.contractor_name.trim() : null,
        location: editFormData.location ? editFormData.location.trim() : null,
        district: editFormData.district ? editFormData.district.trim() : null,
        taluka: editFormData.taluka ? editFormData.taluka.trim() : '',
        state: editFormData.state || 'Maharashtra',
        original_cost: editFormData.original_cost !== '' ? Number(editFormData.original_cost) : undefined,
        revised_cost: editFormData.revised_cost !== '' ? Number(editFormData.revised_cost) : null,
        start_date: editFormData.start_date || null,
        planned_completion_date: editFormData.planned_completion_date || null,
        revised_completion_date: editFormData.revised_completion_date || null,
        actual_completion_date: editFormData.actual_completion_date || null,
        status: editFormData.status || undefined,
      };

      await projectsApi.update(pIdentifier, payload);

      // Refetch from server to guarantee authoritative state
      await fetchProjectDetails();

      setIsEditModalOpen(false);
      setNotification({
        type: 'success',
        message: 'Project details updated successfully.',
      });
    } catch (err) {
      console.warn('Update project error:', err);
      let errMsg = 'Failed to update project. Please verify inputs.';
      if (err.response?.status === 401) {
        errMsg = 'Session expired. Please log in again to edit projects.';
      } else if (err.response?.status === 403) {
        errMsg = 'Permission denied: Only department officers can edit project details.';
      } else if (err.response?.data?.detail) {
        const d = err.response.data.detail;
        errMsg = typeof d === 'string' ? d : JSON.stringify(d);
      }
      setEditFormErrors({ submit: errMsg });
    } finally {
      setIsSavingProject(false);
    }
  };

  // ─── Progress Update Handlers ─────────────────────────────────────────────
  const handleOpenProgressModal = () => {
    if (!project) return;
    const currentPhys = project.physical_progress ?? project.reported_progress ?? 0;
    const currentFin = project.financial_progress ?? 0;
    const currentExp = project.total_expenditure ?? 0;

    setProgressFormData({
      report_date: new Date().toISOString().split('T')[0],
      physical_progress: String(currentPhys),
      financial_progress: String(currentFin),
      expenditure: String(currentExp),
      remarks: '',
      reported_by: user?.full_name || user?.email || '',
    });
    setProgressFormErrors({});
    setIsProgressModalOpen(true);
  };

  const handleSubmitProgress = async (e) => {
    e.preventDefault();
    setProgressFormErrors({});

    const errors = {};
    const physVal = Number(progressFormData.physical_progress);
    const finVal = Number(progressFormData.financial_progress);
    const expVal = Number(progressFormData.expenditure);

    if (!progressFormData.report_date) {
      errors.report_date = 'Report date is required.';
    }
    if (isNaN(physVal) || physVal < 0 || physVal > 100) {
      errors.physical_progress = 'Physical progress must be between 0% and 100%.';
    }
    if (isNaN(finVal) || finVal < 0 || finVal > 100) {
      errors.financial_progress = 'Financial progress must be between 0% and 100%.';
    }
    if (isNaN(expVal) || expVal < 0) {
      errors.expenditure = 'Expenditure must be a valid positive number in Lakhs.';
    }

    if (Object.keys(errors).length > 0) {
      setProgressFormErrors(errors);
      return;
    }

    setIsSubmittingProgress(true);

    try {
      const pIdentifier = project.project_code || project.id;
      const payload = {
        report_date: progressFormData.report_date,
        physical_progress: physVal,
        financial_progress: finVal,
        expenditure: expVal,
        remarks: progressFormData.remarks.trim() || undefined,
        reported_by: progressFormData.reported_by.trim() || user?.full_name || undefined,
      };

      await projectsApi.createProgress(pIdentifier, payload);

      // Refetch everything from server to ensure state consistency
      await fetchProjectDetails();

      setIsProgressModalOpen(false);
      setNotification({
        type: 'success',
        message: 'Progress update recorded and synchronized successfully.',
      });
    } catch (err) {
      console.warn('Progress update error:', err);
      let errMsg = 'Failed to submit progress update.';
      if (err.response?.status === 401) {
        errMsg = 'Session expired. Please log in again.';
      } else if (err.response?.status === 403) {
        errMsg = 'Permission denied: Only department officers can submit progress updates.';
      } else if (err.response?.data?.detail) {
        const d = err.response.data.detail;
        errMsg = typeof d === 'string' ? d : JSON.stringify(d);
      }
      setProgressFormErrors({ submit: errMsg });
    } finally {
      setIsSubmittingProgress(false);
    }
  };

  // ─── Render States ────────────────────────────────────────────────────────

  // Case 1: Loading Skeleton
  if (loading) {
    return (
      <div className="min-h-full pb-16">
        <PageHeader
          title="Project Inspection"
          subtitle="Loading project verification profile from backend..."
          breadcrumbs={['SetuX', 'Projects', id || '...']}
        />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
          <div className="animate-pulse bg-white dark:bg-slate-900 rounded-2xl p-6 border border-gray-200 dark:border-slate-700 space-y-4">
            <div className="h-6 bg-gray-200 dark:bg-slate-700 rounded w-1/3"></div>
            <div className="h-4 bg-gray-100 dark:bg-slate-800 rounded w-1/2"></div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4">
              <div className="h-16 bg-gray-100 dark:bg-slate-800 rounded-xl"></div>
              <div className="h-16 bg-gray-100 dark:bg-slate-800 rounded-xl"></div>
              <div className="h-16 bg-gray-100 dark:bg-slate-800 rounded-xl"></div>
              <div className="h-16 bg-gray-100 dark:bg-slate-800 rounded-xl"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Case 2: 404 Not Found State
  if (notFound) {
    return (
      <div className="min-h-full pb-16">
        <PageHeader
          title="Project Not Found"
          subtitle="The requested project identifier does not exist in the state database."
          breadcrumbs={['SetuX', 'Projects', '404']}
        />
        <div className="max-w-md mx-auto px-4 py-16 text-center space-y-5">
          <div className="w-16 h-16 bg-amber-50 border border-amber-200 text-amber-600 rounded-2xl flex items-center justify-center mx-auto">
            <AlertCircle size={32} />
          </div>
          <div className="space-y-1.5">
            <h2 className="text-xl font-bold text-[#14213D] dark:text-slate-100">Project ID Not Found</h2>
            <p className="text-xs text-[#64748B] dark:text-slate-400">
              No project record matching <span className="font-mono font-semibold">"{id}"</span> was found.
            </p>
          </div>
          <Link
            to="/projects"
            className="inline-flex items-center space-x-2 bg-[#1769D2] hover:bg-[#1459b8] text-white px-5 py-2.5 rounded-lg text-xs font-semibold transition"
          >
            <ArrowLeft size={14} />
            <span>Return to Projects Directory</span>
          </Link>
        </div>
      </div>
    );
  }

  // Case 3: Error State
  if (error || !project) {
    return (
      <div className="min-h-full pb-16">
        <PageHeader
          title="Error Loading Project"
          subtitle="An issue occurred while communicating with the SetuX service."
          breadcrumbs={['SetuX', 'Projects', id || 'Error']}
        />
        <div className="max-w-md mx-auto px-4 py-16 text-center space-y-5">
          <div className="w-16 h-16 bg-red-50 border border-red-200 text-red-600 rounded-2xl flex items-center justify-center mx-auto">
            <AlertCircle size={32} />
          </div>
          <div className="space-y-1.5">
            <h2 className="text-xl font-bold text-red-800">Connection Failed</h2>
            <p className="text-xs text-red-600">{error || 'Unable to load project.'}</p>
          </div>
          <div className="flex items-center justify-center space-x-3">
            <button
              type="button"
              onClick={fetchProjectDetails}
              className="inline-flex items-center space-x-1.5 bg-[#1769D2] hover:bg-[#1459b8] text-white px-4 py-2 rounded-lg text-xs font-semibold transition"
            >
              <RefreshCw size={13} />
              <span>Retry</span>
            </button>
            <Link
              to="/projects"
              className="inline-flex items-center space-x-1.5 bg-white dark:bg-slate-900 hover:bg-gray-50 dark:bg-slate-800/50 text-[#14213D] dark:text-slate-100 border border-gray-200 dark:border-slate-700 px-4 py-2 rounded-lg text-xs font-semibold transition"
            >
              <ArrowLeft size={13} />
              <span>Back to List</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Case 4: Real Data Render
  const pCode = project.project_code || project.project_id || String(project.id);
  const physicalProgress = project.physical_progress ?? project.reported_progress ?? 0;
  const financialProgress = project.financial_progress ?? 0;
  const originalCost = project.original_cost ?? project.budget_lakh ?? 0;
  const revisedCost = project.revised_cost;
  const totalExpenditure = project.total_expenditure ?? 0;

  return (
    <div className="min-h-full pb-16">
      {/* Page Header */}
      <PageHeader
        title={project.name}
        subtitle={project.description || `${project.sector || 'Infrastructure Project'} in ${project.district || 'Maharashtra'}.`}
        badge={pCode}
        breadcrumbs={['SetuX', 'Projects', pCode]}
        actions={
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Update Progress Button */}
            <button
              type="button"
              onClick={handleOpenProgressModal}
              className="inline-flex items-center space-x-1.5 bg-[#1769D2] hover:bg-[#1459b8] text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow-sm transition focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
            >
              <TrendingUp size={14} />
              <span>Update Progress</span>
            </button>

            {/* Edit Project Button */}
            <button
              type="button"
              onClick={handleOpenEditModal}
              className="inline-flex items-center space-x-1.5 bg-white dark:bg-slate-900 hover:bg-gray-50 dark:bg-slate-800/50 text-[#14213D] dark:text-slate-100 border border-gray-200 dark:border-slate-700 px-3.5 py-2 rounded-lg text-xs font-semibold shadow-sm transition focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
            >
              <Edit3 size={14} className="text-[#1769D2]" />
              <span>Edit Details</span>
            </button>

            {/* Refresh Button */}
            <button
              type="button"
              onClick={fetchProjectDetails}
              className="p-2 rounded-lg text-gray-500 dark:text-slate-400 hover:text-gray-900 bg-white dark:bg-slate-900 hover:bg-gray-50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700 transition"
              title="Refresh project details"
            >
              <RefreshCw size={14} />
            </button>

            <Link
              to="/projects"
              className="inline-flex items-center space-x-1.5 text-xs font-semibold text-[#1769D2] bg-white dark:bg-slate-900 hover:bg-[#EAF3FF] dark:bg-blue-950/40 px-3.5 py-2 rounded-lg border border-blue-200 transition"
            >
              <ArrowLeft size={14} />
              <span className="hidden sm:inline">All Projects</span>
            </Link>
          </div>
        }
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        
        {/* Inline Notification Banner */}
        {notification && (
          <div
            className={`p-4 rounded-xl text-xs font-medium flex items-center justify-between border animate-in fade-in duration-200 ${
              notification.type === 'success'
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : 'bg-red-50 text-red-800 border-red-200'
            }`}
          >
            <div className="flex items-center space-x-2">
              {notification.type === 'success' ? (
                <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
              ) : (
                <AlertCircle size={16} className="text-red-600 shrink-0" />
              )}
              <span>{notification.message}</span>
            </div>
            <button
              type="button"
              onClick={() => setNotification(null)}
              className="p-1 text-gray-400 dark:text-slate-500 hover:text-gray-700 dark:text-slate-300"
            >
              <X size={14} />
            </button>
          </div>
        )}

        {/* Section A: Key Identity Banner & Top Metrics */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 shadow-sm space-y-6">
          
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-gray-100 dark:border-slate-800">
            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-sm font-bold text-[#1769D2]">
                  {pCode}
                </span>
                <span className="text-gray-300 dark:text-slate-600">•</span>
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${getStatusBadgeStyle(
                    project.status
                  )}`}
                >
                  {project.status || 'Under Review'}
                </span>
                {project.sector && (
                  <span className="text-xs font-medium text-[#64748B] dark:text-slate-400 bg-gray-100 dark:bg-slate-800 px-2.5 py-0.5 rounded-full">
                    {project.sector}
                  </span>
                )}
              </div>
              <h2 className="text-lg sm:text-xl font-bold text-[#14213D] dark:text-slate-100">
                {project.name}
              </h2>
            </div>

            {/* Department & District Tag */}
            <div className="flex flex-wrap items-center gap-3 text-xs text-[#64748B] dark:text-slate-400">
              <div className="flex items-center space-x-1.5 bg-[#F5F7FA] dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-slate-700">
                <Building2 size={14} className="text-[#1769D2]" />
                <span className="font-semibold text-[#14213D] dark:text-slate-100">{project.department_name || project.department || 'State Department'}</span>
              </div>
              <div className="flex items-center space-x-1.5 bg-[#F5F7FA] dark:bg-slate-800 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-slate-700">
                <MapPin size={14} className="text-red-500" />
                <span className="font-semibold text-[#14213D] dark:text-slate-100">{project.district || 'Maharashtra'}{project.taluka ? `, ${project.taluka}` : ''}</span>
              </div>
            </div>
          </div>

          {/* 4 Financial & Physical Key Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* Sanctioned Budget */}
            <div className="bg-[#F5F7FA] dark:bg-slate-800 rounded-xl p-4 border border-gray-200 dark:border-slate-700 space-y-1">
              <span className="text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider block">
                Sanctioned Budget
              </span>
              <div className="text-lg sm:text-xl font-mono font-bold text-[#14213D] dark:text-slate-100">
                {formatLakhs(originalCost)}
              </div>
              {revisedCost ? (
                <span className="text-[10px] text-[#64748B] dark:text-slate-400 block">
                  Revised: {formatLakhs(revisedCost)}
                </span>
              ) : (
                <span className="text-[10px] text-[#64748B] dark:text-slate-400 block">Original Sanction</span>
              )}
            </div>

            {/* Total Expenditure */}
            <div className="bg-[#F5F7FA] dark:bg-slate-800 rounded-xl p-4 border border-gray-200 dark:border-slate-700 space-y-1">
              <span className="text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider block">
                Total Expenditure
              </span>
              <div className="text-lg sm:text-xl font-mono font-bold text-[#14213D] dark:text-slate-100">
                {formatLakhs(totalExpenditure)}
              </div>
              <span className="text-[10px] text-[#64748B] dark:text-slate-400 block">
                Financial Progress: {formatProgress(financialProgress)}
              </span>
            </div>

            {/* Physical Progress */}
            <div className="bg-[#F5F7FA] dark:bg-slate-800 rounded-xl p-4 border border-gray-200 dark:border-slate-700 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider">
                  Physical Progress
                </span>
                <span className="text-sm font-bold text-[#1769D2]">
                  {formatProgress(physicalProgress)}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                <div
                  className="h-full rounded-full bg-[#1769D2]"
                  style={{ width: `${Math.min(100, Math.max(0, physicalProgress))}%` }}
                />
              </div>
            </div>

            {/* Timeline */}
            <div className="bg-[#F5F7FA] dark:bg-slate-800 rounded-xl p-4 border border-gray-200 dark:border-slate-700 space-y-1">
              <span className="text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider block">
                Target Completion
              </span>
              <div className="text-sm font-bold text-[#14213D] dark:text-slate-100 pt-0.5">
                {formatDate(project.planned_completion_date || project.expected_completion)}
              </div>
              <span className="text-[10px] text-[#64748B] dark:text-slate-400 block">
                Started: {formatDate(project.start_date)}
              </span>
            </div>

          </div>

        </div>

        {/* Section B & C: Project Specifications & Latest Progress Card */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column: Specifications (8 cols) */}
          <div className="lg:col-span-8 bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 p-6 shadow-sm space-y-5">
            <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 tracking-tight flex items-center space-x-2">
                <Layers size={16} className="text-[#1769D2]" />
                <span>Project Identity & Contractor Details</span>
              </h3>
              <button
                type="button"
                onClick={handleOpenEditModal}
                className="text-xs font-semibold text-[#1769D2] hover:underline inline-flex items-center space-x-1"
              >
                <Edit3 size={12} />
                <span>Edit</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-[11px] text-[#64748B] dark:text-slate-400 block">Contractor Name</span>
                <span className="font-semibold text-[#14213D] dark:text-slate-100 mt-0.5 block">
                  {project.contractor_name || project.contractor || 'Contractor information pending assignment'}
                </span>
              </div>

              <div>
                <span className="text-[11px] text-[#64748B] dark:text-slate-400 block">Nodal Ministry</span>
                <span className="font-semibold text-[#14213D] dark:text-slate-100 mt-0.5 block">
                  {project.ministry || 'State Government of Maharashtra'}
                </span>
              </div>

              <div>
                <span className="text-[11px] text-[#64748B] dark:text-slate-400 block">Physical Location / Site</span>
                <span className="font-semibold text-[#14213D] dark:text-slate-100 mt-0.5 block">
                  {project.location || project.location_name || project.district || 'Site details on file'}
                </span>
              </div>

              <div>
                <span className="text-[11px] text-[#64748B] dark:text-slate-400 block">State Jurisdiction</span>
                <span className="font-semibold text-[#14213D] dark:text-slate-100 mt-0.5 block">
                  {project.state || 'Maharashtra'}
                </span>
              </div>

              {project.revised_completion_date && (
                <div>
                  <span className="text-[11px] text-[#64748B] dark:text-slate-400 block">Revised Target Completion</span>
                  <span className="font-semibold text-amber-700 mt-0.5 block">
                    {formatDate(project.revised_completion_date)}
                  </span>
                </div>
              )}

              {project.actual_completion_date && (
                <div>
                  <span className="text-[11px] text-[#64748B] dark:text-slate-400 block">Actual Completion Date</span>
                  <span className="font-semibold text-emerald-700 mt-0.5 block">
                    {formatDate(project.actual_completion_date)}
                  </span>
                </div>
              )}
            </div>

            {project.description && (
              <div className="pt-3 border-t border-gray-100 dark:border-slate-800 text-xs">
                <span className="text-[11px] text-[#64748B] dark:text-slate-400 block mb-1">Scope of Work & Notes</span>
                <p className="text-[#14213D] dark:text-slate-100 leading-relaxed bg-[#F5F7FA] dark:bg-slate-800 p-3.5 rounded-xl border border-gray-200 dark:border-slate-700">
                  {project.description}
                </p>
              </div>
            )}
          </div>

          {/* Right Column: Latest Progress Card (4 cols) */}
          <div className="lg:col-span-4 bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 p-6 shadow-sm space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 tracking-tight flex items-center space-x-2">
                  <Activity size={16} className="text-[#1769D2]" />
                  <span>Latest Progress Update</span>
                </h3>
              </div>

              {latestProgress ? (
                <div className="space-y-3 text-xs">
                  <div className="flex items-center justify-between bg-blue-50 dark:bg-blue-950/40 p-2.5 rounded-xl border border-blue-100">
                    <span className="text-[11px] font-semibold text-[#1769D2]">Report Date</span>
                    <span className="font-bold text-[#14213D] dark:text-slate-100">{formatDate(latestProgress.report_date)}</span>
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex justify-between">
                      <span className="text-[#64748B] dark:text-slate-400">Physical Progress:</span>
                      <span className="font-bold text-[#14213D] dark:text-slate-100">{formatProgress(latestProgress.physical_progress)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#64748B] dark:text-slate-400">Financial Progress:</span>
                      <span className="font-bold text-[#14213D] dark:text-slate-100">{formatProgress(latestProgress.financial_progress)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#64748B] dark:text-slate-400">Cumulative Expenditure:</span>
                      <span className="font-mono font-bold text-[#14213D] dark:text-slate-100">{formatLakhs(latestProgress.expenditure)}</span>
                    </div>
                  </div>

                  {latestProgress.reported_by && (
                    <div className="pt-2 border-t border-gray-100 dark:border-slate-800 text-[11px] text-[#64748B] dark:text-slate-400">
                      Reported by: <span className="font-semibold text-[#14213D] dark:text-slate-100">{latestProgress.reported_by}</span>
                    </div>
                  )}

                  {latestProgress.remarks && (
                    <div className="text-[11px] text-[#64748B] dark:text-slate-400 bg-[#F5F7FA] dark:bg-slate-800 p-2.5 rounded-lg border border-gray-200 dark:border-slate-700">
                      "{latestProgress.remarks}"
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-6 text-xs text-[#64748B] dark:text-slate-400 space-y-1">
                  <Clock size={24} className="text-gray-300 dark:text-slate-600 mx-auto" />
                  <p className="font-semibold text-[#14213D] dark:text-slate-100">No Progress Logs Yet</p>
                  <p className="text-[11px]">No formal site progress update has been logged yet for this project.</p>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-gray-100 dark:border-slate-800">
              <button
                type="button"
                onClick={handleOpenProgressModal}
                className="w-full inline-flex items-center justify-center space-x-1.5 bg-[#1769D2] hover:bg-[#1459b8] text-white py-2 px-3 rounded-lg text-xs font-semibold shadow-sm transition"
              >
                <PlusCircle size={14} />
                <span>Submit New Progress Entry</span>
              </button>
            </div>
          </div>

        </div>

        {/* Section D: Historical Progress Log (Step 7) */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 tracking-tight flex items-center space-x-2">
              <History size={16} className="text-[#1769D2]" />
              <span>Historical Progress Timeline</span>
            </h3>
            <span className="text-xs font-semibold text-[#64748B] dark:text-slate-400">
              {progressHistory.length} {progressHistory.length === 1 ? 'Entry' : 'Entries'}
            </span>
          </div>

          {progressHistory.length === 0 ? (
            <div className="text-center py-8 text-xs text-[#64748B] dark:text-slate-400 space-y-1">
              <p className="font-semibold text-[#14213D] dark:text-slate-100">No progress updates available.</p>
              <p className="text-[11px]">Use the "Update Progress" action to record site inspection progress entries.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F5F7FA] dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider">
                    <th className="py-2.5 px-3">Report Date</th>
                    <th className="py-2.5 px-3">Physical Progress</th>
                    <th className="py-2.5 px-3">Financial Progress</th>
                    <th className="py-2.5 px-3">Cumulative Expenditure</th>
                    <th className="py-2.5 px-3">Reporting Officer</th>
                    <th className="py-2.5 px-3">Site Observations / Remarks</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
                  {progressHistory.map((entry) => (
                    <tr key={entry.id} className="hover:bg-gray-50 dark:bg-slate-800/50/70 transition-colors">
                      <td className="py-3 px-3 font-semibold text-[#14213D] dark:text-slate-100 whitespace-nowrap">
                        {formatDate(entry.report_date)}
                      </td>
                      <td className="py-3 px-3 min-w-[120px]">
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-gray-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-[#1769D2]"
                              style={{ width: `${Math.min(100, Math.max(0, entry.physical_progress || 0))}%` }}
                            />
                          </div>
                          <span className="font-bold text-[#14213D] dark:text-slate-100 text-[11px]">
                            {formatProgress(entry.physical_progress)}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-3 whitespace-nowrap font-medium text-[#14213D] dark:text-slate-100">
                        {formatProgress(entry.financial_progress)}
                      </td>
                      <td className="py-3 px-3 font-mono font-semibold text-[#14213D] dark:text-slate-100 whitespace-nowrap">
                        {formatLakhs(entry.expenditure)}
                      </td>
                      <td className="py-3 px-3 text-[#64748B] dark:text-slate-400 whitespace-nowrap">
                        {entry.reported_by || 'Officer'}
                      </td>
                      <td className="py-3 px-3 text-[#64748B] dark:text-slate-400 max-w-xs">
                        {entry.remarks ? (
                          <span className="line-clamp-2">{entry.remarks}</span>
                        ) : (
                          <span className="text-gray-400 dark:text-slate-500 italic">No remarks noted</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Section E: Milestones Breakdown */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 tracking-tight flex items-center space-x-2">
              <Calendar size={16} className="text-[#1769D2]" />
              <span>Project Milestones & Implementation Stages</span>
            </h3>
            <span className="text-xs font-semibold text-[#64748B] dark:text-slate-400">
              {milestones.length} {milestones.length === 1 ? 'Milestone' : 'Milestones'}
            </span>
          </div>

          {milestones.length === 0 ? (
            <div className="text-center py-8 text-xs text-[#64748B] dark:text-slate-400 space-y-1">
              <p className="font-semibold text-[#14213D] dark:text-slate-100">No Milestones Recorded</p>
              <p className="text-[11px]">There are no formal milestone stages listed for this project.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#F5F7FA] dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider">
                    <th className="py-2.5 px-3">#</th>
                    <th className="py-2.5 px-3">Milestone Stage</th>
                    <th className="py-2.5 px-3">Target Date</th>
                    <th className="py-2.5 px-3">Actual Date</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Progress</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
                  {milestones.map((m, idx) => (
                    <tr key={m.id || idx} className="hover:bg-gray-50 dark:bg-slate-800/50/70 transition-colors">
                      <td className="py-3 px-3 font-mono text-[#64748B] dark:text-slate-400 font-semibold">
                        {idx + 1}
                      </td>
                      <td className="py-3 px-3">
                        <span className="font-bold text-[#14213D] dark:text-slate-100 block">{m.name}</span>
                        {m.description && (
                          <span className="text-[11px] text-[#64748B] dark:text-slate-400 block mt-0.5">{m.description}</span>
                        )}
                      </td>
                      <td className="py-3 px-3 whitespace-nowrap text-[#14213D] dark:text-slate-100">
                        {formatDate(m.planned_date)}
                      </td>
                      <td className="py-3 px-3 whitespace-nowrap text-[#64748B] dark:text-slate-400">
                        {formatDate(m.actual_date)}
                      </td>
                      <td className="py-3 px-3 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${getMilestoneStatusStyle(
                            m.status
                          )}`}
                        >
                          {m.status || 'PENDING'}
                        </span>
                      </td>
                      <td className="py-3 px-3 min-w-[100px]">
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-gray-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-[#1769D2]"
                              style={{ width: `${Math.min(100, Math.max(0, m.completion_percentage || 0))}%` }}
                            />
                          </div>
                          <span className="font-bold text-[#14213D] dark:text-slate-100 text-[11px]">
                            {formatProgress(m.completion_percentage)}
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

        </div>

        {/* Section F: Risk Intelligence, Early Warnings & Reports (Phase 6, 8, 10) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <RiskIntelligenceSection projectId={id} />
          <ProjectEarlyWarningsSection projectId={id} />
          <ProjectReportsSection projectId={id} />
        </div>

      </div>

      {/* ─── MODAL 1: EDIT PROJECT DETAILS ─────────────────────────────────── */}
      {isEditModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
            
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between bg-[#F5F7FA] dark:bg-slate-800">
              <div className="flex items-center space-x-2">
                <Edit3 size={18} className="text-[#1769D2]" />
                <h3 className="text-base font-bold text-[#14213D] dark:text-slate-100">
                  Edit Project Details — <span className="font-mono text-[#1769D2]">{pCode}</span>
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setIsEditModalOpen(false)}
                className="p-1.5 text-gray-400 dark:text-slate-500 hover:text-gray-700 dark:text-slate-300 rounded-lg hover:bg-gray-200 dark:bg-slate-700 transition"
              >
                <X size={16} />
              </button>
            </div>

            {/* Modal Body: Controlled Form */}
            <form onSubmit={handleSaveProject} className="flex-1 overflow-y-auto p-6 space-y-4 text-xs">
              
              {editFormErrors.submit && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-xl flex items-start space-x-2">
                  <AlertCircle size={15} className="text-red-500 shrink-0 mt-0.5" />
                  <span>{editFormErrors.submit}</span>
                </div>
              )}

              {/* Read-Only System Identity Banner */}
              <div className="bg-blue-50 dark:bg-blue-950/40/70 border border-blue-200 p-3 rounded-xl flex items-center justify-between text-[#1769D2]">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider block">Immutable Project Code</span>
                  <span className="font-mono font-bold text-xs text-[#0B2A4A]">{pCode}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-bold uppercase tracking-wider block">Physical Progress</span>
                  <span className="font-bold text-xs text-[#0B2A4A]">{formatProgress(physicalProgress)} (Updated via Site Log)</span>
                </div>
              </div>

              {/* Project Name */}
              <div>
                <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                  Project Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={editFormData.name || ''}
                  onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                  placeholder="e.g. Kondhwa Road Repair & Widening"
                  className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                />
                {editFormErrors.name && (
                  <p className="text-[11px] text-red-600 mt-1">{editFormErrors.name}</p>
                )}
              </div>

              {/* Sector & Status Row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Sector
                  </label>
                  <select
                    value={editFormData.sector || 'Roads & Highways'}
                    onChange={(e) => setEditFormData({ ...editFormData, sector: e.target.value })}
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  >
                    {SECTOR_OPTIONS.map(sec => (
                      <option key={sec} value={sec}>{sec}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Project Status
                  </label>
                  <select
                    value={editFormData.status || 'Under Review'}
                    onChange={(e) => setEditFormData({ ...editFormData, status: e.target.value })}
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  >
                    {STATUS_OPTIONS.map(st => (
                      <option key={st} value={st}>{st}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Department & Contractor Row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Department
                  </label>
                  <input
                    type="text"
                    value={editFormData.department_name || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, department_name: e.target.value })}
                    placeholder="e.g. Public Works Department"
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Contractor
                  </label>
                  <input
                    type="text"
                    value={editFormData.contractor_name || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, contractor_name: e.target.value })}
                    placeholder="e.g. L&T Infrastructure Projects Ltd."
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                </div>
              </div>

              {/* Location, District & Taluka */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Site Location
                  </label>
                  <input
                    type="text"
                    value={editFormData.location || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, location: e.target.value })}
                    placeholder="e.g. Kondhwa Budruk"
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    District
                  </label>
                  <input
                    type="text"
                    value={editFormData.district || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, district: e.target.value })}
                    placeholder="e.g. Pune"
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Taluka
                  </label>
                  <input
                    type="text"
                    value={editFormData.taluka || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, taluka: e.target.value })}
                    placeholder="e.g. Haveli"
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                </div>
              </div>

              {/* Financials: Sanctioned & Revised Budget in Lakhs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Sanctioned Budget (₹ Lakhs)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={editFormData.original_cost}
                    onChange={(e) => setEditFormData({ ...editFormData, original_cost: e.target.value })}
                    placeholder="e.g. 1500"
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 font-mono focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                  {editFormErrors.original_cost && (
                    <p className="text-[11px] text-red-600 mt-1">{editFormErrors.original_cost}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Revised Budget (₹ Lakhs, optional)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={editFormData.revised_cost}
                    onChange={(e) => setEditFormData({ ...editFormData, revised_cost: e.target.value })}
                    placeholder="Leave empty if not revised"
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 font-mono focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                </div>
              </div>

              {/* Timeline Dates */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={editFormData.start_date || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, start_date: e.target.value })}
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Target Completion Date
                  </label>
                  <input
                    type="date"
                    value={editFormData.planned_completion_date || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, planned_completion_date: e.target.value })}
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Revised Completion Date
                  </label>
                  <input
                    type="date"
                    value={editFormData.revised_completion_date || ''}
                    onChange={(e) => setEditFormData({ ...editFormData, revised_completion_date: e.target.value })}
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                  Scope of Work & Notes
                </label>
                <textarea
                  rows="3"
                  value={editFormData.description || ''}
                  onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                  placeholder="Enter detailed scope, technical parameters, or special administrative conditions..."
                  className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                />
              </div>

              {/* Modal Footer Actions */}
              <div className="pt-4 border-t border-gray-200 dark:border-slate-700 flex items-center justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setIsEditModalOpen(false)}
                  disabled={isSavingProject}
                  className="px-4 py-2 border border-gray-300 dark:border-slate-600 hover:bg-gray-50 dark:bg-slate-800/50 rounded-lg font-semibold text-xs text-[#14213D] dark:text-slate-100 transition disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSavingProject}
                  className="inline-flex items-center space-x-1.5 px-5 py-2 bg-[#1769D2] hover:bg-[#1459b8] text-white rounded-lg font-semibold text-xs shadow-sm transition disabled:opacity-50"
                >
                  {isSavingProject ? (
                    <>
                      <Loader2 size={13} className="animate-spin" />
                      <span>Saving Changes...</span>
                    </>
                  ) : (
                    <span>Save Changes</span>
                  )}
                </button>
              </div>

            </form>

          </div>
        </div>
      )}

      {/* ─── MODAL 2: SUBMIT PROGRESS UPDATE ──────────────────────────────── */}
      {isProgressModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 shadow-2xl max-w-lg w-full overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
            
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between bg-[#F5F7FA] dark:bg-slate-800">
              <div className="flex items-center space-x-2">
                <TrendingUp size={18} className="text-[#1769D2]" />
                <h3 className="text-base font-bold text-[#14213D] dark:text-slate-100">
                  Log Verified Progress Update
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setIsProgressModalOpen(false)}
                className="p-1.5 text-gray-400 dark:text-slate-500 hover:text-gray-700 dark:text-slate-300 rounded-lg hover:bg-gray-200 dark:bg-slate-700 transition"
              >
                <X size={16} />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmitProgress} className="p-6 space-y-4 text-xs">
              
              {progressFormErrors.submit && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-xl flex items-start space-x-2">
                  <AlertCircle size={15} className="text-red-500 shrink-0 mt-0.5" />
                  <span>{progressFormErrors.submit}</span>
                </div>
              )}

              {/* Project Badge */}
              <div className="bg-[#F5F7FA] dark:bg-slate-800 p-3 rounded-xl border border-gray-200 dark:border-slate-700 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-[#64748B] dark:text-slate-400 uppercase tracking-wider block">Project</span>
                  <span className="font-bold text-xs text-[#14213D] dark:text-slate-100 line-clamp-1">{project.name}</span>
                </div>
                <span className="font-mono text-xs font-bold text-[#1769D2] shrink-0 ml-2">{pCode}</span>
              </div>

              {/* Verification Report Date */}
              <div>
                <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                  Verification Report Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  required
                  value={progressFormData.report_date}
                  onChange={(e) => setProgressFormData({ ...progressFormData, report_date: e.target.value })}
                  className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                />
                {progressFormErrors.report_date && (
                  <p className="text-[11px] text-red-600 mt-1">{progressFormErrors.report_date}</p>
                )}
              </div>

              {/* Physical & Financial Progress */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Physical Progress (0-100%) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    required
                    value={progressFormData.physical_progress}
                    onChange={(e) => setProgressFormData({ ...progressFormData, physical_progress: e.target.value })}
                    placeholder="e.g. 75.0"
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 font-mono focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                  {progressFormErrors.physical_progress && (
                    <p className="text-[11px] text-red-600 mt-1">{progressFormErrors.physical_progress}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                    Financial Progress (0-100%) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    required
                    value={progressFormData.financial_progress}
                    onChange={(e) => setProgressFormData({ ...progressFormData, financial_progress: e.target.value })}
                    placeholder="e.g. 68.5"
                    className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 font-mono focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                  />
                  {progressFormErrors.financial_progress && (
                    <p className="text-[11px] text-red-600 mt-1">{progressFormErrors.financial_progress}</p>
                  )}
                </div>
              </div>

              {/* Cumulative Expenditure */}
              <div>
                <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                  Cumulative Expenditure (₹ Lakhs) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  value={progressFormData.expenditure}
                  onChange={(e) => setProgressFormData({ ...progressFormData, expenditure: e.target.value })}
                  placeholder="e.g. 1025.5"
                  className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 font-mono focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                />
                {progressFormErrors.expenditure && (
                  <p className="text-[11px] text-red-600 mt-1">{progressFormErrors.expenditure}</p>
                )}
              </div>

              {/* Reporting Officer */}
              <div>
                <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                  Reporting Officer Name
                </label>
                <input
                  type="text"
                  value={progressFormData.reported_by}
                  onChange={(e) => setProgressFormData({ ...progressFormData, reported_by: e.target.value })}
                  placeholder="e.g. Er. Rajesh Patil"
                  className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                />
              </div>

              {/* Remarks */}
              <div>
                <label className="block text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">
                  Site Observations & Field Remarks
                </label>
                <textarea
                  rows="3"
                  value={progressFormData.remarks}
                  onChange={(e) => setProgressFormData({ ...progressFormData, remarks: e.target.value })}
                  placeholder="e.g. Bituminous layer completed up to KM 14. Surface leveling verified on site."
                  className="w-full px-3 py-2 text-xs border border-gray-300 dark:border-slate-600 rounded-lg text-[#14213D] dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                />
              </div>

              {/* Footer Actions */}
              <div className="pt-4 border-t border-gray-200 dark:border-slate-700 flex items-center justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setIsProgressModalOpen(false)}
                  disabled={isSubmittingProgress}
                  className="px-4 py-2 border border-gray-300 dark:border-slate-600 hover:bg-gray-50 dark:bg-slate-800/50 rounded-lg font-semibold text-xs text-[#14213D] dark:text-slate-100 transition disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingProgress}
                  className="inline-flex items-center space-x-1.5 px-5 py-2 bg-[#1769D2] hover:bg-[#1459b8] text-white rounded-lg font-semibold text-xs shadow-sm transition disabled:opacity-50"
                >
                  {isSubmittingProgress ? (
                    <>
                      <Loader2 size={13} className="animate-spin" />
                      <span>Submitting...</span>
                    </>
                  ) : (
                    <span>Record Progress</span>
                  )}
                </button>
              </div>

            </form>

          </div>
        </div>
      )}

    </div>
  );
}
