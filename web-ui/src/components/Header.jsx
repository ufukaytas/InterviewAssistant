export default function Header({ isAuthenticated, onLogout, onLogoClick, onHistoryClick }) {
  return (
    <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px 30px', borderBottom: '1px solid var(--border)' }}>
      
      {/* Logo Alanı */}
      <div className="logo" onClick={onLogoClick} style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold', fontSize: '1.2rem', color: 'var(--primary)' }}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
        InterviewAssistant
      </div>

      {/* Sağ Menü - Sadece giriş yapıldıysa görünür */}
      {isAuthenticated && (
        <nav style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          
          {/* YENİ EKLENEN BUTON */}
          <button 
            onClick={onHistoryClick} 
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontWeight: '500', color: 'var(--text-color)', fontSize: '15px' }}
            onMouseOver={(e) => e.target.style.color = 'var(--primary)'}
            onMouseOut={(e) => e.target.style.color = 'var(--text-color)'}
          >
            Geçmiş Mülakatlarım
          </button>

          <button className="btn btn-outline" onClick={onLogout} style={{ padding: '8px 16px', fontSize: '14px' }}>
            Çıkış Yap
          </button>
        </nav>
      )}
    </header>
  );
}