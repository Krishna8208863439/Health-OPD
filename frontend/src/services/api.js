import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 20000,
});

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// --- ML Predictions ---
export const predictDiabetes = async (payload) => {
  const response = await api.post('/predict/diabetes', payload);
  return response.data;
};

export const predictHeart = async (payload) => {
  const response = await api.post('/predict/heart', payload);
  return response.data;
};

export const getDashboardSummary = async () => {
  const response = await api.get('/dashboard');
  return response.data;
};

export const getPredictions = async (params = {}) => {
  const response = await api.get('/predictions', { params });
  return response.data;
};

export const getPredictionById = async (id) => {
  const response = await api.get(`/predictions/${id}`);
  return response.data;
};

export const deletePrediction = async (id) => {
  const response = await api.delete(`/predictions/${id}`);
  return response.data;
};

export const getModelMetrics = async (disease = '') => {
  const response = await api.get('/model-metrics', { params: { disease } });
  return response.data;
};

export const getFeatureImportance = async (disease) => {
  const response = await api.get(`/feature-importance/${disease}`);
  return response.data;
};

export const getReportDownloadUrl = (id) => {
  const baseUrl = API_BASE_URL.startsWith('http') 
    ? API_BASE_URL 
    : `${window.location.origin}${API_BASE_URL}`;
  return `${baseUrl}/report/${id}`;
};

// --- HealthCare+ Unified Services ---
export const getHospitals = async (params = {}) => {
  const response = await api.get('/hospitals', { params });
  return response.data;
};

export const getVitals = async () => {
  const response = await api.get('/vitals');
  return response.data;
};

export const logVitals = async (payload) => {
  const response = await api.post('/vitals', payload);
  return response.data;
};

export const getMedicines = async () => {
  const response = await api.get('/medicines');
  return response.data;
};

export const addMedicine = async (payload) => {
  const response = await api.post('/medicines', payload);
  return response.data;
};

export const updateMedicine = async (payload) => {
  const response = await api.put('/medicines', payload);
  return response.data;
};

export const deleteMedicine = async (id) => {
  const response = await api.delete('/medicines', { params: { id } });
  return response.data;
};

export const sendChatMessage = async (message) => {
  const response = await api.post('/chat', { message });
  return response.data;
};

export const getOPDTickets = async () => {
  const response = await api.get('/opd/tickets');
  return response.data;
};

export const createOPDTicket = async (payload) => {
  const response = await api.post('/opd/tickets', payload);
  return response.data;
};

export const getDietPlans = async () => {
  const response = await api.get('/diet/plans');
  return response.data;
};

export const triggerSOS = async (coords = {}) => {
  const response = await api.post('/sos/trigger', coords);
  return response.data;
};

// --- User Authentication ---
export const loginUser = async (credentials) => {
  const response = await api.post('/auth/login', credentials);
  return response.data;
};

export const registerUser = async (userData) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

export const forgotPassword = async (email) => {
  const response = await api.post('/auth/forgot-password', { email });
  return response.data;
};

export const resetPassword = async (payload) => {
  const response = await api.post('/auth/reset-password', payload);
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

export default api;
