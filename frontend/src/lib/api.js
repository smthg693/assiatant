/**
 * Debug Dojo API Client
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(endpoint, options = {}, token = null) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, { ...options, headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const errorMsg = data.detail || data.error || `Request failed with status ${res.status}`;
      throw new Error(errorMsg);
    }
    return data;
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  async getHealth() {
    return request('/health');
  },

  async getChallenges(params = {}, token = null) {
    const query = new URLSearchParams();
    if (params.difficulty) query.append('difficulty', params.difficulty);
    if (params.concept) query.append('concept', params.concept);
    if (params.search) query.append('search', params.search);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request(`/api/challenges${qs}`, { method: 'GET' }, token);
  },

  async getChallenge(challengeId, token = null) {
    return request(`/api/challenges/${challengeId}`, { method: 'GET' }, token);
  },

  async submitCode(challengeId, code, token) {
    return request(
      '/api/submit',
      {
        method: 'POST',
        body: JSON.stringify({ challenge_id: challengeId, code }),
      },
      token
    );
  },

  async getHint(submissionId, token) {
    return request(
      '/api/hint',
      {
        method: 'POST',
        body: JSON.stringify({ submission_id: submissionId }),
      },
      token
    );
  },

  async getDashboard(token) {
    return request('/api/learner/me/dashboard', { method: 'GET' }, token);
  },

  async getProfile(token) {
    return request('/api/learner/me/profile', { method: 'GET' }, token);
  },
};
