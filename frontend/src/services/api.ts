import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true,
})

export const authApi = {
  status: () => api.get<{ authenticated: boolean }>('/auth/status'),
  login: () => {
    window.location.href = `${api.defaults.baseURL}/auth/login`
  },
  logout: () => api.post('/auth/logout'),
}

export const dashboardApi = {
  getKPIs: () => api.get('/api/dashboard/kpis'),
  getStages: () => api.get('/api/dashboard/stages'),
  getPipeline: (months = 12) =>
    api.get('/api/dashboard/pipeline', { params: { months } }),
}

export const opportunityApi = {
  list: (params: Record<string, unknown>) =>
    api.get('/api/opportunities', { params }),
}

export default api
