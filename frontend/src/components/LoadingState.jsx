import { Loader2 } from 'lucide-react';

export function LoadingSpinner({ size = 20, text }) {
  return (
    <div className="flex items-center gap-3" style={{ padding: 'var(--space-4)', color: 'var(--clr-ink-3)' }}>
      <Loader2 size={size} className="spinner" style={{ animation: 'spin 0.7s linear infinite' }} />
      {text && <span style={{ fontSize: 'var(--text-sm)' }}>{text}</span>}
    </div>
  );
}

export function LoadingDots() {
  return (
    <div className="loading-dots" style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
      <span></span><span></span><span></span>
    </div>
  );
}

export function PageLoader() {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      height: 200, flexDirection: 'column', gap: 'var(--space-4)',
      color: 'var(--clr-ink-3)',
    }}>
      <div className="spinner" style={{ width: 32, height: 32 }}></div>
      <span style={{ fontSize: 'var(--text-sm)' }}>Loading…</span>
    </div>
  );
}
