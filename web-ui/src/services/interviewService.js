// src/services/interviewService.js

// Backend hazır olana kadar sahte (mock) bekleme süresi
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const interviewService = {
  // 1. POST /api/v1/interviews
  // Mülakat oturumu oluşturur
  createSession: async (params) => {
    console.log("Mülakat oturumu oluşturuluyor (Mock):", params);
    await delay(1000);
    return { 
      success: true, 
      session_id: "mock_session_98765", 
      total_questions: params.questionCount || 5 
    };
  },

  // 2. POST /api/v1/interviews/{session_id}/start
  // Genel mülakat sayacını ve oturumu başlatır
  startInterview: async (sessionId) => {
    console.log(`Mülakat başlatıldı (Mock) - Session: ${sessionId}`);
    await delay(500);
    return { success: true, status: "in_progress" };
  },

  // 3. GET /api/v1/interviews/{session_id}/current-question
  // Sayfa yenilenmesinde veya kopmalarda sıradaki soruyu ve kalan süreyi getirir
  getCurrentQuestion: async (sessionId) => {
    console.log(`Geçerli soru getiriliyor (Mock) - Session: ${sessionId}`);
    await delay(500);
    return { 
      success: true, 
      question_id: "q_101", 
      text: "CV'nizde Python kullandığınızı belirttiniz. Asenkron görev kuyrukları hakkında tecrübeniz nedir?", 
      remaining_sec: 110 
    };
  },

  // 4. POST /api/v1/interviews/{session_id}/questions/{question_id}/start
  // Ekrana gelen sorunun süresini sunucuda başlatır
  startQuestionTimer: async (sessionId, questionId) => {
    console.log(`Soru süresi başlatıldı (Mock) - Soru: ${questionId}`);
    await delay(300);
    return { success: true };
  },

  // 5. POST /api/v1/interviews/{session_id}/questions/{question_id}/answer
  // Cevabı gönderir ve sıradaki soruyu (next_question) döner
  submitAnswer: async (sessionId, questionId, answerData) => {
    console.log(`Cevap iletildi (Mock) - Soru: ${questionId}`, answerData);
    await delay(1000);
    return { 
      success: true, 
      next_question: {
        question_id: `q_${Math.floor(Math.random() * 1000)}`,
        text: "Sıradaki soru: CI/CD süreçlerinde Docker imajlarını nasıl yönetirsiniz?"
      }
    };
  },

  // 6. POST /api/v1/interviews/{session_id}/questions/{question_id}/skip
  // Soruyu pas geçer
  skipQuestion: async (sessionId, questionId) => {
    console.log(`Soru pas geçildi (Mock) - Soru: ${questionId}`);
    await delay(600);
    return { 
      success: true, 
      next_question: {
        question_id: `q_${Math.floor(Math.random() * 1000)}`,
        text: "Sıradaki soru: SOLID prensiplerinden bir örnek verebilir misiniz?"
      }
    };
  },

  // 7. DELETE /api/v1/interviews/{session_id}
  // Mülakatı yarıda bırakıp çıkar
  abandonInterview: async (sessionId) => {
    console.log(`Mülakat terk edildi (Mock) - Session: ${sessionId}`);
    await delay(500);
    return { success: true, status: "abandoned" };
  },

  // 8. POST /api/v1/interviews/{session_id}/complete
  // Mülakatı bitirir, analiz raporunu üretir
  completeInterview: async (sessionId) => {
    console.log(`Mülakat tamamlandı, rapor üretiliyor (Mock) - Session: ${sessionId}`);
    await delay(2000); // Rapor üretimi biraz uzun sürer
    return { 
      success: true, 
      report: {
        score: 76,
        time_spent: "06:45",
        answered: 4,
        skipped: 1,
        positives: ["RabbitMQ mimarisi doğru açıklandı."],
        negatives: ["Docker volüm komutları eksikti."]
      }
    };
  },

  // 9. GET /api/v1/interviews
  // Geçmiş mülakatların listesini getirir
  getPastInterviews: async () => {
    console.log("Geçmiş mülakatlar listeleniyor (Mock)...");
    await delay(800);
    return {
      success: true,
      data: [
        { session_id: "sess_1", title: "Backend Developer", date: "12 Eylül 2026", score: 76 },
        { session_id: "sess_2", title: "Veri Analisti", date: "05 Ağustos 2026", score: 62 }
      ]
    };
  },

  // 10. GET /api/v1/interviews/{session_id}/feedback
  // Belirli bir mülakatın detaylı raporunu getirir
  getFeedback: async (sessionId) => {
    console.log(`Geçmiş rapor getiriliyor (Mock) - Session: ${sessionId}`);
    await delay(800);
    return { success: true, report: { score: 76, positives: [], negatives: [] } }; // Detaylı data
  }
};