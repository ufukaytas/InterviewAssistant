import { useState, useEffect } from 'react';
import { interviewService } from '../services/interviewService';

// 1. matchId'yi props olarak içeri alıyoruz
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

  useEffect(() => {
    const initSession = async () => {
      // Eğer matchId yoksa backend soru üretemez, bunu engelliyoruz.
      if (!matchId) {
        console.error("Match ID eksik! Mülakat başlatılamaz.");
        return;
      }

      try {
        // 2. Backend'e AI'dan soru üretmesi için gerekli tüm verileri yolluyoruz
        const res = await interviewService.createSession({ 
          job_posting_id: matchId, // HomeScreen'den artık job_posting_id geliyor
          question_count: 5,
          use_generated_questions: true // Sihirli kelime!
        });
        
        console.log("Mülakat Oturumu Kuruldu:", res);

        // DEĞİŞEN KISIM: res.session_id yerine res.id arıyoruz
        if (res.id) { 
          setSessionId(res.id);
          // Backend total_questions yerine soruları dizi olarak yollamış, sayısını alıyoruz:
          setTotalQ(res.questions ? res.questions.length : 5); 
          console.log("Session ID başarıyla ayarlandı:", res.id);
        } else {
          console.error("Backend yanıtında id bulunamadı:", res);
        }
      } catch (error) {
        console.error("Oturum oluşturulamadı:", error);
      }
    };
    
    initSession();
  }, [matchId]); // matchId değiştiğinde çalışması için

  useEffect(() => {
    let timer;
    if (phase === 'active' && timeLeft > 0 && !loading) {
      timer = setInterval(() => setTimeLeft((prev) => prev - 1), 1000);
    } else if (timeLeft === 0 && phase === 'active' && !loading) {
      alert("Süreniz doldu! Lütfen cevabınızı tamamlayıp İleri butonuna basınız.");
    }
    return () => clearInterval(timer);
  }, [phase, timeLeft, loading]);

  const formatTime = (secs) => {
    if (secs < 0) secs = 0;
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `0${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const handleStart = async () => {
    if (!sessionId) return alert("Oturum henüz hazırlanıyor...");
    
    setLoading(true);
    try {
      await interviewService.startInterview(sessionId);
      const qRes = await interviewService.getCurrentQuestion(sessionId);
      
      // Backend veriyi 'question' objesinin içinde yolluyor, onu alıyoruz:
      const currentQ = qRes.question;
      
      setQuestionId(currentQ.question_id);
      setQuestionText(currentQ.text);
      setTimeLeft(currentQ.time_limit_seconds || 120); // remaining_seconds yerine time_limit_seconds
      
      await interviewService.startQuestionTimer(sessionId, currentQ.question_id);
      setPhase('active');
    } catch (error) {
      console.error(error);
      alert("Mülakat başlatılırken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (!answer.trim()) return alert("Lütfen cevabınızı boş bırakmayınız. Boş bırakmak istiyorsanız Pas Geç butonunu kullanınız.");
    
    setLoading(true);
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
        
        await interviewService.startQuestionTimer(sessionId, nextQ.question_id);
      } else {
        await interviewService.submitAnswer(sessionId, questionId, { answer_text: answer });
        const res = await interviewService.completeInterview(sessionId);
        onFinish(res); 
      }
    } catch (error) {
      console.error(error);
      alert("İşlem sırasında hata oluştu.");
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = async () => {
    setLoading(true);
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
        
        await interviewService.startQuestionTimer(sessionId, nextQ.question_id);
      } else {
        await interviewService.skipQuestion(sessionId, questionId);
        const res = await interviewService.completeInterview(sessionId);
        onFinish(res);
      }
    } catch (error) {
      console.error(error);
      alert("Hata oluştu.");
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

          <div className="int-question">{questionText}</div>

          <textarea 
            className="int-answer-area" 
            placeholder="Teknik ve detaylı cevabınızı buraya yazınız..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            disabled={loading}
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
              {loading ? 'Gönderiliyor...' : (currentQ === totalQ ? 'Mülakatı Bitir' : 'İleri')}
              {!loading && currentQ !== totalQ && <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>}
            </button>
          </div>
        </div>
      )}
    </>
  );
}