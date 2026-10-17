import { useState, useEffect, useCallback, useRef } from 'react';
import { Plus, Edit, Trash2, CheckSquare, AlertCircle } from 'lucide-react';
import { tasksApi } from '../services/api';
import TaskCard from '../components/TaskCard';
import TaskForm from '../components/TaskForm';
import TaskFilters from '../components/TaskFilters';
import ConfirmDialog from '../components/ConfirmDialog';
import EmptyState from '../components/EmptyState';
import { PageLoader } from '../components/LoadingState';

const EMPTY_FILTERS = { search: '', status: '', priority: '', category: '', sort_by: 'created_at' };

export default function Tasks({ onHeaderChange }) {
  const [tasks, setTasks] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [showForm, setShowForm] = useState(false);
  const [editTask, setEditTask] = useState(null);
  const [deleteTask, setDeleteTask] = useState(null);
  const [saving, setSaving] = useState(false);
  const debounceRef = useRef(null);

  useEffect(() => {
    onHeaderChange?.('My Tasks');
  }, [onHeaderChange]);


  const load = useCallback(async (customFilters) => {
    const f = customFilters || filters;
    setLoading(true);
    try {
      setError(null);
      const params = {
        search: f.search || undefined,
        status: f.status || undefined,
        priority: f.priority || undefined,
        category: f.category || undefined,
        sort_by: f.sort_by || 'created_at',
        sort_dir: f.sort_by === 'title' ? 'asc' : 'desc',
        per_page: 100,
      };
      const data = await tasksApi.list(params);
      setTasks(data.tasks);
      setTotal(data.total);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);


  useEffect(() => {
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => load(filters), filters.search ? 400 : 0);
  }, [filters, load]);

  const handleToggle = async (task) => {
    try {
      if (task.status === 'completed') await tasksApi.reopen(task.id);
      else await tasksApi.complete(task.id);
      load(filters);
    } catch (e) { console.error(e); }
  };

  const handleSave = async (data) => {
    setSaving(true);
    try {
      if (editTask) await tasksApi.update(editTask.id, data);
      else await tasksApi.create(data);
      setShowForm(false);
      setEditTask(null);
      load(filters);
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    if (!deleteTask) return;
    try {
      await tasksApi.delete(deleteTask.id);
      setDeleteTask(null);
      load(filters);
    } catch (e) { console.error(e); }
  };

  const pendingTasks = tasks.filter((t) => t.status !== 'completed');
  const completedTasks = tasks.filter((t) => t.status === 'completed');
  const showCompleted = !filters.status || filters.status === 'completed';

  return (
    <div style={{ maxWidth: 'var(--content-max)', margin: '0 auto' }}>
      {/* Toolbar */}
      <div style={{ marginBottom: 'var(--space-6)' }}>
        <div className="flex items-center justify-between" style={{ marginBottom: 'var(--space-4)' }}>
          <div>
            <span style={{ fontSize: 'var(--text-sm)', color: 'var(--clr-ink-3)' }}>
              {total} task{total !== 1 ? 's' : ''}
            </span>
          </div>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => { setEditTask(null); setShowForm(true); }}
            id="new-task-btn"
          >
            <Plus size={16} />
            New Task
          </button>
        </div>
        <TaskFilters
          filters={filters}
          onChange={setFilters}
          onClear={() => setFilters(EMPTY_FILTERS)}
        />
      </div>

      {/* Error */}
      {error && (
        <div className="alert alert-danger" style={{ marginBottom: 'var(--space-4)' }}>
          <AlertCircle size={16} />
          <span>{error}</span>
          <button className="btn btn-secondary btn-sm" onClick={() => load(filters)} style={{ marginLeft: 'auto' }}>
            Retry
          </button>
        </div>
      )}

      {loading && <PageLoader />}

      {!loading && !error && (
        <>
          {/* Pending tasks */}
          {pendingTasks.length === 0 && completedTasks.length === 0 && (
            <EmptyState
              icon={CheckSquare}
              title="No tasks found"
              description={
                Object.values(filters).some(Boolean)
                  ? "No tasks match your current filters. Try clearing them."
                  : "You have no tasks yet. Create one to get started!"
              }
              action={
                <button className="btn btn-primary" onClick={() => setShowForm(true)}>
                  <Plus size={16} />
                  Create task
                </button>
              }
            />
          )}

          {pendingTasks.length > 0 && (
            <div style={{ marginBottom: 'var(--space-6)' }}>
              <div style={{
                fontSize: 'var(--text-xs)',
                fontWeight: 'var(--weight-semibold)',
                color: 'var(--clr-ink-4)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                marginBottom: 'var(--space-3)',
              }}>
                Pending — {pendingTasks.length}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                {pendingTasks.map((t) => (
                  <TaskRow
                    key={t.id}
                    task={t}
                    onToggle={handleToggle}
                    onEdit={() => { setEditTask(t); setShowForm(true); }}
                    onDelete={() => setDeleteTask(t)}
                    onClick={() => { setEditTask(t); setShowForm(true); }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Completed tasks */}
          {completedTasks.length > 0 && showCompleted && (
            <div>
              <div style={{
                fontSize: 'var(--text-xs)',
                fontWeight: 'var(--weight-semibold)',
                color: 'var(--clr-ink-4)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                marginBottom: 'var(--space-3)',
              }}>
                Completed — {completedTasks.length}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                {completedTasks.map((t) => (
                  <TaskRow
                    key={t.id}
                    task={t}
                    onToggle={handleToggle}
                    onEdit={() => { setEditTask(t); setShowForm(true); }}
                    onDelete={() => setDeleteTask(t)}
                    onClick={() => { setEditTask(t); setShowForm(true); }}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Task Form Modal */}
      {showForm && (
        <TaskForm
          task={editTask}
          onSave={handleSave}
          onCancel={() => { setShowForm(false); setEditTask(null); }}
          loading={saving}
        />
      )}

      {/* Delete Confirm */}
      {deleteTask && (
        <ConfirmDialog
          title="Delete Task"
          message={`Are you sure you want to delete "${deleteTask.title}"? This action cannot be undone.`}
          onConfirm={handleDelete}
          onCancel={() => setDeleteTask(null)}
          confirmLabel="Delete"
          danger
        />
      )}
    </div>
  );
}

function TaskRow({ task, onToggle, onEdit, onDelete, onClick }) {
  return (
    <div style={{ position: 'relative' }}>
      <TaskCard
        task={task}
        onToggleComplete={onToggle}
        onClick={onClick}
      />
      {/* Actions overlay */}
      <div style={{
        position: 'absolute',
        right: 'var(--space-3)',
        top: '50%',
        transform: 'translateY(-50%)',
        display: 'flex',
        gap: 'var(--space-1)',
        opacity: 0,
        transition: 'opacity var(--transition-fast)',
      }}
        className="task-actions"
      >
        <button
          className="btn btn-ghost btn-icon btn-sm"
          onClick={(e) => { e.stopPropagation(); onEdit(); }}
          aria-label={`Edit ${task.title}`}
          title="Edit"
        >
          <Edit size={14} />
        </button>
        <button
          className="btn btn-ghost btn-icon btn-sm"
          onClick={(e) => { e.stopPropagation(); onDelete(); }}
          aria-label={`Delete ${task.title}`}
          title="Delete"
          style={{ color: 'var(--clr-danger)' }}
        >
          <Trash2 size={14} />
        </button>
      </div>

      <style>{`
        .task-card:hover .task-actions { opacity: 1 !important; }
      `}</style>
    </div>
  );
}
