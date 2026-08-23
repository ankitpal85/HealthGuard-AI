import React, { useState } from 'react';
import { searchIndianMeds, searchAyurveda, searchPractoDoctors, checkAQI } from '../services/api';
import { MapPin, Search, Flower2, UserCheck, Wind } from 'lucide-react';

export const IndianHealth: React.FC = () => {
  const [activeTab, setActiveTab] = useState('meds');

  const [medQuery, setMedQuery] = useState('Dolo 650');
  const [medResult, setMedResult] = useState<string | null>(null);
  const [medLoading, setMedLoading] = useState(false);

  const [ayurQuery, setAyurQuery] = useState('Ashwagandha');
  const [ayurResult, setAyurResult] = useState<string | null>(null);
  const [ayurLoading, setAyurLoading] = useState(false);

  const [docSpecialty, setDocSpecialty] = useState('Cardiologist');
  const [docCity, setDocCity] = useState('Mumbai');
  const [docResult, setDocResult] = useState<string | null>(null);
  const [docLoading, setDocLoading] = useState(false);

  const [aqiCity, setAqiCity] = useState('Delhi');
  const [aqiResult, setAqiResult] = useState<string | null>(null);
  const [aqiLoading, setAqiLoading] = useState(false);

  const handleSearchMeds = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const queryToUse = customQuery || medQuery;
    if (!queryToUse.trim()) return;
    setMedLoading(true);
    try { const res = await searchIndianMeds(queryToUse); setMedResult(res); } catch (err) { console.error(err); } finally { setMedLoading(false); }
  };

  const handleSearchAyurveda = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const queryToUse = customQuery || ayurQuery;
    if (!queryToUse.trim()) return;
    setAyurLoading(true);
    try { const res = await searchAyurveda(queryToUse); setAyurResult(res); } catch (err) { console.error(err); } finally { setAyurLoading(false); }
  };

  const handleSearchPracto = async (e?: React.FormEvent, customCity?: string) => {
    if (e) e.preventDefault();
    const cityToUse = customCity || docCity;
    setDocLoading(true);
    try { const res = await searchPractoDoctors(docSpecialty, cityToUse); setDocResult(res); } catch (err) { console.error(err); } finally { setDocLoading(false); }
  };

  const handleCheckAQI = async (e?: React.FormEvent, customCity?: string) => {
    if (e) e.preventDefault();
    const cityToUse = customCity || aqiCity;
    setAqiLoading(true);
    try { const res = await checkAQI(cityToUse); setAqiResult(res); } catch (err) { console.error(err); } finally { setAqiLoading(false); }
  };

  const inputStyle: React.CSSProperties = {
    background: 'rgba(15,23,42,0.8)',
    border: '1px solid rgba(14,165,233,0.15)',
    color: '#F8FAFC',
    borderRadius: '12px',
    padding: '10px 14px',
    fontSize: '14px',
    width: '100%',
    outline: 'none',
  };

  const tabColors: Record<string, { color: string; bg: string; border: string }> = {
    meds: { color: '#0EA5E9', bg: 'rgba(14,165,233,0.12)', border: 'rgba(14,165,233,0.3)' },
    ayurveda: { color: '#06D6A0', bg: 'rgba(6,214,160,0.12)', border: 'rgba(6,214,160,0.3)' },
    practo: { color: '#F472B6', bg: 'rgba(244,114,182,0.12)', border: 'rgba(244,114,182,0.3)' },
    aqi: { color: '#F59E0B', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)' },
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between glass-panel p-6 rounded-2xl" style={{ border: '1px solid rgba(14,165,233,0.1)' }}>
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <MapPin className="w-6 h-6" style={{ color: '#06D6A0' }} /> Indian Healthcare & AYUSH Hub
          </h2>
          <p className="text-xs mt-1" style={{ color: '#64748B' }}>1mg Medicine Price Lookup, Practo Doctor Search, AYUSH Ayurvedic Encyclopedia & City AQI</p>
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="flex items-center gap-2 pb-2" style={{ borderBottom: '1px solid rgba(14,165,233,0.08)' }}>
        {[
          { id: 'meds', label: '1mg Medicines', icon: Search },
          { id: 'ayurveda', label: 'AYUSH Ayurveda', icon: Flower2 },
          { id: 'practo', label: 'Practo Doctors', icon: UserCheck },
          { id: 'aqi', label: 'City AQI', icon: Wind },
        ].map((t) => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          const tc = tabColors[t.id];
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer"
              style={{
                background: isActive ? tc.bg : 'transparent',
                color: isActive ? tc.color : '#94A3B8',
                border: isActive ? `1px solid ${tc.border}` : '1px solid transparent',
              }}
            >
              <Icon className="w-4 h-4" /> {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      {activeTab === 'meds' && (
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Search className="w-4 h-4" style={{ color: '#0EA5E9' }} /> 1mg Indian Medicines & Substitutes Search
          </h3>

          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            <span className="text-xs font-semibold shrink-0" style={{ color: '#64748B' }}>Popular Search:</span>
            {['Dolo 650', 'Crocin 500', 'Pantocid D', 'Azithromycin 500mg', 'Metformin 500mg'].map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => { setMedQuery(q); handleSearchMeds(undefined, q); }}
                className="px-2.5 py-1 rounded-lg text-xs font-medium cursor-pointer transition-all shrink-0"
                style={{ background: 'rgba(14,165,233,0.08)', border: '1px solid rgba(14,165,233,0.2)', color: '#38BDF8' }}
              >
                {q}
              </button>
            ))}
          </div>

          <form onSubmit={handleSearchMeds} className="flex gap-3 pt-1">
            <input type="text" value={medQuery} onChange={(e) => setMedQuery(e.target.value)} placeholder="e.g. Dolo 650, Crocin, Pantocid" style={inputStyle} className="flex-1" />
            <button type="submit" disabled={medLoading} className="btn-primary px-5 py-2.5 rounded-xl font-semibold text-xs disabled:opacity-50 cursor-pointer">
              {medLoading ? 'Searching 1mg...' : 'Search 1mg'}
            </button>
          </form>

          {medResult && (
            <div className="p-4 rounded-xl text-xs whitespace-pre-wrap leading-relaxed" style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(14,165,233,0.12)', color: '#E2E8F0' }}>
              {medResult}
            </div>
          )}
        </div>
      )}

      {activeTab === 'ayurveda' && (
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Flower2 className="w-4 h-4" style={{ color: '#06D6A0' }} /> AYUSH Ayurvedic Herbs & Remedies Directory
          </h3>

          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            <span className="text-xs font-semibold shrink-0" style={{ color: '#64748B' }}>Herbs:</span>
            {['Ashwagandha', 'Tulsi', 'Triphala', 'Brahmi', 'Giloy'].map((h, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => { setAyurQuery(h); handleSearchAyurveda(undefined, h); }}
                className="px-2.5 py-1 rounded-lg text-xs font-medium cursor-pointer transition-all shrink-0"
                style={{ background: 'rgba(6,214,160,0.08)', border: '1px solid rgba(6,214,160,0.2)', color: '#06D6A0' }}
              >
                🌿 {h}
              </button>
            ))}
          </div>

          <form onSubmit={handleSearchAyurveda} className="flex gap-3 pt-1">
            <input type="text" value={ayurQuery} onChange={(e) => setAyurQuery(e.target.value)} placeholder="e.g. Ashwagandha, Tulsi, Triphala" style={inputStyle} className="flex-1" />
            <button type="submit" disabled={ayurLoading} className="px-5 py-2.5 rounded-xl font-semibold text-xs text-white disabled:opacity-50 transition-all cursor-pointer"
              style={{ background: 'linear-gradient(135deg, #06D6A0, #14B8A6)', boxShadow: '0 4px 16px rgba(6,214,160,0.25)' }}>
              {ayurLoading ? 'Searching AYUSH...' : 'Search AYUSH'}
            </button>
          </form>

          {ayurResult && (
            <div className="p-4 rounded-xl text-xs whitespace-pre-wrap leading-relaxed" style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(6,214,160,0.12)', color: '#E2E8F0' }}>
              {ayurResult}
            </div>
          )}
        </div>
      )}

      {activeTab === 'practo' && (
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <UserCheck className="w-4 h-4" style={{ color: '#F472B6' }} /> Find Doctors on Practo
          </h3>

          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            <span className="text-xs font-semibold shrink-0" style={{ color: '#64748B' }}>Cities:</span>
            {['Mumbai', 'Delhi', 'Bengaluru', 'Hyderabad', 'Pune'].map((c, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => { setDocCity(c); handleSearchPracto(undefined, c); }}
                className="px-2.5 py-1 rounded-lg text-xs font-medium cursor-pointer transition-all shrink-0"
                style={{ background: 'rgba(244,114,182,0.08)', border: '1px solid rgba(244,114,182,0.2)', color: '#F472B6' }}
              >
                📍 {c}
              </button>
            ))}
          </div>

          <form onSubmit={handleSearchPracto} className="grid grid-cols-3 gap-3 pt-1">
            <input type="text" value={docSpecialty} onChange={(e) => setDocSpecialty(e.target.value)} placeholder="Specialty (Cardiologist)" style={inputStyle} />
            <input type="text" value={docCity} onChange={(e) => setDocCity(e.target.value)} placeholder="City (Mumbai)" style={inputStyle} />
            <button type="submit" disabled={docLoading} className="py-2.5 rounded-xl font-semibold text-xs text-white disabled:opacity-50 transition-all cursor-pointer"
              style={{ background: 'linear-gradient(135deg, #F472B6, #EC4899)', boxShadow: '0 4px 16px rgba(244,114,182,0.25)' }}>
              {docLoading ? 'Searching...' : 'Search Doctors'}
            </button>
          </form>

          {docResult && (
            <div className="p-4 rounded-xl text-xs whitespace-pre-wrap leading-relaxed" style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(244,114,182,0.12)', color: '#E2E8F0' }}>
              {docResult}
            </div>
          )}
        </div>
      )}

      {activeTab === 'aqi' && (
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Wind className="w-4 h-4" style={{ color: '#F59E0B' }} /> City Air Quality Index (AQI) & Respiratory Health
          </h3>

          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            <span className="text-xs font-semibold shrink-0" style={{ color: '#64748B' }}>Quick AQI Check:</span>
            {['Delhi', 'Mumbai', 'Bengaluru', 'Kolkata', 'Ahmedabad'].map((c, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => { setAqiCity(c); handleCheckAQI(undefined, c); }}
                className="px-2.5 py-1 rounded-lg text-xs font-medium cursor-pointer transition-all shrink-0"
                style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', color: '#F59E0B' }}
              >
                🌬️ {c}
              </button>
            ))}
          </div>

          <form onSubmit={handleCheckAQI} className="flex gap-3 pt-1">
            <input type="text" value={aqiCity} onChange={(e) => setAqiCity(e.target.value)} placeholder="City (Delhi, Mumbai, Bengaluru)" style={inputStyle} className="flex-1" />
            <button type="submit" disabled={aqiLoading} className="px-5 py-2.5 rounded-xl font-semibold text-xs text-white disabled:opacity-50 transition-all cursor-pointer"
              style={{ background: 'linear-gradient(135deg, #F59E0B, #D97706)', boxShadow: '0 4px 16px rgba(245,158,11,0.25)' }}>
              {aqiLoading ? 'Checking AQI...' : 'Check AQI'}
            </button>
          </form>

          {aqiResult && (
            <div className="p-4 rounded-xl text-xs whitespace-pre-wrap leading-relaxed" style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(245,158,11,0.12)', color: '#E2E8F0' }}>
              {aqiResult}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

