import { AlertCircle, Clock } from 'lucide-react';
import { formatDuration } from '../utils/helpers';

const PRIORITY_COLORS = {
  urgent: 'var(--clr-urgent)',
  high: 'var(--clr-high)',
  medium: 'var(--clr-medium)',
  low: 'var(--clr-ink-4)',
};

export default function ScheduleTimeline({ blocks, warnings = [], unscheduled = [], stats }) {
  return (
    <div>
      {/* Stats bar */}
      {stats && (
        <div style={{
          display: 'flex',
          gap: 'var(--space-6)',
          padding: 'var(--space-4)',
          background: 'var(--clr-surface)',
          borderRadius: 'var(--radius)',
          marginBottom: 'var(--space-4)',
          flexWrap: 'wrap',
        }}>
          <div>
            <div style={{ fontSize: 'var(--text-xl)', fontWeight: 'var(--weight-bold)' }}>
              {blocks.length}
            </div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--clr-ink-3)' }}>Tasks scheduled</div>
          </div>
          <div>
            <div style={{ fontSize: 'var(--text-xl)', fontWeight: 'var(--weight-bold)' }}>
              {formatDuration(stats.total_scheduled_minutes)}
            </div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--clr-ink-3)' }}>Total work time</div>
          </div>
          <div>
            <div style={{ fontSize: 'var(--text-xl)', fontWeight: 'var(--weight-bold)' }}>
              {stats.utilization_percent}%
            </div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--clr-ink-3)' }}>Time utilization</div>
          </div>
          <div style={{ flex: 1, minWidth: 120 }}>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--clr-ink-3)', marginBottom: 4 }}>
              {stats.utilization_percent}% of available time
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${Math.min(stats.utilization_percent, 100)}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Warnings */}
      {warnings.map((w, i) => (
        <div key={i} className="alert alert-warning" style={{ marginBottom: 'var(--space-3)' }}>
          <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
          <span>{w}</span>
        </div>
      ))}

      {/* Schedule blocks */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {blocks.map((block, i) => (
          <div key={i} className="schedule-block">
            <div className="schedule-time">
              <div style={{ fontWeight: 'var(--weight-medium)' }}>{block.start_time}</div>
              <div style={{ color: 'var(--clr-ink-4)' }}>↓ {block.end_time}</div>
            </div>

            <div style={{
              width: 3,
              alignSelf: 'stretch',
              borderRadius: 2,
              background: PRIORITY_COLORS[block.priority] || 'var(--clr-border)',
              flexShrink: 0,
            }} />

            <div className="flex-1 min-w-0">
              <div style={{ fontWeight: 'var(--weight-medium)', fontSize: 'var(--text-sm)' }}>
                {block.task_title}
              </div>
              <div style={{
                fontSize: 'var(--text-xs)',
                color: 'var(--clr-ink-3)',
                marginTop: 4,
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-2)',
                flexWrap: 'wrap',
              }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                  <Clock size={11} />
                  {block.duration_minutes}min
                </span>
                <span style={{ color: PRIORITY_COLORS[block.priority] }}>
                  {block.priority}
                </span>
                {block.reason && (
                  <span style={{ fontStyle: 'italic' }}>{block.reason}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Unscheduled tasks */}
      {unscheduled.length > 0 && (
        <div style={{ marginTop: 'var(--space-6)' }}>
          <div style={{
            fontSize: 'var(--text-sm)',
            fontWeight: 'var(--weight-semibold)',
            color: 'var(--clr-ink-2)',
            marginBottom: 'var(--space-3)',
          }}>
            Could not fit ({unscheduled.length})
          </div>
          {unscheduled.map((t) => (
            <div key={t.id} style={{
              padding: 'var(--space-3)',
              border: '1px dashed var(--clr-border)',
              borderRadius: 'var(--radius-sm)',
              marginBottom: 'var(--space-2)',
              opacity: 0.7,
              fontSize: 'var(--text-sm)',
            }}>
              {t.title}
              {t.estimated_duration && (
                <span style={{ color: 'var(--clr-ink-4)', marginLeft: 'var(--space-2)' }}>
                  {t.estimated_duration}min
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
