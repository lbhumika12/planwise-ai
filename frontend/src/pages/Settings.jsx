import { useState, useEffect } from 'react';
import { Save, Trash2, AlertCircle, Check, Bot, Database } from 'lucide-react';
import { settingsApi, tasksApi } from '../services/api';
import ConfirmDialog from '../components/ConfirmDialog';
import { PageLoader } from '../components/LoadingState';

const TIMEZONES = [
  'Asia/Kolkata', 'UTC', 'America/New_York', 'America/Los_Angeles',
  'Europe/London', 'Europe/Paris', 'Asia/Tokyo', 'Asia/Singapore',
  'Australia/Sydney', 'America/Chicago',
];

export default function Settings({ aiStatus, onHeaderChange, onSettingsChange }) {
  const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [clearMsg, setClearMsg] = useState(null);
  const [seedMsg, setSeedMsg] = useState(null);
  const [seeding, setSeeding] = useState(false);

  useEffect(() => {
    onHeaderChange?.('Settings');
  }, [onHeaderChange]);


  useEffect(() => {
    settingsApi.get().then((s) => {
      setForm(s);
      setLoading(false);
    }).catch((e) => {
      setError(e.message);
      setLoading(false);
    });
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    try {
      const updated = await settingsApi.update({
        preferred_name: form.preferred_name || '',
        timezone: form.timezone,
        default_start_time: form.default_start_time,
        default_end_time: form.default_end_time,
        default_break_duration: form.default_break_duration,
        theme: form.theme,
      });
      setForm(updated);
      setSaved(true);
      onSettingsChange?.(updated);
      setTimeout(() => setSaved(false), 2500);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleSeedDemo = async () => {
    setSeeding(true);
    setSeedMsg(null);
    try {
      const res = await tasksApi.seedDemo(form?.timezone || 'Asia/Kolkata');
      setSeedMsg(`✓ ${res.message}`);
    } catch (e) {
      setSeedMsg(`Error: ${e.message}`);
    } finally {
      setSeeding(false);
    }
  };

  const handleClearDemo = async () => {
    setShowClearConfirm(false);
    try {
      const res = await tasksApi.clearDemo();
      setClearMsg(`✓ ${res.message}`);
      setTimeout(() => setClearMsg(null), 3000);
    } catch (e) {
      setClearMsg(`Error: ${e.message}`);
    }
  };

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  if (loading) return <PageLoader />;
  if (!form) return null;

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      {error && (
        <div className="alert alert-danger" style={{ marginBottom: 'var(--space-4)' }}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSave}>
        {/* Profile */}
        <section style={{ marginBottom: 'var(--space-8)' }}>
          <h3 style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-base)' }}>Profile</h3>
          <div className="card">
            <div className="form-group">
              <label className="form-label" htmlFor="pref-name">Your Name</label>
              <input
                id="pref-name"
                type="text"
                className="form-input"
                value={form.preferred_name}
                onChange={(e) => set('preferred_name', e.target.value)}
                placeholder="What should PlanWise call you?"
                maxLength={100}
              />
            </div>
          </div>
        </section>

        {/* Time & Scheduling */}
        <section style={{ marginBottom: 'var(--space-8)' }}>
          <h3 style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-base)' }}>
            Time & Scheduling
          </h3>
          <div className="card">
            <div className="grid grid-2" style={{ gap: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
              <div className="form-group">
                <label className="form-label" htmlFor="settings-timezone">Timezone</label>
                <select
                  id="settings-timezone"
                  className="form-select"
                  value={form.timezone}
                  onChange={(e) => set('timezone', e.target.value)}
                >
                  {TIMEZONES.map((tz) => <option key={tz} value={tz}>{tz}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="break-dur">Default Break (min)</label>
                <input
                  id="break-dur"
                  type="number"
                  className="form-input"
                  value={form.default_break_duration}
                  min={0}
                  max={120}
                  onChange={(e) => set('default_break_duration', parseInt(e.target.value) || 0)}
                />
              </div>
            </div>
            <div className="grid grid-2" style={{ gap: 'var(--space-4)' }}>
              <div className="form-group">
                <label className="form-label" htmlFor="default-start">Default Start Time</label>
                <input
                  id="default-start"
                  type="time"
                  className="form-input"
                  value={form.default_start_time}
                  onChange={(e) => set('default_start_time', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="default-end">Default End Time</label>
                <input
                  id="default-end"
                  type="time"
                  className="form-input"
                  value={form.default_end_time}
                  onChange={(e) => set('default_end_time', e.target.value)}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Appearance */}
        <section style={{ marginBottom: 'var(--space-8)' }}>
          <h3 style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-base)' }}>Appearance</h3>
          <div className="card">
            <div className="form-group">
              <label className="form-label" htmlFor="theme-select">Theme</label>
              <select
                id="theme-select"
                className="form-select"
                value={form.theme}
                onChange={(e) => set('theme', e.target.value)}
                style={{ maxWidth: 200 }}
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </div>
          </div>
        </section>

        {/* Save button */}
        <div className="flex items-center gap-3" style={{ marginBottom: 'var(--space-8)' }}>
          <button type="submit" className="btn btn-primary" disabled={saving} id="save-settings-btn">
            {saving ? <div className="spinner" style={{ width: 16, height: 16 }} /> : <Save size={16} />}
            Save Settings
          </button>
          {saved && (
            <span style={{ color: 'var(--clr-success)', fontSize: 'var(--text-sm)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <Check size={16} /> Saved!
            </span>
          )}
        </div>
      </form>

      {/* AI Status */}
      <section style={{ marginBottom: 'var(--space-8)' }}>
        <h3 style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-base)' }}>AI Configuration</h3>
        <div className="card">
          <div className="flex items-center gap-3" style={{ marginBottom: 'var(--space-3)' }}>
            <Bot size={18} style={{ color: aiStatus?.available ? 'var(--clr-success)' : 'var(--clr-ink-4)' }} />
            <div>
              <div style={{ fontWeight: 'var(--weight-medium)', fontSize: 'var(--text-sm)' }}>
                {aiStatus?.available ? `AI Enabled — ${aiStatus.provider}` : 'Rule-based Mode'}
              </div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--clr-ink-3)' }}>
                {aiStatus?.available
                  ? 'The assistant uses an LLM for smarter responses.'
                  : 'No AI API key configured. The assistant uses deterministic intent handling.'}
              </div>
            </div>
            <span style={{
              marginLeft: 'auto',
              width: 8, height: 8, borderRadius: '50%',
              background: aiStatus?.available ? 'var(--clr-success)' : 'var(--clr-ink-4)',
            }} />
          </div>
          {!aiStatus?.available && (
            <div style={{
              padding: 'var(--space-3)',
              background: 'var(--clr-surface)',
              borderRadius: 'var(--radius-sm)',
              fontSize: 'var(--text-xs)',
              color: 'var(--clr-ink-3)',
              fontFamily: 'monospace',
            }}>
              To enable AI: add AI_PROVIDER and your API key to backend/.env<br />
              Example: AI_PROVIDER=openai<br />
              OPENAI_API_KEY=sk-...
            </div>
          )}
        </div>
      </section>

      {/* Data */}
      <section>
        <h3 style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-base)' }}>Demo Data</h3>
        <div className="card">
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--clr-ink-3)', marginBottom: 'var(--space-4)' }}>
            Load sample student tasks to explore the app, or clear them when you're done.
          </p>
          <div className="flex gap-3 flex-wrap">
            <button
              className="btn btn-secondary btn-sm"
              onClick={handleSeedDemo}
              disabled={seeding}
              id="seed-demo-btn"
            >
              <Database size={14} />
              {seeding ? 'Loading…' : 'Load Demo Data'}
            </button>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setShowClearConfirm(true)}
              style={{ color: 'var(--clr-danger)' }}
              id="clear-demo-btn"
            >
              <Trash2 size={14} />
              Clear Demo Data
            </button>
          </div>
          {seedMsg && (
            <div style={{ marginTop: 'var(--space-3)', fontSize: 'var(--text-sm)', color: 'var(--clr-success)' }}>
              {seedMsg}
            </div>
          )}
          {clearMsg && (
            <div style={{ marginTop: 'var(--space-3)', fontSize: 'var(--text-sm)', color: 'var(--clr-success)' }}>
              {clearMsg}
            </div>
          )}
        </div>
      </section>

      {/* About */}
      <div className="card" style={{ marginTop: 'var(--space-8)', background: 'var(--clr-surface)' }}>
        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--clr-ink-4)', lineHeight: 'var(--leading-relaxed)' }}>
          <strong>PlanWise AI v1.0</strong> — Amazon Developer Hackathon submission.<br />
          This application is a <strong>simulated Alexa+ experience</strong> and is not affiliated with or
          connected to Amazon's official Alexa+ service. Built by a solo B.Tech CSE (AI & ML) student.
        </div>
      </div>

      {showClearConfirm && (
        <ConfirmDialog
          title="Clear Demo Data"
          message="This will delete all demo tasks. Your real tasks will not be affected."
          onConfirm={handleClearDemo}
          onCancel={() => setShowClearConfirm(false)}
          confirmLabel="Clear Demo Data"
          danger
        />
      )}
    </div>
  );
}
