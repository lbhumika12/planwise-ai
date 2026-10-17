import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import TaskForm from './components/TaskForm';
import Overview from './pages/Overview';
import Tasks from './pages/Tasks';
import MyDay from './pages/MyDay';
import Assistant from './pages/Assistant';
import Settings from './pages/Settings';
import { tasksApi, settingsApi, assistantApi } from './services/api';

const PAGE_TITLES = {
  '/': 'Overview',
  '/tasks': 'My Tasks',
  '/my-day': 'My Day',
  '/assistant': 'AI Assistant',
  '/settings': 'Settings',
};

function AppShell() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [theme, setTheme] = useState('light');
  const [appSettings, setAppSettings] = useState(null);
  const [aiStatus, setAiStatus] = useState(null);
  const [pageTitle, setPageTitle] = useState('Overview');
  const [showQuickAdd, setShowQuickAdd] = useState(false);
  const [saving, setSaving] = useState(false);

  // Load settings and AI status on mount
  useEffect(() => {
    settingsApi.get().then((s) => {
      setAppSettings(s);
      if (s.theme) {
        setTheme(s.theme);
        document.documentElement.setAttribute('data-theme', s.theme);
      }
    }).catch(() => {});

    assistantApi.status().then(setAiStatus).catch(() => {
      setAiStatus({ available: false, provider: null, mode: 'rule_based' });
    });
  }, []);

  // Update document title
  useEffect(() => {
    const title = PAGE_TITLES[location.pathname] || 'PlanWise AI';
    document.title = `${title} — PlanWise AI`;
  }, [location]);

  // Apply theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    const next = theme === 'light' ? 'dark' : 'light';
    setTheme(next);
    // Persist theme
    if (appSettings) {
      settingsApi.update({ theme: next }).then(setAppSettings).catch(() => {});
    }
  };

  const handleQuickAddSave = async (data) => {
    setSaving(true);
    try {
      await tasksApi.create(data);
      setShowQuickAdd(false);
    } catch (e) {
      console.error('Quick add failed:', e);
    } finally {
      setSaving(false);
    }
  };

  const handleSettingsChange = (s) => {
    setAppSettings(s);
    setTheme(s.theme || 'light');
  };

  const currentTitle = PAGE_TITLES[location.pathname] || pageTitle || 'PlanWise AI';


  return (
    <div className="app-shell">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          style={{
            position: 'fixed', inset: 0,
            background: 'rgba(0,0,0,0.4)',
            zIndex: 99,
          }}
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <div style={{ position: 'relative' }}>
        <div
          className={`app-sidebar${sidebarOpen ? ' open' : ''}`}
          style={{
            ['@media (max-width: 768px)']: {
              transform: sidebarOpen ? 'translateX(0)' : 'translateX(-100%)',
            },
          }}
        >
          <Sidebar
            onClose={() => setSidebarOpen(false)}
            aiStatus={aiStatus}
          />
        </div>
      </div>

      {/* Main area */}
      <div className="app-main">
        <Header
          title={currentTitle}
          onMenuToggle={() => setSidebarOpen((o) => !o)}
          onQuickAdd={() => setShowQuickAdd(true)}
          theme={theme}
          onThemeToggle={toggleTheme}
        />

        <main className="app-content" id="main-content" role="main">
          <Routes>
            <Route
              path="/"
              element={
                <Overview
                  settings={appSettings}
                  onHeaderChange={setPageTitle}
                />
              }
            />
            <Route
              path="/tasks"
              element={<Tasks onHeaderChange={setPageTitle} />}
            />
            <Route
              path="/my-day"
              element={
                <MyDay
                  settings={appSettings}
                  onHeaderChange={setPageTitle}
                />
              }
            />
            <Route
              path="/assistant"
              element={
                <Assistant
                  settings={appSettings}
                  aiStatus={aiStatus}
                  onHeaderChange={setPageTitle}
                />
              }
            />
            <Route
              path="/settings"
              element={
                <Settings
                  aiStatus={aiStatus}
                  onHeaderChange={setPageTitle}
                  onSettingsChange={handleSettingsChange}
                />
              }
            />
          </Routes>
        </main>
      </div>

      {/* Quick Add Modal */}
      {showQuickAdd && (
        <TaskForm
          onSave={handleQuickAddSave}
          onCancel={() => setShowQuickAdd(false)}
          loading={saving}
        />
      )}
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}
