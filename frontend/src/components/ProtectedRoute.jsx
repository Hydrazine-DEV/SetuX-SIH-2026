import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Loader2, ShieldCheck } from 'lucide-react';

export default function ProtectedRoute({ allowedRoles }) {
  const { user, isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#F5F7FA] text-[#14213D] font-sans">
        <div className="flex flex-col items-center space-y-3 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm max-w-xs text-center">
          <div className="w-10 h-10 rounded-full bg-[#EAF3FF] text-[#1769D2] flex items-center justify-center">
            <Loader2 className="w-5 h-5 animate-spin" />
          </div>
          <div className="space-y-1">
            <p className="text-sm font-bold text-[#14213D]">Validating Official Session</p>
            <p className="text-xs text-[#64748B]">Authenticating with SetuX security service...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/officer-login" state={{ from: location }} replace />;
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const userRole = (user?.role || '').toLowerCase();
    const isAllowed = allowedRoles.map((r) => r.toLowerCase()).includes(userRole);
    if (!isAllowed) {
      if (userRole === 'citizen') {
        return <Navigate to="/citizen-dashboard" replace />;
      } else {
        return <Navigate to="/dashboard" replace />;
      }
    }
  }

  return <Outlet />;
}
