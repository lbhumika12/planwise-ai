import { useState, useRef } from 'react';
import { Send } from 'lucide-react';

export default function ChatComposer({ onSend, disabled }) {
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  const handleSend = () => {
    const msg = value.trim();
    if (!msg || disabled) return;
    onSend(msg);
    setValue('');
    textareaRef.current?.focus();
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{
      borderTop: '1px solid var(--clr-border)',
      padding: 'var(--space-4)',
      background: 'var(--clr-bg)',
    }}>
      <div style={{
        display: 'flex',
        gap: 'var(--space-2)',
        alignItems: 'flex-end',
        border: '1px solid var(--clr-border)',
        borderRadius: 'var(--radius)',
        padding: 'var(--space-2)',
        background: 'var(--clr-bg)',
        transition: 'border-color var(--transition-fast)',
      }}>
        <textarea
          ref={textareaRef}
          className="form-textarea"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Message PlanWise AI… (Enter to send, Shift+Enter for new line)"
          rows={1}
          disabled={disabled}
          style={{
            border: 'none',
            outline: 'none',
            boxShadow: 'none',
            resize: 'none',
            flex: 1,
            minHeight: 36,
            maxHeight: 120,
            padding: 'var(--space-1) var(--space-2)',
            background: 'transparent',
            fontSize: 'var(--text-sm)',
          }}
          id="chat-input"
          aria-label="Message input"
        />
        <button
          className="btn btn-primary btn-sm"
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          id="chat-send-btn"
          aria-label="Send message"
          style={{ flexShrink: 0 }}
        >
          <Send size={16} />
        </button>
      </div>
      <div style={{
        fontSize: 'var(--text-xs)',
        color: 'var(--clr-ink-4)',
        marginTop: 'var(--space-1)',
        textAlign: 'right',
      }}>
        Press Enter to send
      </div>
    </div>
  );
}
