import { useState, useEffect, useMemo, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  SlidersHorizontal,
  FolderKanban,
  ArrowUpDown,
  RefreshCw,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  Building2,
  MapPin,
  Calendar,
  Filter,
  X,
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import { projectsApi } from '../services/api';
import { formatLakhs, formatDate, formatProgress, getStatusBadgeStyle } from '../utils/formatters';

// ─── Progress Color Helper ─────────────────────────────────────
function getProgressColor(value) {
  if (value >= 75) return { bar: 'bg-green-500', text: 'text-green-700 dark:text-green-400' };
  if (value >= 40) return { bar: 'bg-amber-500', text: 'text-amber-700 dark:text-amber-400' };
  return { bar: 'bg-red-500', text: 'text-red-700 dark:text-red-400' };
}

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedDistrict, setSelectedDistrict] = useState('ALL');
  const [selectedDepartment, setSelectedDepartment] = useState('ALL');
  const [showFilters, setShowFilters] = useState(false);

  // Sorting State
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 12;

  // Fetch Projects from Real Backend
  const fetchProjects = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await projectsApi.list({ limit: 500 });
      const data = Array.isArray(res.data) ? res.data : (res.data?.items || []);
      setProjects(data);
    } catch (err) {
      console.warn('Failed to fetch projects from backend:', err);
      setError('Unable to load project monitoring data. Please verify network connectivity.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  // Extract Unique Filter Options from Real Backend Data
  const districts = useMemo(() => {
    const set = new Set(projects.map(p => p.district).filter(Boolean));
    return Array.from(set).sort();
  }, [projects]);

  const departments = useMemo(() => {
    const set = new Set(projects.map(p => p.department_name || p.department).filter(Boolean));
    return Array.from(set).sort();
  }, [projects]);

  const statuses = useMemo(() => {
    const set = new Set(projects.map(p => p.status).filter(Boolean));
    return Array.from(set).sort();
  }, [projects]);

  const hasActiveFilters = searchQuery || selectedStatus !== 'ALL' || selectedDistrict !== 'ALL' || selectedDepartment !== 'ALL';

  // Filter & Search Logic
  const filteredProjects = useMemo(() => {
    let result = [...projects];

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      result = result.filter(p => {
        const name = (p.name || '').toLowerCase();
        const code = (p.project_code || p.project_id || '').toLowerCase();
        const dist = (p.district || '').toLowerCase();
        const loc = (p.location || p.location_name || '').toLowerCase();
        const dept = (p.department_name || p.department || '').toLowerCase();
        const contractor = (p.contractor_name || p.contractor || '').toLowerCase();
        const sector = (p.sector || p.project_type || '').toLowerCase();
        return (
          name.includes(query) ||
          code.includes(query) ||
          dist.includes(query) ||
          loc.includes(query) ||
          dept.includes(query) ||
          contractor.includes(query) ||
          sector.includes(query)
        );
      });
    }

    if (selectedStatus !== 'ALL') {
      result = result.filter(p => (p.status || '').toLowerCase() === selectedStatus.toLowerCase());
    }

    if (selectedDistrict !== 'ALL') {
      result = result.filter(p => (p.district || '').toLowerCase() === selectedDistrict.toLowerCase());
    }

    if (selectedDepartment !== 'ALL') {
      result = result.filter(p => (p.department_name || p.department || '').toLowerCase() === selectedDepartment.toLowerCase());
    }

    // Sort Logic
    result.sort((a, b) => {
      let valA, valB;
      switch (sortBy) {
        case 'budget':
          valA = a.original_cost || a.budget_lakh || 0;
          valB = b.original_cost || b.budget_lakh || 0;
          break;
        case 'progress':
          valA = a.physical_progress ?? a.reported_progress ?? 0;
          valB = b.physical_progress ?? b.reported_progress ?? 0;
          break;
        case 'startDate':
          valA = a.start_date || '';
          valB = b.start_date || '';
          break;
        case 'status':
          valA = a.status || '';
          valB = b.status || '';
          break;
        case 'code':
          valA = a.project_code || a.project_id || '';
          valB = b.project_code || b.project_id || '';
          break;
        case 'name':
        default:
          valA = a.name || '';
          valB = b.name || '';
      }

      if (typeof valA === 'string') {
        const comp = valA.localeCompare(valB);
        return sortOrder === 'asc' ? comp : -comp;
      }
      return sortOrder === 'asc' ? valA - valB : valB - valA;
    });

    return result;
  }, [projects, searchQuery, selectedStatus, selectedDistrict, selectedDepartment, sortBy, sortOrder]);

  // Pagination calculation
  const totalPages = Math.max(1, Math.ceil(filteredProjects.length / pageSize));
  const paginatedProjects = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredProjects.slice(start, start + pageSize);
  }, [filteredProjects, currentPage, pageSize]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedStatus('ALL');
    setSelectedDistrict('ALL');
    setSelectedDepartment('ALL');
    setSortBy('name');
    setSortOrder('asc');
    setCurrentPage(1);
  };

  return (
    <div className="min-h-full pb-16">
      {/* Page Header */}
      <PageHeader
        title="Project Monitoring"
        subtitle="Monitor infrastructure projects, implementation progress and project status."
        badge="Official Directory"
        breadcrumbs={['SetuX', 'Projects']}
        actions={
          <button
            type="button"
            onClick={fetchProjects}
            disabled={loading}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold text-[#14213D] dark:text-slate-200 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700 rounded-lg shadow-sm transition disabled:opacity-50"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
        }
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        
        {/* Controls: Search, Filters & Sorters */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-4 sm:p-5 shadow-sm space-y-4">
          
          {/* Search Row */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400 dark:text-slate-500">
                <Search size={16} />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
                placeholder="Search by project name, code, district, location, contractor..."
                className="w-full pl-10 pr-4 py-2.5 text-xs sm:text-sm border border-gray-300 dark:border-slate-700 rounded-xl text-[#14213D] dark:text-slate-200 placeholder:text-gray-400 dark:placeholder:text-slate-500 bg-[#F5F7FA] dark:bg-slate-800 focus:bg-white dark:focus:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-[#1769D2] focus:border-transparent transition"
              />
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <span className="text-xs font-semibold text-[#64748B] dark:text-slate-400 hidden md:inline tabular-nums">
                {filteredProjects.length} {filteredProjects.length === 1 ? 'Project' : 'Projects'}
              </span>
              <button
                type="button"
                onClick={() => setShowFilters(f => !f)}
                className={`inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border transition ${
                  showFilters || hasActiveFilters
                    ? 'bg-[#EAF3FF] dark:bg-blue-950/50 text-[#1769D2] dark:text-blue-400 border-blue-200 dark:border-blue-800/50'
                    : 'bg-white dark:bg-slate-800 text-[#64748B] dark:text-slate-400 border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700'
                }`}
              >
                <Filter size={13} />
                <span className="hidden sm:inline">Filters</span>
                {hasActiveFilters && (
                  <span className="w-1.5 h-1.5 rounded-full bg-[#1769D2]" />
                )}
              </button>
            </div>
          </div>

          {/* Filter Dropdowns — Collapsible */}
          {showFilters && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-3 border-t border-gray-100 dark:border-slate-800 animate-in">
              
              {/* Status Filter */}
              <div>
                <label className="block text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider mb-1">
                  Status
                </label>
                <select
                  value={selectedStatus}
                  onChange={(e) => { setSelectedStatus(e.target.value); setCurrentPage(1); }}
                  className="w-full py-2 px-3 text-xs bg-[#F5F7FA] dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg text-[#14213D] dark:text-slate-200 focus:bg-white dark:focus:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                >
                  <option value="ALL">All Statuses</option>
                  {statuses.map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              {/* District Filter */}
              <div>
                <label className="block text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider mb-1">
                  District
                </label>
                <select
                  value={selectedDistrict}
                  onChange={(e) => { setSelectedDistrict(e.target.value); setCurrentPage(1); }}
                  className="w-full py-2 px-3 text-xs bg-[#F5F7FA] dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg text-[#14213D] dark:text-slate-200 focus:bg-white dark:focus:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                >
                  <option value="ALL">All Districts</option>
                  {districts.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              {/* Department Filter */}
              <div>
                <label className="block text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider mb-1">
                  Department
                </label>
                <select
                  value={selectedDepartment}
                  onChange={(e) => { setSelectedDepartment(e.target.value); setCurrentPage(1); }}
                  className="w-full py-2 px-3 text-xs bg-[#F5F7FA] dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg text-[#14213D] dark:text-slate-200 focus:bg-white dark:focus:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                >
                  <option value="ALL">All Departments</option>
                  {departments.map(dept => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>

              {/* Sort By */}
              <div>
                <label className="block text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider mb-1">
                  Sort By
                </label>
                <select
                  value={`${sortBy}-${sortOrder}`}
                  onChange={(e) => {
                    const [field, order] = e.target.value.split('-');
                    setSortBy(field);
                    setSortOrder(order);
                  }}
                  className="w-full py-2 px-3 text-xs bg-[#F5F7FA] dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg text-[#14213D] dark:text-slate-200 focus:bg-white dark:focus:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
                >
                  <option value="name-asc">Project Name (A-Z)</option>
                  <option value="name-desc">Project Name (Z-A)</option>
                  <option value="budget-desc">Budget (Highest first)</option>
                  <option value="budget-asc">Budget (Lowest first)</option>
                  <option value="progress-desc">Progress (Highest first)</option>
                  <option value="progress-asc">Progress (Lowest first)</option>
                  <option value="startDate-desc">Start Date (Newest first)</option>
                </select>
              </div>

            </div>
          )}

          {/* Active Filter Indicators & Reset */}
          {hasActiveFilters && (
            <div className="pt-2 border-t border-gray-100 dark:border-slate-800 flex items-center justify-between text-xs text-[#64748B] dark:text-slate-400">
              <span>Filters applied — showing filtered results.</span>
              <button
                type="button"
                onClick={handleResetFilters}
                className="inline-flex items-center gap-1 text-[#1769D2] dark:text-blue-400 font-semibold hover:underline"
              >
                <X size={12} />
                Clear all filters
              </button>
            </div>
          )}

        </div>

        {/* State 1: Error State with Retry */}
        {error && (
          <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/60 rounded-2xl p-6 text-center space-y-4 max-w-lg mx-auto">
            <AlertCircle className="w-10 h-10 text-red-500 dark:text-red-400 mx-auto" />
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-red-800 dark:text-red-300">Unable to Load Project Data</h3>
              <p className="text-xs text-red-600 dark:text-red-400">{error}</p>
            </div>
            <button
              type="button"
              onClick={fetchProjects}
              className="inline-flex items-center space-x-1.5 bg-red-600 hover:bg-red-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition"
            >
              <RefreshCw size={13} />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* State 2: Loading Skeleton */}
        {loading && !error && (
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <div className="p-4 space-y-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="animate-pulse flex items-center justify-between p-3 border-b border-gray-100 dark:border-slate-800 last:border-0 gap-4">
                  <div className="space-y-2 flex-1">
                    <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-1/4"></div>
                    <div className="h-3 bg-gray-100 dark:bg-slate-800 rounded w-1/2"></div>
                  </div>
                  <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-20 hidden sm:block"></div>
                  <div className="h-4 bg-gray-200 dark:bg-slate-700 rounded w-24"></div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* State 3: Empty State */}
        {!loading && !error && filteredProjects.length === 0 && (
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-10 text-center space-y-4 max-w-md mx-auto">
            <div className="w-12 h-12 bg-gray-100 dark:bg-slate-800 text-gray-400 dark:text-slate-500 rounded-2xl flex items-center justify-center mx-auto">
              <FolderKanban size={24} />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-[#14213D] dark:text-slate-200">No Projects Available</h3>
              <p className="text-xs text-[#64748B] dark:text-slate-400">
                {projects.length === 0
                  ? 'There are currently no projects recorded in the system for this context.'
                  : 'No projects match your current search and filter criteria.'}
              </p>
            </div>
            {projects.length > 0 && (
              <button
                type="button"
                onClick={handleResetFilters}
                className="text-xs font-semibold text-[#1769D2] dark:text-blue-400 hover:underline"
              >
                Clear all filters
              </button>
            )}
          </div>
        )}

        {/* State 4: Real Data Table (Desktop) / Cards (Mobile) */}
        {!loading && !error && paginatedProjects.length > 0 && (
          <div className="space-y-4">
            
            {/* Desktop Table View (md and up) */}
            <div className="hidden md:block bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-[#F5F7FA] dark:bg-slate-800/80 border-b border-gray-200 dark:border-slate-700 text-[11px] font-bold text-[#64748B] dark:text-slate-400 uppercase tracking-wider">
                      <th
                        className="py-3 px-4 cursor-pointer hover:text-[#14213D] dark:hover:text-slate-200 transition-colors"
                        onClick={() => handleSort('code')}
                      >
                        <div className="flex items-center space-x-1">
                          <span>Project Code</span>
                          <ArrowUpDown size={11} className={sortBy === 'code' ? 'text-[#1769D2]' : ''} />
                        </div>
                      </th>
                      <th
                        className="py-3 px-4 cursor-pointer hover:text-[#14213D] dark:hover:text-slate-200 transition-colors"
                        onClick={() => handleSort('name')}
                      >
                        <div className="flex items-center space-x-1">
                          <span>Project Name</span>
                          <ArrowUpDown size={11} className={sortBy === 'name' ? 'text-[#1769D2]' : ''} />
                        </div>
                      </th>
                      <th className="py-3 px-4">Department</th>
                      <th className="py-3 px-4">District</th>
                      <th
                        className="py-3 px-4 cursor-pointer hover:text-[#14213D] dark:hover:text-slate-200 transition-colors"
                        onClick={() => handleSort('status')}
                      >
                        <div className="flex items-center space-x-1">
                          <span>Status</span>
                          <ArrowUpDown size={11} className={sortBy === 'status' ? 'text-[#1769D2]' : ''} />
                        </div>
                      </th>
                      <th
                        className="py-3 px-4 cursor-pointer hover:text-[#14213D] dark:hover:text-slate-200 transition-colors text-right"
                        onClick={() => handleSort('budget')}
                      >
                        <div className="flex items-center justify-end space-x-1">
                          <span>Sanctioned Budget</span>
                          <ArrowUpDown size={11} className={sortBy === 'budget' ? 'text-[#1769D2]' : ''} />
                        </div>
                      </th>
                      <th
                        className="py-3 px-4 cursor-pointer hover:text-[#14213D] dark:hover:text-slate-200 transition-colors"
                        onClick={() => handleSort('progress')}
                      >
                        <div className="flex items-center space-x-1">
                          <span>Physical Progress</span>
                          <ArrowUpDown size={11} className={sortBy === 'progress' ? 'text-[#1769D2]' : ''} />
                        </div>
                      </th>
                      <th className="py-3 px-4">Timeline</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
                    {paginatedProjects.map((p) => {
                      const pCode = p.project_code || p.project_id || String(p.id);
                      const progress = p.physical_progress ?? p.reported_progress ?? 0;
                      const budget = p.original_cost ?? p.budget_lakh ?? 0;
                      const progressColor = getProgressColor(progress);

                      return (
                        <tr
                          key={p.id || pCode}
                          className="hover:bg-blue-50/40 dark:hover:bg-blue-950/20 transition-colors group"
                        >
                          {/* Project Code */}
                          <td className="py-3.5 px-4 font-mono font-bold text-[#1769D2] dark:text-blue-400 whitespace-nowrap">
                            <Link
                              to={`/projects/${pCode}`}
                              className="hover:underline"
                            >
                              {pCode}
                            </Link>
                          </td>

                          {/* Project Name & Sector */}
                          <td className="py-3.5 px-4 max-w-xs">
                            <Link
                              to={`/projects/${pCode}`}
                              className="font-bold text-[#14213D] dark:text-slate-100 hover:text-[#1769D2] dark:hover:text-blue-400 line-clamp-1 block transition-colors"
                            >
                              {p.name}
                            </Link>
                            <span className="text-[11px] text-[#64748B] dark:text-slate-500 block truncate">
                              {p.sector || p.project_type || 'Infrastructure'}
                            </span>
                          </td>

                          {/* Department */}
                          <td className="py-3.5 px-4 text-[#14213D] dark:text-slate-300 whitespace-nowrap">
                            <span className="truncate max-w-[150px] block" title={p.department_name || p.department || '—'}>
                              {p.department_name || p.department || '—'}
                            </span>
                          </td>

                          {/* District */}
                          <td className="py-3.5 px-4 text-[#64748B] dark:text-slate-400 whitespace-nowrap">
                            {p.district ? (
                              <span className="inline-flex items-center space-x-1">
                                <MapPin size={11} className="text-gray-400 dark:text-slate-500" />
                                <span>{p.district}</span>
                              </span>
                            ) : (
                              '—'
                            )}
                          </td>

                          {/* Status */}
                          <td className="py-3.5 px-4 whitespace-nowrap">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadgeStyle(
                                p.status
                              )}`}
                            >
                              {p.status || 'Under Review'}
                            </span>
                          </td>

                          {/* Budget */}
                          <td className="py-3.5 px-4 text-right font-mono font-semibold text-[#14213D] dark:text-slate-200 whitespace-nowrap">
                            {formatLakhs(budget)}
                          </td>

                          {/* Progress */}
                          <td className="py-3.5 px-4 min-w-[130px]">
                            <div className="space-y-1">
                              <div className={`flex justify-between text-[11px] font-bold ${progressColor.text}`}>
                                <span>{formatProgress(progress)}</span>
                              </div>
                              <div className="w-full bg-gray-100 dark:bg-slate-700 rounded-full h-1.5 overflow-hidden">
                                <div
                                  className={`h-full rounded-full transition-all duration-500 ${progressColor.bar}`}
                                  style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                                />
                              </div>
                            </div>
                          </td>

                          {/* Timeline */}
                          <td className="py-3.5 px-4 text-[11px] text-[#64748B] dark:text-slate-400 whitespace-nowrap">
                            {p.start_date || p.planned_completion_date ? (
                              <span>
                                {formatDate(p.start_date)} → {formatDate(p.planned_completion_date || p.expected_completion)}
                              </span>
                            ) : (
                              '—'
                            )}
                          </td>

                          {/* Action */}
                          <td className="py-3.5 px-4 text-right whitespace-nowrap">
                            <Link
                              to={`/projects/${pCode}`}
                              className="inline-flex items-center space-x-1 text-xs font-bold text-[#1769D2] dark:text-blue-400 hover:text-[#1459b8] dark:hover:text-blue-300 group-hover:underline transition-colors"
                            >
                              <span>Inspect</span>
                              <ArrowRight size={12} />
                            </Link>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Mobile Cards View (sm and down) */}
            <div className="md:hidden space-y-3">
              {paginatedProjects.map((p) => {
                const pCode = p.project_code || p.project_id || String(p.id);
                const progress = p.physical_progress ?? p.reported_progress ?? 0;
                const budget = p.original_cost ?? p.budget_lakh ?? 0;
                const progressColor = getProgressColor(progress);

                return (
                  <div
                    key={p.id || pCode}
                    className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-4 shadow-sm space-y-3"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-0.5 min-w-0">
                        <span className="font-mono text-xs font-bold text-[#1769D2] dark:text-blue-400 block">
                          {pCode}
                        </span>
                        <h4 className="text-sm font-bold text-[#14213D] dark:text-slate-100 line-clamp-2">
                          {p.name}
                        </h4>
                      </div>
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border shrink-0 ${getStatusBadgeStyle(
                          p.status
                        )}`}
                      >
                        {p.status || 'Under Review'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-gray-100 dark:border-slate-800 text-[#64748B] dark:text-slate-400">
                      <div className="flex items-center space-x-1.5 truncate">
                        <Building2 size={13} className="text-gray-400 dark:text-slate-500 shrink-0" />
                        <span className="truncate">{p.department_name || p.department || '—'}</span>
                      </div>
                      <div className="flex items-center space-x-1.5 truncate">
                        <MapPin size={13} className="text-gray-400 dark:text-slate-500 shrink-0" />
                        <span className="truncate">{p.district || '—'}</span>
                      </div>
                    </div>

                    <div className="space-y-1 pt-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-[#64748B] dark:text-slate-400">Progress</span>
                        <span className={`font-bold ${progressColor.text}`}>{formatProgress(progress)}</span>
                      </div>
                      <div className="w-full bg-gray-100 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${progressColor.bar}`}
                          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-slate-800 text-xs">
                      <div>
                        <span className="text-[10px] text-[#64748B] dark:text-slate-500 block">Approved Budget</span>
                        <span className="font-mono font-bold text-[#14213D] dark:text-slate-200">{formatLakhs(budget)}</span>
                      </div>
                      <Link
                        to={`/projects/${pCode}`}
                        className="inline-flex items-center space-x-1 bg-[#EAF3FF] dark:bg-blue-950/50 hover:bg-blue-100 dark:hover:bg-blue-950/70 text-[#1769D2] dark:text-blue-400 px-3 py-1.5 rounded-lg font-bold text-xs transition"
                      >
                        <span>Inspect</span>
                        <ArrowRight size={13} />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
                <span className="text-[#64748B] dark:text-slate-400 tabular-nums">
                  Showing {(currentPage - 1) * pageSize + 1} to{' '}
                  {Math.min(currentPage * pageSize, filteredProjects.length)} of{' '}
                  {filteredProjects.length} projects
                </span>

                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    className="p-2 rounded-lg border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800 text-[#14213D] dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition"
                    aria-label="Previous page"
                  >
                    <ChevronLeft size={16} />
                  </button>

                  <span className="px-3 font-semibold text-[#14213D] dark:text-slate-200 tabular-nums">
                    Page {currentPage} of {totalPages}
                  </span>

                  <button
                    type="button"
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                    className="p-2 rounded-lg border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800 text-[#14213D] dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition"
                    aria-label="Next page"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            )}

          </div>
        )}

      </div>
    </div>
  );
}
