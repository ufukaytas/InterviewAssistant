import api from './api';

export const interviewService = {
  // 1. POST /api/v1/interviews
  createSession: async (params) => {
    const response = await api.post('/interviews', params);
    return response.data;
  },

  // 2. POST /api/v1/interviews/{session_id}/start
  startInterview: async (sessionId) => {
    const response = await api.post(`/interviews/${sessionId}/start`);
    return response.data;
  },

  // 3. GET /api/v1/interviews/{session_id}/current-question
  getCurrentQuestion: async (sessionId) => {
    const response = await api.get(`/interviews/${sessionId}/current-question`);
    return response.data;
  },

  // 4. POST /api/v1/interviews/{session_id}/questions/{question_id}/start
  startQuestionTimer: async (sessionId, questionId) => {
    const response = await api.post(`/interviews/${sessionId}/questions/${questionId}/start`);
    return response.data;
  },

  // 5. POST /api/v1/interviews/{session_id}/questions/{question_id}/answer
  submitAnswer: async (sessionId, questionId, answerData) => {
    const response = await api.post(`/interviews/${sessionId}/questions/${questionId}/answer`, answerData);
    return response.data;
  },

  // 6. POST /api/v1/interviews/{session_id}/questions/{question_id}/skip
  skipQuestion: async (sessionId, questionId) => {
    const response = await api.post(`/interviews/${sessionId}/questions/${questionId}/skip`);
    return response.data;
  },

  // 7. DELETE /api/v1/interviews/{session_id}
  abandonInterview: async (sessionId) => {
    const response = await api.delete(`/interviews/${sessionId}`);
    return response.data;
  },

  // 8. POST /api/v1/interviews/{session_id}/complete
  completeInterview: async (sessionId) => {
    const response = await api.post(`/interviews/${sessionId}/complete`);
    return response.data;
  },

  // 9. GET /api/v1/interviews
  getPastInterviews: async () => {
    const response = await api.get('/interviews');
    return response.data;
  },

  // 10. GET /api/v1/interviews/{session_id}/feedback
  getFeedback: async (sessionId) => {
    const response = await api.get(`/interviews/${sessionId}/feedback`);
    return response.data;
  }
};