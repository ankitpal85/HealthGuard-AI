import React from 'react';
import {
  LayoutDashboard, Bot, Pill, Activity, UtensilsCrossed,
  TrendingUp, MapPin, Users, Eye, HeartPulse, Sparkles, PhoneCall, Stethoscope
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'chatbot', label: 'AI Assistant', icon: Bot, badge: 'PRO' },
    { id: 'medications', label: 'Medications', icon: Pill },
    { id: 'vitals', label: 'Vitals & Fitness', icon: Activity },
    { id: 'nutrition', label: 'Nutrition & Diet', icon: UtensilsCrossed },
    { id: 'analytics', label: 'Risk Analytics', icon: TrendingUp, badge: 'AI' },
    { id: 'indian_health', label: 'AYUSH & Indian Health', icon: MapPin },
    { id: 'family', label: 'Family & Caregivers', icon: Users },
    { id: 'vision_voice', label: 'Vision & Voice AI', icon: Eye },
  ];



  return (
    <aside className="w-[270px] flex flex-col h-screen sticky top-0 z-30"
      style={{
        background: 'linear-gradient(180deg, #0B1222 0%, #091018 100%)',
        borderRight: '1px solid rgba(14,165,233,0.1)',
      }}
    >
      {/* Brand Logo */}
      <div className="px-6 py-7 flex items-center gap-3.5" style={{ borderBottom: '1px solid rgba(14,165,233,0.08)' }}>
        <div className="relative">
          <div className="w-11 h-11 rounded-2xl flex items-center justify-center shadow-lg"
            style={{ background: 'linear-gradient(135deg, #0EA5E9, #06B6D4)', boxShadow: '0 6px 20px rgba(14,165,233,0.3)' }}>
            <HeartPulse className="w-6 h-6 text-white" />
          </div>
          <span className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full border-2"
            style={{ background: '#06D6A0', borderColor: '#0B1222', boxShadow: '0 0 8px rgba(6,214,160,0.5)' }} />
        </div>
        <div>
          <h1 className="font-extrabold text-lg tracking-tight text-white flex items-center gap-1">
            HealthGuard <span style={{ color: '#0EA5E9' }}>AI</span>
          </h1>
          <p className="text-[10px] font-semibold tracking-wider flex items-center gap-1.5" style={{ color: '#64748B' }}>
            <Stethoscope className="w-3 h-3" style={{ color: '#06D6A0' }} />
            CLINICAL MONITORING
          </p>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 px-4 py-5 space-y-1 overflow-y-auto">
        <p className="px-3 text-[10px] font-extrabold uppercase tracking-[0.15em] mb-3 flex items-center gap-1.5"
          style={{ color: '#0EA5E9' }}>
          <Sparkles className="w-3 h-3" /> Modules
        </p>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => setActiveTab(item.id)}
              className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl font-medium text-[13px] transition-all duration-200 relative group cursor-pointer"
              style={{
                background: isActive ? 'rgba(14,165,233,0.12)' : 'transparent',
                border: isActive ? '1px solid rgba(14,165,233,0.25)' : '1px solid transparent',
                color: isActive ? '#38BDF8' : '#94A3B8',
              }}
            >
              {isActive && (
                <span className="absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-r-full"
                  style={{ background: 'linear-gradient(180deg, #0EA5E9, #06D6A0)' }} />
              )}
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 transition-transform duration-200 group-hover:scale-110"
                  style={{ color: isActive ? '#0EA5E9' : '#64748B' }} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="px-2 py-0.5 text-[9px] font-extrabold rounded-full badge-sky tracking-wider">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Emergency SOS */}
      <div className="mx-4 mb-5 p-4 rounded-xl text-center"
        style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)' }}>
        <div className="flex items-center justify-center gap-1.5 font-extrabold text-xs" style={{ color: '#EF4444' }}>
          <PhoneCall className="w-3.5 h-3.5" /> EMERGENCY SOS
        </div>
        <p className="text-[11px] font-semibold mt-1" style={{ color: '#94A3B8' }}>
          Dial <strong style={{ color: '#EF4444' }}>112</strong> for immediate medical dispatch
        </p>
      </div>
    </aside>
  );
};
