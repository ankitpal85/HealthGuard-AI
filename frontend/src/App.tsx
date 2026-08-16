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

import { fetchUsers } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [users, setUsers] = useState<any[]>([]);
  const [currentUserId, setCurrentUserId] = useState<number>(1);

  useEffect(() => {
    fetchUsers()
      .then((res) => {
        setUsers(res);
        if (res.length > 0) {
          setCurrentUserId(res[0].id);
        }
      })
      .catch((err) => console.error('Failed to fetch users:', err));
  }, []);

  return (
    <div className="flex min-h-screen bg-dark-900 text-slate-100 font-sans">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          activeTab={activeTab}
          currentUserId={currentUserId}
          users={users}
          onSelectUser={(id) => setCurrentUserId(id)}
          onNavigate={(tab) => setActiveTab(tab)}
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
