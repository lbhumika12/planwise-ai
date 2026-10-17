import { useState, useEffect, useCallback } from 'react';
import { Calendar, RefreshCw, Check, AlertCircle } from 'lucide-react';
import { tasksApi, scheduleApi } from '../services/api';
import ScheduleTimeline from '../components/ScheduleTimeline';
import TaskCard from '../components/TaskCard';
import { PageLoader } from '../components/LoadingState';
import { todayString, formatDate } from '../utils/helpers';

export default function MyDay({ settings, onHeaderChange }) {
  const [date, setDate] = useState(todayString());
  const [schedule, setSchedule] = useState(null);
  const [unscheduledTasks, setUnscheduledTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(false);
  const [error, setError] = useState(null);
  const [config, setConfig] = useState({
    start_time: settings?.default_start_time || '09:00',
    end_time: settings?.default_end_time || '21:00',
    break_duration: settings?.default_break_duration ?? 30,
  });

  useEffect(() => {
    onHeaderChange?.('My Day');
  }, [onHeaderChange]);


  const generatePlan = useCallback(async () => {
    setLoading(true);
    setError(null);
    setApplied(false);
    setSchedule(null);
    try {
      const result = await scheduleApi.plan({
        date,
        start_time: config.start_time,
        end_time: config.end_time,
        break_duration: config.break_duration,
        timezone: settings?.timezone || 'Asia/Kolkata',
      });
      setSchedule(result);
      setUnscheduledTasks(result.unscheduled_tasks || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [date, config, settings]);

  const applySchedule = async () => {
    if (!schedule?.scheduled_blocks?.length) return;
    setApplying(true);
    try {
      await scheduleApi.apply({
        date,
        scheduled_blocks: schedule.scheduled_blocks,
      });
      setApplied(true);
    } catch (e) {
      setError(`Could not apply schedule: ${e.message}`);
    } finally {
      setApplying(false);
    }
  };

  const handleToggleTask = async (task) => {
    try {
      if (task.status === 'completed') await tasksApi.reopen(task.id);
      else await tasksApi.complete(task.id);
      generatePlan();
    } catch (e) { console.error(e); }
  };

  return (
    <div style={{ maxWidth: 760, margin: '0 auto' }}>
      {/* Config panel */}
      <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-4)',
        }}>
          <div className="form-group">
            <label className="form-label" htmlFor="plan-date">Date</label>
            <input
              id="plan-date"
              type="date"
              className="form-input"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="plan-start">Start Time</label>
            <input
              id="plan-start"
              type="time"
              className="form-input"
              value={config.start_time}
              onChange={(e) => setConfig((c) => ({ ...c, start_time: e.target.value }))}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="plan-end">End Time</label>
            <input
              id="plan-end"
              type="time"
              className="form-input"
              value={config.end_time}
              onChange={(e) => setConfig((c) => ({ ...c, end_time: e.target.value }))}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="plan-break">Break (min)</label>
            <input
              id="plan-break"
              type="number"
              className="form-input"
              value={config.break_duration}
              min={0}
              max={120}
              onChange={(e) => setConfig((c) => ({ ...c, break_duration: parseInt(e.target.value) || 0 }))}
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            className="btn btn-primary"
            onClick={generatePlan}
            disabled={loading}
            id="generate-plan-btn"
          >
            <RefreshCw size={16} className={loading ? 'spinner' : ''} />
            {loading ? 'Generating…' : 'Generate Plan'}
          </button>

          {schedule && !applied && (
            <button
              className="btn btn-accent"
              onClick={applySchedule}
              disabled={applying || !schedule.scheduled_blocks?.length}
              id="apply-schedule-btn"
            >
              <Check size={16} />
              {applying ? 'Applying…' : 'Apply Schedule'}
            </button>
          )}

          {applied && (
            <div className="alert alert-success" style={{ padding: 'var(--space-2) var(--space-3)' }}>
              <Check size={16} />
              Schedule applied! Tasks have been updated.
            </div>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="alert alert-danger" style={{ marginBottom: 'var(--space-4)' }}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {loading && <PageLoader />}

      {/* No schedule yet */}
      {!loading && !schedule && !error && (
        <div style={{
          textAlign: 'center',
          padding: 'var(--space-16) var(--space-8)',
          color: 'var(--clr-ink-3)',
        }}>
          <Calendar size={48} style={{ color: 'var(--clr-ink-4)', margin: '0 auto var(--space-4)' }} />
          <div style={{ fontWeight: 'var(--weight-semibold)', fontSize: 'var(--text-lg)', color: 'var(--clr-ink-2)', marginBottom: 'var(--space-2)' }}>
            No plan generated yet
          </div>
          <p style={{ fontSize: 'var(--text-sm)', maxWidth: 320, margin: '0 auto' }}>
            Click "Generate Plan" to create an optimized daily schedule based on your tasks.
            Tasks need an estimated duration to be scheduled.
          </p>
        </div>
      )}

      {/* Schedule result */}
      {!loading && schedule && (
        <div>
          <div style={{
            fontSize: 'var(--text-sm)',
            fontWeight: 'var(--weight-semibold)',
            color: 'var(--clr-ink-2)',
            marginBottom: 'var(--space-4)',
          }}>
            Schedule for {formatDate(date)} — {config.start_time} to {config.end_time}
          </div>

          {schedule.scheduled_blocks?.length === 0 ? (
            <div className="alert alert-warning">
              <AlertCircle size={16} />
              <span>
                No tasks could be scheduled. Make sure your pending tasks have estimated durations set.
              </span>
            </div>
          ) : (
            <ScheduleTimeline
              blocks={schedule.scheduled_blocks || []}
              warnings={schedule.warnings || []}
              unscheduled={schedule.unscheduled_tasks || []}
              stats={{
                total_scheduled_minutes: schedule.total_scheduled_minutes,
                available_minutes: schedule.available_minutes,
                utilization_percent: schedule.utilization_percent,
              }}
            />
          )}

          {/* Unscheduled tasks in this session */}
          {unscheduledTasks.length > 0 && schedule.scheduled_blocks?.length > 0 && (
            <div style={{ marginTop: 'var(--space-8)' }}>
              <div style={{
                fontSize: 'var(--text-sm)',
                fontWeight: 'var(--weight-semibold)',
                color: 'var(--clr-ink-2)',
                marginBottom: 'var(--space-3)',
              }}>
                Pending tasks (not scheduled today)
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                {unscheduledTasks.map((t) => (
                  <TaskCard
                    key={t.id}
                    task={t}
                    onToggleComplete={handleToggleTask}
                    compact
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
