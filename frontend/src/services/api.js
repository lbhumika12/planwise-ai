/**
 * PlanWise AI - API Service
 * Central HTTP client for all backend communication.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

async function request(method, path, body = null, params = null) {
  let url = `${API_BASE}${path}`;
  if (params) {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== null && v !== undefined)
    ).toString();
    if (qs) url += `?${qs}`;
  }

  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body !== null) {
    options.body = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(url, options);
  } catch (err) {
    throw new ApiError('Cannot reach backend. Is the server running?', 0, err.message);
  }

  if (res.status === 204) return null;

  let data;
  try {
    data = await res.json();
  } catch {
    throw new ApiError(`Server returned non-JSON response (${res.status})`, res.status, null);
  }

  if (!res.ok) {
    const detail = data?.detail || data?.message || `HTTP ${res.status}`;
    throw new ApiError(
      typeof detail === 'string' ? detail : JSON.stringify(detail),
      res.status,
      data
    );
  }

  return data;
}

// ─── Tasks API ────────────────────────────────────────
export const tasksApi = {
  list: (params = {}) => request('GET', '/tasks', null, params),
  get: (id) => request('GET', `/tasks/${id}`),
  create: (data) => request('POST', '/tasks', data),
  update: (id, data) => request('PATCH', `/tasks/${id}`, data),
  complete: (id) => request('PATCH', `/tasks/${id}/complete`),
  reopen: (id) => request('PATCH', `/tasks/${id}/reopen`),
  delete: (id) => request('DELETE', `/tasks/${id}`),
  dashboard: (timezone = 'Asia/Kolkata') =>
    request('GET', '/tasks/dashboard', null, { timezone }),
  seedDemo: (timezone = 'Asia/Kolkata') =>
    request('POST', '/tasks/demo/seed', null, { timezone }),
  clearDemo: () => request('DELETE', '/tasks/demo/clear'),
};

// ─── Assistant API ────────────────────────────────────
export const assistantApi = {
  chat: (message, history = [], timezone = 'Asia/Kolkata') =>
    request('POST', '/assistant/chat', { message, history, timezone }),
  status: () => request('GET', '/assistant/status'),
};

// ─── Schedule API ─────────────────────────────────────
export const scheduleApi = {
  plan: (data) => request('POST', '/schedule/plan', data),
  apply: (data) => request('POST', '/schedule/apply', data),
};

// ─── Settings API ─────────────────────────────────────
export const settingsApi = {
  get: () => request('GET', '/settings'),
  update: (data) => request('PATCH', '/settings', data),
  aiStatus: () => request('GET', '/settings/ai-status'),
};

// ─── Health ───────────────────────────────────────────
export const healthApi = {
  check: () => request('GET', '/health'),
};

export { ApiError };
