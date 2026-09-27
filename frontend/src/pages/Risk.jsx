import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  Search,
  ChevronRight,
  AlertTriangle,
  TrendingDown,
  Clock,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Loader2,
  ArrowUpRight,
  Info,
  XCircle,
  BarChart3,
  Target,
  FileWarning,
  Zap,
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import { projectsApi } from '../services/api';
import { formatLakhs } from '../utils/formatters';

/* ─── Risk Level Styling ───────────────────────────────────────────── */
const RISK_LEVEL_CONFIG = {
  LOW: { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', dot: 'bg-emerald-500', label: 'Low Risk' },
  MEDIUM: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', dot: 'bg-amber-500', label: 'Medium Risk' },
  HIGH: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', dot: 'bg-red-500', label: 'High Risk' },
  CRITICAL: { bg: 'bg-red-100', border: 'border-red-300', text: 'text-red-900', dot: 'bg-red-700', label: 'Critical Risk' },
};

const SEVERITY_BADGE = {
  LOW: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  MEDIUM: 'bg-amber-50 text-amber-700 border-amber-200',
  HIGH: 'bg-red-50 text-red-700 border-red-200',
  CRITICAL: 'bg-red-100 text-red-900 border-red-300',
};

function getRiskLevelStyle(level) {
  return RISK_LEVEL_CONFIG[level] || RISK_LEVEL_CONFIG.LOW;
}

function formatFactorName(factor) {
  if (!factor) return '';
  return factor
    .replace(/_/g, ' ')
    .replace(/ML PREDICTION/i, '(ML)')
    .split(' ')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ');
}

function formatProbability(prob) {
  if (prob === null || prob === undefined || isNaN(prob)) return '—';
  return `${(prob * 100).toFixed(1)}%`;
}

/* ─── Risk Score Bar (0–100) ───────────────────────────────────────── */
function RiskScoreBar({ score, level }) {
  const style = getRiskLevelStyle(level);
  const clampedScore = Math.min(100, Math.max(0, score));
  return (
    <div className="space-y-2">
      <div className="flex items-end justify-between">
        <div>
          <span className="text-3xl font-bold text-[#14213D] dark:text-slate-100 font-mono">{score.toFixed(1)}</span>
          <span className="text-sm text-[#64748B] dark:text-slate-400 ml-1">/ 100</span>
        </div>
        <span className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold border ${style.bg} ${style.border} ${style.text}`}>
          <span className={`w-2 h-2 rounded-full ${style.dot}`} />
          <span>{level}</span>
        </span>
      </div>
      <div className="w-full bg-gray-100 dark:bg-slate-800 rounded-full h-2.5 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${
            level === 'CRITICAL' ? 'bg-red-700' :
            level === 'HIGH' ? 'bg-red-500' :
            level === 'MEDIUM' ? 'bg-amber-500' : 'bg-emerald-500'
          }`}
          style={{ width: `${clampedScore}%` }}
        />
      </div>
      <div className="flex justify-between text-[10px] text-[#64748B] dark:text-slate-400 font-medium">
        <span>0 — Low</span>
        <span>25 — Medium</span>
        <span>50 — High</span>
        <span>75 — Critical</span>
      </div>
    </div>
  );
}

