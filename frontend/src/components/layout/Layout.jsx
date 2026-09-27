import { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import MobileNav from './MobileNav';

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const location = useLocation();

  // Automatically close mobile sidebar on navigation change
  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [location.pathname]);

  return (
    <div className="flex h-screen overflow-hidden bg-[#F5F7FA] dark:bg-[#07111F] font-sans antialiased text-[#14213D] dark:text-[#F8FAFC]">
      
      {/* Desktop Persistent Sidebar */}
      <div className="hidden md:flex shrink-0">
        <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
        {collapsed && (
          <button
            type="button"
            onClick={() => setCollapsed(false)}
            className="fixed left-20 top-4 z-30 bg-[#0B2A4A] dark:bg-[#050E1A] text-white border border-navy-800 dark:border-slate-800 rounded-r-lg px-1.5 py-2 shadow-md hover:bg-[#1769D2] transition"
            aria-label="Expand Sidebar"
            title="Expand Sidebar"
          >
            <span className="text-xs font-bold">›</span>
          </button>
        )}
      </div>

      {/* Mobile Drawer Overlay */}
      {mobileSidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
            onClick={() => setMobileSidebarOpen(false)}
            aria-hidden="true"
          />

          {/* Drawer Content */}
          <div className="relative z-10 w-64 max-w-[80vw] h-full shadow-2xl animate-in slide-in-from-left duration-200">
            <Sidebar
              collapsed={false}
              setCollapsed={() => setMobileSidebarOpen(false)}
              onNavigate={() => setMobileSidebarOpen(false)}
            />
          </div>
        </div>
      )}

      {/* Main Workspace Area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        
        {/* Officer Top Header */}
        <Header onMenuClick={() => setMobileSidebarOpen(true)} />

        {/* Dynamic Page Content */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden bg-[#F5F7FA] dark:bg-[#07111F]">
          <Outlet />
        </main>

        {/* Mobile Bottom Navigation (Hidden on Tablet / Desktop) */}
        <div className="md:hidden shrink-0 z-10">
          <MobileNav />
        </div>

      </div>

    </div>

  );
}
