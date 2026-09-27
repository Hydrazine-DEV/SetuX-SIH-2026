import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  ShieldCheck,
  Lock,
  Mail,
  AlertCircle,
  Eye,
  EyeOff,
  Building2,
  ArrowRight,
  CheckCircle2,
  Cpu,
  ArrowLeft,
  Loader2
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function OfficerLogin() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, user, loading: authLoading } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // If already authenticated as officer, redirect to intended page or dashboard
  useEffect(() => {
    if (!authLoading && isAuthenticated && user) {
      if (user.role === 'officer') {
        const from = location.state?.from?.pathname || '/dashboard';
        navigate(from, { replace: true });
      } else if (user.role === 'citizen') {
        navigate('/citizen-dashboard', { replace: true });
      }
    }
  }, [isAuthenticated, user, authLoading, navigate, location]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const cleanEmail = email.trim();
    if (!cleanEmail) {
      setError('Please enter your official email address.');
      return;
    }
    if (!password) {
      setError('Please enter your password.');
      return;
    }

    setSubmitting(true);

    try {
      const loggedInUser = await login({
        email: cleanEmail,
        password: password,
        role: 'officer',
      });

      if (loggedInUser.role === 'officer') {
        const from = location.state?.from?.pathname || '/dashboard';
        navigate(from, { replace: true });
      } else {
        navigate('/citizen-dashboard', { replace: true });
      }
    } catch (err) {
      console.warn('Officer authentication error:', err);
      if (err.response?.status === 401) {
        setError('Invalid official email or password. Please verify your credentials.');
      } else if (err.response?.status === 403) {
        setError('Access denied: You are not authorized for Department Officer access.');
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        setError(typeof detail === 'string' ? detail : 'Authentication failed. Please verify your inputs.');
      } else if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')) {
        setError('Unable to connect to the SetuX service. Please ensure the backend is running.');
      } else {
        setError('An unexpected error occurred. Please try again or contact system administration.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F7FA] font-sans flex flex-col justify-between antialiased">
      
      {/* Top Government Navigation Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            
            {/* Branding */}
            <div className="flex items-center space-x-3">
              <Link to="/" className="flex items-center space-x-3 group">
                <img
                  src="/assets/branding/govt-emblem.png"
                  alt="Government Emblem"
                  className="h-10 w-auto object-contain"
                />
                <div className="h-6 w-px bg-gray-300"></div>
                <img
                  src="/assets/branding/setux-logo.png"
                  alt="SetuX Platform"
                  className="h-7 w-auto object-contain"
                />
              </Link>
              <span className="hidden sm:inline-block text-xs font-semibold text-[#64748B] border-l border-gray-200 pl-3">
                Department Officer Gateway
              </span>
            </div>

            {/* Quick Links */}
            <div className="flex items-center space-x-4">
              <Link
                to="/"
                className="inline-flex items-center space-x-1.5 text-xs font-medium text-[#64748B] hover:text-[#1769D2] transition-colors"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Return to Home</span>
              </Link>
              <Link
                to="/citizen-login"
                className="text-xs font-semibold text-[#1769D2] hover:underline hidden sm:inline-block"
              >
                Citizen Portal →
              </Link>
            </div>

          </div>
        </div>
      </header>

      {/* Main Container: Split Command Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 flex items-center justify-center">
        <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Left Column: Command Center Showcase (Desktop) */}
          <div className="hidden lg:flex lg:col-span-7 flex-col justify-between space-y-8 bg-[#0B2A4A] text-white p-8 lg:p-10 rounded-2xl shadow-xl relative overflow-hidden border border-navy-800">
            {/* Background Texture & Image Overlay */}
            <div className="absolute inset-0 z-0 opacity-15">
              <img
                src="/assets/sections/officer-portal.jpg.png"
                alt="Command Center Monitoring"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="absolute inset-0 bg-gradient-to-tr from-[#0B2A4A] via-[#0B2A4A]/95 to-[#1769D2]/30 z-0"></div>

            {/* Content Overlays */}
            <div className="relative z-10 space-y-6">
              
              <div className="inline-flex items-center space-x-2 bg-blue-500/20 text-[#EAF3FF] border border-blue-400/30 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
                <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                <span>Restricted Department Workspace</span>
              </div>

              <div className="space-y-3">
                <h1 className="text-3xl font-extrabold tracking-tight text-white leading-tight">
                  Infrastructure Monitoring <br />
                  <span className="text-[#EAF3FF]">Command & Intelligence Portal</span>
                </h1>
                <p className="text-sm text-gray-300 leading-relaxed max-w-lg">
                  Authorized access for Executive Engineers, Project Directors, and Department Officials to oversee project lifecycles, verify site evidence, and act on AI-driven risk signals.
                </p>
              </div>

              {/* Security & Feature Matrix */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-white">Multi-Tier Project Tracking</p>
                    <p className="text-[11px] text-gray-300">Milestones, expenditures, and physical progress logging.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-white">AI Visual Verification</p>
                    <p className="text-[11px] text-gray-300">Computer vision anomaly scoring on site imagery.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-white">Predictive Risk Models</p>
                    <p className="text-[11px] text-gray-300">Cost & schedule overrun machine learning classifiers.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-white">Audit Trail Governance</p>
                    <p className="text-[11px] text-gray-300">Official executive PDF reports and immutable logging.</p>
                  </div>
                </div>
              </div>

            </div>

            {/* Bottom Security Note */}
            <div className="relative z-10 pt-4 border-t border-white/10 flex items-center justify-between text-[11px] text-gray-300">
              <div className="flex items-center space-x-2">
                <Building2 className="w-3.5 h-3.5 text-blue-400" />
                <span>State Infrastructure Departments</span>
              </div>
              <span className="font-mono text-blue-200">256-Bit Encrypted Session</span>
            </div>

          </div>

          {/* Right Column: Officer Login Card */}
          <div className="lg:col-span-5 w-full max-w-md mx-auto">
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 sm:p-8 space-y-6">
              
              {/* Header Title */}
              <div className="space-y-1.5 text-left border-b border-gray-100 pb-4">
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center space-x-1.5 text-[11px] font-bold text-[#1769D2] bg-[#EAF3FF] px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                    <ShieldCheck className="w-3 h-3" />
                    <span>Officer Authentication</span>
                  </span>
                </div>
                <h2 className="text-2xl font-bold text-[#14213D] tracking-tight">
                  Officer Portal Login
                </h2>
                <p className="text-xs text-[#64748B]">
                  Sign in with your official departmental credentials to access the monitoring dashboard.
                </p>
              </div>

              {/* Error Alert Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-3.5 rounded-xl flex items-start space-x-2.5 text-xs font-medium animate-shake">
                  <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 leading-relaxed">{error}</div>
                </div>
              )}

              {/* Login Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                
                {/* Official Email */}
                <div>
                  <label className="block text-xs font-semibold text-[#14213D] mb-1.5">
                    Official Email Address <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                      <Mail className="w-4 h-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="e.g. patil@setux.gov.in"
                      autoComplete="email"
                      className="w-full pl-9 pr-3.5 py-2.5 text-sm border border-gray-300 rounded-lg text-[#14213D] bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#1769D2] focus:border-transparent transition"
                    />
                  </div>
                </div>

                {/* Password */}
                <div>
                  <label className="block text-xs font-semibold text-[#14213D] mb-1.5">
                    Password <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                      <Lock className="w-4 h-4" />
                    </div>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      autoComplete="current-password"
                      className="w-full pl-9 pr-10 py-2.5 text-sm border border-gray-300 rounded-lg text-[#14213D] bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#1769D2] focus:border-transparent transition"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Remember Me & Help */}
                <div className="flex items-center justify-between text-xs pt-1">
                  <label className="flex items-center space-x-2 text-[#64748B] cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="w-3.5 h-3.5 rounded border-gray-300 text-[#1769D2] focus:ring-[#1769D2]"
                    />
                    <span>Remember this session</span>
                  </label>
                  <span className="text-[11px] text-gray-500 font-medium">
                    Official Support
                  </span>
                </div>

                {/* Submit Action Button */}
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-3 px-4 bg-[#1769D2] hover:bg-[#1459b8] text-white font-semibold text-sm rounded-lg shadow-sm hover:shadow transition-all flex items-center justify-center space-x-2 disabled:opacity-60 focus:outline-none focus:ring-2 focus:ring-[#1769D2] focus:ring-offset-2"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Authenticating Credentials...</span>
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="w-4 h-4" />
                      <span>Sign In as Officer</span>
                      <ArrowRight className="w-4 h-4 ml-0.5" />
                    </>
                  )}
                </button>

              </form>

              {/* Citizen Gateway Switch */}
              <div className="pt-4 border-t border-gray-100 text-center space-y-2">
                <p className="text-xs text-[#64748B]">
                  Looking for public infrastructure transparency?
                </p>
                <Link
                  to="/citizen-login"
                  className="inline-flex items-center space-x-1 text-xs font-semibold text-[#1769D2] hover:underline"
                >
                  <span>Go to Public Citizen Transparency Portal</span>
                  <ArrowRight className="w-3 h-3 ml-0.5" />
                </Link>
              </div>

            </div>
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4 px-4 sm:px-6 lg:px-8 text-center text-xs text-[#64748B]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center space-y-1 sm:space-y-0">
          <span>SetuX Platform — Team VeriX (SIH26103)</span>
          <span className="text-[11px] text-gray-400">Strictly for authorized department monitoring officers</span>
        </div>
      </footer>

    </div>
  );
}
