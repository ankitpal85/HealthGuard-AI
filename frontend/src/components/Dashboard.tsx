import React from 'react';
import {
  HeartPulse, Thermometer, Droplets, Activity, Weight,
  Moon, Pill, Users, TrendingUp, TrendingDown, Minus,
  Timer, Brain, ShieldCheck, Stethoscope, AlertTriangle
} from 'lucide-react';

/* ════════ METRIC CARD ═══════════════════════════════ */
interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  unit: string;
  trend?: 'up' | 'down' | 'stable';
  trendText?: string;
  accentColor: string;
  glowColor: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, label, value, unit, trend, trendText, accentColor, glowColor }) => {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  return (
    <div className="glass-panel glass-panel-hover p-5 flex flex-col gap-3 relative overflow-hidden group cursor-default">
      {/* Ambient glow */}
      <div className="absolute -top-8 -right-8 w-24 h-24 rounded-full opacity-20 group-hover:opacity-30 transition-opacity duration-300"
        style={{ background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)` }} />

      <div className="flex items-center justify-between relative z-10">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ background: glowColor, border: `1px solid ${accentColor}33` }}>
          {icon}
        </div>
        {trend && (
          <span className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold"
            style={{
              background: trend === 'up' ? 'rgba(6,214,160,0.12)' : trend === 'down' ? 'rgba(239,68,68,0.12)' : 'rgba(148,163,184,0.12)',
              color: trend === 'up' ? '#06D6A0' : trend === 'down' ? '#EF4444' : '#94A3B8',
            }}>
            <TrendIcon className="w-3 h-3" />{trendText}
          </span>
        )}
      </div>

      <div className="relative z-10">
        <p className="text-[11px] font-bold uppercase tracking-wider" style={{ color: '#64748B' }}>{label}</p>
        <p className="text-2xl font-extrabold mt-1 flex items-baseline gap-1.5" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
          <span className="text-white">{value}</span>
          <span className="text-xs font-semibold" style={{ color: '#64748B' }}>{unit}</span>
        </p>
      </div>
    </div>
  );
};

/* ════════ DASHBOARD ═════════════════════════════════ */
export const Dashboard: React.FC = () => {
  const metrics = [
    { icon: <HeartPulse className="w-5 h-5" style={{ color: '#F472B6' }} />, label: 'Heart Rate', value: 72, unit: 'BPM', trend: 'stable' as const, trendText: 'Normal', accentColor: '#F472B6', glowColor: 'rgba(244,114,182,0.12)' },
    { icon: <Activity className="w-5 h-5" style={{ color: '#0EA5E9' }} />, label: 'Blood Pressure', value: '120/80', unit: 'mmHg', trend: 'stable' as const, trendText: 'Optimal', accentColor: '#0EA5E9', glowColor: 'rgba(14,165,233,0.12)' },
    { icon: <Thermometer className="w-5 h-5" style={{ color: '#F59E0B' }} />, label: 'Temperature', value: '98.6', unit: '°F', trend: 'stable' as const, trendText: 'Normal', accentColor: '#F59E0B', glowColor: 'rgba(245,158,11,0.12)' },
    { icon: <Droplets className="w-5 h-5" style={{ color: '#06D6A0' }} />, label: 'SpO₂ Level', value: 98, unit: '%', trend: 'up' as const, trendText: '+1%', accentColor: '#06D6A0', glowColor: 'rgba(6,214,160,0.12)' },
    { icon: <Weight className="w-5 h-5" style={{ color: '#8B5CF6' }} />, label: 'Weight (BMI)', value: '72.5', unit: 'kg (24.3)', trend: 'down' as const, trendText: '-0.3', accentColor: '#8B5CF6', glowColor: 'rgba(139,92,246,0.12)' },
    { icon: <Moon className="w-5 h-5" style={{ color: '#6366F1' }} />, label: 'Sleep Quality', value: '7h 20m', unit: 'deep 2h', trend: 'up' as const, trendText: '+15m', accentColor: '#6366F1', glowColor: 'rgba(99,102,241,0.12)' },
    { icon: <Pill className="w-5 h-5" style={{ color: '#14B8A6' }} />, label: 'Medications', value: '4/5', unit: 'taken', trend: 'stable' as const, trendText: 'On Track', accentColor: '#14B8A6', glowColor: 'rgba(20,184,166,0.12)' },
    { icon: <Users className="w-5 h-5" style={{ color: '#0EA5E9' }} />, label: 'Family Members', value: 3, unit: 'active', trend: 'stable' as const, trendText: 'Linked', accentColor: '#0EA5E9', glowColor: 'rgba(14,165,233,0.12)' },
  ];

  return (
    <div className="p-8 space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl p-8"
        style={{
          background: 'linear-gradient(135deg, rgba(14,165,233,0.12) 0%, rgba(6,214,160,0.08) 50%, rgba(244,114,182,0.06) 100%)',
          border: '1px solid rgba(14,165,233,0.15)',
        }}>
        {/* Decorative */}
        <div className="absolute top-0 right-0 w-72 h-72 rounded-full opacity-20"
          style={{ background: 'radial-gradient(circle, rgba(14,165,233,0.3) 0%, transparent 70%)' }} />
        <div className="absolute bottom-0 left-0 w-48 h-48 rounded-full opacity-10"
          style={{ background: 'radial-gradient(circle, rgba(6,214,160,0.4) 0%, transparent 70%)' }} />

        <div className="relative z-10 flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-extrabold text-white flex items-center gap-3" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center"
                style={{ background: 'linear-gradient(135deg, #0EA5E9, #06B6D4)', boxShadow: '0 6px 20px rgba(14,165,233,0.3)' }}>
                <Stethoscope className="w-6 h-6 text-white" />
              </div>
              Good Morning, Dr. Ankit
            </h3>
            <p className="text-sm font-medium mt-3 ml-[60px]" style={{ color: '#94A3B8' }}>
              All vitals are within normal ranges. <strong style={{ color: '#06D6A0' }}>No critical alerts</strong> this morning.
            </p>
          </div>

          <div className="flex gap-3">
            <div className="text-center px-5 py-3 rounded-xl" style={{ background: 'rgba(14,165,233,0.1)', border: '1px solid rgba(14,165,233,0.2)' }}>
              <ShieldCheck className="w-5 h-5 mx-auto mb-1" style={{ color: '#0EA5E9' }} />
              <p className="text-xs font-bold" style={{ color: '#0EA5E9' }}>All Clear</p>
            </div>
            <div className="text-center px-5 py-3 rounded-xl" style={{ background: 'rgba(6,214,160,0.1)', border: '1px solid rgba(6,214,160,0.2)' }}>
              <Brain className="w-5 h-5 mx-auto mb-1" style={{ color: '#06D6A0' }} />
              <p className="text-xs font-bold" style={{ color: '#06D6A0' }}>AI Active</p>
            </div>
          </div>
        </div>
      </div>

      {/* Section Title */}
      <div className="flex items-center gap-2.5">
        <div className="w-1.5 h-5 rounded-full" style={{ background: 'linear-gradient(180deg, #0EA5E9, #06D6A0)' }} />
        <h3 className="text-base font-extrabold text-white" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
          Patient Vitals Overview
        </h3>
        <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full badge-sky">LIVE DATA</span>
      </div>

      {/* Metric Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {metrics.map((m, i) => (
          <MetricCard key={i} {...m} />
        ))}
      </div>

      {/* Quick Insights Row */}
      <div className="flex items-center gap-2.5 mb-2">
        <div className="w-1.5 h-5 rounded-full" style={{ background: 'linear-gradient(180deg, #06D6A0, #14B8A6)' }} />
        <h3 className="text-base font-extrabold text-white" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
          Clinical Insights
        </h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Upcoming */}
        <div className="glass-panel p-5">
          <div className="flex items-center gap-2 mb-4">
            <Timer className="w-4 h-4" style={{ color: '#0EA5E9' }} />
            <span className="text-xs font-bold" style={{ color: '#0EA5E9' }}>UPCOMING</span>
          </div>
          <div className="space-y-3">
            {[
              { time: '10:00 AM', event: 'Metformin 500mg', type: 'medication' },
              { time: '01:00 PM', event: 'Blood Sugar Check', type: 'vital' },
              { time: '06:00 PM', event: 'Evening Walk (30 min)', type: 'fitness' },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors duration-200"
                style={{ background: 'rgba(15,23,42,0.5)', border: '1px solid rgba(14,165,233,0.06)' }}>
                <span className="text-[11px] font-bold shrink-0" style={{ color: '#64748B' }}>{item.time}</span>
                <span className="w-px h-4" style={{ background: 'rgba(14,165,233,0.15)' }} />
                <span className="text-[12px] font-semibold text-white">{item.event}</span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Summary */}
        <div className="glass-panel p-5">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-4 h-4" style={{ color: '#06D6A0' }} />
            <span className="text-xs font-bold" style={{ color: '#06D6A0' }}>AI HEALTH SUMMARY</span>
          </div>
          <div className="space-y-3">
            <p className="text-[13px] font-medium leading-relaxed" style={{ color: '#CBD5E1' }}>
              Your <strong style={{ color: '#06D6A0' }}>cardiovascular health</strong> is trending positively. BP consistent at 120/80 for 7 days.
            </p>
            <p className="text-[13px] font-medium leading-relaxed" style={{ color: '#CBD5E1' }}>
              <strong style={{ color: '#F59E0B' }}>Sleep patterns</strong> improved by 12% this week. Recommend maintaining current routine.
            </p>
            <p className="text-[13px] font-medium leading-relaxed" style={{ color: '#CBD5E1' }}>
              <strong style={{ color: '#F472B6' }}>BMI</strong> is approaching optimal range — weight loss on track.
            </p>
          </div>
        </div>

        {/* Active Alerts */}
        <div className="glass-panel p-5">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-4 h-4" style={{ color: '#F59E0B' }} />
            <span className="text-xs font-bold" style={{ color: '#F59E0B' }}>ACTIVE ALERTS</span>
          </div>
          <div className="space-y-3">
            <div className="flex items-start gap-2.5 px-3 py-2.5 rounded-lg" style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.1)' }}>
              <Pill className="w-4 h-4 mt-0.5 shrink-0" style={{ color: '#F59E0B' }} />
              <div>
                <p className="text-[12px] font-bold" style={{ color: '#F59E0B' }}>Missed Dose</p>
                <p className="text-[11px] font-medium" style={{ color: '#64748B' }}>Vitamin D3 — Yesterday 8 PM</p>
              </div>
            </div>
            <div className="flex items-start gap-2.5 px-3 py-2.5 rounded-lg" style={{ background: 'rgba(14,165,233,0.06)', border: '1px solid rgba(14,165,233,0.1)' }}>
              <Activity className="w-4 h-4 mt-0.5 shrink-0" style={{ color: '#0EA5E9' }} />
              <div>
                <p className="text-[12px] font-bold" style={{ color: '#0EA5E9' }}>Checkup Due</p>
                <p className="text-[11px] font-medium" style={{ color: '#64748B' }}>Annual health check in 5 days</p>
              </div>
            </div>
            <div className="flex items-start gap-2.5 px-3 py-2.5 rounded-lg" style={{ background: 'rgba(6,214,160,0.06)', border: '1px solid rgba(6,214,160,0.1)' }}>
              <ShieldCheck className="w-4 h-4 mt-0.5 shrink-0" style={{ color: '#06D6A0' }} />
              <div>
                <p className="text-[12px] font-bold" style={{ color: '#06D6A0' }}>All Vitals Normal</p>
                <p className="text-[11px] font-medium" style={{ color: '#64748B' }}>No critical values detected</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
