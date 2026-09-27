import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  Lock,
  Mail,
  User,
  Phone,
  Building,
  AlertCircle,
  CheckCircle2,
  Eye,
  EyeOff,
  MapPin,
  Camera,
  Heart,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/api';

const DEFAULT_DEPARTMENTS = [
  { id: 1, name: 'Public Works Department', code: 'PWD' },
  { id: 2, name: 'Municipal Corporation', code: 'PMC' },
  { id: 3, name: 'Rural Development', code: 'RD' },
  { id: 4, name: 'Water Resources', code: 'WR' },
  { id: 5, name: 'Urban Development', code: 'UD' },
];

export default function Login() {
  const navigate = useNavigate();
  const { login, signup, isAuthenticated, user, loading: authLoading } = useAuth();

  const [isLogin, setIsLogin] = useState(true);
  const [role, setRole] = useState('citizen');
  const [showPassword, setShowPassword] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [departmentId, setDepartmentId] = useState(1);

  const [departments, setDepartments] = useState(DEFAULT_DEPARTMENTS);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated && user) {
      if (user.role === 'citizen') {
        navigate('/citizen-dashboard', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    }
  }, [isAuthenticated, user, authLoading, navigate]);

  useEffect(() => {
    async function fetchDepts() {
      try {
        const res = await authApi.getDepartments();
        if (res.data && res.data.length > 0) {
          setDepartments(res.data);
          setDepartmentId(res.data[0].id);
        }
      } catch (_) {}
    }
    fetchDepts();
  }, []);

  const handleRoleChange = (selectedRole) => {
    setRole(selectedRole);
    setError('');
    setSuccess('');
    setEmail('');
    setPassword('');
  };

  const switchTab = (toLogin) => {
    setIsLogin(toLogin);
    setError('');
    setSuccess('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setFullName('');
    setPhone('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSubmitting(true);

    try {
      if (isLogin) {
        const loggedInUser = await login({ email: email.trim(), password, role });
        if (loggedInUser.role === 'citizen') {
          navigate('/citizen-dashboard');
        } else {
          navigate('/dashboard');
        }
      } else {
        if (!fullName.trim()) { setError('Full Name is required.'); setSubmitting(false); return; }
        if (password.length < 8) { setError('Password must be at least 8 characters.'); setSubmitting(false); return; }
        if (password !== confirmPassword) { setError('Passwords do not match.'); setSubmitting(false); return; }

        await signup({
          full_name: fullName.trim(),
          email: email.trim(),
          phone: phone.trim() || undefined,
          password,
          confirm_password: confirmPassword,
          role,
          department_id: role === 'officer' ? Number(departmentId) : undefined,
        });

        setSuccess('Account created successfully. Please sign in.');
        switchTab(true);
      }
    } catch (err) {
      console.error('Auth error:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')) {
        setError('Unable to connect to the server. Please ensure the backend is running.');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const roleLabel = role === 'officer' ? 'Officer' : 'Citizen';
  const emailPlaceholder = role === 'officer' ? 'e.g. officer@gmail.com' : 'e.g. citizen@gmail.com';

  return (
    <div className="w-screen h-screen overflow-hidden flex flex-col font-sans bg-slate-100">

      {/* TOP THIN HEADER BAR */}
      <div className="w-full bg-white border-b border-slate-200 px-6 py-2.5 flex items-center justify-between shrink-0 z-20 shadow-sm">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#0F2942] flex items-center justify-center">
            <ShieldCheck size={18} className="text-orange-400" />
          </div>
          <span className="text-lg font-black tracking-tight text-[#0F2942]">SetuX</span>
        </div>
        <div className="text-xs text-slate-500 font-medium hidden sm:block">
          Transparent Projects &nbsp;|&nbsp; Stronger Tomorrow
        </div>
      </div>

      {/* MAIN SPLIT */}
      <div className="flex-1 flex overflow-hidden">

        {/* LEFT: DARK HERO PANEL */}
        <div className="hidden lg:flex lg:w-[55%] relative flex-col justify-between p-12 text-white shrink-0 bg-[#0B1E36]">
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{
              backgroundImage: `url('https://images.unsplash.com/photo-1590496793929-36417d3117de?auto=format&fit=crop&w=1600&q=80')`,
              opacity: 0.28,
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#071324] via-[#0F2942]/90 to-[#0F2942]/70" />

          <div className="relative z-10 flex-1 flex flex-col justify-center space-y-8 mt-8">
            {!isLogin ? (
              <>
                <div className="space-y-3">
                  <h1 className="text-4xl font-black leading-tight tracking-tight text-white">Join SetuX</h1>
                  <p className="text-sm text-slate-300 leading-relaxed max-w-sm">
                    Your voice matters. Help us build a better tomorrow.
                  </p>
                </div>
                <div className="space-y-5 pt-2">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-orange-500/20 flex items-center justify-center shrink-0">
                      <MapPin size={20} className="text-orange-400" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">Report public issues</div>
                      <div className="text-xs text-slate-400">Share problems with location and photos</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center shrink-0">
                      <Camera size={20} className="text-blue-400" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">Share photos and location</div>
                      <div className="text-xs text-slate-400">Document issues with real evidence</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center shrink-0">
                      <Heart size={20} className="text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">Help improve your community</div>
                      <div className="text-xs text-slate-400">Together for a stronger Maharashtra</div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="space-y-3">
                  <h1 className="text-4xl font-black leading-tight tracking-tight text-white">
                    Be the Voice<br />
                    <span className="text-orange-400">for a Better Tomorrow</span>
                  </h1>
                  <p className="text-sm text-slate-300 leading-relaxed max-w-sm">
                    Report issues. Share your feedback.<br />
                    Help improve public infrastructure.
                  </p>
                </div>
                <div className="space-y-5 pt-2">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-orange-500/20 flex items-center justify-center shrink-0">
                      <MapPin size={20} className="text-orange-400" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">Report Issues</div>
                      <div className="text-xs text-slate-400">Share problems with photos and location</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center shrink-0">
                      <CheckCircle2 size={20} className="text-blue-400" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">Track Progress</div>
                      <div className="text-xs text-slate-400">Stay updated on your complaints</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center shrink-0">
                      <Heart size={20} className="text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">Build a Stronger Community</div>
                      <div className="text-xs text-slate-400">Together for a better Maharashtra</div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="relative z-10 text-xs text-slate-500 border-t border-white/10 pt-4">
            Government of Maharashtra • SetuX Platform
          </div>
        </div>

        {/* RIGHT: WHITE BG + FLOATING CARD */}
        <div className="flex-1 bg-white flex items-center justify-center overflow-y-auto p-6">
          <div className="w-full max-w-sm space-y-5">

            {/* Account type selector */}
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-500 text-center">Select Account Type</p>
              <div className="grid grid-cols-2 gap-2 p-1 rounded-xl border border-slate-200 bg-slate-50">
                <button
                  type="button"
                  onClick={() => handleRoleChange('officer')}
                  className={`py-2 px-3 text-xs font-bold rounded-lg flex items-center justify-center gap-1.5 transition-all ${
                    role === 'officer' ? 'bg-[#0F2942] text-white shadow-sm' : 'text-slate-600 hover:text-slate-800'
                  }`}
                >
                  <ShieldCheck size={14} />
                  Officer Portal
                </button>
                <button
                  type="button"
                  onClick={() => handleRoleChange('citizen')}
                  className={`py-2 px-3 text-xs font-bold rounded-lg flex items-center justify-center gap-1.5 transition-all ${
                    role === 'citizen' ? 'bg-[#0F2942] text-white shadow-sm' : 'text-slate-600 hover:text-slate-800'
                  }`}
                >
                  <User size={14} />
                  Citizen Portal
                </button>
              </div>
            </div>

            {/* Sign In / Register underline tabs */}
            <div className="flex border-b border-slate-200">
              <button
                type="button"
                onClick={() => switchTab(true)}
                className={`flex-1 pb-2.5 text-sm font-semibold transition-all ${
                  isLogin ? 'border-b-2 border-[#0F2942] text-[#0F2942] -mb-px' : 'text-slate-400 hover:text-slate-600'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => switchTab(false)}
                className={`flex-1 pb-2.5 text-sm font-semibold transition-all ${
                  !isLogin ? 'border-b-2 border-[#0F2942] text-[#0F2942] -mb-px' : 'text-slate-400 hover:text-slate-600'
                }`}
              >
                Register
              </button>
            </div>

            {/* Form heading */}
            <h2 className="text-lg font-black text-[#0F2942]">
              {isLogin ? `${roleLabel} Login` : `${roleLabel} Registration`}
            </h2>

            {/* Alerts */}
            {success && (
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3 rounded-xl flex items-start gap-2 text-xs font-medium">
                <CheckCircle2 size={15} className="shrink-0 mt-0.5 text-emerald-600" />
                <span>{success}</span>
              </div>
            )}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-xl flex items-start gap-2 text-xs font-medium">
                <AlertCircle size={15} className="shrink-0 mt-0.5 text-red-500" />
                <span>{error}</span>
              </div>
            )}

            {/* Form */}
            <form className="space-y-4" onSubmit={handleSubmit}>

              {!isLogin && (
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Full Name</label>
                  <div className="relative">
                    <User size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Enter your full name"
                      className="w-full pl-9 pr-3 py-2.5 border border-slate-200 rounded-xl text-sm text-slate-800 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-[#0F2942] focus:bg-white transition"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Email Address</label>
                <div className="relative">
                  <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={emailPlaceholder}
                    className="w-full pl-9 pr-3 py-2.5 border border-slate-200 rounded-xl text-sm text-slate-800 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-[#0F2942] focus:bg-white transition"
                  />
                </div>
              </div>

              {!isLogin && (
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Phone Number</label>
                  <div className="relative">
                    <Phone size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="Enter your phone number"
                      className="w-full pl-9 pr-3 py-2.5 border border-slate-200 rounded-xl text-sm text-slate-800 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-[#0F2942] focus:bg-white transition"
                    />
                  </div>
                </div>
              )}

              {!isLogin && role === 'officer' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Department</label>
                  <div className="relative">
                    <Building size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <select
                      value={departmentId}
                      onChange={(e) => setDepartmentId(e.target.value)}
                      required
                      className="w-full pl-9 pr-3 py-2.5 border border-slate-200 rounded-xl text-sm text-slate-800 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-[#0F2942] focus:bg-white transition"
                    >
                      {departments.map((dept) => (
                        <option key={dept.id} value={dept.id}>
                          {dept.name} ({dept.code})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Password</label>
                <div className="relative">
                  <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full pl-9 pr-10 py-2.5 border border-slate-200 rounded-xl text-sm text-slate-800 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-[#0F2942] focus:bg-white transition"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </div>

              {!isLogin && (
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Confirm Password</label>
                  <div className="relative">
                    <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="password"
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Re-enter your password"
                      className="w-full pl-9 pr-3 py-2.5 border border-slate-200 rounded-xl text-sm text-slate-800 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-[#0F2942] focus:bg-white transition"
                    />
                  </div>
                </div>
              )}

              {isLogin && (
                <div className="flex items-center justify-between text-xs">
                  <label className="flex items-center gap-2 text-slate-600 cursor-pointer select-none">
                    <input type="checkbox" defaultChecked className="w-3.5 h-3.5 rounded border-slate-300 accent-[#0F2942]" />
                    Remember this device
                  </label>
                  <button
                    type="button"
                    onClick={() => alert('Password reset coming soon.')}
                    className="font-semibold text-slate-500 hover:text-[#0F2942] hover:underline transition"
                  >
                    Forgot password?
                  </button>
                </div>
              )}

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 rounded-xl text-sm font-bold text-white bg-[#0F2942] hover:bg-[#0B1E36] flex items-center justify-center gap-2 transition-all disabled:opacity-60 shadow-sm hover:shadow-md"
              >
                {submitting
                  ? 'Processing...'
                  : isLogin
                  ? `Login as ${roleLabel}`
                  : `Create a ${roleLabel} Account`}
              </button>
            </form>

            <p className="text-center text-xs text-slate-500">
              {isLogin ? (
                <>
                  New to SetuX?{' '}
                  <button type="button" onClick={() => switchTab(false)} className="font-semibold text-[#0F2942] hover:underline">
                    Create a {role} account
                  </button>
                </>
              ) : (
                <>
                  Already have an account?{' '}
                  <button type="button" onClick={() => switchTab(true)} className="font-semibold text-[#0F2942] hover:underline">
                    Sign in
                  </button>
                </>
              )}
            </p>

          </div>
        </div>
      </div>
    </div>
  );
}
