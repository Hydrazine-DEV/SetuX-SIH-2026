import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderKanban,
  BarChart3,
  ShieldAlert,
  AlertTriangle,
  Map,
  FileCheck2,
  FileSpreadsheet,
  Settings,
  LogOut,
  ChevronLeft,
  Building2,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const NAV_SECTIONS = [
  {
    title: 'MONITORING',
    items: [
      { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
      { to: '/projects', icon: FolderKanban, label: 'Projects' },
      { to: '/map', icon: Map, label: 'Project Map' },
    ],
  },
  {
    title: 'INTELLIGENCE',
    items: [
      { to: '/analytics', icon: BarChart3, label: 'Analytics' },
      { to: '/risk', icon: ShieldAlert, label: 'Risk Intelligence' },
      { to: '/warnings', icon: AlertTriangle, label: 'Early Warnings' },
    ],
  },
  {
    title: 'OPERATIONS',
    items: [
      { to: '/issues', icon: FileCheck2, label: 'Issues & Evidence' },
      { to: '/reports', icon: FileSpreadsheet, label: 'Reports' },
    ],
  },
];

export default function Sidebar({ collapsed, setCollapsed, onNavigate }) {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
    } finally {
      navigate('/officer-login');
    }
  };

  const handleClick = () => {
    if (onNavigate) onNavigate();
  };

  return (
    <aside
      className={`h-screen bg-[#0B2A4A] dark:bg-[#050E1A] text-white flex flex-col flex-shrink-0 transition-all duration-200 border-r border-navy-800 dark:border-slate-800/80 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
      aria-label="Officer Sidebar Navigation"
    >
      {/* Sidebar Header / Brand Identity */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-white/10 shrink-0">
        {!collapsed ? (
          <div className="flex items-center space-x-3 overflow-hidden">
            <img
              src="/assets/branding/govt-emblem.png"
              alt="Government Emblem"
              className="h-8 w-auto object-contain shrink-0"
              onError={(e) => { e.currentTarget.style.display = 'none'; }}
            />
            <div className="leading-tight">
              <div className="font-extrabold text-base tracking-tight text-white flex items-center space-x-1.5">
                <span>SetuX</span>
                <span className="text-[10px] font-bold bg-[#1769D2] text-white px-1.5 py-0.2 rounded">
                  COMMAND
                </span>
              </div>
              <div className="text-[11px] text-blue-200/80 truncate font-medium">
                Infrastructure Intelligence
              </div>
            </div>
          </div>
        ) : (
          <div className="mx-auto">
            <span className="font-black text-lg text-white">SX</span>
          </div>
        )}

        {/* Desktop Collapse Button */}
        {!collapsed && setCollapsed && (
          <button
            type="button"
            onClick={() => setCollapsed(true)}
            className="hidden md:flex p-1.5 rounded-xl hover:bg-white/10 text-slate-300 hover:text-white transition focus:outline-none focus:ring-2 focus:ring-[#1769D2]"
            aria-label="Collapse Sidebar"
            title="Collapse Sidebar"
          >
            <ChevronLeft size={16} />
          </button>
        )}
      </div>

      {/* Officer Department Badge (when expanded) */}
      {!collapsed && user?.department_name && (
        <div className="px-4 py-2 bg-black/20 dark:bg-black/40 border-b border-white/5 flex items-center space-x-2 text-xs text-blue-200">
          <Building2 size={13} className="text-blue-400 shrink-0" />
          <span className="truncate font-medium">{user.department_name}</span>
        </div>
      )}

      {/* Main Sectioned Navigation */}
      <nav className="flex-1 py-3 px-3 space-y-4 overflow-y-auto" aria-label="Main Navigation">
        {NAV_SECTIONS.map((section) => (
          <div key={section.title} className="space-y-1">
            <div className="text-[10px] font-bold text-blue-300/70 dark:text-slate-400 uppercase tracking-widest px-3 py-1">
              {!collapsed ? section.title : '•'}
            </div>

            {section.items.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                onClick={handleClick}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all select-none ${
                    collapsed ? 'justify-center' : ''
                  } ${
                    isActive
                      ? 'bg-[#1769D2] text-white shadow-sm ring-1 ring-white/20'
                      : 'text-slate-300 hover:bg-white/10 hover:text-white'
                  }`
                }
                title={collapsed ? label : undefined}
              >
                <Icon size={18} className="shrink-0" />
                {!collapsed && <span className="truncate">{label}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* SYSTEM Navigation (Settings & Logout) */}
      <div className="p-3 border-t border-white/10 space-y-1 shrink-0 bg-black/10 dark:bg-black/30">
        <div className="text-[10px] font-bold text-blue-300/70 dark:text-slate-400 uppercase tracking-widest px-3 py-1 mb-1">
          {!collapsed ? 'SYSTEM' : '•'}
        </div>

        {/* Settings */}
        <NavLink
          to="/settings"
          onClick={handleClick}
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all select-none ${
              collapsed ? 'justify-center' : ''
            } ${
              isActive
                ? 'bg-[#1769D2] text-white shadow-sm'
                : 'text-slate-300 hover:bg-white/10 hover:text-white'
            }`
          }
          title={collapsed ? 'Settings' : undefined}
        >
          <Settings size={18} className="shrink-0" />
          {!collapsed && <span className="truncate">Settings</span>}
        </NavLink>

        {/* Logout */}
        <button
          type="button"
          onClick={handleLogout}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-red-300 hover:bg-red-500/20 hover:text-red-200 transition-all text-left focus:outline-none focus:ring-2 focus:ring-red-400 ${
            collapsed ? 'justify-center' : ''
          }`}
          title={collapsed ? 'Sign Out' : undefined}
          aria-label="Sign Out Session"
        >
          <LogOut size={18} className="shrink-0 text-red-400" />
          {!collapsed && <span className="truncate">Sign Out</span>}
        </button>
      </div>
    </aside>
  );
}

