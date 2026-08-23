import React, { useState, useEffect } from 'react';
import { Search, Activity, Sun, Moon, LogOut, AlertCircle, X, ShieldAlert, Settings, Save, CheckCircle2, User as UserIcon } from 'lucide-react';
import { fetchUserProfile, updateUserProfile, fetchUserAllergies, updateUserAllergies } from '../services/api';

interface HeaderProps {
  activeTab?: string;
  currentUserId?: number;
  users?: any[];
  onSelectUser?: (id: number) => void;
  onNavigate?: (tab: string) => void;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab = 'dashboard', currentUserId = 1, users = [], onSelectUser, onNavigate, onLogout }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Settings & Profile Modal States
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [profileName, setProfileName] = useState('');
  const [profileEmail, setProfileEmail] = useState('');
  const [profileAge, setProfileAge] = useState<number>(30);
  const [profileGender, setProfileGender] = useState('Male');
  const [profileWeight, setProfileWeight] = useState<number>(70);
  const [profileHeight, setProfileHeight] = useState<number>(170);
  const [profileBloodGroup, setProfileBloodGroup] = useState('O+');
  const [profileAllergies, setProfileAllergies] = useState('None');

  const [savingSettings, setSavingSettings] = useState(false);
  const [settingsSuccess, setSettingsSuccess] = useState('');
  const [settingsError, setSettingsError] = useState('');

  useEffect(() => {
    fetchUserAllergies(currentUserId).then((res) => {
      setProfileAllergies(res);
    });

    const savedTheme = localStorage.getItem('healthguard_theme');
    if (savedTheme === 'light') {
      setIsDarkMode(false);
      document.documentElement.classList.add('light-mode');
    } else {
      setIsDarkMode(true);
      document.documentElement.classList.remove('light-mode');
    }
  }, [currentUserId]);

  const loadUserProfile = async () => {
    setSettingsSuccess('');
    setSettingsError('');
    const u = await fetchUserProfile(currentUserId);
    if (u) {
      setProfileName(u.name || '');
      setProfileEmail(u.email || '');
      setProfileAge(u.age || 30);
      setProfileGender(u.gender || 'Male');
      setProfileWeight(u.weight_kg || 70);
      setProfileHeight(u.height_cm || 170);
      setProfileBloodGroup(u.blood_group || 'O+');
      setProfileAllergies(u.allergies || 'None');
    }
  };

  const toggleTheme = () => {
    const nextMode = !isDarkMode;
    setIsDarkMode(nextMode);
    if (nextMode) {
      document.documentElement.classList.remove('light-mode');
      localStorage.setItem('healthguard_theme', 'dark');
    } else {
      document.documentElement.classList.add('light-mode');
      localStorage.setItem('healthguard_theme', 'light');
    }
  };


  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingSettings(true);
    setSettingsSuccess('');
    setSettingsError('');

    try {
      await updateUserProfile(currentUserId, {
        name: profileName,
        email: profileEmail,
        age: profileAge,
        gender: profileGender,
        weight_kg: profileWeight,
        height_cm: profileHeight,
        blood_group: profileBloodGroup,
        allergies: profileAllergies,
      });

      await updateUserAllergies(currentUserId, profileAllergies);
      setSettingsSuccess('Patient profile & clinical settings updated successfully!');

      setTimeout(() => setShowSettingsModal(false), 1200);
    } catch (err: any) {
      setSettingsError(err.message || 'Failed to save settings');
    } finally {
      setSavingSettings(false);
    }
  };

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
              width: '190px',
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

        {/* Theme Toggle Button */}
        <button
          type="button"
          onClick={toggleTheme}
          className="w-9 h-9 rounded-xl flex items-center justify-center transition-all cursor-pointer hover:border-sky-500/40"
          style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(14,165,233,0.15)', color: isDarkMode ? '#F59E0B' : '#0EA5E9' }}
          title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Patient Settings & Profile Button */}
        <button
          type="button"
          onClick={() => {
            loadUserProfile();
            setShowSettingsModal(true);
          }}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-extrabold btn-primary cursor-pointer shadow-lg hover:scale-105 transition-all"
        >
          <Settings className="w-3.5 h-3.5" />
          <span>Patient Settings</span>
        </button>

        {/* User Selector Dropdown */}
        {users.length > 0 && onSelectUser && (
          <select
            value={currentUserId}
            onChange={(e) => onSelectUser(Number(e.target.value))}
            className="px-3 py-2 rounded-xl text-xs font-bold focus:outline-none cursor-pointer"
            style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(14,165,233,0.15)', color: '#F8FAFC' }}
          >
            {users.map((u) => (
              <option key={u.id} value={u.id} style={{ background: '#0F172A', color: '#F8FAFC' }}>
                👤 {u.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Settings & Profile Modal */}
      {showSettingsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-in fade-in">
          <div className="glass-panel p-7 rounded-3xl max-w-lg w-full relative space-y-5 shadow-2xl" style={{ border: '1px solid rgba(14,165,233,0.25)' }}>
            <button
              onClick={() => setShowSettingsModal(false)}
              className="absolute right-5 top-5 p-1.5 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-white cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(14,165,233,0.15)', border: '1px solid rgba(14,165,233,0.3)', color: '#38BDF8' }}>
                <UserIcon className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-xl font-extrabold text-white">Patient Profile & Clinical Settings</h3>
                <p className="text-xs text-slate-400">View and edit personal health parameters & allergies.</p>
              </div>
            </div>

            {settingsError && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-semibold flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" /> {settingsError}
              </div>
            )}

            {settingsSuccess && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" /> {settingsSuccess}
              </div>
            )}

            <form onSubmit={handleSaveSettings} className="space-y-4 max-h-[60vh] overflow-y-auto pr-1">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    value={profileName}
                    onChange={(e) => setProfileName(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Email Address</label>
                  <input
                    type="email"
                    required
                    value={profileEmail}
                    onChange={(e) => setProfileEmail(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Age</label>
                  <input
                    type="number"
                    value={profileAge}
                    onChange={(e) => setProfileAge(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Gender</label>
                  <select
                    value={profileGender}
                    onChange={(e) => setProfileGender(e.target.value)}
                    className="w-full px-2 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Blood Group</label>
                  <select
                    value={profileBloodGroup}
                    onChange={(e) => setProfileBloodGroup(e.target.value)}
                    className="w-full px-2 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                  >
                    <option value="O+">O+</option>
                    <option value="A+">A+</option>
                    <option value="B+">B+</option>
                    <option value="AB+">AB+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Weight (kg)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={profileWeight}
                    onChange={(e) => setProfileWeight(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Height (cm)</label>
                  <input
                    type="number"
                    value={profileHeight}
                    onChange={(e) => setProfileHeight(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-medium focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1 flex items-center gap-1">
                  <ShieldAlert className="w-3.5 h-3.5 text-red-400" /> Known Allergies (e.g. Penicillin, Aspirin)
                </label>
                <input
                  type="text"
                  value={profileAllergies}
                  onChange={(e) => setProfileAllergies(e.target.value)}
                  placeholder="Penicillin, Aspirin, Sulfa"
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-medium focus:outline-none focus:border-red-500"
                />
              </div>

              <div className="pt-2 flex items-center justify-between gap-3">
                <button
                  type="submit"
                  disabled={savingSettings}
                  className="flex-1 py-3 rounded-xl btn-primary font-extrabold text-xs shadow-lg flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  <span>{savingSettings ? 'Saving...' : 'Save Profile Changes'}</span>
                </button>

                {onLogout && (
                  <button
                    type="button"
                    onClick={() => {
                      setShowSettingsModal(false);
                      onLogout();
                    }}
                    className="px-4 py-3 rounded-xl font-extrabold text-xs text-white bg-red-600 hover:bg-red-700 transition-all flex items-center gap-1.5 cursor-pointer shadow-lg"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Sign Out</span>
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      )}
    </header>
  );
};



