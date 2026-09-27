import { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Bell,
  Menu,
  ChevronDown,
  User,
  LogOut,
  ShieldCheck,
  Building,
  MapPin,
  BadgeAlert,
  Sun,
  Moon,
  Globe,
  Search,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';

// Route Title Mapping
const ROUTE_TITLES = {
  '/dashboard': { title: 'Officer Command Center', section: 'Overview' },
  '/projects': { title: 'Infrastructure Projects Portfolio', section: 'Projects' },
  '/analytics': { title: 'Infrastructure Analytics & Intelligence', section: 'Analytics' },
  '/risk': { title: 'Risk Intelligence & Predictions', section: 'Risk' },
  '/warnings': { title: 'Early Warning Signals', section: 'Monitoring' },
  '/map': { title: 'Geospatial Project Distribution Map', section: 'GIS' },
  '/issues': { title: 'Field Issues & Site Evidence', section: 'Verification' },
  '/reports': { title: 'Executive Project Reports', section: 'Audit' },
  '/settings': { title: 'Department Settings & Profile', section: 'Configuration' },
};

export default function Header({ onMenuClick }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifs, setShowNotifs] = useState(false);
  const [lang, setLang] = useState('EN');

  const profileRef = useRef(null);
  const notifRef = useRef(null);

  // Close menus on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setShowProfileMenu(false);
      }
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setShowNotifs(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
    } finally {
      navigate('/officer-login');
    }
  };

  // Derive active title based on path
  const currentPath = location.pathname;
  let pageInfo = ROUTE_TITLES[currentPath];
  if (!pageInfo && currentPath.startsWith('/projects/')) {
    pageInfo = { title: 'Project Inspection Details', section: 'Projects' };
  }
  if (!pageInfo) {
    pageInfo = { title: 'Department Officer Workspace', section: 'SetuX' };
  }

  // Officer display credentials
  const officerName = user?.full_name || 'Department Officer';
  const officerInitial = officerName.charAt(0).toUpperCase();
  const officerDesignation = user?.designation || (user?.role === 'officer' ? 'Department Official' : 'Officer');
  const officerDepartment = user?.department_name || user?.department?.name || 'Public Works Department';
  const officerDistrict = user?.district;

  return (
    <header className="h-16 bg-white dark:bg-[#0B1B2D] border-b border-gray-200 dark:border-slate-800/80 px-4 sm:px-6 flex items-center justify-between gap-4 sticky top-0 z-20 shadow-xs transition-colors">
      
      {/* Left: Mobile Toggle & Page Title */}
      <div className="flex items-center space-x-3 sm:space-x-4 min-w-0">
        <button
          type="button"
          onClick={onMenuClick}
          className="md:hidden p-2 rounded-xl text-gray-600 dark:text-slate-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
          aria-label="Open Navigation Sidebar"
        >
          <Menu size={20} />
        </button>

        <div className="min-w-0">
          <div className="flex items-center space-x-2">
            <span className="text-[11px] font-extrabold text-[#1769D2] dark:text-blue-400 uppercase tracking-wider hidden sm:inline-block">
              {pageInfo.section}
            </span>
            <span className="hidden sm:inline-block text-gray-300 dark:text-slate-700">•</span>
            <h1 className="text-sm sm:text-base font-bold text-[#14213D] dark:text-slate-100 truncate tracking-tight">
              {pageInfo.title}
            </h1>
          </div>
        </div>
      </div>

      {/* Center: Global Search Bar Affordance */}
      <div className="hidden lg:flex items-center flex-1 max-w-xs mx-4">
        <div className="relative w-full">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-slate-500 pointer-events-none" />
          <input
            type="text"
            placeholder="Search projects, IDs, risks..."
            className="w-full bg-gray-50 dark:bg-[#10243A] border border-gray-200 dark:border-slate-700/80 rounded-xl pl-9 pr-3 py-1.5 text-xs text-[#14213D] dark:text-slate-200 placeholder:text-gray-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-[#1769D2] transition-colors"
            readOnly
            onClick={() => navigate('/projects')}
          />
        </div>
      </div>

      {/* Right: Controls, Notifications & Officer Profile */}
      <div className="flex items-center space-x-2 sm:space-x-3 shrink-0">
        
        {/* Language Selector Affordance */}
        <button
          type="button"
          onClick={() => setLang(lang === 'EN' ? 'HI' : 'EN')}
          className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-xl border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-[#10243A] text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 text-xs font-semibold transition focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
          title="Switch Display Language"
          aria-label="Switch Language"
        >
          <Globe size={14} className="text-[#1769D2]" />
          <span>{lang}</span>
        </button>

        {/* Global Theme Toggle */}
        <button
          type="button"
          onClick={toggleTheme}
          className="p-2 rounded-xl border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-[#10243A] text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 transition focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {theme === 'dark' ? (
            <Sun size={17} className="text-amber-400" />
          ) : (
            <Moon size={17} className="text-slate-600" />
          )}
        </button>

        {/* Notification Bell */}
        <div className="relative" ref={notifRef}>
          <button
            type="button"
            onClick={() => { setShowNotifs(!showNotifs); setShowProfileMenu(false); }}
            className="p-2 rounded-xl text-gray-600 dark:text-slate-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-slate-800 transition relative focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
            aria-label="Department Notifications"
            title="Notifications"
          >
            <Bell size={18} />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#1769D2] rounded-full ring-2 ring-white dark:ring-[#0B1B2D]"></span>
          </button>

          {showNotifs && (
            <div className="absolute right-0 top-12 w-72 bg-white dark:bg-[#0B1B2D] rounded-2xl shadow-xl border border-gray-200 dark:border-slate-800 p-4 z-50 text-left">
              <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-slate-800">
                <span className="text-xs font-bold text-[#14213D] dark:text-slate-100">System Notifications</span>
                <span className="text-[10px] font-semibold text-[#1769D2] dark:text-blue-400 bg-[#EAF3FF] dark:bg-blue-950/60 px-2 py-0.5 rounded-full">
                  Official Feed
                </span>
              </div>
              <div className="py-4 text-center space-y-1">
                <BadgeAlert className="w-8 h-8 text-gray-300 dark:text-slate-600 mx-auto" />
                <p className="text-xs font-semibold text-[#14213D] dark:text-slate-200">No New Critical Alerts</p>
                <p className="text-[11px] text-[#64748B] dark:text-slate-400">All project streams operate under normal status parameters.</p>
              </div>
            </div>
          )}
        </div>

        <div className="h-6 w-px bg-gray-200 dark:bg-slate-800 hidden sm:block"></div>

        {/* Officer Identity Card & Dropdown */}
        <div className="relative" ref={profileRef}>
          <button
            type="button"
            onClick={() => { setShowProfileMenu(!showProfileMenu); setShowNotifs(false); }}
            className="flex items-center space-x-2.5 p-1 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-800/60 transition border border-transparent hover:border-gray-200 dark:hover:border-slate-700/60 focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
            aria-label="Officer Profile and Options"
          >
            {/* Avatar Initials Badge */}
            <div className="w-9 h-9 rounded-xl bg-[#0B2A4A] dark:bg-[#1769D2] text-white flex items-center justify-center font-bold text-xs shadow-xs shrink-0">
              {officerInitial}
            </div>

            {/* Officer Details (Desktop) */}
            <div className="text-left hidden md:block max-w-[190px]">
              <div className="text-xs font-bold text-[#14213D] dark:text-slate-100 truncate leading-tight">
                {officerName}
              </div>
              <div className="text-[11px] text-[#64748B] dark:text-slate-400 truncate leading-tight mt-0.5">
                {officerDesignation}
              </div>
              <div className="text-[10px] text-gray-500 dark:text-slate-500 truncate leading-tight">
                {officerDepartment} {officerDistrict ? `· ${officerDistrict}` : ''}
              </div>
            </div>

            <ChevronDown size={14} className="text-gray-400 dark:text-slate-500 hidden sm:block" />
          </button>

          {/* Profile Dropdown Menu */}
          {showProfileMenu && (
            <div className="absolute right-0 top-12 w-64 bg-white dark:bg-[#0B1B2D] rounded-2xl shadow-xl border border-gray-200 dark:border-slate-800 p-3 z-50 text-left animate-in fade-in slide-in-from-top-2 duration-150">
              {/* Officer Account Details */}
              <div className="p-3 bg-[#F5F7FA] dark:bg-[#10243A] rounded-xl border border-gray-100 dark:border-slate-800 space-y-1.5">
                <div className="flex items-center space-x-1.5">
                  <ShieldCheck size={14} className="text-[#1769D2] dark:text-blue-400" />
                  <span className="text-xs font-bold text-[#14213D] dark:text-slate-100">{officerName}</span>
                </div>
                <div className="text-[11px] text-[#64748B] dark:text-slate-400">{user?.email}</div>

                <div className="pt-1.5 border-t border-gray-200/60 dark:border-slate-700/60 space-y-1 text-[11px] text-[#14213D] dark:text-slate-200">
                  <div className="flex items-center space-x-1.5">
                    <Building size={12} className="text-gray-400 dark:text-slate-500 shrink-0" />
                    <span className="truncate">{officerDepartment}</span>
                  </div>
                  {officerDistrict && (
                    <div className="flex items-center space-x-1.5">
                      <MapPin size={12} className="text-gray-400 dark:text-slate-500 shrink-0" />
                      <span>{officerDistrict}, Maharashtra</span>
                    </div>
                  )}
                  {user?.employee_id && (
                    <div className="text-[10px] font-mono text-gray-500 dark:text-slate-400 pt-0.5">
                      ID: {user.employee_id}
                    </div>
                  )}
                </div>
              </div>

              {/* Action Links */}
              <div className="pt-2 space-y-1">
                <button
                  type="button"
                  onClick={() => { setShowProfileMenu(false); navigate('/settings'); }}
                  className="w-full flex items-center space-x-2 px-3 py-2 text-xs font-semibold text-[#14213D] dark:text-slate-200 hover:bg-gray-50 dark:hover:bg-slate-800 rounded-lg transition"
                >
                  <User size={14} className="text-gray-400 dark:text-slate-400" />
                  <span>Account & Department Settings</span>
                </button>

                <button
                  type="button"
                  onClick={handleLogout}
                  className="w-full flex items-center space-x-2 px-3 py-2 text-xs font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition"
                >
                  <LogOut size={14} className="text-red-500" />
                  <span>Sign Out Session</span>
                </button>
              </div>
            </div>
          )}

        </div>

      </div>

    </header>
  );
}

