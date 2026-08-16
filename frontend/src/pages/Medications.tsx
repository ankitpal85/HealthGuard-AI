import React, { useEffect, useState } from 'react';
import { fetchMedications, addMedication, logMedicationTaken } from '../services/api';
import { Pill, Plus, Check, Clock, Sparkles } from 'lucide-react';

interface MedicationsProps {
  userId: number;
}

export const Medications: React.FC<MedicationsProps> = ({ userId }) => {
  const [meds, setMeds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [takenStatus, setTakenStatus] = useState<Record<string, boolean>>({});
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const [newMed, setNewMed] = useState({
    name: '',
    dosage: '1 tablet',
    frequency: 'Once daily',
    time_slots: ['08:00'],
    start_date: new Date().toISOString().split('T')[0],
    notes: 'Take after food',
  });

  const loadMeds = () => {
    setLoading(true);
    fetchMedications(userId)
      .then((res) => {
        setMeds(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadMeds();
  }, [userId]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleAddMedication = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addMedication({ ...newMed, user_id: userId });
      setShowAddModal(false);
      showToast(`✅ Added ${newMed.name} to medication schedule`);
      loadMeds();
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkTaken = async (medId: number, slot: string, medName: string) => {
    const key = `${medId}_${slot}`;
    try {
      await logMedicationTaken({
        medication_id: medId,
        user_id: userId,
        scheduled_at: `${new Date().toISOString().split('T')[0]} ${slot}`,
        taken_at: new Date().toISOString(),
        status: 'taken',
      });
      setTakenStatus((prev) => ({ ...prev, [key]: true }));
      showToast(`🎉 Logged dose: ${medName} (${slot}) as taken!`);
      loadMeds();
    } catch (err) {
      console.error(err);
    }
  };

  const toggleSlot = (slot: string) => {
    if (newMed.time_slots.includes(slot)) {
      setNewMed({ ...newMed, time_slots: newMed.time_slots.filter((s) => s !== slot) });
    } else {
      setNewMed({ ...newMed, time_slots: [...newMed.time_slots, slot] });
    }
  };

  const inputStyle = {
    background: 'rgba(15,23,42,0.8)',
    border: '1px solid rgba(14,165,233,0.15)',
    color: '#F8FAFC',
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
        <div className="fixed top-6 right-6 z-50 px-4 py-3 rounded-xl shadow-2xl font-bold text-xs flex items-center gap-2 animate-in fade-in"
          style={{ background: '#06D6A0', color: '#0F172A', boxShadow: '0 8px 24px rgba(6,214,160,0.3)' }}>
          {toastMessage}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between glass-panel p-6 rounded-2xl" style={{ border: '1px solid rgba(14,165,233,0.1)' }}>
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Pill className="w-6 h-6" style={{ color: '#0EA5E9' }} /> Medication Tracker & Reminder Engine
          </h2>
          <p className="text-xs mt-1" style={{ color: '#64748B' }}>Manage active prescriptions, daily time slots, and log dosage adherence</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary px-4 py-2.5 rounded-xl font-semibold text-xs flex items-center gap-2 cursor-pointer"
        >
          <Plus className="w-4 h-4" /> Add Medication
        </button>
      </div>

      {/* Medication Cards List */}
      {loading ? (
        <div className="text-center py-12" style={{ color: '#64748B' }}>Loading medications schedule...</div>
      ) : meds.length === 0 ? (
        <div className="glass-panel p-12 text-center" style={{ color: '#64748B' }}>
          <Pill className="w-12 h-12 mx-auto mb-3" style={{ color: '#475569' }} />
          <p className="font-semibold" style={{ color: '#94A3B8' }}>No active medications added yet.</p>
          <p className="text-xs mt-1 mb-4">Click "Add Medication" to configure your daily pill reminders.</p>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary px-4 py-2 rounded-xl text-xs font-bold cursor-pointer"
          >
            + Add First Prescription
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {meds.map((med) => {
            const slots: string[] = typeof med.time_slots === 'string' ? JSON.parse(med.time_slots || '["08:00"]') : med.time_slots;
            return (
              <div key={med.id} className="glass-panel glass-panel-hover p-5 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-white text-base">{med.name}</h3>
                    <p className="text-xs" style={{ color: '#64748B' }}>{med.dosage} • {med.frequency}</p>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-bold badge-mint">Active</span>
                </div>

                <div className="flex items-center gap-2 text-xs pt-2" style={{ borderTop: '1px solid rgba(14,165,233,0.08)', color: '#94A3B8' }}>
                  <Clock className="w-4 h-4" style={{ color: '#0EA5E9' }} />
                  <span>Slots:</span>
                  <div className="flex flex-wrap gap-2">
                    {slots.map((s: string, idx: number) => {
                      const isTaken = takenStatus[`${med.id}_${s}`];
                      return (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => handleMarkTaken(med.id, s, med.name)}
                          className="px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer"
                          style={{
                            background: isTaken ? 'rgba(6,214,160,0.2)' : 'rgba(15,23,42,0.7)',
                            border: `1px solid ${isTaken ? '#06D6A0' : 'rgba(14,165,233,0.15)'}`,
                            color: isTaken ? '#06D6A0' : '#E2E8F0',
                          }}
                        >
                          <Check className="w-3.5 h-3.5" style={{ color: isTaken ? '#06D6A0' : '#64748B' }} />
                          <span>{s}</span>
                          {isTaken && <span className="text-[10px] font-bold uppercase">(Taken)</span>}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {med.notes && (
                  <p className="text-[11px] p-2 rounded-lg italic" style={{ background: 'rgba(15,23,42,0.5)', color: '#64748B' }}>
                    Note: {med.notes}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Add Medication Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md rounded-2xl p-6 shadow-2xl" style={{ background: '#0F172A', border: '1px solid rgba(14,165,233,0.15)' }}>
            <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              <Pill className="w-5 h-5" style={{ color: '#0EA5E9' }} /> Add New Medication
            </h3>

            {/* Presets */}
            <div className="space-y-1.5 mb-4">
              <span className="text-xs font-semibold flex items-center gap-1" style={{ color: '#64748B' }}>
                <Sparkles className="w-3.5 h-3.5" style={{ color: '#0EA5E9' }} /> Preset Prescriptions:
              </span>
              <div className="flex flex-wrap gap-2">
                {[
                  { name: 'Metformin 500mg', dosage: '1 tablet', freq: 'Twice daily', slots: ['08:00', '20:00'] },
                  { name: 'Dolo 650mg', dosage: '1 tablet', freq: 'As needed', slots: ['14:00'] },
                  { name: 'Amlodipine 5mg', dosage: '1 tablet', freq: 'Once daily', slots: ['08:00'] },
                ].map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setNewMed({ ...newMed, name: preset.name, dosage: preset.dosage, frequency: preset.freq, time_slots: preset.slots })}
                    className="px-2.5 py-1 rounded-lg text-xs font-semibold cursor-pointer transition-all"
                    style={{ background: 'rgba(14,165,233,0.08)', border: '1px solid rgba(14,165,233,0.2)', color: '#38BDF8' }}
                  >
                    + {preset.name}
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleAddMedication} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Medication Name *</label>
                <input
                  type="text"
                  required
                  value={newMed.name}
                  onChange={(e) => setNewMed({ ...newMed, name: e.target.value })}
                  placeholder="e.g. Metformin 500mg"
                  style={inputStyle}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Dosage</label>
                  <input
                    type="text"
                    value={newMed.dosage}
                    onChange={(e) => setNewMed({ ...newMed, dosage: e.target.value })}
                    placeholder="e.g. 1 tablet"
                    style={inputStyle}
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Frequency</label>
                  <select
                    value={newMed.frequency}
                    onChange={(e) => setNewMed({ ...newMed, frequency: e.target.value })}
                    style={inputStyle}
                  >
                    <option>Once daily</option>
                    <option>Twice daily</option>
                    <option>Three times daily</option>
                    <option>As needed</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold mb-1.5" style={{ color: '#94A3B8' }}>Daily Time Slots</label>
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { label: 'Morning', time: '08:00' },
                    { label: 'Noon', time: '14:00' },
                    { label: 'Evening', time: '20:00' },
                    { label: 'Night', time: '22:00' },
                  ].map((ts, idx) => {
                    const isSelected = newMed.time_slots.includes(ts.time);
                    return (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => toggleSlot(ts.time)}
                        className="py-2 rounded-xl text-xs font-bold transition-all cursor-pointer"
                        style={{
                          background: isSelected ? 'rgba(14,165,233,0.25)' : 'rgba(15,23,42,0.8)',
                          border: `1px solid ${isSelected ? '#0EA5E9' : 'rgba(14,165,233,0.15)'}`,
                          color: isSelected ? '#38BDF8' : '#94A3B8',
                        }}
                      >
                        {ts.label}<br /><span className="text-[10px] font-normal">{ts.time}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Notes / Instructions</label>
                <input
                  type="text"
                  value={newMed.notes}
                  onChange={(e) => setNewMed({ ...newMed, notes: e.target.value })}
                  placeholder="Take after food"
                  style={inputStyle}
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2.5 rounded-xl font-semibold text-xs transition-all cursor-pointer"
                  style={{ border: '1px solid rgba(14,165,233,0.15)', color: '#94A3B8' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 rounded-xl btn-primary font-semibold text-xs cursor-pointer"
                >
                  Save Medication
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

