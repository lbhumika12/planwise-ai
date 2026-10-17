import { Search, X } from 'lucide-react';
import { PRIORITIES, CATEGORIES, STATUS_LABELS } from '../utils/helpers';


export default function TaskFilters({ filters, onChange, onClear }) {
  const hasFilters = Object.values(filters).some((v) => v && v !== '');

  const set = (key, value) => onChange({ ...filters, [key]: value });

  return (
    <div style={{
      display: 'flex',
      gap: 'var(--space-3)',
      flexWrap: 'wrap',
      alignItems: 'center',
    }}>
      {/* Search */}
      <div style={{ position: 'relative', flex: '1 1 200px', minWidth: 180 }}>
        <Search
          size={15}
          style={{
            position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)',
            color: 'var(--clr-ink-4)', pointerEvents: 'none',
          }}
        />
        <input
          type="search"
          className="form-input"
          value={filters.search || ''}
          onChange={(e) => set('search', e.target.value)}
          placeholder="Search tasks…"
          style={{ paddingLeft: 34 }}
          aria-label="Search tasks"
          id="task-search"
        />
      </div>

      {/* Status filter */}
      <select
        className="form-select"
        value={filters.status || ''}
        onChange={(e) => set('status', e.target.value)}
        style={{ minWidth: 120 }}
        aria-label="Filter by status"
        id="status-filter"
      >
        <option value="">All statuses</option>
        {Object.entries(STATUS_LABELS).map(([v, l]) => (
          <option key={v} value={v}>{l}</option>
        ))}
      </select>

      {/* Priority filter */}
      <select
        className="form-select"
        value={filters.priority || ''}
        onChange={(e) => set('priority', e.target.value)}
        style={{ minWidth: 120 }}
        aria-label="Filter by priority"
        id="priority-filter"
      >
        <option value="">All priorities</option>
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
        ))}
      </select>

      {/* Category filter */}
      <select
        className="form-select"
        value={filters.category || ''}
        onChange={(e) => set('category', e.target.value)}
        style={{ minWidth: 120 }}
        aria-label="Filter by category"
        id="category-filter"
      >
        <option value="">All categories</option>
        {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
      </select>

      {/* Sort */}
      <select
        className="form-select"
        value={filters.sort_by || 'created_at'}
        onChange={(e) => set('sort_by', e.target.value)}
        style={{ minWidth: 130 }}
        aria-label="Sort by"
        id="sort-select"
      >
        <option value="created_at">Newest first</option>
        <option value="due_date">Due date</option>
        <option value="priority">Priority</option>
        <option value="title">A–Z</option>
      </select>

      {/* Clear filters */}
      {hasFilters && (
        <button
          className="btn btn-ghost btn-sm"
          onClick={onClear}
          aria-label="Clear all filters"
        >
          <X size={14} />
          Clear
        </button>
      )}
    </div>
  );
}
