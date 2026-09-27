import { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Map,
  Search,
  RefreshCw,
  Building2,
  MapPin,
  AlertTriangle,
  ArrowUpRight,
  Loader2,
  FileQuestion,
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import ProjectsMap from '../components/maps/ProjectsMap';
import { projectsApi } from '../services/api';

export default function MapView() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sectorFilter, setSectorFilter] = useState('');

  // ─── Fetch Projects ───────────────────────────────────────────────
  const fetchProjects = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await projectsApi.list();
      setProjects(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setError(
        err.response?.status === 401
          ? 'Authentication required to access GIS project map.'
          : 'Unable to load projects from backend.'
      );
      setProjects([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  // ─── Coordinate Validity Helper ───────────────────────────────────
  const hasValidCoordinates = (proj) => {
    const lat = proj.latitude ?? proj.lat;
    const lng = proj.longitude ?? proj.lng;
    return (
      lat !== null &&
      lat !== undefined &&
      lng !== null &&
      lng !== undefined &&
      !isNaN(Number(lat)) &&
      !isNaN(Number(lng)) &&
      (Number(lat) !== 0 || Number(lng) !== 0)
    );
  };

  // ─── Filtered Projects ───────────────────────────────────────────
  const filteredProjects = useMemo(() => {
    return projects.filter((p) => {
      if (statusFilter && (p.status || '').toLowerCase() !== statusFilter.toLowerCase()) {
        return false;
      }
      if (sectorFilter && (p.sector || '').toLowerCase() !== sectorFilter.toLowerCase()) {
        return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const code = (p.project_code || `id-${p.id}`).toLowerCase();
        const name = (p.name || '').toLowerCase();
        const district = (p.district || '').toLowerCase();
        const sector = (p.sector || '').toLowerCase();
        if (!code.includes(q) && !name.includes(q) && !district.includes(q) && !sector.includes(q)) {
          return false;
        }
      }
      return true;
    });
  }, [projects, statusFilter, sectorFilter, searchQuery]);

  // Mapped vs Unmapped project counts
  const mappedProjects = useMemo(() => filteredProjects.filter(hasValidCoordinates), [filteredProjects]);
  const unmappedProjects = useMemo(() => filteredProjects.filter((p) => !hasValidCoordinates(p)), [filteredProjects]);

  // Unique sectors for filter dropdown
  const availableSectors = useMemo(() => {
    const set = new Set();
    projects.forEach((p) => { if (p.sector) set.add(p.sector); });
    return Array.from(set);
  }, [projects]);

  // Dynamic Map Center calculation based on mapped markers
  const mapCenter = useMemo(() => {
    if (mappedProjects.length === 0) return [19.7515, 75.7139]; // Maharashtra default
    const avgLat = mappedProjects.reduce((sum, p) => sum + Number(p.latitude ?? p.lat), 0) / mappedProjects.length;
    const avgLng = mappedProjects.reduce((sum, p) => sum + Number(p.longitude ?? p.lng), 0) / mappedProjects.length;
    return [avgLat, avgLng];
  }, [mappedProjects]);

  return (
    <div className="min-h-full pb-12">
      <PageHeader
        title="Geospatial Infrastructure Map"
        subtitle="GIS location mapping of state infrastructure projects with GPS-tagged coordinate verification."
        badge="GIS Layer"
        breadcrumbs={['SetuX', 'Project Map']}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">

        {/* Controls & Summary Bar */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-700 p-4 shadow-sm">
          
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center space-x-2 text-[#14213D] dark:text-slate-100">
              <Map size={18} className="text-[#1769D2]" />
              <h2 className="text-sm font-bold">GIS Command Overview</h2>
            </div>

            <div className="h-4 w-px bg-gray-200 dark:bg-slate-700 hidden sm:block" />

            <div className="flex items-center space-x-2 text-xs text-[#64748B] dark:text-slate-400">
              <span className="font-semibold text-[#14213D] dark:text-slate-100">{filteredProjects.length}</span> Total Filtered
              <span className="text-gray-300 dark:text-slate-600">•</span>
              <span className="font-semibold text-emerald-700">{mappedProjects.length}</span> Mapped
              {unmappedProjects.length > 0 && (
                <>
                  <span className="text-gray-300 dark:text-slate-600">•</span>
                  <span className="font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                    {unmappedProjects.length} Projects without location data
                  </span>
                </>
              )}
            </div>
          </div>

          <button
            type="button"
            onClick={fetchProjects}
            disabled={loading}
            className="inline-flex items-center space-x-1.5 bg-white dark:bg-slate-900 hover:bg-gray-50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700 text-[#14213D] dark:text-slate-100 px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-sm transition self-start lg:self-auto"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin text-[#1769D2]' : 'text-gray-500 dark:text-slate-400'} />
            <span>Refresh GIS Data</span>
          </button>
        </div>

        {/* Filters Bar */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-4 shadow-sm grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by code, name, district..."
              className="w-full pl-9 pr-3 py-2 text-xs border border-gray-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1769D2] text-[#14213D] dark:text-slate-100"
            />
          </div>

          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-gray-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1769D2] text-[#14213D] dark:text-slate-100 bg-white dark:bg-slate-900"
            >
              <option value="">All Project Statuses</option>
              <option value="Verified">Verified</option>
              <option value="Review Required">Review Required</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Delayed">Delayed</option>
              <option value="High Risk">High Risk</option>
              <option value="Completed">Completed</option>
            </select>
          </div>

          <div>
            <select
              value={sectorFilter}
              onChange={(e) => setSectorFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-gray-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1769D2] text-[#14213D] dark:text-slate-100 bg-white dark:bg-slate-900"
            >
              <option value="">All Sectors</option>
              {availableSectors.map((sec) => (
                <option key={sec} value={sec}>{sec}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Map Workspace */}
        {loading ? (
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-12 h-[550px] animate-pulse flex flex-col items-center justify-center space-y-3">
            <Loader2 size={32} className="text-[#1769D2] animate-spin" />
            <p className="text-xs font-semibold text-[#64748B] dark:text-slate-400">Loading GIS spatial data...</p>
          </div>
        ) : error ? (
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm p-10 text-center space-y-4">
            <div className="w-12 h-12 bg-red-50 text-red-500 rounded-xl flex items-center justify-center mx-auto border border-red-200">
              <AlertTriangle size={24} />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#14213D] dark:text-slate-100">GIS Map Unavailable</h3>
              <p className="text-xs text-red-600 mt-1 max-w-md mx-auto">{error}</p>
            </div>
            <button
              type="button"
              onClick={fetchProjects}
              className="inline-flex items-center space-x-1.5 bg-[#1769D2] text-white px-4 py-2 rounded-lg text-xs font-semibold hover:bg-[#1459b8] transition"
            >
              <RefreshCw size={13} />
              <span>Retry</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

            {/* Map Canvas Column */}
            <div className="lg:col-span-8 xl:col-span-9 h-[550px] min-h-[450px]">
              <ProjectsMap
                projects={mappedProjects}
                center={mapCenter}
                zoom={mappedProjects.length > 0 ? 8 : 7}
              />
            </div>

            {/* Side Drawer Column: Mapped / Unmapped Inspection List */}
            <div className="lg:col-span-4 xl:col-span-3 space-y-4">
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col h-[550px]">
                
                <div className="p-4 border-b border-gray-100 dark:border-slate-800 bg-[#F5F7FA] dark:bg-slate-800">
                  <h3 className="text-xs font-bold text-[#14213D] dark:text-slate-100 flex items-center space-x-2">
                    <Building2 size={15} className="text-[#1769D2]" />
                    <span>Project Location Directory</span>
                  </h3>
                </div>

                <div className="flex-1 overflow-y-auto divide-y divide-gray-100 dark:divide-slate-800 p-2">
                  {filteredProjects.length === 0 ? (
                    <div className="p-6 text-center text-xs text-[#64748B] dark:text-slate-400">
                      No projects match your filter.
                    </div>
                  ) : (
                    filteredProjects.map((p) => {
                      const isMapped = hasValidCoordinates(p);
                      const pCode = p.project_code || `ID-${p.id}`;
                      const phys = p.physical_progress ?? p.reported_progress ?? 0;

                      return (
                        <div key={p.id} className="p-3 hover:bg-[#EAF3FF] dark:bg-blue-950/40/40 rounded-xl transition-colors space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-[10px] font-bold text-[#1769D2]">{pCode}</span>
                            <span className={`inline-flex items-center space-x-1 text-[9px] font-bold px-2 py-0.5 rounded border ${
                              isMapped ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200'
                            }`}>
                              {isMapped ? <MapPin size={10} /> : <FileQuestion size={10} />}
                              <span>{isMapped ? 'GPS Mapped' : 'No Location Data'}</span>
                            </span>
                          </div>

                          <h4 className="text-xs font-bold text-[#14213D] dark:text-slate-100 truncate">{p.name}</h4>

                          <div className="flex items-center justify-between text-[10px] text-[#64748B] dark:text-slate-400">
                            <span>{p.district || p.state || 'Maharashtra'}</span>
                            <span>{phys.toFixed(0)}% Progress</span>
                          </div>

                          <div className="pt-1 flex justify-end">
                            <Link
                              to={`/projects/${p.id}`}
                              className="text-[10px] font-bold text-[#1769D2] hover:underline inline-flex items-center space-x-0.5"
                            >
                              <span>Inspect Project</span>
                              <ArrowUpRight size={10} />
                            </Link>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>

              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
