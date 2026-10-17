import { useMemo } from 'react';
import { Menu, Plus, Sun, Moon } from 'lucide-react';

export default function Header({ title, onMenuToggle, onQuickAdd, theme, onThemeToggle }) {
  const today = useMemo(() => new Date().toLocaleDateString('en-IN', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  }), []);


  return (
    <header className="app-header">
      {/* Mobile menu button */}
      <button
        className="btn btn-ghost btn-icon"
        onClick={onMenuToggle}
        aria-label="Toggle menu"
        id="menu-toggle"
        style={{ display: 'none' }}
      >
        <Menu size={20} />
      </button>

      {/* Page title */}
      <div className="flex-1 min-w-0">
        <h1 style={{
          fontSize: 'var(--text-lg)',
          fontWeight: 'var(--weight-semibold)',
          color: 'var(--clr-ink)',
          lineHeight: 1,
        }}>
          {title}
        </h1>
        <div style={{
          fontSize: 'var(--text-xs)',
          color: 'var(--clr-ink-4)',
          marginTop: 2,
        }}>
          {today}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          className="btn btn-ghost btn-icon"
          onClick={onThemeToggle}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          title={`${theme === 'dark' ? 'Light' : 'Dark'} mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button
          className="btn btn-accent btn-sm"
          onClick={onQuickAdd}
          id="quick-add-btn"
          aria-label="Quick add task"
        >
          <Plus size={16} />
          Add Task
        </button>
      </div>
    </header>
  );
}
