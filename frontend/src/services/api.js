import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/';

const api = axios.create({
  baseURL: API_BASE,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE}auth/refresh/`, {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', response.data.access);
          api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
          return api(originalRequest);
        } catch (err) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (username, password) =>
    axios.post(`${API_BASE}auth/login/`, { username, password }),
  refresh: (refresh) =>
    axios.post(`${API_BASE}auth/refresh/`, { refresh }),
};

export const accountsAPI = {
  register: (data) => axios.post(`${API_BASE}accounts/register/`, data),
  getMe: () => api.get('accounts/me/'),
  updateMe: (data) => api.put('accounts/me/', data),
  deleteMe: () => api.delete('accounts/me/'),
  changePassword: (data) => api.post('accounts/password/change/', data),
};

export const workersAPI = {
  list: () => api.get('workers/'),
  get: (id) => api.get(`workers/${id}/`),
  create: (data) => api.post('workers/', data),
  update: (id, data) => api.put(`workers/${id}/`, data),
  delete: (id) => api.delete(`workers/${id}/`),
  getServices: (id) => api.get(`workers/${id}/services/`),
  getReviews: (id) => api.get(`workers/${id}/reviews/`),
};

export const servicesAPI = {
  list: () => api.get('services/'),
  get: (id) => api.get(`services/${id}/`),
  getWorkers: (id) => api.get(`services/${id}/workers/`),
};

export const reviewsAPI = {
  create: (data) => api.post('reviews/', data),
  get: (id) => api.get(`reviews/${id}/`),
  update: (id, data) => api.put(`reviews/${id}/`, data),
  delete: (id) => api.delete(`reviews/${id}/`),
};

export const searchAPI = {
  search: (params) => api.get('search/', { params }),
};

export default api;