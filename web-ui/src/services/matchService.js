// API_URL şimdilik durabilir, ileride kullanacağız
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3010'; 

export const matchService = {
  // 1. CV Yükleme ve İlan Eşleştirme (Mock)
  analyzeMatch: async (cvFile, jobText) => {
    // Gerçek bir API isteği gibi 1.5 saniye bekleme süresi (Loading ekranını test etmek için)
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // API Gateway hazır olana kadar dönecek sahte başarılı cevap
    return {
      status: "success",
      match_id: "m_1001",
      score: 85,
      analysis: {
        matched_skills: ["React", "JavaScript", "Docker", "Git"],
        missing_skills: ["Kubernetes", "CI/CD"],
        recommendation: "Aday bu pozisyon için güçlü bir eşleşme sağlıyor. CI/CD konularında pratik yapması önerilir."
      }
    };
  },

  // 2. Geçmiş Analiz Raporlarını Listeleme (Mock)
  getMatchHistory: async () => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return [
      { id: "m_1001", jobTitle: "Frontend Developer", score: 85, date: "2026-09-26" },
      { id: "m_0954", jobTitle: "React Native Developer", score: 62, date: "2026-09-20" },
      { id: "m_0890", jobTitle: "UI/UX Designer", score: 45, date: "2026-09-15" }
    ];
  },

  // 3. Seçilen Analizin Detayı (Mock)
  getMatchDetail: async (matchId) => {
    await new Promise(resolve => setTimeout(resolve, 800));
    return {
      id: matchId,
      jobTitle: "Frontend Developer",
      score: 85,
      date: "2026-09-26",
      details: "Bu analiz mock verisidir. Gerçek API Gateway bağlandığında detaylar buraya gelecektir."
    };
  }
};