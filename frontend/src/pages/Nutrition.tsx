import React, { useEffect, useState } from 'react';
import { fetchNutritionLogs, logNutrition, deleteNutritionLog } from '../services/api';
import { UtensilsCrossed, Plus, Droplet, Flame, Sparkles, Trash2 } from 'lucide-react';

interface NutritionProps {
  userId: number;
}

export const Nutrition: React.FC<NutritionProps> = ({ userId }) => {
  const [logs, setLogs] = useState<any[]>([]);
  const [showLogModal, setShowLogModal] = useState(false);
  const [waterTotal, setWaterTotal] = useState(2250);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const [form, setForm] = useState({
    meal_type: 'Breakfast',
    food_items: '',
    calories: '',
    protein_g: '',
    carbs_g: '',
    fats_g: '',
    water_ml: '250',
  });

  const loadNutrition = () => {
    fetchNutritionLogs(userId)
      .then((res) => {
        setLogs(res.logs || []);
      })
      .catch((err) => {
        console.error(err);
      });
  };

  useEffect(() => {
    loadNutrition();
  }, [userId]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleDeleteNutrition = async (logId: number, foodName: string) => {
    try {
      await deleteNutritionLog(logId, userId);
      showToast(`🗑️ Removed meal: ${foodName}`);
      loadNutrition();
    } catch (err) {
      console.error(err);
    }
  };

  const handleQuickWater = async (amountMl: number) => {
    try {
      await logNutrition({
        user_id: userId,
        meal_type: 'Water Intake',
        food_items: `Hydration (${amountMl}ml)`,
        calories: 0,
        protein_g: 0,
        carbs_g: 0,
        fats_g: 0,
        water_ml: amountMl,
      });
      setWaterTotal((prev) => prev + amountMl);
      showToast(`💧 Added +${amountMl}ml water intake!`);
      loadNutrition();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await logNutrition({
        user_id: userId,
        meal_type: form.meal_type,
        food_items: form.food_items,
        calories: parseFloat(form.calories) || 350,
        protein_g: parseFloat(form.protein_g) || 0,
        carbs_g: parseFloat(form.carbs_g) || 0,
        fats_g: parseFloat(form.fats_g) || 0,
        water_ml: parseFloat(form.water_ml) || 0,
      });
      setShowLogModal(false);
      showToast(`🥗 Logged ${form.meal_type}: ${form.food_items}`);
      loadNutrition();
    } catch (err) {
      console.error(err);
    }
  };

  const inputStyle = {
    background: 'var(--bg-card)',
    border: '1px solid var(--border-color)',
    borderRadius: '12px',
    padding: '10px 14px',
    fontSize: '14px',
    width: '100%',
    outline: 'none',
  };

  return (
    <div className="space-y-6 relative">
      {/* Toast Notification */}
      {toastMessage && (
        <div
          className="fixed top-6 right-6 z-50 px-4 py-3 rounded-xl shadow-2xl font-bold text-xs flex items-center gap-2 animate-in fade-in"
          style={{ background: '#F59E0B', color: '#0F172A', boxShadow: '0 8px 24px rgba(245,158,11,0.3)' }}
        >
          {toastMessage}
        </div>
      )}

      <div className="flex items-center justify-between glass-panel p-6 rounded-2xl" style={{ border: '1px solid var(--border-color)' }}>
        <div>
          <h2 className="text-xl font-extrabold flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <UtensilsCrossed className="w-6 h-6 text-amber-500" /> Nutrition & Diet Intelligence
          </h2>
          <p className="text-xs font-semibold mt-1" style={{ color: '#64748B' }}>Track daily meals, calories, macro breakdowns, and hydration goals</p>
        </div>
        <button
          onClick={() => setShowLogModal(true)}
          className="btn-primary px-4 py-2.5 rounded-xl font-extrabold text-xs flex items-center gap-2 cursor-pointer hover:scale-105 shadow-md"
        >
          <Plus className="w-4 h-4" /> Log Meal / Water
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel glass-panel-hover p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(245,158,11,0.12)', border: '1px solid rgba(245,158,11,0.25)' }}>
            <Flame className="w-6 h-6 text-amber-500" />
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-wider" style={{ color: '#64748B' }}>Daily Calories</p>
            <h3 className="text-2xl font-extrabold" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>1,850 <span className="text-xs font-normal" style={{ color: '#64748B' }}>/ 2,200 kcal</span></h3>
          </div>
        </div>

        <div className="glass-panel glass-panel-hover p-5 flex flex-col justify-between space-y-3">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0" style={{ background: 'rgba(14,165,233,0.12)', border: '1px solid rgba(14,165,233,0.25)' }}>
              <Droplet className="w-6 h-6 text-sky-500" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider" style={{ color: '#64748B' }}>Water Intake</p>
              <h3 className="text-2xl font-extrabold" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>{waterTotal} <span className="text-xs font-normal" style={{ color: '#64748B' }}>/ 3,000 ml</span></h3>
            </div>
          </div>
          <div className="flex items-center gap-2 pt-1">
            <button onClick={() => handleQuickWater(250)} className="px-2.5 py-1 rounded-lg text-xs font-extrabold transition-all cursor-pointer badge-sky">+250ml Glass</button>
            <button onClick={() => handleQuickWater(500)} className="px-2.5 py-1 rounded-lg text-xs font-extrabold transition-all cursor-pointer badge-sky">+500ml Bottle</button>
          </div>
        </div>

        <div className="glass-panel glass-panel-hover p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(6,214,160,0.12)', border: '1px solid rgba(6,214,160,0.25)' }}>
            <UtensilsCrossed className="w-6 h-6 text-emerald-500" />
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-wider" style={{ color: '#64748B' }}>Macro Split</p>
            <h3 className="text-sm font-extrabold">P: 65g • C: 210g • F: 45g</h3>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h3 className="font-extrabold text-sm" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>Logged Meals History</h3>
        {logs.length === 0 ? (
          <p className="text-xs italic font-medium" style={{ color: '#64748B' }}>No meals logged for today.</p>
        ) : (
          <div className="space-y-2">
            {logs.map((l: any, i: number) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 rounded-xl text-xs font-medium"
                style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)' }}
              >
                <div>
                  <span className="font-bold text-sky-500">{l.meal_type}:</span>{' '}
                  <span className="font-semibold">{l.food_items}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-bold" style={{ color: '#64748B' }}>
                    {l.calories} kcal
                  </span>
                  <button
                    onClick={() => handleDeleteNutrition(l.id || i, l.food_items)}
                    className="p-1.5 rounded-xl transition-all cursor-pointer text-red-500 hover:bg-red-500/15"
                    title="Delete Meal Log"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {showLogModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md glass-panel p-6 shadow-2xl" style={{ border: '1px solid var(--border-color)' }}>
            <h3 className="text-lg font-bold mb-3" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>Log Meal / Nutrition</h3>

            {/* Presets */}
            <div className="space-y-1.5 mb-3">
              <span className="text-xs font-semibold flex items-center gap-1" style={{ color: '#64748B' }}>
                <Sparkles className="w-3.5 h-3.5" style={{ color: '#F59E0B' }} /> Quick Meal Presets:
              </span>
              <div className="flex flex-wrap gap-2">
                {[
                  { type: 'Breakfast', food: 'Oats with Almond Milk & Banana', cal: '320' },
                  { type: 'Lunch', food: 'Dal Tadka, Roti & Brown Rice', cal: '480' },
                  { type: 'Dinner', food: 'Grilled Paneer & Mixed Salad', cal: '380' },
                ].map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setForm({ ...form, meal_type: preset.type, food_items: preset.food, calories: preset.cal })}
                    className="px-2.5 py-1 rounded-lg text-xs font-semibold cursor-pointer transition-all"
                    style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', color: '#F59E0B' }}
                  >
                    + {preset.food.split(' ')[0]} {preset.type}
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Meal Type</label>
                <select value={form.meal_type} onChange={(e) => setForm({ ...form, meal_type: e.target.value })} style={inputStyle}>
                  <option>Breakfast</option>
                  <option>Lunch</option>
                  <option>Dinner</option>
                  <option>Snack</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Food Items *</label>
                <input type="text" required value={form.food_items} onChange={(e) => setForm({ ...form, food_items: e.target.value })} placeholder="e.g. Oats with Almond Milk & Banana" style={inputStyle} />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Calories (kcal)</label>
                  <input type="number" value={form.calories} onChange={(e) => setForm({ ...form, calories: e.target.value })} placeholder="350" style={inputStyle} />
                </div>
                <div>
                  <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Water (ml)</label>
                  <input type="number" value={form.water_ml} onChange={(e) => setForm({ ...form, water_ml: e.target.value })} placeholder="250" style={inputStyle} />
                </div>
              </div>

              <div className="flex gap-3 pt-3">
                <button type="button" onClick={() => setShowLogModal(false)} className="flex-1 py-2 rounded-xl text-xs font-semibold cursor-pointer transition-all" style={{ border: '1px solid rgba(14,165,233,0.15)', color: '#94A3B8' }}>
                  Cancel
                </button>
                <button type="submit" className="flex-1 py-2 rounded-xl btn-primary font-semibold text-xs cursor-pointer">
                  Save Meal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

