import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // FastAPI backend URL
});

export const getChatResponse = async (query) => {
  const response = await apiClient.post('/chat', { query });
  return response.data;
};

