import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001',
  timeout: 30000,
});

export const getEnvironment = (lat, lon) =>
  API.get('/api/environment/live', { params: { lat, lon } });

export const predictCrop = (payload) =>
  API.post('/api/crop/predict', payload);

export const calculateEconomics = (crop, farm_area_hectares) =>
  API.post('/api/economics/calculate', { crop, farm_area_hectares });

export const diagnosePlant = (file) => {
  const form = new FormData();
  form.append('file', file);
  return API.post('/api/disease/diagnose', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  });
};

export const sendChatMessage = (message, session_id, history) =>
  API.post('/api/chat', { message, session_id, history });

export default API;
