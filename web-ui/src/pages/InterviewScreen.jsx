import { useState, useEffect } from 'react';
import { interviewService } from '../services/interviewService';

export default function InterviewScreen({ matchId, onFinish, onCancel }) {
  const [phase, setPhase] = useState('intro'); 
  const [loading, setLoading] = useState(false);
  
  const [sessionId, setSessionId] = useState(null);
  const [currentQ, setCurrentQ] = useState(1);
  const [totalQ, setTotalQ] = useState(5);
  const [questionId, setQuestionId] = useState(null);
  const [questionText, setQuestionText] = useState('Soru yükleniyor...');
  
  const [timeLeft, setTimeLeft] = useState(120);
  const [answer, setAnswer] = useState('');

  const [isTimeUp, setIsTimeUp] = useState(false);
  const [feedback, setFeedback] = useState({ type: '', text: '' });

  useEffect(() => {
    const initSession = async () => {
      if (!matchId) {
        console.error("Match ID eksik! Mülakat başlatılamaz.");
        setFeedback({ type: 'error', text: 'Geçersiz mülakat ilanı (Match ID eksik).' });
        return;
      }

      try {
        const res = await interviewService.createSession({ 
          job_posting_id: matchId, 
          question_count: 5,
          use_generated_questions: true 
        });
        
        if (res.id) { 
          setSessionId(res.id);
          setTotalQ(res.questions ? res.questions.length : 5); 
        } else {
          console.error("Backend yanıtında id bulunamadı:", res);
        }
      } catch (error) {
        console.error("Oturum oluşturulamadı:", error);
        setFeedback({ type: 'error', text: 'Mülakat oturumu oluşturulurken bir hata meydana geldi.' });
      }
    };
    
    initSession();
  }, [matchId]);

  useEffect(() => {
    let timer;
    if (phase === 'active' && timeLeft > 0 && !loading) {
      timer = setInterval(() => setTimeLeft((prev) => prev - 1), 1000);
    } else if (timeLeft === 0 && phase === 'active' && !loading && !isTimeUp) {
      setIsTimeUp(true);
      setFeedback({ type: 'error', text: 'Süreniz doldu! Yanıt alanı kilitlendi, lütfen sıradaki soruya geçiniz.' });
    }
    return () => clearInterval(timer);
  }, [phase, timeLeft, loading, isTimeUp]);

  const formatTime = (secs) => {
    if (secs < 0) secs = 0;
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `0${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const clearFeedback = () => setFeedback({ type: '', text: '' });

  const handleStart = async () => {
    if (!sessionId) {
      setFeedback({ type: 'error', text: 'Oturum henüz hazırlanıyor, lütfen bekleyin...' });
      return;
    }
    
    setLoading(true);
    clearFeedback();
    try {
      await interviewService.startInterview(sessionId);
      const qRes = await interviewService.getCurrentQuestion(sessionId);
      
      const currentQ = qRes.question;
      
      setQuestionId(currentQ.question_id);
      setQuestionText(currentQ.text);
      setTimeLeft(currentQ.time_limit_seconds || 120); 
      setIsTimeUp(false);
      
      await interviewService.startQuestionTimer(sessionId, currentQ.question_id);
      setPhase('active');
    } catch (error) {
      console.error("Başlatma hatası:", error);
      setFeedback({ type: 'error', text: 'Mülakat başlatılırken bir hata oluştu.' });
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (!answer.trim() && !isTimeUp) {
      setFeedback({ type: 'error', text: 'Lütfen cevabınızı boş bırakmayınız. Boş bırakmak istiyorsanız Pas Geç butonunu kullanınız.' });
      return;
    }
    
    setLoading(true);
    clearFeedback();
    try {
      if (currentQ < totalQ) {
        await interviewService.submitAnswer(sessionId, questionId, { answer_text: answer });
        
        const qRes = await interviewService.getCurrentQuestion(sessionId);
        const nextQ = qRes.question;
        
        setQuestionId(nextQ.question_id);
        setQuestionText(nextQ.text);
        setCurrentQ((prev) => prev + 1);
        setTimeLeft(nextQ.time_limit_seconds || 120);
        setAnswer('');
        setIsTimeUp(false); 
        
        await interviewService.startQuestionTimer(sessionId, nextQ.question_id);
      } else {
        await interviewService.submitAnswer(sessionId, questionId, { answer_text: answer });
        const res = await interviewService.completeInterview(sessionId);
        onFinish(res); 
      }
    } catch (error) {
      console.error("Cevap gönderme hatası:", error);
      setFeedback({ type: 'error', text: 'Cevabınız iletilirken bir hata oluştu (Süre aşımı veya bağlantı sorunu).' });
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = async () => {
    setLoading(true);
    clearFeedback();
    try {
      if (currentQ < totalQ) {
        await interviewService.skipQuestion(sessionId, questionId);
        
        const qRes = await interviewService.getCurrentQuestion(sessionId);
        const nextQ = qRes.question;
        
        setQuestionId(nextQ.question_id);
        setQuestionText(nextQ.text);
        setCurrentQ((prev) => prev + 1);
        setTimeLeft(nextQ.time_limit_seconds || 120);
        setAnswer('');
        setIsTimeUp(false); 
        
        await interviewService.startQuestionTimer(sessionId, nextQ.question_id);
      } else {
        await interviewService.skipQuestion(sessionId, questionId);
        const res = await interviewService.completeInterview(sessionId);
        onFinish(res);
      }
    } catch (error) {
      console.error("Pas geçme hatası:", error);
      setFeedback({ type: 'error', text: 'Soru atlanırken sistemde bir hata oluştu.' });
    } finally {
      setLoading(false);
    }
  };

  const handleAbandon = async () => {
    if (window.confirm("Mülakatı yarıda bırakmak istediğinize emin misiniz? (Oturum iptal edilecek)")) {
      if (sessionId) await interviewService.abandonInterview(sessionId);
      onCancel();
    }
  };

  const renderFeedback = () => {
    if (!feedback.text) return null;
    const isError = feedback.type === 'error';
    return (
      <div style={{
        padding: '10px', marginBottom: '15px', borderRadius: '5px', textAlign: 'center', fontSize: '14px',
        backgroundColor: isError ? '#fee2e2' : '#dcfce3', color: isError ? '#991b1b' : '#166534',
        border: `1px solid ${isError ? '#f87171' : '#86efac'}`
      }}>
        {feedback.text}
      </div>
    );
  };

  return (
    <>
      {phase === 'intro' ? (
        <div className="view active" style={{ alignItems: 'center', justifyContent: 'center', minHeight: '70vh' }}>
          <div className="back-link" onClick={handleAbandon} style={{ alignSelf: 'flex-start', cursor: 'pointer', marginBottom: '20px' }}>
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg> Analiz Ekranına Dön
          </div>
          
          <div className="intro-card">
            <h2>Mülakat Simülasyonu</h2>
            <p>Aday profiline ve iş ilanındaki eksiklerine göre özel olarak oluşturulmuş yapay zeka mülakatına başlamak üzeresin.</p>
            {renderFeedback()}
            <div className="rules-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
              <div className="rule-box"><h4>0{totalQ}</h4><span>Toplam Soru</span></div>
              <div className="rule-box"><h4>02:00</h4><span>Soru Başına Süre</span></div>
            </div>
            
            <button className="btn" style={{ width: '100%', padding: '18px', fontSize: '18px' }} onClick={handleStart} disabled={loading || !sessionId}>
              {loading ? 'Hazırlanıyor...' : (!sessionId ? 'Sorular Üretiliyor...' : 'Simülasyonu Başlat')}
            </button>
          </div>
        </div>
      ) : (
        <div className="view active" style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
          <div className="back-link" onClick={handleAbandon} style={{ cursor: 'pointer', marginBottom: '20px' }}>
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg> Mülakattan Çık
          </div>
          
          <div className="int-header">
            <div className="q-order">
              <span>Soru Sırası</span>
              <h3>0{currentQ} / 0{totalQ}</h3>
            </div>
            <div className="timer-box">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <span className="timer-time" style={{ color: timeLeft <= 30 ? 'var(--danger)' : 'inherit', marginLeft: '8px', fontWeight: 'bold' }}>
                {formatTime(timeLeft)}
              </span>
            </div>
          </div>

          {renderFeedback()}

          <div className="int-question">{questionText}</div>

          <textarea 
            className="int-answer-area" 
            placeholder="Teknik ve detaylı cevabınızı buraya yazınız..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            disabled={loading || isTimeUp}
            style={{ opacity: isTimeUp ? 0.6 : 1, cursor: isTimeUp ? 'not-allowed' : 'text' }}
          ></textarea>

          <div className="int-nav-btns" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
            <button className="btn btn-outline" style={{ borderColor: '#4B5563', padding: '12px 24px' }} onClick={handleSkip} disabled={loading}>
              {loading ? 'İşleniyor...' : 'Pas Geç'}
            </button>
            
            <button 
              className="btn" 
              style={{ background: currentQ === totalQ ? 'var(--success)' : 'var(--primary)', padding: '12px 24px', display: 'flex', alignItems: 'center', gap: '8px' }} 
              onClick={handleNext} 
              disabled={loading}
            >
              {loading ? 'İşleniyor...' : (currentQ === totalQ ? 'Mülakatı Bitir' : 'İleri')}
              {!loading && currentQ !== totalQ && <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>}
            </button>
          </div>
        </div>
      )}
    </>
  );
}