export default function ReportScreen({ reportData, onReturnHome }) {
  if (!reportData || !reportData.feedback) {
    return (
      <div className="view active" style={{ alignItems: 'center', justifyContent: 'center', minHeight: '50vh' }}>
        <p>Rapor verisi bulunamadı veya yükleniyor...</p>
        <button className="btn btn-outline" onClick={onReturnHome}>Ana Sayfaya Dön</button>
      </div>
    );
  }

  const feedback = reportData.feedback;
  const questions = reportData.questions || [];

  const score = Math.round(feedback.overall_score || 0);
  const totalQuestions = questions.length;
  const answeredCount = questions.filter(q => q.status === 'answered').length;
  const skippedCount = questions.filter(q => q.status === 'skipped').length;

  const totalSeconds = questions.reduce((acc, q) => acc + (q.elapsed_seconds || 0), 0);
  const timeSpent = `${Math.floor(totalSeconds / 60)} dk ${totalSeconds % 60} sn`;

  return (
    <div className="view active" style={{ alignItems: 'center' }}>
      <div className="report-header">
        <h2>Mülakat Performans Raporu</h2>
        <p>Yapay zeka değerlendirmesine göre cevaplarınızın detaylı analizi.</p>
      </div>

      <div className="report-score-box">
        <div className="score-val">%{score}</div>
        <div className="score-text">
          <h4>Genel Doğruluk Skoru</h4>
          <p>
            {score >= 80 
              ? "Harika bir iş çıkardınız! Soruların büyük bir kısmına tatmin edici ve doğru yanıtlar verdiniz." 
              : "Bazı konularda eksikleriniz olsa da genel olarak iyi bir performans sergilediniz."}
          </p>
          <p style={{ marginTop: '12px', fontSize: '0.95rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
            "{feedback.summary}"
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-box">
          <div className="stat-val">{timeSpent}</div>
          <div className="stat-label">Toplam Süre</div>
        </div>
        <div className="stat-box">
          <div className="stat-val">{answeredCount}/{totalQuestions}</div>
          <div className="stat-label">Yanıtlanan Soru</div>
        </div>
        <div className="stat-box">
          <div className="stat-val">{skippedCount}</div>
          <div className="stat-label">Pas Geçilen</div>
        </div>
      </div>

      <div className="plus-minus-grid">
        <div className="pm-card">
          <div className="pm-header plus">Başarılı Yanıtlar (Doğru)</div>
          <ul className="pm-list">
            {feedback.strengths && feedback.strengths.length > 0 ? (
              feedback.strengths.map((item, index) => (
                <li key={`pos-${index}`}>
                  <div className="pm-icon plus">+</div>
                  <div>{item}</div>
                </li>
              ))
            ) : (
              <li><div>Henüz olumlu bir değerlendirme bulunmuyor.</div></li>
            )}
          </ul>
        </div>
        <div className="pm-card">
          <div className="pm-header minus">Hatalı / Eksik Yanıtlar</div>
          <ul className="pm-list">
            {feedback.improvements && feedback.improvements.length > 0 ? (
              feedback.improvements.map((item, index) => (
                <li key={`neg-${index}`}>
                  <div className="pm-icon minus">-</div>
                  <div>{item}</div>
                </li>
              ))
            ) : (
              <li><div>Harika! Eksik veya hatalı bir yanıtınız bulunmuyor.</div></li>
            )}
          </ul>
        </div>
      </div>
      
      <div className="proceed-btn-container">
        <button className="btn btn-outline" style={{ padding: '16px 48px', borderRadius: '100px', fontSize: '16px' }} onClick={onReturnHome}>
          Ana Sayfaya Dön
        </button>
      </div>
    </div>
  );
}