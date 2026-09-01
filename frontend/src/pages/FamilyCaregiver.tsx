import React, { useEffect, useState } from 'react';
import { fetchFamilyMembers, addFamilyMember, fetchCaregivers, addCaregiver } from '../services/api';
import { Users, UserPlus, Shield, HeartHandshake, PhoneCall, BellRing } from 'lucide-react';

interface FamilyCaregiverProps {
  userId: number;
}

export const FamilyCaregiver: React.FC<FamilyCaregiverProps> = ({ userId }) => {
  const [family, setFamily] = useState<any[]>([]);
  const [caregivers, setCaregivers] = useState<any[]>([]);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const [showAddFamily, setShowAddFamily] = useState(false);
  const [showAddCaregiver, setShowAddCaregiver] = useState(false);

  const [familyForm, setFamilyForm] = useState({ name: '', relationship: 'Parent', age: '50', blood_group: 'B+' });
  const [caregiverForm, setCaregiverForm] = useState({ name: '', relationship: 'Doctor / Caregiver', phone: '+91 9876543210', email: '' });

  const loadData = () => {
    Promise.all([fetchFamilyMembers(userId), fetchCaregivers(userId)])
      .then(([fRes, cRes]) => {
        setFamily(fRes);
        setCaregivers(cRes);
      })
      .catch((err) => {
        console.error(err);
      });
  };

  useEffect(() => {
    loadData();
  }, [userId]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleAddFamily = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addFamilyMember({ ...familyForm, user_id: userId, age: parseInt(familyForm.age) });
      setShowAddFamily(false);
      showToast(`👤 Added ${familyForm.name} to family network`);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddCaregiver = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addCaregiver({ ...caregiverForm, user_id: userId });
      setShowAddCaregiver(false);
      showToast(`🤝 Added caregiver ${caregiverForm.name} to emergency dispatch`);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleTestEmergencyAlert = (caregiverName: string, phone: string) => {
    showToast(`🚨 ALERT SENT! Simulated Emergency SMS/Email sent to ${caregiverName} (${phone})`);
  };

  const inputStyle: React.CSSProperties = {
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
          style={{ background: '#EF4444', color: '#FFFFFF', boxShadow: '0 8px 24px rgba(239,68,68,0.3)' }}
        >
          {toastMessage}
        </div>
      )}

      <div className="flex items-center justify-between glass-panel p-6 rounded-2xl" style={{ border: '1px solid var(--border-color)' }}>
        <div>
          <h2 className="text-xl font-extrabold flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Users className="w-6 h-6 text-sky-500" /> Family Profiles & Caregiver Network
          </h2>
          <p className="text-xs font-semibold mt-1" style={{ color: '#64748B' }}>Manage family health profiles, emergency contacts, and ABHA Insurance locker</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Family Members Panel */}
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-extrabold text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              <Users className="w-4 h-4 text-sky-500" /> Family Members ({family.length})
            </h3>
            <button
              onClick={() => setShowAddFamily(true)}
              className="btn-primary px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1 cursor-pointer hover:scale-105 shadow-md"
            >
              <UserPlus className="w-3.5 h-3.5" /> Add Member
            </button>
          </div>

          {family.length === 0 ? (
            <p className="text-xs italic font-medium" style={{ color: '#64748B' }}>No family members added yet.</p>
          ) : (
            <div className="space-y-2">
              {family.map((f: any, i: number) => (
                <div
                  key={i}
                  className="p-3 rounded-xl flex items-center justify-between text-xs font-medium"
                  style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)' }}
                >
                  <div>
                    <h4 className="font-bold">{f.name}</h4>
                    <p style={{ color: '#64748B' }}>{f.relationship} • Age {f.age || 'N/A'}</p>
                  </div>
                  <span className="px-2 py-0.5 rounded font-extrabold badge-sky">{f.blood_group || 'Unknown'}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Caregiver Emergency Contacts */}
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-extrabold text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              <HeartHandshake className="w-4 h-4 text-emerald-500" /> Emergency Caregivers
            </h3>
            <button
              onClick={() => setShowAddCaregiver(true)}
              className="px-3 py-1.5 rounded-xl text-white text-xs font-extrabold flex items-center gap-1 transition-all cursor-pointer shadow-md hover:scale-105"
              style={{ background: 'linear-gradient(135deg, #06D6A0, #14B8A6)', boxShadow: '0 4px 12px rgba(6,214,160,0.25)' }}
            >
              <PhoneCall className="w-3.5 h-3.5" /> Add Contact
            </button>
          </div>

          {caregivers.length === 0 ? (
            <p className="text-xs italic font-medium" style={{ color: '#64748B' }}>No emergency contacts added yet.</p>
          ) : (
            <div className="space-y-2">
              {caregivers.map((c: any, i: number) => (
                <div
                  key={i}
                  className="p-3 rounded-xl flex items-center justify-between text-xs font-medium"
                  style={{ background: 'var(--bg-card)', border: '1px solid rgba(6,214,160,0.2)' }}
                >
                  <div>
                    <h4 className="font-bold">{c.name}</h4>
                    <p style={{ color: '#64748B' }}>{c.relationship} • {c.phone}</p>
                  </div>
                  <button
                    onClick={() => handleTestEmergencyAlert(c.name, c.phone)}
                    className="px-2.5 py-1 rounded-lg text-[10px] font-extrabold flex items-center gap-1 transition-all cursor-pointer hover:scale-105"
                    style={{ background: 'rgba(239,68,68,0.12)', color: '#EF4444', border: '1px solid rgba(239,68,68,0.25)' }}
                  >
                    <BellRing className="w-3 h-3 animate-pulse" /> Test Alert
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ABHA Insurance Locker Box */}
      <div
        className="glass-panel p-6 rounded-2xl flex items-center justify-between shadow-lg"
        style={{ border: '1px solid rgba(139,92,246,0.25)', background: 'linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(14,165,233,0.05) 100%)' }}
      >
        <div>
          <h3 className="font-extrabold text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Shield className="w-5 h-5 text-purple-500" /> ABHA Health Locker & Ayushman Bharat Insurance
          </h3>
          <p className="text-xs font-semibold mt-1" style={{ color: '#64748B' }}>Policy Number: ABHA-9821-4412-3301 • Coverage Amount: ₹5,00,000</p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-extrabold badge-mint">Active Locker</span>
      </div>

      {/* Modals */}
      {showAddFamily && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md glass-panel p-6 shadow-2xl" style={{ border: '1px solid var(--border-color)' }}>
            <h3 className="text-lg font-bold mb-4" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>Add Family Member</h3>
            <form onSubmit={handleAddFamily} className="space-y-3">
              <input type="text" required placeholder="Full Name" value={familyForm.name} onChange={(e) => setFamilyForm({ ...familyForm, name: e.target.value })} style={inputStyle} className="font-medium" />
              <div className="grid grid-cols-2 gap-3">
                <input type="text" placeholder="Relationship (e.g. Spouse)" value={familyForm.relationship} onChange={(e) => setFamilyForm({ ...familyForm, relationship: e.target.value })} style={inputStyle} className="font-medium" />
                <input type="number" placeholder="Age" value={familyForm.age} onChange={(e) => setFamilyForm({ ...familyForm, age: e.target.value })} style={inputStyle} className="font-medium" />
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowAddFamily(false)} className="flex-1 py-2 rounded-xl text-xs font-bold cursor-pointer card-action-btn">Cancel</button>
                <button type="submit" className="flex-1 py-2 rounded-xl btn-primary font-bold text-xs cursor-pointer shadow-md">Save Member</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showAddCaregiver && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md glass-panel p-6 shadow-2xl" style={{ border: '1px solid rgba(6,214,160,0.3)' }}>
            <h3 className="text-lg font-bold mb-4" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>Add Caregiver Contact</h3>
            <form onSubmit={handleAddCaregiver} className="space-y-3">
              <input type="text" required placeholder="Caregiver Name" value={caregiverForm.name} onChange={(e) => setCaregiverForm({ ...caregiverForm, name: e.target.value })} style={inputStyle} className="font-medium" />
              <div className="grid grid-cols-2 gap-3">
                <input type="text" placeholder="Relationship" value={caregiverForm.relationship} onChange={(e) => setCaregiverForm({ ...caregiverForm, relationship: e.target.value })} style={inputStyle} className="font-medium" />
                <input type="text" placeholder="Phone" value={caregiverForm.phone} onChange={(e) => setCaregiverForm({ ...caregiverForm, phone: e.target.value })} style={inputStyle} className="font-medium" />
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowAddCaregiver(false)} className="flex-1 py-2 rounded-xl text-xs font-bold cursor-pointer card-action-btn">Cancel</button>
                <button type="submit" className="flex-1 py-2 rounded-xl font-bold text-xs text-white cursor-pointer shadow-md" style={{ background: 'linear-gradient(135deg, #06D6A0, #14B8A6)' }}>Save Contact</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

