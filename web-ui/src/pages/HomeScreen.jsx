import { useState, useEffect } from 'react';
import { matchService } from '../services/matchService';
import { interviewService } from '../services/interviewService'; 

export default function HomeScreen({ onStartInterview }) {

  const [cvFile, setCvFile] = useState(null);
  const [cvName, setCvName] = useState('Dosya Seç veya Sürükle');
  const [jobText, setJobText] = useState('');
  
  const [cvStyle, setCvStyle] = useState({});
  const [status, setStatus] = useState('idle'); 
  const [progress, setProgress] = useState(null); 
  const [analysisResult, setAnalysisResult] = useState(null);
  
  const [pastInterviews, setPastInterviews] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await interviewService.getPastInterviews();
        const dataList = res.items || res.data || res;
        setPastInterviews(dataList);
      } catch (error) {
        console.error("Geçmiş mülakatlar çekilemedi:", error);
      } finally {
        setLoadingHistory(false);
      }
    };

    fetchHistory();
  }, []);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCvFile(file);
      setCvName(file.name);
      setCvStyle({ borderColor: 'var(--success)', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' });
    }
  };

  const handleAnalyze = async () => {
    if (!cvFile && cvName === 'Dosya Seç veya Sürükle') {
      alert("Lütfen önce bir CV dosyası yükleyin.");
      return;
    }
    if (!jobText.trim()) {
      alert("Lütfen bir ilan metni girin.");
      return;
    }

    setStatus('analyzing');
    setProgress(null); 
    
    try {
      const res = await matchService.analyzeMatch(cvFile || 'mock.pdf', jobText);
      
      setProgress(res.match_score); 
      setAnalysisResult(res);       
      
      setStatus('done');
      
      setTimeout(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }), 100);
    } catch (error) {
      setStatus('idle');
      console.error("İşte gizlenen hata:", error);
      alert("Analiz sırasında bir hata oluştu.");
    }
  };

  return (
    <div className="view active" style={{ justifyContent: 'flex-start', minHeight: '75vh' }}>
      
      <div className="home-info-section">
        <h3 className="info-title">CV'ni yükle, ilana göre güçlendir, mülakatı burada prova et.</h3>
        <p className="info-desc">Mülakat Hazırlık, başvurduğun ilana özel CV düzeltme önerileri çıkarır, ardından aynı ilana göre üretilmiş sorularla seni mülakata hazırlar — hepsi tek yerde.</p>
        <div className="info-steps-grid">
          <div className="info-step"><div className="info-step-num">1</div><div className="info-step-content"><h4>CV'ni yükle, ilanı yapıştır</h4><p>Sistem ikisini karşılaştırıp uyum oranını hesaplar.</p></div></div>
          <div className="info-step"><div className="info-step-num">2</div><div className="info-step-content"><h4>Kişisel düzeltme önerilerini al</h4><p>Eksik beceriler ve zayıf ifadeler için somut öneriler görürsün.</p></div></div>
          <div className="info-step"><div className="info-step-num">3</div><div className="info-step-content"><h4>İlana özel mülakatı yanıtla</h4><p>Gerçek sorularla pratik yap, istersen tekrar tekrar dene.</p></div></div>
        </div>
      </div>

      <div className="input-grid">
        <div className="square-card">
          <div className="card-header">
            <div className="card-header-title">
              <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
              Özgeçmiş Belgesi
            </div>
          </div>
          
          <input type="file" id="cv-upload" style={{ display: 'none' }} onChange={handleFileChange} accept=".pdf,.doc,.docx" />
          
          <div className="cv-dropzone" onClick={() => document.getElementById('cv-upload').click()} style={cvStyle}>
            <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            <p style={{ color: cvStyle.color || 'inherit' }}>{cvName}</p>
            <span>{status === 'idle' && cvName === 'Dosya Seç veya Sürükle' ? 'PDF veya DOCX (Maks 5MB)' : 'Başarıyla Yüklendi ✓'}</span>
          </div>
        </div>

        <div className="square-card">
          <div className="card-header">
            <div className="card-header-title">
              <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
              Hedef İş İlanı
            </div>
          </div>
          <textarea 
            className="job-textarea" 
            placeholder="İlanın aranan nitelikler ve iş tanımı kısımlarını buraya yapıştırın..."
            value={jobText}
            onChange={(e) => setJobText(e.target.value)}
          ></textarea>
        </div>
      </div>
      
      {status === 'idle' && (
        <div className="analyze-btn-container">
          <button className="btn" onClick={handleAnalyze}>
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            Analiz Et
          </button>
        </div>
      )}

      {status !== 'idle' && (
        <div id="analysis-section" style={{ display: 'block', width: '100%', borderTop: '1px dashed var(--border)', paddingTop: '40px', marginTop: '10px' }}>
          <div className="anim-container" style={{ marginBottom: '40px' }}>
            
            {/* ÇEMBER DÜZENLEMESİ: Yüklenirken gri çember ve "..." gösteriyor */}
            <div className="progress-circle" style={{ background: status === 'done' ? `conic-gradient(var(--primary) ${progress}%, var(--border) 0%)` : 'var(--border)' }}>
              <div className="progress-inner">
                <span className="pct-num">{status === 'done' ? `${progress}%` : '...'}</span>
                <span className="pct-label">{status === 'done' ? 'UYUM SKORU' : 'ANALİZ EDİLİYOR'}</span>
              </div>
            </div>
            
            <p style={{ marginTop: '24px', color: status === 'done' ? 'var(--success)' : 'var(--text-muted)', fontWeight: 500 }}>
              {status === 'done' ? 'Analiz Tamamlandı!' : 'Yapay Zeka Verileri İşliyor...'}
            </p>
          </div>

          {status === 'done' && analysisResult && (
            <div style={{ animation: 'fadeIn 0.6s ease' }}>
              
              <p style={{ textAlign: 'center', marginBottom: '20px', fontSize: '1.1rem' }}>
                {analysisResult.feedback} 
              </p>

              <div className="plus-minus-grid">
                <div className="pm-card">
                  <div className="pm-header plus">Güçlü Eşleşmeler</div>
                  <ul className="pm-list">
                    {analysisResult.matching_skills.map((skill, index) => (
                      <li key={`matched-${index}`}>
                        <div className="pm-icon plus">+</div>
                        <div><b>{skill}</b> yetkinliği ilanla örtüşüyor.</div>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="pm-card">
                  <div className="pm-header minus">Geliştirilmesi Gerekenler</div>
                  <ul className="pm-list">
                    {analysisResult.missing_skills.map((skill, index) => (
                      <li key={`missing-${index}`}>
                        <div className="pm-icon minus">-</div>
                        <div><b>{skill}</b> eksik. Mülakata hazırlıklı olun.</div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
               <div className="proceed-btn-container" style={{ marginBottom: '60px' }}>
              <button 
                className="btn" 
                style={{ padding: '16px 48px', borderRadius: '100px', fontSize: '16px', background: 'var(--success)' }} 
                onClick={() => onStartInterview(analysisResult.job_posting_id)}
              >
                Mülakata Geç
              </button>
            </div>
            </div>
          )}
        </div>
      )}

      {/* GEÇMİŞ MÜLAKATLAR ALANI (Şema hataları giderildi) */}
      <div className="history-section" id="past-interviews" style={{ display: 'block', width: '100%', marginTop: '40px' }}>
        <div className="history-header">Önceki Mülakat Kayıtları</div>
        <div className="history-list">
          {loadingHistory ? (
            <p style={{ color: 'var(--text-muted)', padding: '20px 0' }}>Kayıtlar yükleniyor...</p>
          ) : pastInterviews.length > 0 ? (
            pastInterviews.map((item) => (
              <div className="history-item" key={item.id}>
                <div className="history-info">
                  <h4>{item.title || "Yapay Zeka Mülakatı"}</h4>
                  <p>{item.created_at ? new Date(item.created_at).toLocaleDateString('tr-TR') : 'Tarih Yok'}</p>
                </div>
                <div 
                  className="history-score" 
                  style={item.overall_score !== undefined && item.overall_score < 70 ? { background: 'rgba(245, 158, 11, 0.15)', color: 'var(--warning)' } : {}}
                >
                  {item.overall_score !== undefined ? `%${Math.round(item.overall_score)} Uyum` : '% Uyum'}
                </div>
              </div>
            ))
          ) : (
            <p style={{ color: 'var(--text-muted)', padding: '20px 0' }}>Henüz tamamlanmış bir mülakat kaydınız bulunmuyor.</p>
          )}
        </div>
      </div>
    </div>
  );
}