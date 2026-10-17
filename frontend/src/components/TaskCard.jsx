import { Check, Clock, AlertCircle, Tag } from 'lucide-react';
import { relativeDate, isOverdue, formatDuration, classNames } from '../utils/helpers';

const PRIORITY_CLASS = {
  urgent: 'badge-urgent',
  high: 'badge-high',
  medium: 'badge-medium',
  low: 'badge-low',
};

export default function TaskCard({ task, onToggleComplete, onClick, compact = false }) {
  const overdue = isOverdue(task.due_date) && task.status !== 'completed';
  const isDone = task.status === 'completed';

  const handleCheck = (e) => {
    e.stopPropagation();
    onToggleComplete?.(task);
  };

  return (
    <div
      className={classNames(
        'task-card',
        overdue && 'overdue',
        isDone && 'completed'
      )}
      onClick={() => onClick?.(task)}
      role="article"
      aria-label={`Task: ${task.title}`}
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter') onClick?.(task); }}
    >
      <div className="task-card-header">
        {/* Checkbox */}
        <button
          className={classNames('task-card-checkbox', isDone && 'checked')}
          onClick={handleCheck}
          aria-label={isDone ? `Reopen ${task.title}` : `Complete ${task.title}`}
          aria-pressed={isDone}
        >
          {isDone && <Check size={11} strokeWidth={3} />}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className={classNames('task-card-title', isDone && 'completed')}>
            {task.title}
          </div>

          {!compact && task.description && (
            <div style={{
              fontSize: 'var(--text-xs)',
              color: 'var(--clr-ink-4)',
              marginTop: 'var(--space-1)',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}>
              {task.description}
            </div>
          )}

          <div className="task-card-meta">
            {/* Priority badge */}
            <span className={`badge ${PRIORITY_CLASS[task.priority]}`}>
              {task.priority}
            </span>

            {/* Status badge — only show non-todo */}
            {task.status !== 'todo' && (
              <span className={`badge badge-${task.status}`}>
                {task.status.replace('_', ' ')}
              </span>
            )}

            {/* Due date */}
            {task.due_date && (
              <span className={classNames('task-card-date', overdue && 'overdue')}>
                {overdue && <AlertCircle size={11} />}
                {!overdue && <Clock size={11} />}
                {relativeDate(task.due_date)}
              </span>
            )}

            {/* Duration */}
            {task.estimated_duration && !compact && (
              <span className="task-card-date">
                ~{formatDuration(task.estimated_duration)}
              </span>
            )}

            {/* Category */}
            {task.category && task.category !== 'General' && !compact && (
              <span className="task-card-date">
                <Tag size={10} />
                {task.category}
              </span>
            )}

            {/* Demo badge */}
            {task.is_demo && !compact && (
              <span className="badge" style={{ background: 'var(--clr-surface-2)', color: 'var(--clr-ink-4)' }}>
                demo
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
