const API_URL = process.env.REACT_APP_BACKEND_URL;

async function fetchApi(endpoint, options = {}) {
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  return res.json();
}

export const api = {
  getHealth: () => fetchApi('/api/health'),
  getLessons: () => fetchApi('/api/lessons'),
  getLesson: (id) => fetchApi(`/api/lessons/${id}`),
  getTheory: () => fetchApi('/api/theory'),
  getTheoryTopic: (id) => fetchApi(`/api/theory/${id}`),
  getSheetMusic: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return fetchApi(`/api/sheet-music${q ? `?${q}` : ''}`);
  },
  getSheetMusicPiece: (id) => fetchApi(`/api/sheet-music/${id}`),
  getCareGuides: () => fetchApi('/api/care-guides'),
  getCareGuide: (id) => fetchApi(`/api/care-guides/${id}`),
  getPracticeLogs: () => fetchApi('/api/practice-logs'),
  createPracticeLog: (data) => fetchApi('/api/practice-logs', { method: 'POST', body: JSON.stringify(data) }),
  deletePracticeLog: (id) => fetchApi(`/api/practice-logs/${id}`, { method: 'DELETE' }),
  getProgress: () => fetchApi('/api/progress'),
  updateProgress: (data) => fetchApi('/api/progress', { method: 'POST', body: JSON.stringify(data) }),
  getBookmarks: () => fetchApi('/api/bookmarks'),
  addBookmark: (data) => fetchApi('/api/bookmarks', { method: 'POST', body: JSON.stringify(data) }),
  removeBookmark: (id) => fetchApi(`/api/bookmarks/${id}`, { method: 'DELETE' }),
  getSchedule: () => fetchApi('/api/schedule'),
  createSchedule: (data) => fetchApi('/api/schedule', { method: 'POST', body: JSON.stringify(data) }),
  deleteSchedule: (id) => fetchApi(`/api/schedule/${id}`, { method: 'DELETE' }),
  getStats: () => fetchApi('/api/stats'),
};
