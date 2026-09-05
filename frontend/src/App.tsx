import { useEffect, useState } from 'react';

import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { HealthInsightsPanel } from './components/HealthInsightsPanel';

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

import {
  fetchUsers,
  fetchMedications,
  getStoredAuthSession,
  logoutUser,
  saveAuthSession,
  type AuthSession,
} from './services/api';


function playChimeSound() {
  try {
    const AudioContextClass =
      window.AudioContext ||
      (window as typeof window & {
        webkitAudioContext?: typeof AudioContext;
      }).webkitAudioContext;

    if (!AudioContextClass) {
      return;
    }

    const ctx = new AudioContextClass();

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';

    osc.frequency.setValueAtTime(
      587.33,
      ctx.currentTime
    );

    osc.frequency.exponentialRampToValueAtTime(
      880,
      ctx.currentTime + 0.3
    );

    gain.gain.setValueAtTime(
      0.15,
      ctx.currentTime
    );

    gain.gain.exponentialRampToValueAtTime(
      0.01,
      ctx.currentTime + 0.5
    );

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.5);
  } catch (e) {
    console.log(
      'Audio Context not allowed yet'
    );
  }
}


export function App() {

  // ─────────────────────────────────────────────
  // Application State
  // ─────────────────────────────────────────────

  const [activeTab, setActiveTab] =
    useState('dashboard');

  const [users, setUsers] =
    useState<any[]>([]);


  // ─────────────────────────────────────────────
  // Authentication
  // ─────────────────────────────────────────────

  const storedSession =
    getStoredAuthSession();

  const [currentUserId, setCurrentUserId] =
    useState<number>(
      storedSession?.user_id || 1
    );

  const [isAuthenticated, setIsAuthenticated] =
    useState<boolean>(
      !!storedSession
    );

  const [authSession, setAuthSession] =
    useState<AuthSession | null>(
      storedSession
    );


  // ─────────────────────────────────────────────
  // Load Users
  // ─────────────────────────────────────────────

  useEffect(() => {

    fetchUsers()
      .then((res) => {

        setUsers(res);

        if (
          res.length > 0 &&
          !storedSession
        ) {
          setCurrentUserId(
            res[0].id
          );
        }

      })
      .catch((err) => {

        console.error(
          'Failed to fetch users:',
          err
        );

      });


    // Request notification permission
    if (
      'Notification' in window &&
      Notification.permission !== 'granted' &&
      Notification.permission !== 'denied'
    ) {

      Notification.requestPermission();

    }

  }, []);


  // ─────────────────────────────────────────────
  // Background Medication Alarm
  // Runs every 30 seconds
  // ─────────────────────────────────────────────

  useEffect(() => {

    if (!isAuthenticated) {
      return;
    }


    const checkPillAlarms =
      async () => {

        try {

          const meds =
            await fetchMedications(
              currentUserId
            );

          const now =
            new Date();

          const currentHHMM =
            now
              .toTimeString()
              .slice(0, 5);


          meds.forEach((m) => {

            try {

              const slots: string[] =
                JSON.parse(
                  m.time_slots || '[]'
                );


              if (
                slots.includes(
                  currentHHMM
                )
              ) {

                playChimeSound();


                if (
                  'Notification' in window &&
                  Notification.permission ===
                    'granted'
                ) {

                  new Notification(
                    '💊 HealthGuard Pill Alarm',
                    {
                      body:
                        `Time to take your scheduled dose: ${m.name} (${m.dosage})`,
                      icon:
                        '/favicon.ico',
                    }
                  );

                }

              }

            } catch (e) {

              console.error(
                'Failed to process medication alarm:',
                e
              );

            }

          });

        } catch (err) {

          console.error(
            'Failed to check medication alarms:',
            err
          );

        }

      };


    // Check immediately
    checkPillAlarms();


    // Then every 30 seconds
    const interval =
      setInterval(
        checkPillAlarms,
        30000
      );


    return () =>
      clearInterval(interval);

  }, [
    currentUserId,
    isAuthenticated,
  ]);


  // ─────────────────────────────────────────────
  // Login Success
  // ─────────────────────────────────────────────

  const handleLoginSuccess = (
    newUserId: number,
    userObj?: any
  ) => {

    saveAuthSession({

      user_id: newUserId,

      name:
        userObj?.name ||
        'User',

      email:
        userObj?.email ||
        '',

      provider:
        userObj?.provider ||
        'Local Database',

      id_token:
        userObj?.id_token,

      firebase_uid:
        userObj?.firebase_uid,

    });


    const session =
      getStoredAuthSession();


    setAuthSession(
      session
    );


    setCurrentUserId(
      newUserId
    );


    setIsAuthenticated(
      true
    );


    fetchUsers()
      .then((res) => {

        setUsers(res);

      })
      .catch((err) => {

        console.error(
          'Failed to refresh users:',
          err
        );

      });


    setActiveTab(
      'dashboard'
    );

  };


  // ─────────────────────────────────────────────
  // Logout
  // ─────────────────────────────────────────────

  const handleLogout =
    async () => {

      try {

        await logoutUser();

      } catch (err) {

        console.error(
          'Logout API failed:',
          err
        );

      }


      setIsAuthenticated(
        false
      );

      setAuthSession(
        null
      );

      setCurrentUserId(
        1
      );

      setActiveTab(
        'dashboard'
      );

    };


  // ─────────────────────────────────────────────
  // Authentication Page
  // ─────────────────────────────────────────────

  if (!isAuthenticated) {

    return (
      <AuthPage
        users={users}
        onLoginSuccess={
          handleLoginSuccess
        }
      />
    );

  }


  // ─────────────────────────────────────────────
  // Main Application
  // ─────────────────────────────────────────────

  return (

    <div className="flex min-h-screen font-sans transition-colors duration-300">

      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />


      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">


        {/* Header */}
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


        {/* Page Content */}
        <main className="flex-1 p-8 max-w-7xl w-full mx-auto">


          {/* ─────────────────────────────
              DASHBOARD
          ───────────────────────────── */}

          {activeTab === 'dashboard' && (

            <>

              {/* Existing Dashboard */}
              <Dashboard
                userId={currentUserId}
                setActiveTab={
                  setActiveTab
                }
              />


              {/* NEW SMART HEALTH SNAPSHOT */}
              <HealthInsightsPanel
                userId={
                  currentUserId
                }
              />

            </>

          )}


          {/* ─────────────────────────────
              AI CHATBOT
          ───────────────────────────── */}

          {activeTab === 'chatbot' && (

            <Chatbot
              userId={
                currentUserId
              }
            />

          )}


          {/* ─────────────────────────────
              MEDICATIONS
          ───────────────────────────── */}

          {activeTab === 'medications' && (

            <Medications
              userId={
                currentUserId
              }
            />

          )}


          {/* ─────────────────────────────
              VITALS / HEALTH LOG
          ───────────────────────────── */}

          {activeTab === 'vitals' && (

            <HealthLog
              userId={
                currentUserId
              }
            />

          )}


          {/* ─────────────────────────────
              NUTRITION
          ───────────────────────────── */}

          {activeTab === 'nutrition' && (

            <Nutrition
              userId={
                currentUserId
              }
            />

          )}


          {/* ─────────────────────────────
              ANALYTICS
          ───────────────────────────── */}

          {activeTab === 'analytics' && (

            <Analytics
              userId={
                currentUserId
              }
            />

          )}


          {/* ─────────────────────────────
              INDIAN HEALTH
          ───────────────────────────── */}

          {activeTab === 'indian_health' && (

            <IndianHealth />

          )}


          {/* ─────────────────────────────
              FAMILY CAREGIVER
          ───────────────────────────── */}

          {activeTab === 'family' && (

            <FamilyCaregiver
              userId={
                currentUserId
              }
            />

          )}


          {/* ─────────────────────────────
              VISION + VOICE AI
          ───────────────────────────── */}

          {activeTab === 'vision_voice' && (

            <VisionVoice
              userId={
                currentUserId
              }
            />

          )}

        </main>

      </div>

    </div>

  );
}


export default App;