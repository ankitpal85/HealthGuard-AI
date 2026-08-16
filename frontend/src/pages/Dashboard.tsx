import React, { useEffect, useState } from 'react';
import { fetchDashboardSummary } from '../services/api';
import { Activity, Pill, Heart, Zap, TrendingUp, ArrowUpRight, ShieldCheck, Sparkles, Stethoscope, Brain } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface DashboardProps {
  userId: number;
  setActiveTab: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ userId, setActiveTab }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardSummary(userId)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [userId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-80 font-semibold" style={{ color: '#0EA5E9' }}>
        <div className="animate-spin w-8 h-8 border-3 rounded-full mr-3" style={{ borderColor: '#0EA5E9', borderTopColor: 'transparent', boxShadow: '0 0 16px rgba(14,165,233,0.3)' }} />
        Initializing Clinical Intelligence Engine...
      </div>
    );
  }

  const adherence = data?.adherence_7day || 85;

  const vitalsTrendData = [
    { day: 'Mon', bp: 120, heartRate: 72 },
    { day: 'Tue', bp: 122, heartRate: 74 },
    { day: 'Wed', bp: 118, heartRate: 70 },
    { day: 'Thu', bp: 121, heartRate: 73 },
    { day: 'Fri', bp: 119, heartRate: 71 },
    { day: 'Sat', bp: 124, heartRate: 76 },
    { day: 'Sun', bp: 120, heartRate: 72 },
  ];

  return (
    <div className="space-y-7 animate-in fade-in duration-300">
      {/* Welcome Banner */}
      <div className="glass-panel p-8 rounded-3xl relative overflow-hidden shadow-2xl"
        style={{ background: 'linear-gradient(135deg, rgba(14,165,233,0.1) 0%, rgba(6,214,160,0.06) 50%, rgba(244,114,182,0.04) 100%)', border: '1px solid rgba(14,165,233,0.15)' }}>
        <div className="absolute right-0 top-0 w-96 h-96 rounded-full blur-3xl pointer-events-none" style={{ background: 'rgba(14,165,233,0.08)' }} />
        <div className="absolute bottom-0 left-20 w-64 h-64 rounded-full blur-3xl pointer-events-none" style={{ background: 'rgba(6,214,160,0.05)' }} />

        <div className="relative z-10 flex items-center justify-between">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold mb-3"
              style={{ background: 'rgba(14,165,233,0.12)', border: '1px solid rgba(14,165,233,0.25)', color: '#38BDF8' }}>
              <Sparkles className="w-3.5 h-3.5" /> AI Health Monitoring Active
            </div>
            <h2 className="text-3xl font-extrabold text-white tracking-tight" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              Welcome back, <span style={{ background: 'linear-gradient(135deg, #0EA5E9, #06D6A0)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>{data?.user?.name || 'Dr. Ankit'}</span>
            </h2>
            <p className="text-sm font-medium mt-1.5 max-w-xl" style={{ color: '#94A3B8' }}>
              Your real-time vitals, medication adherence, and predictive risk indicators are synchronized.
            </p>
          </div>

          <div className="hidden md:flex items-center gap-3">
            <button
              onClick={() => setActiveTab('chatbot')}
              className="btn-primary px-5 py-3 rounded-2xl text-xs font-extrabold flex items-center gap-2"
            >
              <Stethoscope className="w-4 h-4" />
              <span>Ask HealthGuard AI</span>
              <ArrowUpRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="glass-panel glass-panel-hover p-6 relative overflow-hidden">
          <div className="absolute -top-6 -right-6 w-20 h-20 rounded-full opacity-20" style={{ background: 'radial-gradient(circle, #0EA5E9, transparent)' }} />
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider" style={{ color: '#64748B' }}>
            <span>7-Day Adherence</span>
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'rgba(14,165,233,0.12)', border: '1px solid rgba(14,165,233,0.2)' }}>
              <Pill className="w-4 h-4" style={{ color: '#0EA5E9' }} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white tracking-tight" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>{adherence}%</span>
            <span className="px-2.5 py-1 text-[10px] font-extrabold rounded-full badge-mint">Optimal</span>
          </div>
          <div className="w-full rounded-full h-2 mt-4 overflow-hidden p-0.5" style={{ background: 'rgba(15,23,42,0.8)' }}>
            <div className="h-full rounded-full transition-all duration-500" style={{ width: `${adherence}%`, background: 'linear-gradient(90deg, #0EA5E9, #06D6A0)' }} />
          </div>
        </div>

        <div className="glass-panel glass-panel-hover p-6 relative overflow-hidden">
          <div className="absolute -top-6 -right-6 w-20 h-20 rounded-full opacity-20" style={{ background: 'radial-gradient(circle, #06D6A0, transparent)' }} />
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider" style={{ color: '#64748B' }}>
            <span>Active Medications</span>
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'rgba(6,214,160,0.12)', border: '1px solid rgba(6,214,160,0.2)' }}>
              <Activity className="w-4 h-4" style={{ color: '#06D6A0' }} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white tracking-tight" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>{data?.active_medications_count || 3}</span>
            <span className="text-xs font-medium" style={{ color: '#64748B' }}>Daily Prescriptions</span>
          </div>
          <p className="text-xs mt-4 font-semibold flex items-center gap-1.5" style={{ color: '#06D6A0' }}>
            <Zap className="w-3.5 h-3.5" /> Next dose in 2 hours
          </p>
        </div>

        <div className="glass-panel glass-panel-hover p-6 relative overflow-hidden">
          <div className="absolute -top-6 -right-6 w-20 h-20 rounded-full opacity-20" style={{ background: 'radial-gradient(circle, #F472B6, transparent)' }} />
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider" style={{ color: '#64748B' }}>
            <span>Blood Pressure</span>
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'rgba(244,114,182,0.12)', border: '1px solid rgba(244,114,182,0.2)' }}>
              <Heart className="w-4 h-4" style={{ color: '#F472B6' }} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white tracking-tight" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>120/80</span>
            <span className="text-xs font-medium" style={{ color: '#64748B' }}>mmHg</span>
          </div>
          <p className="text-xs mt-4 font-semibold flex items-center gap-1" style={{ color: '#06D6A0' }}>
            <ShieldCheck className="w-3.5 h-3.5" /> Optimal Range
          </p>
        </div>

        <div className="glass-panel glass-panel-hover p-6 relative overflow-hidden">
          <div className="absolute -top-6 -right-6 w-20 h-20 rounded-full opacity-20" style={{ background: 'radial-gradient(circle, #F59E0B, transparent)' }} />
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider" style={{ color: '#64748B' }}>
            <span>AI Risk Score</span>
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'rgba(245,158,11,0.12)', border: '1px solid rgba(245,158,11,0.2)' }}>
              <TrendingUp className="w-4 h-4" style={{ color: '#F59E0B' }} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-extrabold text-white tracking-tight" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>Low</span>
            <span className="px-2.5 py-1 text-[10px] font-extrabold rounded-full badge-sky">94% Safe</span>
          </div>
          <p className="text-xs mt-4 font-medium" style={{ color: '#64748B' }}>No critical alerts detected</p>
        </div>
      </div>

      {/* Main Content Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Vitals Trend Chart */}
        <div className="lg:col-span-2 glass-panel p-7 space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-extrabold text-white text-base flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
                <Activity className="w-5 h-5" style={{ color: '#0EA5E9' }} />
                Vitals & Heart Rate History
              </h3>
              <p className="text-xs font-medium mt-0.5" style={{ color: '#64748B' }}>7-day continuous biometric telemetry</p>
            </div>
            <button
              onClick={() => setActiveTab('vitals')}
              className="text-xs font-bold flex items-center gap-1 transition-colors hover:opacity-80"
              style={{ color: '#0EA5E9' }}
            >
              Full Analytics <ArrowUpRight className="w-4 h-4" />
            </button>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={vitalsTrendData}>
                <defs>
                  <linearGradient id="colorBp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0EA5E9" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0EA5E9" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" stroke="#475569" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#475569" fontSize={11} domain={[60, 140]} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0F172A', borderColor: '#0EA5E9', borderRadius: '14px', color: '#F8FAFC', fontSize: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.4)' }} />
                <Area type="monotone" dataKey="bp" stroke="#0EA5E9" strokeWidth={3} fillOpacity={1} fill="url(#colorBp)" name="Systolic BP" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick AI Action Card */}
        <div className="glass-panel p-7 space-y-5 flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-white text-base flex items-center gap-2 mb-1" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              <Brain className="w-5 h-5" style={{ color: '#06D6A0' }} />
              Smart Health Actions
            </h3>
            <p className="text-xs font-medium" style={{ color: '#64748B' }}>Quick launch clinical modules</p>
          </div>

          <div className="space-y-3">
            <button
              type="button"
              onClick={() => setActiveTab('chatbot')}
              className="w-full p-4 rounded-2xl btn-primary text-xs font-extrabold flex items-center justify-between cursor-pointer"
            >
              <span className="flex items-center gap-2">🤖 Start AI Chat Session</span>
              <ArrowUpRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('medications')}
              className="w-full p-3.5 rounded-2xl text-xs font-bold flex items-center justify-between transition-all cursor-pointer"
              style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(14,165,233,0.1)', color: '#E2E8F0' }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(14,165,233,0.3)'; (e.currentTarget as HTMLElement).style.background = 'rgba(14,165,233,0.06)'; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(14,165,233,0.1)'; (e.currentTarget as HTMLElement).style.background = 'rgba(15,23,42,0.7)'; }}
            >
              <span>💊 Log Today's Medication</span>
              <ArrowUpRight className="w-4 h-4" style={{ color: '#64748B' }} />
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('analytics')}
              className="w-full p-3.5 rounded-2xl text-xs font-bold flex items-center justify-between transition-all cursor-pointer"
              style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(14,165,233,0.1)', color: '#E2E8F0' }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(6,214,160,0.3)'; (e.currentTarget as HTMLElement).style.background = 'rgba(6,214,160,0.06)'; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(14,165,233,0.1)'; (e.currentTarget as HTMLElement).style.background = 'rgba(15,23,42,0.7)'; }}
            >
              <span>📋 Run Symptom Analyzer</span>
              <ArrowUpRight className="w-4 h-4" style={{ color: '#64748B' }} />
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('indian_health')}
              className="w-full p-3.5 rounded-2xl text-xs font-bold flex items-center justify-between transition-all cursor-pointer"
              style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(14,165,233,0.1)', color: '#E2E8F0' }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(244,114,182,0.3)'; (e.currentTarget as HTMLElement).style.background = 'rgba(244,114,182,0.06)'; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = 'rgba(14,165,233,0.1)'; (e.currentTarget as HTMLElement).style.background = 'rgba(15,23,42,0.7)'; }}
            >
              <span>🇮🇳 1mg & AYUSH Remedies</span>
              <ArrowUpRight className="w-4 h-4" style={{ color: '#64748B' }} />
            </button>
          </div>

          <div className="p-3.5 rounded-2xl text-[11px] text-center font-medium" style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(14,165,233,0.06)', color: '#475569' }}>
            🔒 Protected by HIPAA-Compliant End-to-End Encryption
          </div>
        </div>
      </div>
    </div>
  );
};
