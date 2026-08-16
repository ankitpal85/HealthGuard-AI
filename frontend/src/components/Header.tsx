import React, { useState } from 'react';
import { Search, Shield, Activity } from 'lucide-react';

interface HeaderProps {
  activeTab?: string;
  currentUserId?: number;
  users?: any[];
  onSelectUser?: (id: number) => void;
  onNavigate?: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab = 'dashboard', currentUserId, users = [], onSelectUser, onNavigate }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  const modules = [
    { id: 'dashboard', label: 'Clinical Dashboard', category: 'Overview' },
    { id: 'chatbot', label: 'AI Medical Assistant', category: 'AI Tools' },
    { id: 'medications', label: 'Medication Tracker', category: 'Clinical' },
    { id: 'vitals', label: 'Vitals & Fitness Log', category: 'Biometrics' },
    { id: 'nutrition', label: 'Nutrition & Diet', category: 'Diet' },
    { id: 'analytics', label: 'Risk Analytics & Symptom Checker', category: 'AI Tools' },
    { id: 'indian_health', label: '1mg & AYUSH Indian Health', category: 'Integrations' },
    { id: 'family', label: 'Family Profiles & Caregiver SOS', category: 'Family' },
    { id: 'vision_voice', label: 'Vision OCR & Voice AI', category: 'AI Tools' },
  ];

  const filteredModules = searchQuery.trim()
    ? modules.filter((m) => m.label.toLowerCase().includes(searchQuery.toLowerCase()) || m.category.toLowerCase().includes(searchQuery.toLowerCase()))
    : [];

  const titles: Record<string, { label: string; subtitle: string }> = {
    dashboard: { label: 'Clinical Dashboard', subtitle: 'Patient vitals & health metrics overview' },
    chatbot: { label: 'AI Medical Assistant', subtitle: 'Intelligent clinical dialogue engine' },
    medications: { label: 'Medication Tracker', subtitle: 'Active prescriptions & schedule' },
    vitals: { label: 'Vitals & Fitness Log', subtitle: 'Real-time biometric monitoring' },
    nutrition: { label: 'Nutrition & Diet', subtitle: 'Dietary analysis & recommendations' },
    analytics: { label: 'Risk Analytics', subtitle: 'AI-powered health risk assessments' },
    indian_health: { label: 'AYUSH & Indian Health', subtitle: 'Ayurveda, Yoga, Naturopathy resources' },
    family: { label: 'Family & Caregivers', subtitle: 'Dependent profiles & access management' },
    vision_voice: { label: 'Vision & Voice AI', subtitle: 'Image analysis & voice interface' },
  };

  const { label, subtitle } = titles[activeTab] || titles.dashboard;
  const currentUser = users.find((u) => u.id === currentUserId) || { name: 'Dr. Ankit' };

  return (
    <header className="flex items-center justify-between px-8 py-5 relative" style={{ borderBottom: '1px solid rgba(14,165,233,0.08)' }}>
      <div>
        <h2 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2.5" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
          <span className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: 'rgba(14,165,233,0.12)', border: '1px solid rgba(14,165,233,0.2)' }}>
            <Activity className="w-4 h-4" style={{ color: '#0EA5E9' }} />
          </span>
          {label}
        </h2>
        <p className="text-xs font-medium mt-1 ml-[42px]" style={{ color: '#64748B' }}>{subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 z-10" style={{ color: '#64748B' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search modules..."
            className="pl-10 pr-4 py-2 rounded-xl text-[13px] font-medium focus:outline-none transition-all duration-200"
            style={{
              width: '220px',
              background: 'rgba(15,23,42,0.6)',
              border: '1px solid rgba(14,165,233,0.15)',
              color: '#F8FAFC',
            }}
            onFocus={(e) => {
              setIsSearchFocused(true);
              e.target.style.borderColor = 'rgba(14,165,233,0.4)';
              e.target.style.boxShadow = '0 0 16px rgba(14,165,233,0.1)';
            }}
            onBlur={() => {
              setTimeout(() => setIsSearchFocused(false), 200);
            }}
          />

          {/* Search Dropdown */}
          {isSearchFocused && filteredModules.length > 0 && (
            <div className="absolute top-12 left-0 right-0 z-50 rounded-xl p-2 shadow-2xl space-y-1 animate-in fade-in"
              style={{ background: '#0F172A', border: '1px solid rgba(14,165,233,0.2)' }}>
              {filteredModules.map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onMouseDown={() => {
                    if (onNavigate) onNavigate(m.id);
                    setSearchQuery('');
                    setIsSearchFocused(false);
                  }}
                  className="w-full text-left px-3 py-2 rounded-lg text-xs font-semibold hover:bg-sky-500/10 flex items-center justify-between cursor-pointer"
                  style={{ color: '#E2E8F0' }}
                >
                  <span>{m.label}</span>
                  <span className="text-[10px] uppercase font-bold text-sky-400">{m.category}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* AI Status Badge */}
        <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl"
          style={{ background: 'rgba(6,214,160,0.08)', border: '1px solid rgba(6,214,160,0.15)' }}>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-60" style={{ background: '#06D6A0' }} />
            <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: '#06D6A0' }} />
          </span>
          <span className="text-[11px] font-bold" style={{ color: '#06D6A0' }}>AI ENGINE ONLINE</span>
        </div>

        {/* User Selector Dropdown / Profile Badge */}
        {users.length > 0 && onSelectUser ? (
          <select
            value={currentUserId}
            onChange={(e) => onSelectUser(Number(e.target.value))}
            className="px-3 py-2 rounded-xl text-xs font-bold focus:outline-none cursor-pointer"
            style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(14,165,233,0.15)', color: '#F8FAFC' }}
          >
            {users.map((u) => (
              <option key={u.id} value={u.id} style={{ background: '#0F172A', color: '#F8FAFC' }}>
                👤 {u.name} ({u.role || 'Patient'})
              </option>
            ))}
          </select>
        ) : (
          <button className="flex items-center gap-2.5 px-3 py-2 rounded-xl group transition-all duration-200"
            style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(14,165,233,0.1)' }}>
            <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
              style={{ background: 'linear-gradient(135deg, #0EA5E9, #06D6A0)' }}>
              Dr
            </div>
            <div className="text-left">
              <p className="text-[12px] font-bold text-white leading-none">{currentUser.name}</p>
              <p className="text-[10px] font-semibold flex items-center gap-1" style={{ color: '#0EA5E9' }}>
                <Shield className="w-2.5 h-2.5" /> Verified Clinician
              </p>
            </div>
          </button>
        )}
      </div>
    </header>
  );
};

