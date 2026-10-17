import { useEffect, useRef } from 'react';

export default function ConfirmDialog({ title, message, onConfirm, onCancel, confirmLabel = 'Delete', danger = true }) {
  const cancelRef = useRef(null);

  useEffect(() => {
    cancelRef.current?.focus();
    const onKey = (e) => { if (e.key === 'Escape') onCancel(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onCancel]);

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
      <div className="modal-box" style={{ maxWidth: 400 }}>
        <h3 id="confirm-title" style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-3)' }}>
          {title}
        </h3>
        <p style={{ color: 'var(--clr-ink-3)', fontSize: 'var(--text-sm)', lineHeight: 'var(--leading-relaxed)' }}>
          {message}
        </p>
        <div className="flex gap-3 justify-end" style={{ marginTop: 'var(--space-6)' }}>
          <button ref={cancelRef} className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button
            className={`btn ${danger ? 'btn-danger' : 'btn-primary'}`}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
