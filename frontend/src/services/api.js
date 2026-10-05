/**
 * API Service for ResumeForge AI
 * Communicates with FastAPI backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 45000,
  headers: {
    'Accept': 'application/json',
  },
});

export const checkHealth = async () => {
  const response = await client.get('/health');
  return response.data;
};

export const getModelInfo = async () => {
  const response = await client.get('/model-info');
  return response.data;
};

export const predictResumeText = async (resumeText) => {
  const response = await client.post('/predict', {
    resume_text: resumeText,
  });
  return response.data;
};

export const predictResumeFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await client.post('/predict/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getAnalytics = async () => {
  const response = await client.get('/analytics');
  return response.data;
};

export const getMetrics = async () => {
  const response = await client.get('/metrics');
  return response.data;
};

export const getCategories = async () => {
  const response = await client.get('/categories');
  return response.data;
};

export const getCategoryFeatures = async (category) => {
  const response = await client.get(`/features/${encodeURIComponent(category)}`);
  return response.data;
};

export default {
  checkHealth,
  getModelInfo,
  predictResumeText,
  predictResumeFile,
  getAnalytics,
  getMetrics,
  getCategories,
  getCategoryFeatures,
};
