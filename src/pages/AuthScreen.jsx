import { useState } from 'react';
import { authService } from '../services/authService';

export default function AuthScreen({ onLogin }) {
  const [view, setView] = useState('login'); // 'login', 'register', 'forgot', 'verify'
  
  // Form State'leri
  const [email, setEmail] = useState('baha@KariyerAI.com');
  const [password, setPassword] = useState('password123');
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);

  // 1. Giriş İşlemi
  const handleLogin = async () => {
    setLoading(true);
    try {
      const response = await authService.login(email, password);
      if (response.success) {
        onLogin(); // App.jsx'teki başarılı giriş fonksiyonunu tetikler
      }
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  // 2. Google Giriş İşlemi
  const handleGoogleLogin = async () => {
    setLoading(true);
    try {
      const response = await authService.googleLogin();
      if (response.success) onLogin();
    } catch (error) {
      alert("Google girişi başarısız.");
    } finally {
      setLoading(false);
    }
  };

  // 3. Kayıt İşlemi
  const handleRegister = async () => {
    setLoading(true);
    try {
      const response = await authService.register({ name, email, password });
      if (response.success) {
        alert(response.message);
        setView('login');
      }
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  // 4. Şifremi Unuttum İşlemi
  const handleForgot = async () => {
    setLoading(true);
    try {
      const response = await authService.forgotPassword(email);
      if (response.success) {
        alert(response.message);
        setView('verify');
      }
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  // 5. Kod Doğrulama İşlemi
  const handleVerify = async () => {
    setLoading(true);
    try {
      const response = await authService.verifyCode(code);
      if (response.success) {
        alert("Kod doğrulandı! Şimdi yeni şifrenizle giriş yapabilirsiniz.");
        setView('login');
      }
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="view active auth-wrapper">
      {/* --- GİRİŞ EKRANI --- */}
      {view === 'login' && (
        <div className="login-card">
          <h1 className="auth-main-title">Kariyer AI</h1>
          <p className="auth-subtitle">Yapay zeka destekli analiz ve mülakat simülasyonu ile kariyerinize hazırlanın.</p>
          
          <div className="input-group">
            <label>E-posta Adresi</label>
            <input type="email" className="input-field" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="input-group">
            <label>Şifre</label>
            <input type="password" className="input-field" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          
          <button className="btn" style={{ width: '100%', marginTop: '10px' }} onClick={handleLogin} disabled={loading}>
            {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
          </button>

          <div className="auth-divider">veya</div>

          <button className="btn btn-google" onClick={handleGoogleLogin} disabled={loading}>
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            Google ile Giriş Yap
          </button>

          <div className="auth-footer">
            <span className="text-link" onClick={() => setView('forgot')}>Şifremi Unuttum</span>
            <span>Hesabın yok mu? <span className="text-link" onClick={() => setView('register')}>Kayıt Ol</span></span>
          </div>
        </div>
      )}

      {/* --- KAYIT EKRANI --- */}
      {view === 'register' && (
        <div className="login-card">
          <h2>Hesap Oluştur</h2>
          <p className="subtitle">Mülakat hazırlıklarına hemen başlamak için bilgilerinizi girin.</p>
          
          <div className="input-group">
            <label>Ad Soyad</label>
            <input type="text" className="input-field" placeholder="Adınız Soyadınız" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="input-group">
            <label>E-posta Adresi</label>
            <input type="email" className="input-field" placeholder="ornek@posta.com" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="input-group">
            <label>Şifre</label>
            <input type="password" className="input-field" placeholder="En az 8 karakter" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          
          <button className="btn" style={{ width: '100%', marginTop: '10px' }} onClick={handleRegister} disabled={loading}>
            {loading ? 'Kayıt Yapılıyor...' : 'Kayıt Ol ve Başla'}
          </button>
          <div className="auth-footer">
            <div className="auth-footer-center">Zaten hesabın var mı? <span className="text-link" onClick={() => setView('login')}>Giriş Yap</span></div>
          </div>
        </div>
      )}

      {/* --- ŞİFREMİ UNUTTUM EKRANI --- */}
      {view === 'forgot' && (
        <div className="login-card">
          <h2>Şifre Sıfırlama</h2>
          <p className="subtitle">Hesabınıza bağlı e-posta adresini girin, size bir doğrulama kodu gönderelim.</p>
          <div className="input-group">
            <label>E-posta Adresi</label>
            <input type="email" className="input-field" placeholder="ornek@posta.com" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <button className="btn" style={{ width: '100%', marginTop: '10px' }} onClick={handleForgot} disabled={loading}>
            {loading ? 'Gönderiliyor...' : 'Kodu Gönder'}
          </button>
          <div className="auth-footer">
            <div className="auth-footer-center"><span className="text-link" onClick={() => setView('login')}>Giriş ekranına dön</span></div>
          </div>
        </div>
      )}

      {/* --- KOD DOĞRULAMA EKRANI --- */}
      {view === 'verify' && (
        <div className="login-card">
          <h2>Kodu Doğrula</h2>
          <p className="subtitle">E-posta adresinize gönderdiğimiz 6 haneli doğrulama kodunu girin.</p>
          <div className="input-group">
            <label>Doğrulama Kodu</label>
            <input type="text" className="input-field" placeholder="000000" style={{ textAlign: 'center', letterSpacing: '4px', fontSize: '18px', fontWeight: 'bold' }} value={code} onChange={(e) => setCode(e.target.value)} />
          </div>
          <button className="btn" style={{ width: '100%', marginTop: '10px' }} onClick={handleVerify} disabled={loading}>
            {loading ? 'Doğrulanıyor...' : 'Doğrula ve Şifre Belirle'}
          </button>
          <div className="auth-footer">
            <div className="auth-footer-center"><span className="text-link" onClick={() => setView('forgot')}>Kodu tekrar gönder</span></div>
          </div>
        </div>
      )}
    </div>
  );
}