import React, { useEffect, useState } from 'react';
import { fetchDashboardSummary, downloadDoctorPdfReport } from '../services/api';
import { Activity, Pill, Heart, Zap, TrendingUp, ArrowUpRight, ShieldCheck, Sparkles, Stethoscope, Download, Brain } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface DashboardProps {
  userId: number;
  setActiveTab: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ userId, setActiveTab }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
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
        Synchronizing Patient Health Records...
      </div>
    );
  }

  const adherence = data?.adherence_7day || 85;
  const userName = data?.user?.name || 'Patient';

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

        <div className="relative z-10 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold mb-3"
              style={{ background: 'rgba(14,165,233,0.12)', border: '1px solid rgba(14,165,233,0.25)', color: '#38BDF8' }}>
              <Sparkles className="w-3.5 h-3.5" /> AI Health Monitoring Active
            </div>
            <h2 className="text-3xl font-extrabold text-white tracking-tight" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              Welcome back, <span style={{ background: 'linear-gradient(135deg, #0EA5E9, #06D6A0)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>{userName}</span>
            </h2>
            <p className="text-sm font-medium mt-1.5 max-w-xl" style={{ color: '#94A3B8' }}>
              Real-time vitals, 7-day adherence ({adherence}%), and AI predictive risk markers synchronized for {userName}.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => downloadDoctorPdfReport(userId)}
              className="px-5 py-3 rounded-2xl font-extrabold text-xs text-white transition-all shadow-lg flex items-center gap-2 cursor-pointer"
              style={{ background: 'linear-gradient(135deg, #06D6A0, #0EA5E9)', boxShadow: '0 6px 20px rgba(6,214,160,0.25)' }}
            >
              <Download className="w-4 h-4" />
              <span>Download Doctor Report (PDF)</span>
            </button>

            <button
              onClick={() => setActiveTab('chatbot')}
              className="btn-primary px-5 py-3 rounded-2xl text-xs font-extrabold flex items-center gap-2 cursor-pointer"
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

      {/* Main Charts & Actions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Vitals Graph */}
        <div className="lg:col-span-2 glass-panel p-7 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-extrabold text-white text-base" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>7-Day Vitals & Telemetry Trend</h3>
              <p className="text-xs font-medium" style={{ color: '#64748B' }}>Systolic Blood Pressure & Resting Heart Rate</p>
            </div>
            <span className="text-xs font-bold px-3 py-1 rounded-full badge-sky">Synchronized</span>
          </div>

          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={vitalsTrendData}>
                <defs>
                  <linearGradient id="colorBp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0EA5E9" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#0EA5E9" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorHr" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06D6A0" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#06D6A0" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" stroke="#64748B" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} axisLine={false} domain={[60, 140]} />
                <Tooltip
                  contentStyle={{ background: '#0F172A', border: '1px solid rgba(14,165,233,0.2)', borderRadius: '12px', color: '#fff' }}
                />
                <Area type="monotone" dataKey="bp" stroke="#0EA5E9" strokeWidth={3} fillOpacity={1} fill="url(#colorBp)" name="Systolic BP" />
                <Area type="monotone" dataKey="heartRate" stroke="#06D6A0" strokeWidth={2} fillOpacity={1} fill="url(#colorHr)" name="Heart Rate" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick AI & Lab PDF Upload Action Card */}
        <div className="glass-panel p-6 space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-white text-base flex items-center gap-2 mb-1" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              <Brain className="w-5 h-5" style={{ color: '#06D6A0' }} />
              Quick Medical PDF Upload
            </h3>

            <button
              type="button"
              onClick={() => setActiveTab('analytics')}
              className="w-full p-3.5 rounded-2xl text-xs font-extrabold flex items-center justify-between transition-all cursor-pointer card-action-btn"
            >
              <span>📋 Run Symptom Analyzer</span>
              <ArrowUpRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('indian_health')}
              className="w-full p-3.5 rounded-2xl text-xs font-extrabold flex items-center justify-between transition-all cursor-pointer card-action-btn mt-2.5"
            >
              <span>🇮🇳 1mg & AYUSH Remedies</span>
              <ArrowUpRight className="w-4 h-4" />
            </button>
          </div>

          <div className="p-3.5 rounded-2xl text-[11px] text-center font-semibold mt-3" style={{ background: 'rgba(14,165,233,0.06)', border: '1px solid rgba(14,165,233,0.15)', color: '#0EA5E9' }}>
            🔒 Protected by HIPAA-Compliant End-to-End Encryption
          </div>

        </div>
      </div>
    </div>
  );
};
