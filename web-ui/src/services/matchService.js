// API_URL şimdilik durabilir, ileride kullanacağız
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'; 

export const matchService = {
  // 1. POST /api/v1/matches/analyze 
  analyzeMatch: async (cvFile, jobText) => {
    const formData = new FormData();
    formData.append('cv', cvFile); 
    formData.append('jobText', jobText);

    const response = await api.post('/matches/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  // 2. GET /api/v1/matches/history 
  getMatchHistory: async () => {
    const response = await api.get('/matches/history');
    return response.data;
  },

  // 3. GET /api/v1/matches/{match_id} 
  getMatchDetail: async (matchId) => {
    const response = await api.get(`/matches/${matchId}`);
    return response.data;
  }
};