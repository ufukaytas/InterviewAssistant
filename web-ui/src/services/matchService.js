const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3010';

export const matchService = {
  analyzeMatch: async (cvFile, jobText) => {
    const formData = new FormData();
    formData.append('cv_file', cvFile); 
    formData.append('job_text', jobText);

    const token = localStorage.getItem('accessToken'); 

    const response = await fetch(`${API_URL}/api/v1/matches/analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP hatası! Durum: ${response.status}`);
    }

    return await response.json();
  },

  // 2. GET /api/v1/matches/history 
  getMatchHistory: async () => {
    const response = await fetch(`${API_URL}/api/v1/matches/history`);
    
    if (!response.ok) throw new Error("Geçmiş verisi alınamadı");
    return await response.json();
  },

  // 3. GET /api/v1/matches/{match_id} 
  getMatchDetail: async (matchId) => {
    const response = await fetch(`${API_URL}/api/v1/matches/${matchId}`);
    
    if (!response.ok) throw new Error("Detay verisi alınamadı");
    return await response.json();
  }
};