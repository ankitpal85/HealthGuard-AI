import React, { useState } from 'react';
import { Activity, Sparkles, Mail, Lock, User, ArrowRight, CheckCircle2, ShieldCheck, HeartPulse, Stethoscope, AlertCircle } from 'lucide-react';
import { loginUser, registerUser } from '../services/api';

interface AuthPageProps {
  users: any[];
  onLoginSuccess: (userId: number, userObj?: any) => void;
  onSkipToDashboard?: () => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ users, onLoginSuccess, onSkipToDashboard }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [age, setAge] = useState<number>(30);
  const [gender, setGender] = useState('Male');
  const [bloodGroup, setBloodGroup] = useState('O+');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setLoading(true);

    try {
      if (mode === 'login') {
        const res = await loginUser(email, password);
        setSuccessMsg(`Welcome back, ${res.name}! Synchronizing health records...`);
        setTimeout(() => {
          onLoginSuccess(res.user_id, res);
        }, 1000);
      } else {
        const res = await registerUser(email, password, name, age, gender, bloodGroup);
        setSuccessMsg(`Account created successfully via ${res.provider}! Initializing patient telemetry...`);
        setTimeout(() => {
          onLoginSuccess(res.user_id, res);
        }, 1200);
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-dark-900" style={{ background: '#090D16' }}>
      {/* Dynamic Background Glowing Orbs */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full blur-[140px] pointer-events-none opacity-20" style={{ background: 'radial-gradient(circle, #0EA5E9, transparent)' }} />
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] rounded-full blur-[140px] pointer-events-none opacity-20" style={{ background: 'radial-gradient(circle, #06D6A0, transparent)' }} />
      <div className="absolute top-10 right-10 w-96 h-96 rounded-full blur-[120px] pointer-events-none opacity-15" style={{ background: 'radial-gradient(circle, #F472B6, transparent)' }} />

      <div className="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10 animate-in fade-in zoom-in-95 duration-500">
        
        {/* Left Side: Product Showcase Card */}
        <div className="glass-panel p-8 rounded-3xl flex flex-col justify-between relative overflow-hidden shadow-2xl"
          style={{ background: 'linear-gradient(135deg, rgba(14,165,233,0.12) 0%, rgba(6,214,160,0.06) 100%)', border: '1px solid rgba(14,165,233,0.2)' }}
        >
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #0EA5E9, #06D6A0)' }}>
                <Activity className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-extrabold text-white tracking-tight" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>HealthGuard AI</h1>
                <p className="text-xs font-semibold text-sky-400">Clinical Intelligence & Voice Monitoring</p>
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold" style={{ background: 'rgba(14,165,233,0.15)', border: '1px solid rgba(14,165,233,0.3)', color: '#38BDF8' }}>
                <Sparkles className="w-3.5 h-3.5" /> Firebase Cloud & Salted SHA-256 Security
              </div>
              <h2 className="text-3xl font-extrabold text-white leading-tight">
                Empowering Patient Longevity with AI Medical Intelligence.
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed">
                Securely log vitals, track 1mg Indian medicines, receive real-time voice consultations, and analyze diagnostic lab reports.
              </p>
            </div>

            <div className="space-y-2.5 pt-4">
              <div className="flex items-center gap-3 p-3 rounded-2xl" style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(14,165,233,0.1)' }}>
                <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
                <span className="text-xs text-slate-300 font-semibold">End-to-End Encrypted Patient Data Isolation</span>
              </div>

              <div className="flex items-center gap-3 p-3 rounded-2xl" style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(14,165,233,0.1)' }}>
                <HeartPulse className="w-5 h-5 text-sky-400 shrink-0" />
                <span className="text-xs text-slate-300 font-semibold">Predictive Cardiovascular & Diabetes Risk Scoring</span>
              </div>

              <div className="flex items-center gap-3 p-3 rounded-2xl" style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(14,165,233,0.1)' }}>
                <Stethoscope className="w-5 h-5 text-pink-400 shrink-0" />
                <span className="text-xs text-slate-300 font-semibold">Continuous Voice Mode & Diagnostic PDF Parser</span>
              </div>
            </div>
          </div>

          {/* Quick Switching Demo Account List */}
          {users.length > 0 && (
            <div className="pt-6 border-t border-slate-800/60 mt-6">
              <p className="text-[11px] font-extrabold text-slate-400 uppercase tracking-wider mb-2.5">
                ⚡ Quick Switch Registered Demo Accounts:
              </p>
              <div className="flex flex-wrap gap-2">
                {users.slice(0, 4).map((u) => (
                  <button
                    key={u.id}
                    type="button"
                    onClick={() => onLoginSuccess(u.id, u)}
                    className="px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer hover:scale-105"
                    style={{ background: 'rgba(14,165,233,0.12)', border: '1px solid rgba(14,165,233,0.25)', color: '#38BDF8' }}
                  >
                    👤 {u.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Auth Form */}
        <div className="glass-panel p-8 rounded-3xl flex flex-col justify-between relative shadow-2xl"
          style={{ background: 'rgba(15,23,42,0.85)', border: '1px solid rgba(14,165,233,0.2)' }}
        >
          <div>
            {/* Header Tabs */}
            <div className="flex items-center justify-between p-1 rounded-2xl mb-6" style={{ background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(14,165,233,0.15)' }}>
              <button
                type="button"
                onClick={() => setMode('login')}
                className={`flex-1 py-2.5 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
                  mode === 'login' ? 'btn-primary text-white shadow-lg' : 'text-slate-400 hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setMode('register')}
                className={`flex-1 py-2.5 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
                  mode === 'register' ? 'btn-primary text-white shadow-lg' : 'text-slate-400 hover:text-white'
                }`}
              >
                Create Account
              </button>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-semibold flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" /> {error}
              </div>
            )}

            {successMsg && (
              <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" /> {successMsg}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === 'register' && (
                <>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1.5">Full Name</label>
                    <div className="relative">
                      <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                      <input
                        type="text"
                        required
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Dr. Ankit Sharma"
                        className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-300 mb-1.5">Age</label>
                      <input
                        type="number"
                        value={age}
                        onChange={(e) => setAge(Number(e.target.value))}
                        className="w-full px-3 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-300 mb-1.5">Gender</label>
                      <select
                        value={gender}
                        onChange={(e) => setGender(e.target.value)}
                        className="w-full px-2 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                      >
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-300 mb-1.5">Blood Group</label>
                      <select
                        value={bloodGroup}
                        onChange={(e) => setBloodGroup(e.target.value)}
                        className="w-full px-2 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                      >
                        <option value="O+">O+</option>
                        <option value="A+">A+</option>
                        <option value="B+">B+</option>
                        <option value="AB+">AB+</option>
                        <option value="O-">O-</option>
                      </select>
                    </div>
                  </div>
                </>
              )}

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1.5">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="ankit@healthguard.ai"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1.5">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 rounded-2xl btn-primary font-extrabold text-xs shadow-xl flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 transition-all hover:scale-[1.02]"
              >
                <span>{loading ? 'Authenticating Credentials...' : mode === 'login' ? 'Sign In to HealthGuard' : 'Create Secure Patient Profile'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          </div>

          <div className="pt-4 text-center">
            {onSkipToDashboard && (
              <button
                type="button"
                onClick={onSkipToDashboard}
                className="text-xs font-semibold text-slate-400 hover:text-sky-400 transition-colors cursor-pointer"
              >
                Skip Authentication & Continue as Guest →
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
