const API_BASE_URL = 'http://localhost:8000';

const request = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: `Request failed with status ${response.status}` }));
      throw new Error(errorData.detail || 'API request failed');
    }
    const text = await response.text();
    return text ? JSON.parse(text) : {};
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
};

export const getStats = () => request('/dashboard/stats');
export const getPendingActions = () => request('/actions/pending');
export const getActivityLog = () => request('/activities');
export const getRuns = () => request('/runs');
export const getRunDetails = (runId) => request(`/runs/${runId}`);

export const runOptimization = (dryRun = false) => request('/optimize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ dry_run: dryRun }),
});

export const approveAction = (actionId) => request(`/actions/${actionId}/approve`, { method: 'POST' });
export const rejectAction = (actionId) => request(`/actions/${actionId}/reject`, { method: 'POST' });