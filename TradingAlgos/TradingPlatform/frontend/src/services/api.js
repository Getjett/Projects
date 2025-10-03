import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Services
export const authApi = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  refreshToken: () => api.post('/auth/refresh'),
};

export const dashboardApi = {
  getDashboardData: () => api.get('/dashboard'),
  getHealth: () => api.get('/health'),
};

export const strategiesApi = {
  getStrategies: () => api.get('/strategies'),
  createStrategy: (strategy) => api.post('/strategies', strategy),
  updateStrategy: (id, strategy) => api.put(`/strategies/${id}`, strategy),
  deleteStrategy: (id) => api.delete(`/strategies/${id}`),
  getStrategy: (id) => api.get(`/strategies/${id}`),
  cloneStrategy: (id) => api.post(`/strategies/${id}/clone`),
};

export const backtestApi = {
  runBacktest: (config) => api.post('/backtest/run', config),
  getBacktests: () => api.get('/backtest'),
  getBacktest: (id) => api.get(`/backtest/${id}`),
  deleteBacktest: (id) => api.delete(`/backtest/${id}`),
  getBacktestResults: (id) => api.get(`/backtest/${id}/results`),
  compareBacktests: (ids) => api.post('/backtest/compare', { backtest_ids: ids }),
};

export const mlApi = {
  getModels: () => api.get('/ml/models'),
  createModel: (model) => api.post('/ml/models', model),
  trainModel: (id, config) => api.post(`/ml/models/${id}/train`, config),
  predict: (id, data = {}) => api.post(`/ml/models/${id}/predict`, data),
  deleteModel: (id) => api.delete(`/ml/models/${id}`),
  getFeatureImportance: (id) => api.get(`/ml/feature-importance/${id}`),
  getModelMetrics: (id) => api.get(`/ml/models/${id}/metrics`),
  optimizeModel: (id, config) => api.post(`/ml/models/${id}/optimize`, config),
};

export const dataApi = {
  getSymbols: () => api.get('/data/symbols'),
  getHistoricalData: (symbol, timeframe, days) => 
    api.get(`/data/historical/${symbol}`, { 
      params: { timeframe, days } 
    }),
  getRealtimeData: (symbol) => api.get(`/data/realtime/${symbol}`),
  getIndicators: (symbol, timeframe, indicators) =>
    api.post('/data/indicators', { symbol, timeframe, indicators }),
  downloadData: (symbol, timeframe, startDate, endDate) =>
    api.get('/data/download', {
      params: { symbol, timeframe, start_date: startDate, end_date: endDate },
      responseType: 'blob',
    }),
};

export const portfolioApi = {
  getPortfolios: () => api.get('/portfolio'),
  createPortfolio: (portfolio) => api.post('/portfolio', portfolio),
  updatePortfolio: (id, portfolio) => api.put(`/portfolio/${id}`, portfolio),
  deletePortfolio: (id) => api.delete(`/portfolio/${id}`),
  getPortfolioPerformance: (id) => api.get(`/portfolio/${id}/performance`),
  optimizePortfolio: (id, config) => api.post(`/portfolio/${id}/optimize`, config),
};

export const alertsApi = {
  getAlerts: () => api.get('/alerts'),
  createAlert: (alert) => api.post('/alerts', alert),
  updateAlert: (id, alert) => api.put(`/alerts/${id}`, alert),
  deleteAlert: (id) => api.delete(`/alerts/${id}`),
  markAsRead: (id) => api.patch(`/alerts/${id}/read`),
};

export const settingsApi = {
  getSettings: () => api.get('/settings'),
  updateSettings: (settings) => api.put('/settings', settings),
  getApiKeys: () => api.get('/settings/api-keys'),
  updateApiKeys: (keys) => api.put('/settings/api-keys', keys),
  testConnection: () => api.post('/settings/test-connection'),
};

export default api;