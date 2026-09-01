import { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';

import { Dashboard } from './pages/Dashboard';
import { Chatbot } from './pages/Chatbot';
import { Medications } from './pages/Medications';
import { HealthLog } from './pages/HealthLog';
import { Nutrition } from './pages/Nutrition';
import { Analytics } from './pages/Analytics';
import { IndianHealth } from './pages/IndianHealth';
import { FamilyCaregiver } from './pages/FamilyCaregiver';
import { VisionVoice } from './pages/VisionVoice';
import { AuthPage } from './pages/AuthPage';

import { fetchUsers, fetchMedications, getStoredAuthSession, logoutUser, saveAuthSession, type AuthSession } from './services/api';


function playChimeSound() {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
    osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.3); // A5
    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.5);
  } catch (e) {
    console.log('Audio Context not allowed yet');
  }
}

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [users, setUsers] = useState<any[]>([]);

  // Restore auth session from localStorage on mount
  const storedSession = getStoredAuthSession();
  const [currentUserId, setCurrentUserId] = useState<number>(storedSession?.user_id || 1);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!storedSession);
  const [authSession, setAuthSession] = useState<AuthSession | null>(storedSession);

  useEffect(() => {
    fetchUsers()
      .then((res) => {
        setUsers(res);
        if (res.length > 0 && !storedSession) {
          setCurrentUserId(res[0].id);
        }
      })
      .catch((err) => console.error('Failed to fetch users:', err));

    if ('Notification' in window && Notification.permission !== 'granted' && Notification.permission !== 'denied') {
      Notification.requestPermission();
    }
  }, []);

  // Background Pill Alarm Checker (Runs every 30s)
  useEffect(() => {
    if (!isAuthenticated) return;
    const checkPillAlarms = async () => {
      const meds = await fetchMedications(currentUserId);
      const now = new Date();
      const currentHHMM = now.toTimeString().slice(0, 5); // "HH:MM"

      meds.forEach((m) => {
        try {
          const slots: string[] = JSON.parse(m.time_slots || '[]');
          if (slots.includes(currentHHMM)) {
            playChimeSound();
            if ('Notification' in window && Notification.permission === 'granted') {
              new Notification('💊 HealthGuard Pill Alarm', {
                body: `Time to take your scheduled dose: ${m.name} (${m.dosage})`,
                icon: '/favicon.ico',
              });
            }
          }
        } catch (e) {}
      });
    };

    const interval = setInterval(checkPillAlarms, 30000);
    return () => clearInterval(interval);
  }, [currentUserId, isAuthenticated]);

  const handleLoginSuccess = (newUserId: number, userObj?: any) => {
    // Save complete auth session
    saveAuthSession({
      user_id: newUserId,
      name: userObj?.name || 'User',
      email: userObj?.email || '',
      provider: userObj?.provider || 'Local Database',
      id_token: userObj?.id_token,
      firebase_uid: userObj?.firebase_uid,
    });

    const session = getStoredAuthSession();
    setAuthSession(session);
    setCurrentUserId(newUserId);
    setIsAuthenticated(true);
    fetchUsers().then((res) => setUsers(res));
    setActiveTab('dashboard');
  };

  const handleLogout = async () => {
    // Call backend logout API + clear all local auth data
    await logoutUser();
    setIsAuthenticated(false);
    setAuthSession(null);
    setCurrentUserId(1);
    setActiveTab('dashboard');
  };

  if (!isAuthenticated) {
    return (
      <AuthPage
        users={users}
        onLoginSuccess={handleLoginSuccess}
      />
    );
  }

  return (
    <div className="flex min-h-screen font-sans transition-colors duration-300">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          activeTab={activeTab}
          currentUserId={currentUserId}
          users={users}
          authSession={authSession}
          onSelectUser={(id) => {
            setCurrentUserId(id);
            localStorage.setItem('healthguard_active_user_id', String(id));
          }}
          onNavigate={(tab) => setActiveTab(tab)}
          onLogout={handleLogout}
        />

        <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
          {activeTab === 'dashboard' && <Dashboard userId={currentUserId} setActiveTab={setActiveTab} />}
          {activeTab === 'chatbot' && <Chatbot userId={currentUserId} />}
          {activeTab === 'medications' && <Medications userId={currentUserId} />}
          {activeTab === 'vitals' && <HealthLog userId={currentUserId} />}
          {activeTab === 'nutrition' && <Nutrition userId={currentUserId} />}
          {activeTab === 'analytics' && <Analytics userId={currentUserId} />}
          {activeTab === 'indian_health' && <IndianHealth />}
          {activeTab === 'family' && <FamilyCaregiver userId={currentUserId} />}
          {activeTab === 'vision_voice' && <VisionVoice userId={currentUserId} />}
        </main>
      </div>

    </div>
  );
}

export default App;


