import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderKanban,
  ShieldAlert,
  Map,
  FileCheck2,
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/projects', icon: FolderKanban, label: 'Projects' },
  { to: '/risk', icon: ShieldAlert, label: 'Risk AI' },
  { to: '/map', icon: Map, label: 'Map' },
  { to: '/issues', icon: FileCheck2, label: 'Evidence' },
];

export default function MobileNav() {
  return (
    <nav
      className="bg-white dark:bg-[#0B1B2D] border-t border-gray-200 dark:border-slate-800 flex items-center justify-around px-2 py-1.5 shadow-lg transition-colors"
      aria-label="Mobile Bottom Navigation"
    >
      {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            `flex flex-col items-center justify-center py-1 px-3 min-w-[56px] min-h-[44px] rounded-xl text-[10px] font-semibold transition-all select-none focus:outline-none focus:ring-2 focus:ring-[#1769D2] ${
              isActive
                ? 'text-[#1769D2] dark:text-blue-400 font-bold'
                : 'text-[#64748B] dark:text-slate-400 hover:text-[#14213D] dark:hover:text-slate-200'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <div
                className={`p-1 rounded-xl transition-colors ${
                  isActive ? 'bg-[#EAF3FF] dark:bg-blue-950/60' : 'bg-transparent'
                }`}
              >
                <Icon size={18} />
              </div>
              <span className="mt-0.5">{label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}

