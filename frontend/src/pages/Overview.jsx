import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CheckSquare, AlertCircle, Calendar, TrendingUp,
  ArrowRight, PlayCircle, MessageSquare
} from 'lucide-react';
import { tasksApi } from '../services/api';
import TaskCard from '../components/TaskCard';
import TaskForm from '../components/TaskForm';
import { PageLoader } from '../components/LoadingState';
import EmptyState from '../components/EmptyState';
import { greetingByTime } from '../utils/helpers';

export default function Overview({ settings, onHeaderChange }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    onHeaderChange?.('Overview');
  }, [onHeaderChange]);


  const load = useCallback(async () => {
    try {
      setError(null);
      const data = await tasksApi.dashboard(settings?.timezone || 'Asia/Kolkata');
      setStats(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [settings]);

  useEffect(() => { load(); }, [load]);

  const handleToggle = async (task) => {
    try {
      if (task.status === 'completed') {
        await tasksApi.reopen(task.id);
      } else {
        await tasksApi.complete(task.id);
      }
      load();
    } catch (e) {
      console.error(e);
    }
  };

  const handleSave = async (data) => {
    setSaving(true);
    try {
      await tasksApi.create(data);
      setShowForm(false);
      load();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const name = settings?.preferred_name;
  const greeting = `${greetingByTime()}${name ? `, ${name}` : ''}`;

  if (loading) return <PageLoader />;

  if (error) {
    return (
      <div className="alert alert-danger" style={{ margin: 'var(--space-8)' }}>
        <AlertCircle size={16} />
        <span>Could not load dashboard: {error}</span>
        <button className="btn btn-secondary btn-sm" onClick={load} style={{ marginLeft: 'auto' }}>
          Retry
        </button>
      </div>
    );
  }

  const completionPct = stats?.completion_rate || 0;

  return (
    <div style={{ maxWidth: 'var(--content-max)', margin: '0 auto' }}>
      {/* Greeting */}
      <div style={{ marginBottom: 'var(--space-8)' }}>
        <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-3xl)', fontWeight: 400 }}>
          {greeting} 👋
        </h2>
        <p style={{ color: 'var(--clr-ink-3)', marginTop: 'var(--space-2)' }}>
          {stats?.total_tasks === 0
            ? "You have no tasks yet. Add some to get started."
            : `You have ${stats.due_today} task${stats.due_today !== 1 ? 's' : ''} due today` +
              (stats.overdue > 0 ? ` and ${stats.overdue} overdue.` : '.')}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-4" style={{ gap: 'var(--space-4)', marginBottom: 'var(--space-8)' }}>
        <StatCard
          value={stats?.due_today || 0}
          label="Due Today"
          icon={Calendar}
          color="var(--clr-primary)"
          onClick={() => navigate('/tasks?status=&due=today')}
        />
        <StatCard
          value={stats?.overdue || 0}
          label="Overdue"
          icon={AlertCircle}
          color="var(--clr-danger)"
          onClick={() => navigate('/tasks')}
        />
        <StatCard
          value={stats?.in_progress || 0}
          label="In Progress"
          icon={PlayCircle}
          color="var(--clr-info)"
          onClick={() => navigate('/tasks?status=in_progress')}
        />
        <StatCard
          value={`${Math.round(completionPct)}%`}
          label="Completed"
          icon={TrendingUp}
          color="var(--clr-success)"
          onClick={() => navigate('/tasks?status=completed')}
        />
      </div>

      {/* Progress */}
      <div className="card" style={{ marginBottom: 'var(--space-8)' }}>
        <div className="flex items-center justify-between" style={{ marginBottom: 'var(--space-3)' }}>
          <span style={{ fontSize: 'var(--text-sm)', fontWeight: 'var(--weight-medium)' }}>
            Overall Progress
          </span>
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--clr-ink-3)' }}>
            {stats?.total_tasks || 0} tasks total
          </span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${completionPct}%` }} />
        </div>
        <div style={{
          fontSize: 'var(--text-xs)', color: 'var(--clr-ink-4)',
          marginTop: 'var(--space-2)', textAlign: 'right',
        }}>
          {Math.round(completionPct)}% done
        </div>
      </div>

      {/* Main CTA row */}
      <div className="grid grid-2" style={{ gap: 'var(--space-4)', marginBottom: 'var(--space-8)' }}>
        <button
          className="card"
          style={{
            textAlign: 'left', cursor: 'pointer', border: '1px solid var(--clr-border)',
            transition: 'all var(--transition-fast)',
            background: 'var(--clr-primary-bg)',
            borderColor: 'var(--clr-primary)',
          }}
          onClick={() => navigate('/my-day')}
          onMouseEnter={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-sm)'}
          onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
        >
          <div className="flex items-center gap-3" style={{ marginBottom: 'var(--space-2)' }}>
            <Calendar size={20} style={{ color: 'var(--clr-primary)' }} />
            <span style={{ fontWeight: 'var(--weight-semibold)', color: 'var(--clr-primary-text)' }}>
              Plan My Day
            </span>
          </div>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--clr-ink-3)' }}>
            Generate a personalized schedule for today.
          </p>
        </button>

        <button
          className="card"
          style={{
            textAlign: 'left', cursor: 'pointer',
            background: 'var(--clr-accent-bg)',
            borderColor: 'var(--clr-accent)',
            border: '1px solid var(--clr-accent)',
            transition: 'all var(--transition-fast)',
          }}
          onClick={() => navigate('/assistant')}
          onMouseEnter={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-sm)'}
          onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
        >
          <div className="flex items-center gap-3" style={{ marginBottom: 'var(--space-2)' }}>
            <MessageSquare size={20} style={{ color: 'var(--clr-accent)' }} />
            <span style={{ fontWeight: 'var(--weight-semibold)', color: 'var(--clr-accent)' }}>
              Ask PlanWise
            </span>
          </div>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--clr-ink-3)' }}>
            Add tasks and get priority advice through conversation.
          </p>
        </button>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-2" style={{ gap: 'var(--space-6)', alignItems: 'start' }}>
        {/* Due Today */}
        <div>
          <SectionHeader
            title="Due Today"
            count={stats?.tasks_due_today?.length || 0}
            onViewAll={() => navigate('/tasks')}
          />
          {stats?.tasks_due_today?.length === 0 ? (
            <div style={{ color: 'var(--clr-ink-4)', fontSize: 'var(--text-sm)', padding: 'var(--space-4) 0' }}>
              Nothing due today 🎉
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              {stats.tasks_due_today.map((t) => (
                <TaskCard
                  key={t.id}
                  task={t}
                  onToggleComplete={handleToggle}
                  onClick={() => navigate('/tasks')}
                  compact
                />
              ))}
            </div>
          )}
        </div>

        {/* High Priority */}
        <div>
          <SectionHeader
            title="Overdue"
            count={stats?.overdue_tasks?.length || 0}
            onViewAll={() => navigate('/tasks')}
          />
          {stats?.overdue_tasks?.length === 0 ? (
            <div style={{ color: 'var(--clr-ink-4)', fontSize: 'var(--text-sm)', padding: 'var(--space-4) 0' }}>
              No overdue tasks — great work!
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              {stats.overdue_tasks.map((t) => (
                <TaskCard
                  key={t.id}
                  task={t}
                  onToggleComplete={handleToggle}
                  onClick={() => navigate('/tasks')}
                  compact
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Upcoming */}
      {stats?.upcoming_tasks?.length > 0 && (
        <div style={{ marginTop: 'var(--space-8)' }}>
          <SectionHeader
            title="Upcoming"
            count={stats.upcoming_tasks.length}
            onViewAll={() => navigate('/tasks')}
          />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            {stats.upcoming_tasks.slice(0, 4).map((t) => (
              <TaskCard
                key={t.id}
                task={t}
                onToggleComplete={handleToggle}
                onClick={() => navigate('/tasks')}
                compact
              />
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {stats?.total_tasks === 0 && (
        <div style={{ marginTop: 'var(--space-8)' }}>
          <EmptyState
            icon={CheckSquare}
            title="No tasks yet"
            description="Start by adding your first task, or load demo data to explore the app."
            action={
              <div className="flex gap-3">
                <button className="btn btn-primary" onClick={() => setShowForm(true)}>
                  Add your first task
                </button>
              </div>
            }
          />
        </div>
      )}

      {showForm && (
        <TaskForm
          onSave={handleSave}
          onCancel={() => setShowForm(false)}
          loading={saving}
        />
      )}
    </div>
  );
}

function StatCard({ value, label, icon: Icon, color, onClick }) {
  return (
    <div className="stat-card" onClick={onClick} role="button" tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter') onClick?.(); }}
      style={{ cursor: 'pointer' }}
    >
      <div className="flex items-center justify-between" style={{ marginBottom: 'var(--space-3)' }}>
        <Icon size={18} style={{ color }} aria-hidden="true" />
      </div>
      <div className="stat-value" style={{ color }}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function SectionHeader({ title, count, onViewAll }) {
  return (
    <div className="flex items-center justify-between" style={{ marginBottom: 'var(--space-3)' }}>
      <div className="flex items-center gap-2">
        <span style={{ fontWeight: 'var(--weight-semibold)', fontSize: 'var(--text-base)' }}>
          {title}
        </span>
        {count > 0 && (
          <span style={{
            background: 'var(--clr-surface-2)',
            color: 'var(--clr-ink-3)',
            fontSize: 'var(--text-xs)',
            padding: '1px 7px',
            borderRadius: 'var(--radius-full)',
          }}>
            {count}
          </span>
        )}
      </div>
      <button className="btn btn-ghost btn-sm" onClick={onViewAll} style={{ color: 'var(--clr-primary)' }}>
        View all <ArrowRight size={14} />
      </button>
    </div>
  );
}
