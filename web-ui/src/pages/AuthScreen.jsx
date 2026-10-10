import { useState } from 'react';
import { authService } from '../services/authService';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

function AuthForm({ onLogin }) {
  const [view, setView] = useState('login'); 
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);

  const [feedback, setFeedback] = useState({ type: '', text: '' });

  const changeView = (newView) => {
    setFeedback({ type: '', text: '' });
    setView(newView);
  };

  const handleLogin = async () => {
    setLoading(true);
    setFeedback({ type: '', text: '' });
    try {
      const response = await authService.login(email, password);
      if (response.isSuccessfull) {
        onLogin();
      } else {
        setFeedback({ type: 'error', text: 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.' });
      }
    } catch (error) {
      setFeedback({ type: 'error', text: 'Sisteme bağlanırken bir hata oluştu.' });
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    setLoading(true);
    setFeedback({ type: '', text: '' });
    try {
      const response = await authService.register({ name, email, password });
      if (response.isSuccessfull) {
        setFeedback({ type: 'success', text: 'Kayıt başarılı! Lütfen giriş yapın.' });
        changeView('login');
      }
    } catch (error) {
      setFeedback({ type: 'error', text: 'Kayıt işlemi gerçekleştirilemedi. Bilgilerinizi kontrol edin.' });
    } finally {
      setLoading(false);
    }
  };

  const handleForgot = async () => {
    if (!email) {
      setFeedback({ type: 'error', text: 'Lütfen e-posta adresinizi girin.' });
      return;
    }
    setLoading(true);
    setFeedback({ type: '', text: '' });
    try {
      const response = await authService.forgotPassword(email);
      if (response.isSuccessfull) {
        setFeedback({ type: 'success', text: 'Şifre sıfırlama kodu e-posta adresinize gönderildi.' });
        changeView('reset'); 
      }
    } catch (error) {
      setFeedback({ type: 'error', text: 'Şifre sıfırlama işlemi başlatılamadı.' });
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async () => {
    if (!code || code.length < 6) {
      setFeedback({ type: 'error', text: 'Lütfen 6 haneli doğrulama kodunu eksiksiz girin.' });
      return;
    }
    if (!newPassword || newPassword.length < 6) {
      setFeedback({ type: 'error', text: 'Lütfen en az 6 karakterli yeni bir şifre girin.' });
      return;
    }

    setLoading(true);
    setFeedback({ type: '', text: '' });
    try {
      const response = await authService.resetPassword(email, code, newPassword);
      if (response.isSuccessfull || response.success !== false) {
        setFeedback({ type: 'success', text: 'Şifreniz başarıyla güncellendi! Yeni şifrenizle giriş yapabilirsiniz.' });
        changeView('login');
      }
    } catch (error) {
      setFeedback({ type: 'error', text: 'Şifre güncellenemedi. Girdiğiniz kod hatalı veya süresi dolmuş olabilir.' });
    } finally {
      setLoading(false);
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
    <div className="view active auth-wrapper">
      {view === 'login' && (
        <div className="auth-card">
          <h1 className="auth-main-title">Interview Assistant</h1>
          <p className="auth-subtitle">Yapay zeka destekli analiz ve mülakat simülasyonu ile kariyerinize hazırlanın.</p>
          {renderFeedback()}
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
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '10px' }}>
            <GoogleLogin
              onSuccess={async (credentialResponse) => {
                setLoading(true); setFeedback({ type: '', text: '' });
                try {
                  const response = await authService.googleLogin(credentialResponse.credential);
                  if (response.isSuccessfull || response.success !== false) { onLogin(); } 
                  else { setFeedback({ type: 'error', text: 'Google ile giriş yapılamadı.' }); }
                } catch (error) { setFeedback({ type: 'error', text: 'Google girişi sırasında bir hata oluştu.' }); } 
                finally { setLoading(false); }
              }}
              onError={() => { setFeedback({ type: 'error', text: 'Google girişi iptal edildi veya başarısız oldu.' }); }}
            />
          </div>
          <div className="auth-footer">
            <span className="text-link" onClick={() => changeView('forgot')}>Şifremi Unuttum</span>
            <span>Hesabın yok mu? <span className="text-link" onClick={() => changeView('register')}>Kayıt Ol</span></span>
          </div>
        </div>
      )}

      {view === 'register' && (
        <div className="auth-card">
          <h2>Hesap Oluştur</h2>
          <p className="subtitle">Mülakat hazırlıklarına hemen başlamak için bilgilerinizi girin.</p>
          {renderFeedback()}
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
            <div className="auth-footer-center">Zaten hesabın var mı? <span className="text-link" onClick={() => changeView('login')}>Giriş Yap</span></div>
          </div>
        </div>
      )}

      {view === 'forgot' && (
        <div className="auth-card">
          <h2>Şifre Sıfırlama</h2>
          <p className="subtitle">Hesabınıza bağlı e-posta adresini girin, size bir doğrulama kodu gönderelim.</p>
          {renderFeedback()}
          <div className="input-group">
            <label>E-posta Adresi</label>
            <input type="email" className="input-field" placeholder="ornek@posta.com" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <button className="btn" style={{ width: '100%', marginTop: '10px' }} onClick={handleForgot} disabled={loading}>
            {loading ? 'Gönderiliyor...' : 'Kodu Gönder'}
          </button>
          <div className="auth-footer">
            <div className="auth-footer-center"><span className="text-link" onClick={() => changeView('login')}>Giriş ekranına dön</span></div>
          </div>
        </div>
      )}

      {view === 'reset' && (
        <div className="auth-card">
          <h2>Yeni Şifre Belirle</h2>
          <p className="subtitle">E-posta adresinize gönderdiğimiz 6 haneli kodu ve yeni şifrenizi aşağıya girin.</p>
          {renderFeedback()}
          
          <div className="input-group">
            <label>Doğrulama Kodu</label>
            <input type="text" className="input-field" placeholder="000000" style={{ textAlign: 'center', letterSpacing: '4px', fontSize: '18px', fontWeight: 'bold' }} value={code} onChange={(e) => setCode(e.target.value)} />
          </div>

          <div className="input-group">
            <label>Yeni Şifre</label>
            <input type="password" className="input-field" placeholder="Yeni şifreniz" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
          </div>

          <button className="btn" style={{ width: '100%', marginTop: '10px' }} onClick={handleResetPassword} disabled={loading}>
            {loading ? 'Güncelleniyor...' : 'Şifreyi Güncelle ve Giriş Yap'}
          </button>
          
          <div className="auth-footer">
            <div className="auth-footer-center"><span className="text-link" onClick={() => changeView('forgot')}>Kodu tekrar gönder</span></div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AuthScreen({ onLogin }) {
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthForm onLogin={onLogin} />
    </GoogleOAuthProvider>
  );
}