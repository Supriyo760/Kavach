import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchDashboardData = async () => {
  const response = await api.get('/dashboard');
  return response.data;
};

export const fetchHistoryData = async () => {
  const response = await api.get('/history');
  return response.data;
};

export const fetchRiskEvents = async () => {
  const response = await api.get('/risk-events');
  return response.data;
};

export const startReplay = async () => {
  const response = await api.post('/replay/start');
  return response.data;
};

export const stopReplay = async () => {
  const response = await api.post('/replay/stop');
  return response.data;
};

export const stepReplay = async () => {
  const response = await api.post('/replay/step');
  return response.data;
};

export const getReplayStatus = async () => {
  const response = await api.get('/replay');
  return response.data;
};
