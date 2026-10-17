import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, Sparkles } from 'lucide-react';
import { assistantApi } from '../services/api';
import { UserMessage, AssistantMessage } from '../components/ChatMessage';
import ChatComposer from '../components/ChatComposer';

const SUGGESTED_STARTERS = [
  "Help me plan my day.",
  "Add an assignment due tomorrow.",
  "What should I focus on first?",
  "Show my overdue tasks.",
  "I have 90 minutes free. What can I finish?",
  "What tasks do I have this week?",
];

const WELCOME_MESSAGE = {
  role: 'assistant',
  content:
    "Hi! I'm **PlanWise AI**, your personal productivity assistant. 🌿\n\n" +
    "I can help you:\n" +
    "• **Add tasks** — 'Add a machine learning assignment due tomorrow, high priority'\n" +
    "• **Plan your day** — 'Plan my day from 9 AM to 6 PM'\n" +
    "• **Prioritize** — 'What should I work on first?'\n" +
    "• **Track progress** — 'Show my overdue tasks'\n" +
    "• **Find free-time tasks** — 'I have 2 hours free, what can I finish?'\n\n" +
    "What would you like to do?",
  suggested_prompts: SUGGESTED_STARTERS.slice(0, 3),
  ai_powered: false,
};

export default function Assistant({ settings, aiStatus, onHeaderChange }) {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    onHeaderChange?.('AI Assistant');
  }, [onHeaderChange]);

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => { scrollToBottom(); }, [messages, loading]);

  const sendMessage = useCallback(async (text) => {
    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    const history = messages.slice(1).map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const res = await assistantApi.chat(
        text,
        history,
        settings?.timezone || 'Asia/Kolkata'
      );
      const assistantMsg = {
        role: 'assistant',
        content: res.message,
        intent: res.intent,
        tasks: res.tasks,
        schedule_blocks: res.schedule_blocks,
        suggested_prompts: res.suggested_prompts,
        ai_powered: res.ai_powered,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Sorry, I ran into an error: ${e.message}. Please check that the backend is running.`,
          ai_powered: false,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [messages, settings]);

  const handleSuggestClick = (prompt) => {
    sendMessage(prompt);
  };

  const handleTaskClick = () => {
    navigate('/tasks');
  };


  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      maxWidth: 760,
      margin: '0 auto',
    }}>
      {/* Header bar */}
      <div style={{
        padding: 'var(--space-4) 0',
        borderBottom: '1px solid var(--clr-border)',
        marginBottom: 'var(--space-4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div className="flex items-center gap-3">
          <div style={{
            width: 36, height: 36,
            borderRadius: 'var(--radius-sm)',
            background: 'var(--clr-primary-bg)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Bot size={18} style={{ color: 'var(--clr-primary)' }} />
          </div>
          <div>
            <div style={{ fontWeight: 'var(--weight-semibold)', fontSize: 'var(--text-sm)' }}>
              PlanWise AI
            </div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--clr-ink-4)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{
                width: 6, height: 6, borderRadius: '50%',
                background: aiStatus?.available ? 'var(--clr-success)' : 'var(--clr-ink-4)',
                display: 'inline-block',
              }} />
              {aiStatus?.available ? `AI mode: ${aiStatus.provider}` : 'Rule-based mode'}
            </div>
          </div>
        </div>

        <button
          className="btn btn-ghost btn-sm"
          onClick={() => setMessages([WELCOME_MESSAGE])}
          aria-label="Clear conversation"
        >
          Clear chat
        </button>
      </div>

      {/* Suggested prompts (when only welcome message) */}
      {messages.length === 1 && (
        <div style={{ marginBottom: 'var(--space-6)' }}>
          <div style={{
            fontSize: 'var(--text-xs)',
            fontWeight: 'var(--weight-semibold)',
            color: 'var(--clr-ink-4)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: 'var(--space-3)',
          }}>
            Try asking
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
            {SUGGESTED_STARTERS.map((s, i) => (
              <button
                key={i}
                className="btn btn-secondary btn-sm"
                onClick={() => sendMessage(s)}
                style={{ fontSize: 'var(--text-xs)' }}
              >
                <Sparkles size={12} />
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', paddingBottom: 'var(--space-4)' }}>
        {messages.map((msg, i) => (
          msg.role === 'user' ? (
            <UserMessage key={i} content={msg.content} />
          ) : (
            <AssistantMessage
              key={i}
              message={msg}
              onSuggestClick={handleSuggestClick}
              onTaskClick={handleTaskClick}
            />
          )
        ))}

        {loading && (
          <AssistantMessage message={{}} isLoading />
        )}

        <div ref={bottomRef} />
      </div>

      {/* Composer */}
      <ChatComposer onSend={sendMessage} disabled={loading} />
    </div>
  );
}
