import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  FileSpreadsheet,
  Download,
  FileText,
  PlusCircle,
  RefreshCw,
  Search,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Clock,
  ArrowUpRight,
  ShieldAlert,
  FileCheck2,
  Target,
  Building2,
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import { projectsApi, reportApi } from '../services/api';
import { formatDate } from '../utils/formatters';

/* ─── Report Types Configuration ───────────────────────────────────── */
const REPORT_TYPES = [
  {
    id: 'PROJECT_SUMMARY',
    name: 'Project Progress Summary',
    description: 'Overview of physical progress, financial expenditure, and milestone status.',
    badge: 'Summary',
  },
  {
    id: 'EXECUTIVE_PROJECT_REPORT',
    name: 'Executive Inspection Report',
    description: 'Comprehensive executive briefing report with verification audit logs.',
    badge: 'Executive',
  },
  {
    id: 'RISK_ASSESSMENT',
    name: 'Risk & Predictive Intelligence',
    description: 'Engineering risk evaluation score breakdown and ML overrun model drivers.',
    badge: 'Risk Audit',
  },
  {
    id: 'EARLY_WARNING',
    name: 'Early Warning Bottlenecks',
    description: 'Active threshold warnings, critical issue escalations, and action plans.',
    badge: 'Early Warnings',
  },
];

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default function Reports() {
  const [projects, setProjects] = useState([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [reports, setReports] = useState([]);
  const [reportsLoading, setReportsLoading] = useState(false);
  const [reportsError, setReportsError] = useState(null);

  const [selectedReportType, setSelectedReportType] = useState('PROJECT_SUMMARY');
  const [generating, setGenerating] = useState(false);
  const [downloadingId, setDownloadingId] = useState(null);
  const [notification, setNotification] = useState(null);

  // ─── Fetch Projects List ──────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    async function loadProjects() {
      setProjectsLoading(true);
      setProjectsError(null);
      try {
        const res = await projectsApi.list();
        if (!cancelled) {
          const list = Array.isArray(res.data) ? res.data : [];
          setProjects(list);
          if (list.length > 0) {
            const firstId = list[0].project_code || String(list[0].id);
            setSelectedProjectId(firstId);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setProjectsError('Unable to load projects list from backend.');
        }
      } finally {
        if (!cancelled) setProjectsLoading(false);
      }
    }
    loadProjects();
    return () => { cancelled = true; };
  }, []);

  // ─── Fetch Reports for Selected Project ───────────────────────────
  const fetchProjectReports = useCallback(async (projId) => {
    if (!projId) return;
    setReportsLoading(true);
    setReportsError(null);
    try {
      const res = await reportApi.getByProject(projId);
      setReports(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      if (err.response?.status === 404) {
        setReports([]);
      } else {
        setReportsError('Failed to fetch report listing for selected project.');
        setReports([]);
      }
    } finally {
      setReportsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      fetchProjectReports(selectedProjectId);
    }
  }, [selectedProjectId, fetchProjectReports]);

  const handleSelectProject = (projId) => {
    setSelectedProjectId(projId);
    setNotification(null);
  };

  // ─── Generate PDF Report ──────────────────────────────────────────
  const handleGenerateReport = async () => {
    if (!selectedProjectId) return;
    setGenerating(true);
    setNotification(null);
    try {
      const res = await reportApi.generate(selectedProjectId, selectedReportType);
      setNotification({
        type: 'success',
        message: `PDF report '${res.data?.file_name || selectedReportType}' generated successfully!`,
      });
      fetchProjectReports(selectedProjectId);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to generate PDF report. Officer authorization required.';
      setNotification({ type: 'error', message: msg });
    } finally {
      setGenerating(false);
    }
  };

  // ─── Download Report PDF ──────────────────────────────────────────
  const handleDownloadReport = async (reportId, fileName) => {
    setDownloadingId(reportId);
    setNotification(null);
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

      setNotification({
        type: 'success',
        message: `Downloaded report '${fileName || reportId}' successfully.`,
      });
    } catch (err) {
      const status = err.response?.status;
      let msg = 'Failed to download report file.';
      if (status === 404) msg = 'Physical PDF report file not found on server storage disk.';
      else if (status === 403) msg = 'Access forbidden: unauthorized file access.';
      else if (status === 500) msg = 'Server error streaming PDF report.';

      setNotification({ type: 'error', message: msg });
    } finally {
      setDownloadingId(null);
    }
  };

  // Filter Projects List
  const filteredProjects = projects.filter((p) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const code = (p.project_code || `id-${p.id}`).toLowerCase();
    const name = (p.name || '').toLowerCase();
    const district = (p.district || '').toLowerCase();
    return code.includes(q) || name.includes(q) || district.includes(q);
  });

  const selectedProjectObj = projects.find(
    (p) => String(p.id) === String(selectedProjectId) || p.project_code === selectedProjectId
  );

  return (
    <div className="min-h-full pb-12">
      <PageHeader
        title="Executive Reports & Audit Documentation"
        subtitle="Departmental progress summaries, executive PDF generation, and state audit documentation."
        badge="Phase 10"
        breadcrumbs={['SetuX', 'Executive Reports']}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">

        {/* Notification Banner */}
        {notification && (
          <div className={`p-4 rounded-xl border flex items-center justify-between text-xs ${
            notification.type === 'success' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-red-50 text-red-800 border-red-200'
          }`}>
            <div className="flex items-center space-x-2">
              {notification.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
              <span className="font-semibold">{notification.message}</span>
            </div>
            <button type="button" onClick={() => setNotification(null)} className="font-bold underline ml-4">
              Dismiss
            </button>
          </div>
        )}

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
                    No projects found.
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
                              <span className="text-[10px] text-[#64748B] dark:text-slate-400">{p.district || p.state || 'Maharashtra'}</span>
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

          {/* ─── Right: Reports Management Panel ──────────────────────────── */}
          <div className="lg:col-span-8 xl:col-span-9 space-y-6">

            {!selectedProjectId ? (
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-10 text-center space-y-4">
                <FileSpreadsheet size={32} className="text-[#1769D2] mx-auto" />
                <h3 className="text-base font-bold text-[#14213D] dark:text-slate-100">Select a Project to View & Generate Reports</h3>
              </div>
            ) : (
              <div className="space-y-6">

                {/* Project Header Bar */}
                {selectedProjectObj && (
                  <div className="flex flex-wrap items-center justify-between gap-3 bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 p-5 shadow-sm">
                    <div>
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-mono text-xs font-bold text-[#1769D2]">{selectedProjectObj.project_code || selectedProjectId}</span>
                        <span className="text-[10px] text-[#64748B] dark:text-slate-400 bg-gray-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">{selectedProjectObj.sector || 'Infrastructure'}</span>
                      </div>
                      <h2 className="text-base font-bold text-[#14213D] dark:text-slate-100">{selectedProjectObj.name}</h2>
                    </div>

                    <Link
                      to={`/projects/${selectedProjectId}`}
                      className="inline-flex items-center space-x-1 text-xs font-semibold text-[#1769D2] bg-white dark:bg-slate-900 hover:bg-[#EAF3FF] dark:bg-blue-950/40 px-3.5 py-2 rounded-lg border border-blue-200 transition"
                    >
                      <span>View Project Details</span>
                      <ArrowUpRight size={13} />
                    </Link>
                  </div>
                )}

                {/* 1. PDF Report Generator Card */}
                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-6 space-y-5">
                  <div className="flex items-center space-x-2 pb-3 border-b border-gray-100 dark:border-slate-800">
                    <FileCheck2 size={18} className="text-[#1769D2]" />
                    <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100">Generate Official Executive PDF Report</h3>
                  </div>

                  {/* Report Type Selector */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {REPORT_TYPES.map((type) => {
                      const isSelected = selectedReportType === type.id;
                      return (
                        <button
                          key={type.id}
                          type="button"
                          onClick={() => setSelectedReportType(type.id)}
                          className={`text-left p-3.5 rounded-xl border transition-all ${
                            isSelected
                              ? 'bg-[#EAF3FF] dark:bg-blue-950/40 border-[#1769D2] ring-1 ring-[#1769D2]'
                              : 'bg-white dark:bg-slate-900 border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:bg-slate-800/50'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-bold text-[#14213D] dark:text-slate-100">{type.name}</span>
                            <span className="text-[10px] font-semibold text-[#1769D2] bg-white dark:bg-slate-900 px-2 py-0.5 rounded border border-blue-200">
                              {type.badge}
                            </span>
                          </div>
                          <p className="text-[11px] text-[#64748B] dark:text-slate-400 leading-relaxed">{type.description}</p>
                        </button>
                      );
                    })}
                  </div>

                  <div className="pt-2 flex justify-end">
                    <button
                      type="button"
                      onClick={handleGenerateReport}
                      disabled={generating}
                      className="inline-flex items-center space-x-2 bg-[#1769D2] hover:bg-[#1459b8] text-white px-5 py-2.5 rounded-xl text-xs font-semibold shadow-sm transition disabled:opacity-60"
                    >
                      {generating ? (
                        <Loader2 size={15} className="animate-spin" />
                      ) : (
                        <PlusCircle size={15} />
                      )}
                      <span>{generating ? 'Generating PDF...' : 'Generate PDF Report'}</span>
                    </button>
                  </div>
                </div>

                {/* 2. Generated Reports History Table */}
                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-6 space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-slate-800">
                    <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2">
                      <FileSpreadsheet size={18} className="text-[#1769D2]" />
                      <span>Available Reports for Selected Project</span>
                    </h3>
                    <button
                      type="button"
                      onClick={() => fetchProjectReports(selectedProjectId)}
                      className="p-1.5 rounded-lg text-gray-500 dark:text-slate-400 hover:text-gray-900 bg-gray-50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700 transition"
                      title="Refresh report listing"
                    >
                      <RefreshCw size={13} className={reportsLoading ? 'animate-spin text-[#1769D2]' : ''} />
                    </button>
                  </div>

                  {reportsLoading ? (
                    <div className="p-8 text-center space-y-2">
                      <Loader2 size={20} className="text-[#1769D2] animate-spin mx-auto" />
                      <p className="text-xs text-[#64748B] dark:text-slate-400">Fetching report records...</p>
                    </div>
                  ) : reportsError ? (
                    <div className="p-6 text-center text-xs text-red-600 space-y-2">
                      <AlertCircle size={20} className="mx-auto text-red-400" />
                      <p>{reportsError}</p>
                    </div>
                  ) : reports.length === 0 ? (
                    <div className="p-8 text-center text-xs text-[#64748B] dark:text-slate-400 space-y-2">
                      <FileText size={28} className="mx-auto text-gray-300 dark:text-slate-600" />
                      <p className="font-semibold text-[#14213D] dark:text-slate-100">No reports available for this project.</p>
                      <p className="text-[11px]">Use the PDF generator above to create an official report.</p>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead>
                          <tr className="bg-[#F5F7FA] dark:bg-slate-800 text-[#64748B] dark:text-slate-400 font-bold border-b border-gray-200 dark:border-slate-700">
                            <th className="py-2.5 px-3">Report ID</th>
                            <th className="py-2.5 px-3">Report Type</th>
                            <th className="py-2.5 px-3">File Name</th>
                            <th className="py-2.5 px-3 text-center">File Size</th>
                            <th className="py-2.5 px-3">Generated Date</th>
                            <th className="py-2.5 px-3">Generated By</th>
                            <th className="py-2.5 px-3 text-right">Action</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
                          {reports.map((rpt) => {
                            const isDownloading = downloadingId === rpt.id;
                            return (
                              <tr key={rpt.id} className="hover:bg-[#EAF3FF] dark:bg-blue-950/40/40 transition-colors">
                                <td className="py-3 px-3 font-mono font-bold text-[#1769D2]">#{rpt.id}</td>
                                <td className="py-3 px-3">
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 dark:bg-blue-950/40 text-blue-700 border border-blue-200">
                                    {rpt.report_type}
                                  </span>
                                </td>
                                <td className="py-3 px-3 font-medium text-[#14213D] dark:text-slate-100 max-w-[200px] truncate">
                                  {rpt.file_name || `Report_${rpt.id}.pdf`}
                                </td>
                                <td className="py-3 px-3 text-center font-mono text-[#64748B] dark:text-slate-400">
                                  {formatBytes(rpt.file_size)}
                                </td>
                                <td className="py-3 px-3 text-[#64748B] dark:text-slate-400">
                                  {formatDate(rpt.created_at)}
                                </td>
                                <td className="py-3 px-3 text-[#64748B] dark:text-slate-400 text-[11px] truncate max-w-[120px]">
                                  {rpt.generated_by || 'Officer'}
                                </td>
                                <td className="py-3 px-3 text-right">
                                  <button
                                    type="button"
                                    onClick={() => handleDownloadReport(rpt.id, rpt.file_name)}
                                    disabled={isDownloading}
                                    className="inline-flex items-center space-x-1 bg-[#1769D2] hover:bg-[#1459b8] text-white px-3 py-1.5 rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-60"
                                  >
                                    {isDownloading ? (
                                      <Loader2 size={12} className="animate-spin" />
                                    ) : (
                                      <Download size={12} />
                                    )}
                                    <span>{isDownloading ? 'Downloading...' : 'Download PDF'}</span>
                                  </button>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>

              </div>
            )}

          </div>

        </div>
      </div>
    </div>
  );
}
