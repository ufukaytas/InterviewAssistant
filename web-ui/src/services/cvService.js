const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3010';

export const cvService = {
  // 1. Son CV Özetini Getirme (Mock)
  getLatestCV: async () => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return {
      user_id: "u_123",
      last_updated: "2026-09-25",
      summary: "Bilgisayar Mühendisliği 4. sınıf öğrencisi. React ve modern web teknolojileri üzerine deneyimli.",
      skills: ["React", "JavaScript", "Python", "Docker", "Git", "C#"],
      experience_years: 1
    };
  }
};