/* ─── Prediction Card ──────────────────────────────────────────────── */
function PredictionCard({ title, icon: Icon, prediction, isLoading, error }) {
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 p-5 space-y-3 animate-pulse">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gray-100 dark:bg-slate-800 rounded-lg" />
          <div className="h-4 bg-gray-100 dark:bg-slate-800 rounded w-40" />
        </div>
        <div className="h-6 bg-gray-100 dark:bg-slate-800 rounded w-24" />
        <div className="h-2 bg-gray-100 dark:bg-slate-800 rounded w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 p-5 space-y-3">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gray-100 dark:bg-slate-800 rounded-lg flex items-center justify-center">
            <Icon size={16} className="text-gray-400 dark:text-slate-500" />
          </div>
          <span className="text-sm font-bold text-[#14213D] dark:text-slate-100">{title}</span>
        </div>
        <div className="flex items-center space-x-2 text-xs text-amber-700 bg-amber-50 p-3 rounded-lg border border-amber-200">
          <FileWarning size={14} className="shrink-0" />
          <span>Prediction unavailable. {typeof error === 'string' ? error : ''}</span>
        </div>
      </div>
    );
  }

  if (!prediction || !prediction.is_available) {
    const reason = prediction?.error || 'Model is not currently trained or available.';
    return (
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 p-5 space-y-3">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gray-100 dark:bg-slate-800 rounded-lg flex items-center justify-center">
            <Icon size={16} className="text-gray-400 dark:text-slate-500" />
          </div>
          <span className="text-sm font-bold text-[#14213D] dark:text-slate-100">{title}</span>
        </div>
        <div className="flex items-center space-x-2 text-xs text-[#64748B] dark:text-slate-400 bg-gray-50 dark:bg-slate-800/50 p-3 rounded-lg border border-gray-200 dark:border-slate-700">
          <Info size={14} className="shrink-0" />
          <span>{reason}</span>
        </div>
      </div>
    );
  }

  const prob = prediction.probability;
  const hasRisk = prediction.has_overrun_risk || prediction.prediction?.includes('OVERRUN');
  const probPct = (prob * 100).toFixed(1);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${hasRisk ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-600'}`}>
            <Icon size={16} />
          </div>
          <span className="text-sm font-bold text-[#14213D] dark:text-slate-100">{title}</span>
        </div>
        {prediction.model_name && (
          <span className="text-[10px] text-[#64748B] dark:text-slate-400 bg-gray-50 dark:bg-slate-800/50 px-2 py-0.5 rounded border border-gray-200 dark:border-slate-700">
            {prediction.model_name}
          </span>
        )}
      </div>

      <div className="flex items-end justify-between">
        <div>
          <span className={`text-2xl font-bold font-mono ${hasRisk ? 'text-red-700' : 'text-emerald-700'}`}>
            {probPct}%
          </span>
          <span className="text-xs text-[#64748B] dark:text-slate-400 ml-2">model output probability</span>
        </div>
        <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${
          hasRisk ? 'bg-red-50 text-red-700 border-red-200' : 'bg-emerald-50 text-emerald-700 border-emerald-200'
        }`}>
          {hasRisk ? <AlertTriangle size={11} /> : <CheckCircle2 size={11} />}
          <span>{hasRisk ? 'Risk Detected' : 'No Risk Detected'}</span>
        </span>
      </div>

      <div className="w-full bg-gray-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${hasRisk ? 'bg-red-500' : 'bg-emerald-500'}`}
          style={{ width: `${Math.min(100, prob * 100)}%` }}
        />
      </div>

      {prediction.top_factors && prediction.top_factors.length > 0 && (
        <div className="space-y-1.5 pt-2 border-t border-gray-100 dark:border-slate-800">
          <span className="text-[10px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider">Top Contributing Features</span>
          {prediction.top_factors.slice(0, 3).map((f, i) => (
            <div key={i} className="flex items-center justify-between text-xs">
              <span className="text-[#14213D] dark:text-slate-100 font-medium truncate max-w-[60%]">
                {f.feature?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
              </span>
              <span className="text-[#64748B] dark:text-slate-400 font-mono text-[11px]">
                {f.current_value !== null && f.current_value !== undefined ? String(f.current_value) : '—'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ─── Risk Factor Row ──────────────────────────────────────────────── */
function RiskFactorRow({ factor }) {
  const severity = factor.severity || 'LOW';
  const badgeStyle = SEVERITY_BADGE[severity] || SEVERITY_BADGE.LOW;
  const isObserved = factor.type === 'OBSERVED';

  return (
    <div className="flex flex-col sm:flex-row sm:items-start gap-3 p-3.5 rounded-xl bg-[#F5F7FA] dark:bg-slate-800 border border-gray-200 dark:border-slate-700 hover:bg-white dark:bg-slate-900 transition-colors">
      <div className="flex-1 space-y-1.5 min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold text-[#14213D] dark:text-slate-100">{formatFactorName(factor.factor)}</span>
          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${badgeStyle}`}>
            {severity}
          </span>
          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
            isObserved ? 'bg-blue-50 dark:bg-blue-950/40 text-blue-700 border-blue-200' : 'bg-purple-50 text-purple-700 border-purple-200'
          }`}>
            {isObserved ? 'Observed' : 'Predictive'}
          </span>
          {factor.category && (
            <span className="text-[10px] text-[#64748B] dark:text-slate-400 font-medium">{factor.category}</span>
          )}
        </div>
        <p className="text-[11px] text-[#64748B] dark:text-slate-400 leading-relaxed">
          {factor.explanation || factor.reason || 'No explanation available.'}
        </p>
      </div>
      {(factor.score_contribution > 0 || (factor.evidence?.predicted_probability !== undefined)) && (
        <div className="shrink-0 text-right">
          {factor.score_contribution > 0 && (
            <div>
              <span className="text-[10px] text-[#64748B] dark:text-slate-400 block">Score Impact</span>
              <span className="text-sm font-bold font-mono text-[#14213D] dark:text-slate-100">+{factor.score_contribution.toFixed(1)}</span>
            </div>
          )}
          {factor.evidence?.predicted_probability !== undefined && (
            <div className="mt-1">
              <span className="text-[10px] text-[#64748B] dark:text-slate-400 block">Probability</span>
              <span className="text-sm font-bold font-mono text-[#14213D] dark:text-slate-100">{formatProbability(factor.evidence.predicted_probability)}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
   MAIN RISK INTELLIGENCE PAGE
   ═══════════════════════════════════════════════════════════════════════ */
export default function Risk() {
  const [projects, setProjects] = useState([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [riskData, setRiskData] = useState(null);
  const [riskLoading, setRiskLoading] = useState(false);
  const [riskError, setRiskError] = useState(null);

  const fetchInFlightRef = useRef(null);

  // ─── Load Projects ────────────────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    async function loadProjects() {
      setProjectsLoading(true);
      setProjectsError(null);
      try {
        const res = await projectsApi.list();
        if (!cancelled) {
          setProjects(Array.isArray(res.data) ? res.data : []);
        }
      } catch (err) {
        if (!cancelled) {
          setProjectsError(
            err.response?.status === 401
              ? 'Authentication required. Please log in.'
              : 'Unable to load projects. Please check connection.'
          );
        }
      } finally {
        if (!cancelled) setProjectsLoading(false);
      }
    }
    loadProjects();
    return () => { cancelled = true; };
  }, []);

  // ─── Load Risk Intelligence for Selected Project ──────────────────────────
  const fetchRiskIntelligence = useCallback(async (projectId) => {
    if (!projectId) return;

    const fetchId = Date.now();
    fetchInFlightRef.current = fetchId;

    setRiskLoading(true);
    setRiskError(null);
    setRiskData(null);

    try {
      const res = await projectsApi.getRiskIntelligence(projectId);
      if (fetchInFlightRef.current === fetchId) {
        setRiskData(res.data);
      }
    } catch (err) {
      if (fetchInFlightRef.current === fetchId) {
        const status = err.response?.status;
        if (status === 401 || status === 403) {
          setRiskError('Access denied. You may not have permission to view risk intelligence for this project.');
        } else if (status === 404) {
          setRiskError('Risk intelligence data not found for this project.');
        } else if (status === 422) {
          setRiskError('Invalid project identifier.');
        } else if (status === 500) {
          setRiskError('Server error while computing risk intelligence. Please try again later.');
        } else {
          setRiskError('Unable to load risk intelligence. Please check your connection and try again.');
        }
      }
    } finally {
      if (fetchInFlightRef.current === fetchId) {
        setRiskLoading(false);
      }
    }
  }, []);

  const handleSelectProject = useCallback((projId) => {
    setSelectedProjectId(projId);
    fetchRiskIntelligence(projId);
  }, [fetchRiskIntelligence]);

  // ─── Filtered Projects ─────────────────────────────────────────────────
  const filteredProjects = projects.filter((p) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const code = (p.project_code || '').toLowerCase();
    const name = (p.name || '').toLowerCase();
    const district = (p.district || '').toLowerCase();
    const sector = (p.sector || '').toLowerCase();
    return code.includes(q) || name.includes(q) || district.includes(q) || sector.includes(q);
  });

  const selectedProject = projects.find(
    (p) => String(p.id) === String(selectedProjectId) || p.project_code === selectedProjectId
  );

  return (
    <div className="min-h-full pb-12">
      <PageHeader
        title="Risk Intelligence"
        subtitle="Integrated rule-based and ML-powered risk assessment for government infrastructure projects."
        badge="Phase 6"
        breadcrumbs={['SetuX', 'Risk Intelligence']}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* ─── Left: Project Selector ─────────────────────────────────────── */}
          <div className="lg:col-span-4 xl:col-span-3 space-y-4">
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-gray-100 dark:border-slate-800">
                <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2 mb-3">
                  <Target size={16} className="text-[#1769D2]" />
                  <span>Select Project</span>
                </h3>
                <div className="relative">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-slate-500" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by name, code, district..."
                    className="w-full pl-9 pr-3 py-2 text-xs border border-gray-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1769D2] text-[#14213D] dark:text-slate-100"
                  />
                </div>
              </div>

              <div className="max-h-[60vh] overflow-y-auto">
                {projectsLoading ? (
                  <div className="p-8 text-center">
                    <Loader2 size={20} className="text-[#1769D2] animate-spin mx-auto" />
                    <p className="text-xs text-[#64748B] dark:text-slate-400 mt-2">Loading projects...</p>
                  </div>
                ) : projectsError ? (
                  <div className="p-6 text-center text-xs text-red-600 space-y-2">
                    <AlertCircle size={20} className="mx-auto text-red-400" />
                    <p>{projectsError}</p>
                  </div>
                ) : filteredProjects.length === 0 ? (
                  <div className="p-6 text-center text-xs text-[#64748B] dark:text-slate-400">
                    <p className="font-semibold text-[#14213D] dark:text-slate-100">No projects found</p>
                    {searchQuery && <p className="mt-1">Try a different search term.</p>}
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100 dark:divide-slate-800">
                    {filteredProjects.map((p) => {
                      const pId = p.project_code || String(p.id);
                      const isSelected = String(selectedProjectId) === pId || String(selectedProjectId) === String(p.id);
                      return (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => handleSelectProject(pId)}
                          className={`w-full text-left px-4 py-3 transition-colors hover:bg-[#EAF3FF] dark:bg-blue-950/40/60 ${
                            isSelected ? 'bg-[#EAF3FF] dark:bg-blue-950/40 border-l-2 border-l-[#1769D2]' : ''
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="min-w-0">
                              <span className="text-[10px] font-mono font-bold text-[#1769D2] block">{p.project_code || `ID-${p.id}`}</span>
                              <span className="text-xs font-semibold text-[#14213D] dark:text-slate-100 block truncate">{p.name}</span>
                              <span className="text-[10px] text-[#64748B] dark:text-slate-400">{p.district || p.state || 'Maharashtra'} • {p.sector || 'Infrastructure'}</span>
                            </div>
                            <ChevronRight size={14} className="text-gray-300 dark:text-slate-600 shrink-0" />
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* ─── Right: Risk Intelligence Content ──────────────────────────── */}
          <div className="lg:col-span-8 xl:col-span-9 space-y-6">
            {!selectedProjectId ? (
              /* Empty State */
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-10 text-center space-y-4">
                <div className="w-14 h-14 bg-[#EAF3FF] dark:bg-blue-950/40 rounded-2xl border border-blue-100 flex items-center justify-center mx-auto">
                  <ShieldAlert size={28} className="text-[#1769D2]" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-[#14213D] dark:text-slate-100">Select a Project</h3>
                  <p className="text-xs text-[#64748B] dark:text-slate-400 mt-1 max-w-md mx-auto">
                    Choose a project from the list to view its comprehensive risk intelligence assessment, 
                    including rule-based indicators and ML predictions.
                  </p>
                </div>
              </div>
            ) : riskLoading ? (
              /* Loading State */
              <div className="space-y-4">
                {/* Skeleton cards */}
                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 animate-pulse space-y-4">
                  <div className="h-5 bg-gray-100 dark:bg-slate-800 rounded w-60" />
                  <div className="h-8 bg-gray-100 dark:bg-slate-800 rounded w-32" />
                  <div className="h-2 bg-gray-100 dark:bg-slate-800 rounded w-full" />
                  <div className="h-2 bg-gray-100 dark:bg-slate-800 rounded w-3/4" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 p-5 animate-pulse space-y-3">
                    <div className="h-4 bg-gray-100 dark:bg-slate-800 rounded w-40" />
                    <div className="h-6 bg-gray-100 dark:bg-slate-800 rounded w-24" />
                  </div>
                  <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-700 p-5 animate-pulse space-y-3">
                    <div className="h-4 bg-gray-100 dark:bg-slate-800 rounded w-40" />
                    <div className="h-6 bg-gray-100 dark:bg-slate-800 rounded w-24" />
                  </div>
                </div>
                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-6 animate-pulse space-y-3">
                  <div className="h-4 bg-gray-100 dark:bg-slate-800 rounded w-48" />
                  <div className="h-3 bg-gray-100 dark:bg-slate-800 rounded w-full" />
                  <div className="h-3 bg-gray-100 dark:bg-slate-800 rounded w-5/6" />
                </div>
              </div>
            ) : riskError ? (
              /* Error State */
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-8 text-center space-y-4">
                <div className="w-14 h-14 bg-red-50 rounded-2xl border border-red-200 flex items-center justify-center mx-auto">
                  <XCircle size={28} className="text-red-500" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-red-800">Risk Intelligence Unavailable</h3>
                  <p className="text-xs text-red-600 mt-1 max-w-md mx-auto">{riskError}</p>
                </div>
                <button
                  type="button"
                  onClick={() => fetchRiskIntelligence(selectedProjectId)}
                  className="inline-flex items-center space-x-1.5 bg-[#1769D2] hover:bg-[#1459b8] text-white px-4 py-2 rounded-lg text-xs font-semibold transition"
                >
                  <RefreshCw size={13} />
                  <span>Retry</span>
                </button>
              </div>
            ) : riskData ? (
              /* ─── REAL RISK INTELLIGENCE ─────────────────────────────── */
              <div className="space-y-6">

                {/* Header: Project Info + Refresh */}
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-0.5">
                      <span className="font-mono text-xs font-bold text-[#1769D2]">{riskData.project_code || selectedProjectId}</span>
                      {riskData.sector && <span className="text-[10px] text-[#64748B] dark:text-slate-400 bg-gray-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">{riskData.sector}</span>}
                      {riskData.district && <span className="text-[10px] text-[#64748B] dark:text-slate-400 bg-gray-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">{riskData.district}</span>}
                    </div>
                    <h2 className="text-base sm:text-lg font-bold text-[#14213D] dark:text-slate-100 truncate">{riskData.project_name}</h2>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Link
                      to={`/projects/${selectedProjectId}`}
                      className="inline-flex items-center space-x-1 text-xs font-semibold text-[#1769D2] bg-white dark:bg-slate-900 hover:bg-[#EAF3FF] dark:bg-blue-950/40 px-3 py-1.5 rounded-lg border border-blue-200 transition"
                    >
                      <span>View Project</span>
                      <ArrowUpRight size={12} />
                    </Link>
                    <button
                      type="button"
                      onClick={() => fetchRiskIntelligence(selectedProjectId)}
                      className="p-2 rounded-lg text-gray-500 dark:text-slate-400 hover:text-gray-900 bg-white dark:bg-slate-900 hover:bg-gray-50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700 transition"
                      title="Refresh risk intelligence"
                    >
                      <RefreshCw size={14} />
                    </button>
                  </div>
                </div>

                {/* 1. Overall Risk Score */}
                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-6 space-y-5">
                  <div className="flex items-center space-x-2 pb-3 border-b border-gray-100 dark:border-slate-800">
                    <ShieldAlert size={18} className="text-[#1769D2]" />
                    <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100">Overall Risk Assessment</h3>
                    {riskData.overall_risk?.version && (
                      <span className="text-[10px] text-[#64748B] dark:text-slate-400 bg-gray-50 dark:bg-slate-800/50 px-2 py-0.5 rounded border border-gray-200 dark:border-slate-700 ml-auto">
                        {riskData.overall_risk.version}
                      </span>
                    )}
                  </div>

                  <RiskScoreBar
                    score={riskData.overall_risk?.score ?? 0}
                    level={riskData.overall_risk?.level || 'LOW'}
                  />

                  {/* Score Composition */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                    <div className="bg-[#F5F7FA] dark:bg-slate-800 rounded-xl p-3 border border-gray-200 dark:border-slate-700">
                      <span className="text-[10px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider block">Rule-Based Baseline Score</span>
                      <span className="text-lg font-bold font-mono text-[#14213D] dark:text-slate-100">
                        {riskData.overall_risk?.rule_based_baseline_score !== null && riskData.overall_risk?.rule_based_baseline_score !== undefined
                          ? riskData.overall_risk.rule_based_baseline_score.toFixed(1)
                          : '—'}
                      </span>
                      <span className="text-[10px] text-[#64748B] dark:text-slate-400 ml-1">/ 100 (70% weight)</span>
                    </div>
                    <div className="bg-[#F5F7FA] dark:bg-slate-800 rounded-xl p-3 border border-gray-200 dark:border-slate-700">
                      <span className="text-[10px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider block">Predictive ML Score</span>
                      <span className="text-lg font-bold font-mono text-[#14213D] dark:text-slate-100">
                        {riskData.overall_risk?.predictive_ml_score !== null && riskData.overall_risk?.predictive_ml_score !== undefined
                          ? riskData.overall_risk.predictive_ml_score.toFixed(1)
                          : '—'}
                      </span>
                      <span className="text-[10px] text-[#64748B] dark:text-slate-400 ml-1">
                        {riskData.overall_risk?.predictive_ml_score !== null ? '/ 100 (30% weight)' : 'Not available'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 2. Risk Summary */}
                {riskData.summary && (
                  <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-5">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-blue-50 dark:bg-blue-950/40 rounded-lg flex items-center justify-center shrink-0">
                        <BarChart3 size={16} className="text-[#1769D2]" />
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-[#14213D] dark:text-slate-100 mb-1">Risk Summary</h4>
                        <p className="text-xs text-[#64748B] dark:text-slate-400 leading-relaxed">{riskData.summary}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* 3. ML Predictions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <PredictionCard
                    title="Cost Overrun Prediction"
                    icon={TrendingDown}
                    prediction={riskData.cost_overrun_prediction}
                    isLoading={false}
                    error={null}
                  />
                  <PredictionCard
                    title="Time Overrun Prediction"
                    icon={Clock}
                    prediction={riskData.time_overrun_prediction}
                    isLoading={false}
                    error={null}
                  />
                </div>

                {/* 4. Risk Factors / Drivers */}
                {riskData.prioritized_risk_factors && riskData.prioritized_risk_factors.length > 0 && (
                  <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-6 space-y-4">
                    <div className="flex items-center space-x-2 pb-3 border-b border-gray-100 dark:border-slate-800">
                      <Zap size={16} className="text-amber-500" />
                      <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100">Risk Drivers</h3>
                      <span className="text-[10px] text-[#64748B] dark:text-slate-400 bg-gray-50 dark:bg-slate-800/50 px-2 py-0.5 rounded border border-gray-200 dark:border-slate-700 ml-auto">
                        {riskData.prioritized_risk_factors.length} factor{riskData.prioritized_risk_factors.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                    <div className="space-y-3">
                      {riskData.prioritized_risk_factors.map((f, i) => (
                        <RiskFactorRow key={`${f.factor}-${i}`} factor={f} />
                      ))}
                    </div>
                  </div>
                )}

                {/* 5. Recommended Actions */}
                {((riskData.recommendations && riskData.recommendations.length > 0) || (riskData.recommended_actions && riskData.recommended_actions.length > 0)) && (
                  <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-6 space-y-4">
                    <div className="flex items-center space-x-2 pb-3 border-b border-gray-100 dark:border-slate-800">
                      <CheckCircle2 size={16} className="text-emerald-600" />
                      <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100">Recommended Actions</h3>
                    </div>
                    <ul className="space-y-2">
                      {(riskData.recommendations || riskData.recommended_actions).map((action, i) => (
                        <li key={i} className="flex items-start space-x-2.5 text-xs">
                          <span className="w-5 h-5 bg-[#EAF3FF] dark:bg-blue-950/40 text-[#1769D2] rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                            {i + 1}
                          </span>
                          <span className="text-[#14213D] dark:text-slate-100 leading-relaxed">{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 6. Data Quality */}
                {riskData.data_quality && (
                  <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-5">
                    <div className="flex items-center space-x-2 pb-3 border-b border-gray-100 dark:border-slate-800 mb-3">
                      <Info size={16} className="text-[#64748B] dark:text-slate-400" />
                      <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100">Data Quality & Model Availability</h3>
                    </div>
                    <div className="flex flex-wrap gap-3 text-xs">
                      <div className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border ${
                        riskData.data_quality.status === 'COMPLETE' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                        riskData.data_quality.status === 'PARTIAL' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                        'bg-red-50 text-red-700 border-red-200'
                      }`}>
                        {riskData.data_quality.status === 'COMPLETE' ? <CheckCircle2 size={13} /> :
                         riskData.data_quality.status === 'PARTIAL' ? <AlertTriangle size={13} /> :
                         <XCircle size={13} />}
                        <span className="font-semibold">
                          {riskData.data_quality.status === 'COMPLETE' ? 'All Components Available' :
                           riskData.data_quality.status === 'PARTIAL' ? 'Partial Data Coverage' :
                           'Insufficient Data'}
                        </span>
                      </div>

                      {riskData.data_quality.available_components?.map((c, i) => (
                        <span key={i} className="inline-flex items-center space-x-1 px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg">
                          <CheckCircle2 size={11} />
                          <span className="font-medium">{c.replace(/_/g, ' ').replace(/\b\w/g, ch => ch.toUpperCase())}</span>
                        </span>
                      ))}

                      {riskData.data_quality.missing_components?.map((c, i) => (
                        <span key={i} className="inline-flex items-center space-x-1 px-2.5 py-1 bg-gray-50 dark:bg-slate-800/50 text-[#64748B] dark:text-slate-400 border border-gray-200 dark:border-slate-700 rounded-lg">
                          <XCircle size={11} />
                          <span className="font-medium">{c.replace(/_/g, ' ').replace(/\b\w/g, ch => ch.toUpperCase())}</span>
                        </span>
                      ))}
                    </div>

                    {riskData.data_quality.missing_data_fields?.length > 0 && (
                      <div className="mt-3 text-[11px] text-amber-700 bg-amber-50 p-2.5 rounded-lg border border-amber-200">
                        <span className="font-bold">Missing Data Fields: </span>
                        {riskData.data_quality.missing_data_fields.map(f => f.replace(/_/g, ' ')).join(', ')}
                      </div>
                    )}
                  </div>
                )}

                {/* 7. Disclaimer */}
                {riskData.disclaimer && (
                  <div className="text-[10px] text-[#64748B] dark:text-slate-400 bg-[#F5F7FA] dark:bg-slate-800 px-4 py-3 rounded-xl border border-gray-200 dark:border-slate-700 leading-relaxed">
                    <span className="font-bold uppercase tracking-wider">Disclaimer: </span>
                    {riskData.disclaimer}
                  </div>
                )}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
