import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Users,
  Lock,
  Mail,
  User,
  Phone,
  AlertCircle,
  Eye,
  EyeOff,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Loader2,
  Compass,
  MapPin
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function CitizenLogin() {
  const navigate = useNavigate();
  const { login, signup, isAuthenticated, user, loading: authLoading } = useAuth();

  const [isSignIn, setIsSignIn] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // If already authenticated as citizen, redirect to citizen dashboard
  useEffect(() => {
    if (!authLoading && isAuthenticated && user) {
      if (user.role === 'citizen') {
        navigate('/citizen-dashboard', { replace: true });
      } else if (user.role === 'officer') {
        navigate('/dashboard', { replace: true });
      }
    }
  }, [isAuthenticated, user, authLoading, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const cleanEmail = email.trim();
    if (!cleanEmail) {
      setError('Please enter your email address.');
      return;
    }
    if (!password) {
      setError('Please enter your password.');
      return;
    }

    setSubmitting(true);

    try {
      if (isSignIn) {
        const loggedInUser = await login({
          email: cleanEmail,
          password: password,
          role: 'citizen',
        });
        if (loggedInUser.role === 'citizen') {
          navigate('/citizen-dashboard');
        } else {
          navigate('/dashboard');
        }
      } else {
        if (!fullName.trim()) {
          setError('Full name is required.');
          setSubmitting(false);
          return;
        }
        if (password.length < 8) {
          setError('Password must be at least 8 characters.');
          setSubmitting(false);
          return;
        }
        if (password !== confirmPassword) {
          setError('Passwords do not match.');
          setSubmitting(false);
          return;
        }

        await signup({
          full_name: fullName.trim(),
          email: cleanEmail,
          phone: phone.trim() || undefined,
          password: password,
          confirm_password: confirmPassword,
          role: 'citizen',
        });

        setSuccess('Citizen account registered successfully. You may now sign in.');
        setIsSignIn(true);
        setPassword('');
        setConfirmPassword('');
      }
    } catch (err) {
      console.warn('Citizen authentication error:', err);
      if (err.response?.status === 401) {
        setError('Invalid citizen email or password. Please verify your credentials.');
      } else if (err.response?.status === 403) {
        setError('Role mismatch: This account is not registered under Citizen access.');
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        setError(typeof detail === 'string' ? detail : 'Authentication failed. Please verify your inputs.');
      } else if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')) {
        setError('Unable to connect to the SetuX service. Please ensure the backend is running.');
      } else {
        setError('An unexpected error occurred. Please try again or browse public projects.');
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
              <span className="hidden sm:inline-block text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200 ml-2">
                Public Transparency Gateway
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
                to="/officer-login"
                className="text-xs font-semibold text-[#1769D2] hover:underline hidden sm:inline-block"
              >
                Officer Portal Login →
              </Link>
            </div>

          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 flex items-center justify-center">
        <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Left Column: Public Transparency Showcase */}
          <div className="hidden lg:flex lg:col-span-7 flex-col justify-between space-y-8 bg-gradient-to-br from-[#0B2A4A] via-[#103761] to-[#0e487c] text-white p-8 lg:p-10 rounded-2xl shadow-xl relative overflow-hidden border border-navy-800">
            {/* Image Overlay */}
            <div className="absolute inset-0 z-0 opacity-20">
              <img
                src="/assets/sections/citizen-portal.jpg.png"
                alt="Citizen Transparency Portal"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-[#0B2A4A] via-[#0B2A4A]/80 to-transparent z-0"></div>

            {/* Content */}
            <div className="relative z-10 space-y-6">
              
              <div className="inline-flex items-center space-x-2 bg-emerald-500/20 text-emerald-200 border border-emerald-400/30 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
                <Users className="w-3.5 h-3.5 text-emerald-400" />
                <span>Open Public Civic Access</span>
              </div>

              <div className="space-y-3">
                <h1 className="text-3xl font-extrabold tracking-tight text-white leading-tight">
                  Public Infrastructure <br />
                  <span className="text-[#EAF3FF]">Transparency & Civic Oversight</span>
                </h1>
                <p className="text-sm text-gray-200 leading-relaxed max-w-lg">
                  Empowering citizens with direct visibility into state infrastructure projects, expenditure tracking, and verified milestone progress across Maharashtra.
                </p>
              </div>

              {/* Public Features List */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-white">Public Project Directory</p>
                    <p className="text-[11px] text-gray-300">Explore roads, schools, and water projects by district.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-white">Interactive Map Views</p>
                    <p className="text-[11px] text-gray-300">Geospatial project distribution across regional districts.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-white">Milestone Verification</p>
                    <p className="text-[11px] text-gray-300">View progress milestones confirmed by field evidence.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-white">Civic Accountability</p>
                    <p className="text-[11px] text-gray-300">Open data standards fostering trust and transparency.</p>
                  </div>
                </div>
              </div>

              {/* Instant Public Browse CTA Banner */}
              <div className="pt-2">
                <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 flex items-center justify-between">
                  <div className="space-y-0.5">
                    <p className="text-xs font-bold text-white">Public Transparency Portal</p>
                    <p className="text-[11px] text-gray-300">Public transparency features are being prepared for open citizen access.</p>
                  </div>
                  <Link
                    to="/citizen-dashboard"
                    className="inline-flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-2 rounded-lg text-xs font-bold transition shadow-sm"
                  >
                    <Compass className="w-3.5 h-3.5" />
                    <span>Open Dashboard</span>
                  </Link>
                </div>
              </div>

            </div>

            {/* Bottom Note */}
            <div className="relative z-10 pt-4 border-t border-white/10 flex items-center justify-between text-[11px] text-gray-300">
              <div className="flex items-center space-x-2">
                <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                <span>Open Governance Portal</span>
              </div>
              <span className="font-mono text-emerald-200">Public Citizen Access</span>
            </div>

          </div>

          {/* Right Column: Citizen Login / Register Card */}
          <div className="lg:col-span-5 w-full max-w-md mx-auto">
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 sm:p-8 space-y-6">
              
              {/* Header Title & Tab Switcher */}
              <div className="space-y-3 border-b border-gray-100 pb-4">
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center space-x-1.5 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                    <Users className="w-3 h-3" />
                    <span>Citizen Portal</span>
                  </span>
                </div>
                
                <h2 className="text-2xl font-bold text-[#14213D] tracking-tight">
                  {isSignIn ? 'Citizen Account Login' : 'Register Citizen Account'}
                </h2>

                {/* Subheading Tabs */}
                <div className="flex border-b border-gray-200 pt-1">
                  <button
                    type="button"
                    onClick={() => { setIsSignIn(true); setError(''); setSuccess(''); }}
                    className={`flex-1 pb-2 text-xs font-bold transition-all ${
                      isSignIn
                        ? 'border-b-2 border-emerald-600 text-emerald-700 -mb-px'
                        : 'text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    Sign In
                  </button>
                  <button
                    type="button"
                    onClick={() => { setIsSignIn(false); setError(''); setSuccess(''); }}
                    className={`flex-1 pb-2 text-xs font-bold transition-all ${
                      !isSignIn
                        ? 'border-b-2 border-emerald-600 text-emerald-700 -mb-px'
                        : 'text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    Create Account
                  </button>
                </div>
              </div>

              {/* Alerts */}
              {success && (
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3.5 rounded-xl flex items-start space-x-2.5 text-xs font-medium">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 leading-relaxed">{success}</div>
                </div>
              )}

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-3.5 rounded-xl flex items-start space-x-2.5 text-xs font-medium">
                  <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 leading-relaxed">{error}</div>
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                
                {/* Full Name for Registration */}
                {!isSignIn && (
                  <div>
                    <label className="block text-xs font-semibold text-[#14213D] mb-1.5">
                      Full Name <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                        <User className="w-4 h-4" />
                      </div>
                      <input
                        type="text"
                        required
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="e.g. Suresh More"
                        className="w-full pl-9 pr-3.5 py-2.5 text-sm border border-gray-300 rounded-lg text-[#14213D] bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent transition"
                      />
                    </div>
                  </div>
                )}

                {/* Email Address */}
                <div>
                  <label className="block text-xs font-semibold text-[#14213D] mb-1.5">
                    Email Address <span className="text-red-500">*</span>
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
                      placeholder="e.g. citizen@gmail.com"
                      autoComplete="email"
                      className="w-full pl-9 pr-3.5 py-2.5 text-sm border border-gray-300 rounded-lg text-[#14213D] bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent transition"
                    />
                  </div>
                </div>

                {/* Phone for Registration */}
                {!isSignIn && (
                  <div>
                    <label className="block text-xs font-semibold text-[#14213D] mb-1.5">
                      Phone Number (Optional)
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                        <Phone className="w-4 h-4" />
                      </div>
                      <input
                        type="tel"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="e.g. 9822009988"
                        className="w-full pl-9 pr-3.5 py-2.5 text-sm border border-gray-300 rounded-lg text-[#14213D] bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent transition"
                      />
                    </div>
                  </div>
                )}

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
                      placeholder="Min 8 characters"
                      autoComplete={isSignIn ? "current-password" : "new-password"}
                      className="w-full pl-9 pr-10 py-2.5 text-sm border border-gray-300 rounded-lg text-[#14213D] bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent transition"
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

                {/* Confirm Password for Registration */}
                {!isSignIn && (
                  <div>
                    <label className="block text-xs font-semibold text-[#14213D] mb-1.5">
                      Confirm Password <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                        <Lock className="w-4 h-4" />
                      </div>
                      <input
                        type="password"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Re-enter password"
                        autoComplete="new-password"
                        className="w-full pl-9 pr-3.5 py-2.5 text-sm border border-gray-300 rounded-lg text-[#14213D] bg-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent transition"
                      />
                    </div>
                  </div>
                )}

                {/* Submit Action Button */}
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm rounded-lg shadow-sm hover:shadow transition-all flex items-center justify-center space-x-2 disabled:opacity-60 focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:ring-offset-2"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : isSignIn ? (
                    <>
                      <Users className="w-4 h-4" />
                      <span>Sign In to Citizen Portal</span>
                      <ArrowRight className="w-4 h-4 ml-0.5" />
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Register Citizen Account</span>
                      <ArrowRight className="w-4 h-4 ml-0.5" />
                    </>
                  )}
                </button>

              </form>

              {/* Direct Open Access CTA */}
              <div className="pt-4 border-t border-gray-100 text-center space-y-3">
                <p className="text-xs text-[#64748B]">
                  Prefer to preview public transparency?
                </p>
                <Link
                  to="/citizen-dashboard"
                  className="w-full inline-flex items-center justify-center space-x-2 bg-[#EAF3FF] hover:bg-blue-100 text-[#1769D2] py-2.5 px-4 rounded-lg font-semibold text-xs transition border border-blue-200"
                >
                  <Compass className="w-3.5 h-3.5" />
                  <span>Public Transparency Overview</span>
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
          <span className="text-[11px] text-gray-400">Public transparency & infrastructure oversight</span>
        </div>
      </footer>

    </div>
  );
}
