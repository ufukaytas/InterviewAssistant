export default function ReportScreen({ reportData, onReturnHome }) {
  // Eğer herhangi bir sebepten veri henüz gelmediyse veya boşsa hata vermemesi için güvenlik önlemi
  if (!reportData) {
    return (
      <div className="view active" style={{ alignItems: 'center', justifyContent: 'center', minHeight: '50vh' }}>
        <p>Rapor verisi bulunamadı veya yükleniyor...</p>
        <button className="btn btn-outline" onClick={onReturnHome}>Ana Sayfaya Dön</button>
      </div>
    );
  }

  // Toplam soru sayısını yanıtlanan ve pas geçilenlerden hesaplıyoruz
  const totalQuestions = (reportData.answered || 0) + (reportData.skipped || 0);

  return (
    <div className="view active" style={{ alignItems: 'center' }}>
      <div className="report-header">
        <h2>Mülakat Performans Raporu</h2>
        <p>Yapay zeka değerlendirmesine göre cevaplarınızın detaylı analizi.</p>
      </div>

      <div className="report-score-box">
        <div className="score-val">%{reportData.score}</div>
        <div className="score-text">
          <h4>Genel Doğruluk Skoru</h4>
          <p>
            {reportData.score >= 80 
              ? "Harika bir iş çıkardınız! Soruların büyük bir kısmına tatmin edici ve doğru yanıtlar verdiniz." 
              : "Bazı konularda eksikleriniz olsa da genel olarak iyi bir performans sergilediniz."}
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-box">
          <div className="stat-val">{reportData.time_spent}</div>
          <div className="stat-label">Toplam Süre</div>
        </div>
        <div className="stat-box">
          <div className="stat-val">{reportData.answered}/{totalQuestions}</div>
          <div className="stat-label">Yanıtlanan Soru</div>
        </div>
        <div className="stat-box">
          <div className="stat-val">{reportData.skipped}</div>
          <div className="stat-label">Pas Geçilen</div>
        </div>
      </div>

      <div className="plus-minus-grid">
        <div className="pm-card">
          <div className="pm-header plus">Başarılı Yanıtlar (Doğru)</div>
          <ul className="pm-list">
            {reportData.positives && reportData.positives.length > 0 ? (
              reportData.positives.map((item, index) => (
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
            {reportData.negatives && reportData.negatives.length > 0 ? (
              reportData.negatives.map((item, index) => (
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