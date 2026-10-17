import { useState, useEffect } from 'react';
import { X, Loader2 } from 'lucide-react';
import { PRIORITIES, CATEGORIES, STATUS_LABELS, todayString } from '../utils/helpers';

const DEFAULT_FORM = {
  title: '',
  description: '',
  category: 'General',
  priority: 'medium',
  status: 'todo',
  due_date: '',
  due_time: '',
  estimated_duration: '',
  tags: '',
};

export default function TaskForm({ task, onSave, onCancel, loading = false }) {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [errors, setErrors] = useState({});
  const isEdit = !!task;

  useEffect(() => {
    if (task) {
      setForm({
        title: task.title || '',
        description: task.description || '',
        category: task.category || 'General',
        priority: task.priority || 'medium',
        status: task.status || 'todo',
        due_date: task.due_date || '',
        due_time: task.due_time || '',
        estimated_duration: task.estimated_duration || '',
        tags: task.tags || '',
      });
    }
  }, [task]);

  const validate = () => {
    const errs = {};
    if (!form.title.trim()) errs.title = 'Task title is required';
    if (form.title.trim().length > 500) errs.title = 'Title too long (max 500 chars)';
    if (form.estimated_duration && (isNaN(form.estimated_duration) || form.estimated_duration < 1)) {
      errs.estimated_duration = 'Duration must be a positive number';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    const data = {
      ...form,
      estimated_duration: form.estimated_duration ? parseInt(form.estimated_duration) : null,
      due_date: form.due_date || null,
      due_time: form.due_time || null,
      description: form.description || null,
      tags: form.tags || null,
    };
    onSave(data);
  };

  const field = (name, value) => {
    setForm((f) => ({ ...f, [name]: value }));
    if (errors[name]) setErrors((e) => ({ ...e, [name]: null }));
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="task-form-title">
      <div className="modal-box">
        {/* Header */}
        <div className="flex items-center justify-between" style={{ marginBottom: 'var(--space-6)' }}>
          <h2 id="task-form-title" style={{ fontSize: 'var(--text-xl)' }}>
            {isEdit ? 'Edit Task' : 'New Task'}
          </h2>
          <button className="btn btn-ghost btn-icon" onClick={onCancel} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} noValidate>
          {/* Title */}
          <div className="form-group" style={{ marginBottom: 'var(--space-4)' }}>
            <label className="form-label required" htmlFor="task-title">Title</label>
            <input
              id="task-title"
              type="text"
              className="form-input"
              value={form.title}
              onChange={(e) => field('title', e.target.value)}
              placeholder="What needs to be done?"
              autoFocus
              maxLength={500}
            />
            {errors.title && <div className="form-error">{errors.title}</div>}
          </div>

          {/* Description */}
          <div className="form-group" style={{ marginBottom: 'var(--space-4)' }}>
            <label className="form-label" htmlFor="task-desc">Description</label>
            <textarea
              id="task-desc"
              className="form-textarea"
              value={form.description}
              onChange={(e) => field('description', e.target.value)}
              placeholder="Optional details…"
              rows={3}
            />
          </div>

          {/* Row: Priority + Category */}
          <div className="grid grid-2" style={{ gap: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="task-priority">Priority</label>
              <select
                id="task-priority"
                className="form-select"
                value={form.priority}
                onChange={(e) => field('priority', e.target.value)}
              >
                {PRIORITIES.map((p) => (
                  <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="task-category">Category</label>
              <select
                id="task-category"
                className="form-select"
                value={form.category}
                onChange={(e) => field('category', e.target.value)}
              >
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </div>

          {/* Row: Due date + Time */}
          <div className="grid grid-2" style={{ gap: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="task-due">Due Date</label>
              <input
                id="task-due"
                type="date"
                className="form-input"
                value={form.due_date}
                min={todayString()}
                onChange={(e) => field('due_date', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="task-time">Due Time</label>
              <input
                id="task-time"
                type="time"
                className="form-input"
                value={form.due_time}
                onChange={(e) => field('due_time', e.target.value)}
              />
            </div>
          </div>

          {/* Row: Duration + Status */}
          <div className="grid grid-2" style={{ gap: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="task-duration">Est. Duration (min)</label>
              <input
                id="task-duration"
                type="number"
                className="form-input"
                value={form.estimated_duration}
                min={1}
                max={1440}
                onChange={(e) => field('estimated_duration', e.target.value)}
                placeholder="e.g. 60"
              />
              {errors.estimated_duration && <div className="form-error">{errors.estimated_duration}</div>}
            </div>
            {isEdit && (
              <div className="form-group">
                <label className="form-label" htmlFor="task-status">Status</label>
                <select
                  id="task-status"
                  className="form-select"
                  value={form.status}
                  onChange={(e) => field('status', e.target.value)}
                >
                  {Object.entries(STATUS_LABELS).map(([v, l]) => (
                    <option key={v} value={v}>{l}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Tags */}
          <div className="form-group" style={{ marginBottom: 'var(--space-6)' }}>
            <label className="form-label" htmlFor="task-tags">Tags</label>
            <input
              id="task-tags"
              type="text"
              className="form-input"
              value={form.tags}
              onChange={(e) => field('tags', e.target.value)}
              placeholder="e.g. study,exam,project (comma separated)"
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end">
            <button type="button" className="btn btn-secondary" onClick={onCancel}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? <Loader2 size={16} className="spinner" /> : null}
              {isEdit ? 'Save Changes' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
