import api from './api';

export const cvService = {
  // 1. GET /api/v1/cvs/latest (Son CV Özetini Getirme)
  getLatestCV: async () => {
    const response = await api.get('/cvs/latest');
    return response.data;
  }
};