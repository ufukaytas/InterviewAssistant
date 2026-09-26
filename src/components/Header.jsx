export default function Header({ isAuthenticated, onLogout, onLogoClick }) {
    return (
      <header>
        <div className="logo" onClick={onLogoClick}>Interview<span> Asistant</span></div>
        
        {isAuthenticated && (
          <div className="profile-badge" style={{ display: 'flex' }}>
            <div className="avatar">B</div>
            <span>Baha Ok</span>
            <button className="logout-btn" onClick={onLogout} title="Çıkış Yap">
              <svg viewBox="0 0 24 24">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
            </button>
          </div>
        )}
      </header>
    );
  }