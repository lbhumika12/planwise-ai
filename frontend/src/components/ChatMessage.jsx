import { parseMarkdown } from '../utils/helpers';
import { LoadingDots } from './LoadingState';
import TaskCard from './TaskCard';

const PRIORITY_COLORS = {
  urgent: 'var(--clr-urgent)',
  high: 'var(--clr-high)',
  medium: 'var(--clr-medium)',
  low: 'var(--clr-ink-4)',
};

export function UserMessage({ content }) {
  return (
    <div className="flex" style={{ justifyContent: 'flex-end', marginBottom: 'var(--space-4)' }}>
      <div className="chat-bubble chat-bubble-user">
        {content}
      </div>
    </div>
  );
}

export function AssistantMessage({ message, isLoading, onSuggestClick, onTaskClick }) {
  if (isLoading) {
    return (
      <div className="flex" style={{ marginBottom: 'var(--space-4)' }}>
        <div className="chat-bubble chat-bubble-assistant" style={{ minWidth: 80 }}>
          <LoadingDots />
        </div>
      </div>
    );
  }

  return (
    <div style={{ marginBottom: 'var(--space-4)' }}>
      {/* Main message bubble */}
      <div className="flex">
        <div className="chat-bubble chat-bubble-assistant">
          <div
            dangerouslySetInnerHTML={{ __html: parseMarkdown(message.content) }}
            style={{ lineHeight: 'var(--leading-relaxed)' }}
          />

          {/* AI indicator */}
          {message.ai_powered !== undefined && (
            <div style={{
              marginTop: 'var(--space-2)',
              paddingTop: 'var(--space-2)',
              borderTop: '1px solid var(--clr-border)',
              fontSize: 'var(--text-xs)',
              color: 'var(--clr-ink-4)',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}>
              <span
                style={{
                  width: 6, height: 6,
                  borderRadius: '50%',
                  background: message.ai_powered ? 'var(--clr-success)' : 'var(--clr-ink-4)',
                  display: 'inline-block',
                }}
              />
              {message.ai_powered ? 'AI response' : 'Rule-based response'}
            </div>
          )}
        </div>
      </div>

      {/* Task list if present */}
      {message.tasks && message.tasks.length > 0 && (
        <div style={{ marginTop: 'var(--space-3)', marginLeft: 0 }}>
          {message.tasks.map((task) => (
            <div key={task.id} style={{ marginBottom: 'var(--space-2)' }}>
              <TaskCard task={task} onClick={onTaskClick} compact />
            </div>
          ))}
        </div>
      )}

      {/* Schedule blocks if present */}
      {message.schedule_blocks && message.schedule_blocks.length > 0 && (
        <div style={{ marginTop: 'var(--space-3)' }}>
          {message.schedule_blocks.map((block, i) => (
            <div key={i} className="schedule-block" style={{ marginBottom: 'var(--space-2)' }}>
              <div className="schedule-time">
                {block.start_time} – {block.end_time}
              </div>
              <div className="flex-1 min-w-0">
                <div style={{ fontWeight: 'var(--weight-medium)', fontSize: 'var(--text-sm)' }}>
                  {block.task_title}
                </div>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--clr-ink-3)', marginTop: 2 }}>
                  {block.duration_minutes}min ·{' '}
                  <span style={{ color: PRIORITY_COLORS[block.priority] }}>
                    {block.priority}
                  </span>
                  {block.reason && ` · ${block.reason}`}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Suggested prompts */}
      {message.suggested_prompts && message.suggested_prompts.length > 0 && (
        <div style={{
          marginTop: 'var(--space-3)',
          display: 'flex',
          flexWrap: 'wrap',
          gap: 'var(--space-2)',
        }}>
          {message.suggested_prompts.map((prompt, i) => (
            <button
              key={i}
              className="btn btn-secondary btn-sm"
              onClick={() => onSuggestClick?.(prompt)}
              style={{ fontSize: 'var(--text-xs)' }}
            >
              {prompt}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
