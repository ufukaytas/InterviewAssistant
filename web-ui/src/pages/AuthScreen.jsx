import { useState } from 'react';
import { authService } from '../services/authService';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google'; // Sadece Provider ve GoogleLogin var

// Bütün Auth işlemlerini barındıran İç Bileşen
function AuthForm({ onLogin }) {
  const [view, setView] = useState('login'); 
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const response = await authService.login(email, password);
      if (response.isSuccessfull) {
        onLogin();
      } else {
        alert(response.message || "Giriş başarısız.");
      }
    } catch (error) {
      const errorMsg = error.response?.data?.message || error.response?.data?.detail || "Bir hata oluştu.";
      alert(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    setLoading(true);
    try {
      const response = await authService.register({ name, email, password });
      if (response.isSuccessfull) {
        alert(response.message || "Kayıt başarılı! Lütfen giriş yapın.");
        setView('login');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || "Kayıt işlemi başarısız.";
      alert(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleForgot = async () => {
    setLoading(true);
    try {
      const response = await authService.forgotPassword(email);
      if (response.isSuccessfull) {
        alert(response.message || "Şifre sıfırlama kodu gönderildi.");
        setView('verify');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.message || error.response?.data?.detail || "Bir hata oluştu.";
      alert(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    setView('reset');
  };

  const handleResetPassword = async () => {
    setLoading(true);
    try {
      const response = await authService.resetPassword(email, code, newPassword);
      if (response.isSuccessfull || response.success !== false) {
        alert("Şifreniz başarıyla güncellendi! Yeni şifrenizle giriş yapabilirsiniz.");
        setView('login');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.message || error.response?.data?.detail || "Şifre güncellenemedi.";
      alert(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="view active auth-wrapper">
      {view === 'login' && (
        <div className="auth-card">
          <h1 className="auth-main-title">Kariyer AI</h1>
          <p className="auth-subtitle">Yapay zeka destekli analiz ve mülakat simülasyonu ile kariyerinize hazırlanın.</p>
          
          <div className="input-group">
            <label>E-posta Adresi</label>
            <input type="email" className="input-field" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="ornek@posta.com" />
          </div>
          <div className="input-group">
            <label>Şifre</label>
            <input type="password" className="input-field" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Şifreniz" />
          </div>
          
          <button className="btn" style={{ width: '100%', marginTop: '10px' }} onClick={handleLogin} disabled={loading}>
            {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
          </button>

          <div className="auth-divider">veya</div>

          {/* YENİ GOOGLE BUTONU BURADA */}
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '10px' }}>
            <GoogleLogin
              onSuccess={async (credentialResponse) => {
                setLoading(true);
                try {
                  // credentialResponse.credential, backend'in beklediği asıl JWT Token'dır.
                  const response = await authService.googleLogin(credentialResponse.credential);
                  if (response.isSuccessfull || response.success !== false) {
                    onLogin();
                  } else {
                    alert(response.message || "Google girişi başarısız.");
                  }
                } catch (error) {
                  alert("Google girişi sırasında bir hata oluştu.");
                } finally {
                  setLoading(false);
                }
              }}
              onError={() => {
                alert('Google girişi iptal edildi veya başarısız oldu.');
              }}
            />
          </div>

          <div className="auth-footer">
            <span className="text-link" onClick={() => setView('forgot')}>Şifremi Unuttum</span>
            <span>Hesabın yok mu? <span className="text-link" onClick={() => setView('register')}>Kayıt Ol</span></span>
          </div>
        </div>
      )}

      {view === 'register' && (
        <div className="auth-card">
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

      {view === 'forgot' && (
        <div className="auth-card">
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

      {view === 'verify' && (
        <div className="auth-card">
          <h2>Kodu Doğrula</h2>
          <p className="subtitle">E-posta adresinize gönderdiğimiz doğrulama kodunu girin.</p>
          <div className="input-group">
            <label>Doğrulama Kodu</label>
            <input type="text" className="input-field" placeholder="000000" style={{ textAlign: 'center', letterSpacing: '4px', fontSize: '18px', fontWeight: 'bold' }} value={code} onChange={(e) => setCode(e.target.value)} />
          </div>
          <button className="btn" style={{ width: '100%', marginTop: '10px' }} onClick={handleVerify} disabled={loading}>
            İleri
          </button>
          <div className="auth-footer">
            <div className="auth-footer-center"><span className="text-link" onClick={() => setView('forgot')}>Kodu tekrar gönder</span></div>
          </div>
        </div>
      )}

      {view === 'reset' && (
        <div className="auth-card">
          <h2>Yeni Şifre Belirle</h2>
          <p className="subtitle">Lütfen hesabınız için yeni bir şifre girin.</p>
          <div className="input-group">
            <label>Yeni Şifre</label>
            <input type="password" className="input-field" placeholder="Yeni şifreniz" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
          </div>
          <button className="btn" style={{ width: '100%', marginTop: '10px' }} onClick={handleResetPassword} disabled={loading}>
            {loading ? 'Güncelleniyor...' : 'Şifreyi Güncelle ve Giriş Yap'}
          </button>
        </div>
      )}
    </div>
  );
}

// Ana Component
export default function AuthScreen({ onLogin }) {
  // Docker veya .env içerisinden alınan ID
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthForm onLogin={onLogin} />
    </GoogleOAuthProvider>
  );
}