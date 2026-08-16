import React, { useEffect, useState } from 'react';
import { fetchVitals, logVital } from '../services/api';
import { Activity, Heart, Footprints, Moon, Plus, Sparkles, Thermometer } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface HealthLogProps {
  userId: number;
}

export const HealthLog: React.FC<HealthLogProps> = ({ userId }) => {
  const [vitals, setVitals] = useState<any[]>([]);
  const [metricType, setMetricType] = useState('heart_rate');
  const [newValue, setNewValue] = useState('');
  const [newValue2, setNewValue2] = useState(''); // Diastolic BP
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const loadVitals = () => {
    fetchVitals(userId, metricType)
      .then((res) => {
        setVitals(res);
      })
      .catch((err) => {
        console.error(err);
      });
  };

  useEffect(() => {
    loadVitals();
  }, [userId, metricType]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleLogVital = async (e?: React.FormEvent, customVal?: number, customVal2?: number) => {
    if (e) e.preventDefault();
    const val = customVal !== undefined ? customVal : parseFloat(newValue);
    const val2 = customVal2 !== undefined ? customVal2 : newValue2 ? parseFloat(newValue2) : undefined;
    if (isNaN(val)) return;

    try {
      await logVital({
        user_id: userId,
        metric_type: metricType,
        value: val,
        value2: val2,
        unit: metricType === 'heart_rate' ? 'bpm' : metricType === 'steps' ? 'steps' : metricType === 'blood_pressure' ? 'mmHg' : metricType === 'sleep' ? 'hours' : '°F',
      });
      setNewValue('');
      setNewValue2('');
      showToast(`✅ Logged ${metricType.replace('_', ' ').toUpperCase()}: ${val}${val2 ? '/' + val2 : ''}`);
      loadVitals();
    } catch (err) {
      console.error(err);
    }
  };

  const chartData = vitals.map((v) => ({
    time: v.recorded_at ? v.recorded_at.substring(5, 16) : 'Now',
    val: v.value,
  }));

  const metricColors: Record<string, string> = {
    heart_rate: '#F472B6',
    steps: '#06D6A0',
    blood_pressure: '#0EA5E9',
    sleep: '#8B5CF6',
    temperature: '#F59E0B',
  };

  const activeColor = metricColors[metricType] || '#0EA5E9';

  return (
    <div className="space-y-6 relative">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 px-4 py-3 rounded-xl shadow-2xl font-bold text-xs flex items-center gap-2 animate-in fade-in"
          style={{ background: '#0EA5E9', color: '#FFFFFF', boxShadow: '0 8px 24px rgba(14,165,233,0.3)' }}>
          {toastMessage}
        </div>
      )}

      <div className="flex items-center justify-between glass-panel p-6 rounded-2xl" style={{ border: '1px solid rgba(14,165,233,0.1)' }}>
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Activity className="w-6 h-6" style={{ color: '#0EA5E9' }} /> Health Vitals & Fitness Logger
          </h2>
          <p className="text-xs mt-1" style={{ color: '#64748B' }}>Track continuous health metrics, heart rate, blood pressure, and sleep history</p>
        </div>
      </div>

      {/* Select Metric Tabs */}
      <div className="flex flex-wrap items-center gap-3">
        {[
          { id: 'heart_rate', label: 'Heart Rate', icon: Heart, color: '#F472B6' },
          { id: 'blood_pressure', label: 'Blood Pressure', icon: Activity, color: '#0EA5E9' },
          { id: 'steps', label: 'Daily Steps', icon: Footprints, color: '#06D6A0' },
          { id: 'sleep', label: 'Sleep Hours', icon: Moon, color: '#8B5CF6' },
          { id: 'temperature', label: 'Temperature', icon: Thermometer, color: '#F59E0B' },
        ].map((m) => {
          const Icon = m.icon;
          const isActive = metricType === m.id;
          return (
            <button
              key={m.id}
              onClick={() => { setMetricType(m.id); setNewValue(''); setNewValue2(''); }}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-xs transition-all cursor-pointer"
              style={{
                background: isActive ? `${m.color}15` : 'rgba(15,23,42,0.6)',
                color: isActive ? m.color : '#94A3B8',
                border: isActive ? `1px solid ${m.color}40` : '1px solid transparent',
              }}
            >
              <Icon className="w-4 h-4" /> {m.label}
            </button>
          );
        })}
      </div>

      {/* Log Input & Chart Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-6 space-y-4">
          <h3 className="font-bold text-white text-sm" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>Visual Telemetry Trend — {metricType.replace('_', ' ').toUpperCase()}</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData.length > 0 ? chartData : [{ time: 'Mon', val: 72 }, { time: 'Tue', val: 74 }, { time: 'Wed', val: 70 }, { time: 'Thu', val: 73 }]}>
                <XAxis dataKey="time" stroke="#475569" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#475569" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0F172A', borderColor: activeColor, borderRadius: '12px', color: '#F8FAFC', fontSize: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.4)' }} />
                <Line type="monotone" dataKey="val" stroke={activeColor} strokeWidth={3} dot={{ r: 4, fill: activeColor }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Log Form */}
        <div className="glass-panel p-6 space-y-4">
          <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Plus className="w-4 h-4" style={{ color: '#0EA5E9' }} /> Log {metricType.replace('_', ' ').toUpperCase()}
          </h3>

          {/* Quick Preset Buttons */}
          <div className="space-y-1.5">
            <span className="text-xs font-semibold flex items-center gap-1" style={{ color: '#64748B' }}>
              <Sparkles className="w-3.5 h-3.5" style={{ color: activeColor }} /> Fast 1-Click Presets:
            </span>
            <div className="flex flex-wrap gap-2">
              {metricType === 'heart_rate' && [
                { label: '❤️ 72 BPM (Resting)', v1: 72 },
                { label: '🔥 110 BPM (Post-Workout)', v1: 110 },
              ].map((p, i) => (
                <button key={i} type="button" onClick={() => handleLogVital(undefined, p.v1)} className="px-2.5 py-1 rounded-lg text-xs font-bold cursor-pointer" style={{ background: 'rgba(244,114,182,0.12)', color: '#F472B6', border: '1px solid rgba(244,114,182,0.25)' }}>
                  {p.label}
                </button>
              ))}

              {metricType === 'blood_pressure' && [
                { label: '🩺 120/80 (Normal)', v1: 120, v2: 80 },
                { label: '⚠️ 135/88 (Prehypertension)', v1: 135, v2: 88 },
              ].map((p, i) => (
                <button key={i} type="button" onClick={() => handleLogVital(undefined, p.v1, p.v2)} className="px-2.5 py-1 rounded-lg text-xs font-bold cursor-pointer" style={{ background: 'rgba(14,165,233,0.12)', color: '#38BDF8', border: '1px solid rgba(14,165,233,0.25)' }}>
                  {p.label}
                </button>
              ))}

              {metricType === 'steps' && [
                { label: '🚶 5,000 Steps', v1: 5000 },
                { label: '🏃 10,000 Steps Goal', v1: 10000 },
              ].map((p, i) => (
                <button key={i} type="button" onClick={() => handleLogVital(undefined, p.v1)} className="px-2.5 py-1 rounded-lg text-xs font-bold cursor-pointer" style={{ background: 'rgba(6,214,160,0.12)', color: '#06D6A0', border: '1px solid rgba(6,214,160,0.25)' }}>
                  {p.label}
                </button>
              ))}

              {metricType === 'sleep' && [
                { label: '🌙 7.5 Hours', v1: 7.5 },
                { label: '😴 8.0 Hours', v1: 8.0 },
              ].map((p, i) => (
                <button key={i} type="button" onClick={() => handleLogVital(undefined, p.v1)} className="px-2.5 py-1 rounded-lg text-xs font-bold cursor-pointer" style={{ background: 'rgba(139,92,246,0.12)', color: '#8B5CF6', border: '1px solid rgba(139,92,246,0.25)' }}>
                  {p.label}
                </button>
              ))}

              {metricType === 'temperature' && [
                { label: '🌡️ 98.6 °F (Normal)', v1: 98.6 },
                { label: '🔥 100.4 °F (Mild Fever)', v1: 100.4 },
              ].map((p, i) => (
                <button key={i} type="button" onClick={() => handleLogVital(undefined, p.v1)} className="px-2.5 py-1 rounded-lg text-xs font-bold cursor-pointer" style={{ background: 'rgba(245,158,11,0.12)', color: '#F59E0B', border: '1px solid rgba(245,158,11,0.25)' }}>
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleLogVital} className="space-y-4 pt-1">
            {metricType === 'blood_pressure' ? (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Systolic (mmHg)</label>
                  <input
                    type="number"
                    required
                    value={newValue}
                    onChange={(e) => setNewValue(e.target.value)}
                    placeholder="120"
                    className="w-full rounded-xl p-2.5 text-sm focus:outline-none transition-all"
                    style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(14,165,233,0.15)', color: '#F8FAFC' }}
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Diastolic (mmHg)</label>
                  <input
                    type="number"
                    required
                    value={newValue2}
                    onChange={(e) => setNewValue2(e.target.value)}
                    placeholder="80"
                    className="w-full rounded-xl p-2.5 text-sm focus:outline-none transition-all"
                    style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(14,165,233,0.15)', color: '#F8FAFC' }}
                  />
                </div>
              </div>
            ) : (
              <div>
                <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>
                  Measurement Value ({metricType === 'heart_rate' ? 'BPM' : metricType === 'steps' ? 'Steps' : metricType === 'sleep' ? 'Hours' : '°F'})
                </label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  placeholder="e.g. 72"
                  className="w-full rounded-xl p-2.5 text-sm focus:outline-none transition-all"
                  style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(14,165,233,0.15)', color: '#F8FAFC' }}
                />
              </div>
            )}

            <button
              type="submit"
              className="w-full py-2.5 rounded-xl btn-primary font-semibold text-xs cursor-pointer"
            >
              Record Metric
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

