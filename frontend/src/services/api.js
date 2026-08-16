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

export default api;
