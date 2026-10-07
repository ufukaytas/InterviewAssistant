const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const cvService = {
  // 1. GET /api/v1/cvs/latest (Son CV Özetini Getirme)
  getLatestCV: async () => {
    const response = await api.get('/cvs/latest');
    return response.data;
  }
};