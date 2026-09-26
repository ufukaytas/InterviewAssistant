export default function ReportScreen({ onReturnHome }) {
    return (
      <div className="view active" style={{ alignItems: 'center' }}>
        <div className="report-header">
          <h2>Mülakat Performans Raporu</h2>
          <p>Yapay zeka değerlendirmesine göre cevaplarınızın detaylı analizi.</p>
        </div>
  
        <div className="report-score-box">
          <div className="score-val">%76</div>
          <div className="score-text">
            <h4>Genel Doğruluk Skoru</h4>
            <p>Aday, mimari sorulara yetkin cevaplar verdi ancak teorik kavramlarda bazı eksiklikler tespit edildi.</p>
          </div>
        </div>
  
        <div className="stats-grid">
          <div className="stat-box"><div className="stat-val">06:45</div><div className="stat-label">Toplam Süre</div></div>
          <div className="stat-box"><div className="stat-val">4/5</div><div className="stat-label">Yanıtlanan Soru</div></div>
          <div className="stat-box"><div className="stat-val">1</div><div className="stat-label">Pas Geçilen</div></div>
        </div>
  
        <div className="plus-minus-grid">
          <div className="pm-card">
            <div className="pm-header plus">Başarılı Yanıtlar (Doğru)</div>
            <ul className="pm-list">
              <li><div className="pm-icon plus">+</div><div><b>RabbitMQ Kullanımı:</b> Asenkron kuyruk mimarisini kusursuz açıkladınız.</div></li>
            </ul>
          </div>
          <div className="pm-card">
            <div className="pm-header minus">Hatalı / Eksik Yanıtlar</div>
            <ul className="pm-list">
              <li><div className="pm-icon minus">-</div><div><b>Docker Konteyner:</b> Volüm yönetimiyle ilgili komut örneği eksikti.</div></li>
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