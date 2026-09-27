import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  ShieldCheck,
  Home,
  FileText,
  User,
  LogOut,
  Search,
  ChevronDown,
  Camera,
  Activity,
  CheckCircle2,
} from 'lucide-react';

export default function CitizenDashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('home');
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const userName = user?.full_name || (user ? 'Citizen User' : 'Public Guest');
  const userInitial = userName.charAt(0).toUpperCase();

  return (
    <div className="flex h-screen overflow-hidden bg-slate-100 font-sans">

      {/* DARK BLUE LEFT SIDEBAR */}
      <aside className="w-56 bg-[#0F2942] text-white flex flex-col justify-between py-6 px-3 shrink-0">
        <div className="space-y-7">
          {/* Brand */}
          <div className="flex items-center gap-2.5 px-3">
            <div className="w-8 h-8 rounded-lg bg-orange-500 flex items-center justify-center shrink-0">
              <ShieldCheck size={18} className="text-white" />
            </div>
            <span className="text-xl font-black tracking-tight text-white">SetuX</span>
          </div>

          {/* Nav */}
          <nav className="space-y-1">
            {[
              { id: 'home', icon: Home, label: 'Home' },
              { id: 'complaints', icon: FileText, label: 'My Complaints' },
              { id: 'profile', icon: User, label: 'Profile' },
            ].map(({ id, icon: Icon, label }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all text-left ${
                  activeTab === id
                    ? 'bg-[#193B5E] text-white'
                    : 'text-slate-400 hover:bg-[#193B5E]/50 hover:text-white'
                }`}
              >
                <Icon size={17} />
                {label}
              </button>
            ))}
          </nav>
        </div>

        {/* Logout / Login button */}
        {user ? (
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-400 hover:bg-red-500/20 hover:text-red-300 transition-all"
          >
            <LogOut size={17} />
            Logout
          </button>
        ) : (
          <a
            href="/citizen-login"
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-400 hover:bg-[#193B5E]/50 hover:text-white transition-all"
          >
            <User size={17} />
            Citizen Login
          </a>
        )}
      </aside>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

        {/* Top Header */}
        <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between gap-4 shrink-0">
          {/* Search */}
          <div className="relative w-64">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search..."
              className="w-full pl-8 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-[#0F2942]"
            />
          </div>

          {/* User Widget */}
          <div className="relative">
            <button
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="flex items-center gap-2.5 p-1.5 rounded-xl hover:bg-slate-100 transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-[#0F2942] text-white flex items-center justify-center font-bold text-sm">
                {userInitial}
              </div>
              <div className="text-left hidden sm:block">
                <div className="text-xs font-extrabold text-slate-900 leading-tight">{userName}</div>
                <div className="text-[10px] font-medium text-slate-500 capitalize">
                  {user?.role || 'Guest Visitor'}
                </div>
              </div>
              <ChevronDown size={14} className="text-slate-400" />
            </button>

            {showProfileMenu && (
              <div className="absolute right-0 top-12 w-52 bg-white rounded-2xl shadow-xl border border-slate-200 p-2 z-50">
                <div className="px-3 py-2 border-b border-slate-100">
                  <div className="text-xs font-bold text-slate-900">{user?.full_name || 'Public Guest'}</div>
                  <div className="text-[10px] text-slate-500">{user?.email || 'Unauthenticated'}</div>
                </div>
                {user ? (
                  <button
                    onClick={logout}
                    className="w-full text-left px-3 py-2 text-xs font-semibold text-red-600 hover:bg-red-50 rounded-xl flex items-center gap-2 mt-1"
                  >
                    <LogOut size={13} />
                    Logout
                  </button>
                ) : (
                  <a
                    href="/citizen-login"
                    className="w-full text-left px-3 py-2 text-xs font-semibold text-[#0F2942] hover:bg-slate-50 rounded-xl flex items-center gap-2 mt-1"
                  >
                    <User size={13} />
                    Sign In
                  </a>
                )}
              </div>
            )}
          </div>
        </header>

        {/* Dashboard Body */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* Welcome Banner */}
          <div className="relative rounded-2xl overflow-hidden min-h-[160px] flex flex-col justify-center p-7 bg-[#0F2942]">
            <div
              className="absolute inset-0 bg-cover bg-center opacity-25"
              style={{
                backgroundImage: `url('https://images.unsplash.com/photo-1590496793929-36417d3117de?auto=format&fit=crop&w=1200&q=80')`,
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-[#0F2942] via-[#0F2942]/85 to-transparent" />
            <div className="relative z-10 space-y-1.5">
              <h1 className="text-2xl font-black text-white">Welcome to SetuX</h1>
              <p className="text-sm text-slate-300">Together we can build a better Maharashtra.</p>
            </div>
          </div>

          {/* 3 Action Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-md transition-shadow flex flex-col items-center text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center">
                <Camera size={26} className="text-blue-500" />
              </div>
              <div>
                <h3 className="text-sm font-extrabold text-[#0F2942]">Report an Issue</h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  Share problems with photos and location
                </p>
              </div>
              <button
                onClick={() => alert('Issue reporting module is being prepared.')}
                className="w-full py-2 px-4 bg-slate-50 hover:bg-[#0F2942] text-[#0F2942] hover:text-white rounded-xl text-xs font-bold transition-all border border-slate-200 hover:border-[#0F2942]"
              >
                Create Report
              </button>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-md transition-shadow flex flex-col items-center text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center">
                <Activity size={26} className="text-blue-500" />
              </div>
              <div>
                <h3 className="text-sm font-extrabold text-[#0F2942]">Track Status</h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  Check your complaints and updates
                </p>
              </div>
              <button
                onClick={() => alert('Tracking dashboard is being prepared.')}
                className="w-full py-2 px-4 bg-slate-50 hover:bg-[#0F2942] text-[#0F2942] hover:text-white rounded-xl text-xs font-bold transition-all border border-slate-200 hover:border-[#0F2942]"
              >
                View Status
              </button>
            </div>

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-md transition-shadow flex flex-col items-center text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center">
                <User size={26} className="text-blue-500" />
              </div>
              <div>
                <h3 className="text-sm font-extrabold text-[#0F2942]">Profile</h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  Manage your account information
                </p>
              </div>
              <button
                onClick={() => setActiveTab('profile')}
                className="w-full py-2 px-4 bg-slate-50 hover:bg-[#0F2942] text-[#0F2942] hover:text-white rounded-xl text-xs font-bold transition-all border border-slate-200 hover:border-[#0F2942]"
              >
                Account Details
              </button>
            </div>

          </div>

          {/* Session info / Public Notice strip */}
          {user ? (
            <div className="bg-white rounded-2xl p-4 border border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
                  <CheckCircle2 size={18} />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-900">Authenticated Citizen Session</div>
                  <div className="text-[11px] text-slate-500">{user.email} &bull; {user.role}</div>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-200">
                Verified Citizen
              </span>
            </div>
          ) : (
            <div className="bg-blue-50/70 rounded-2xl p-4 border border-blue-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center shrink-0">
                  <ShieldCheck size={18} />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-900">Public Transparency Mode</div>
                  <div className="text-[11px] text-slate-600">
                    Public transparency features are being prepared. Sign in or register to access citizen services.
                  </div>
                </div>
              </div>
              <a
                href="/citizen-login"
                className="shrink-0 px-3.5 py-1.5 bg-[#0F2942] hover:bg-[#193B5E] text-white text-xs font-semibold rounded-lg transition-colors"
              >
                Sign In / Register
              </a>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
