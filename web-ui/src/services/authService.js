// Backend hazır olduğunda buradaki mock mantıklarını silip axios.post(...) kullanacağız.
// Şimdilik sahte (mock) bir bekleme süresi oluşturuyoruz.
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const authService = {
  // POST /api/v1/auth/Register
  register: async (userData) => {
    console.log("Kayıt isteği atıldı (Mock):", userData);
    await delay(1000); // 1 saniye sunucu yanıtını bekleme simülasyonu
    return { success: true, message: "Kayıt başarılı, lütfen giriş yapın." };
  },

  // POST /api/v1/auth/Login
  login: async (email, password) => {
    console.log("Giriş isteği atıldı (Mock):", { email, password });
    await delay(1000);
    
    // Gömülü şifre (hardcoded) kaldırıldı. Basit bir boşluk/format kontrolü yapılıyor.
    if (email && email.includes("@") && password.length > 0) {
      return { 
        success: true, 
        accessToken: "mock_access_token_12345", 
        refreshToken: "mock_refresh_token_67890" 
      };
    }
    throw new Error("Lütfen geçerli bir e-posta ve şifre girin!");
  },

  // POST /api/v1/auth/Logout
  logout: async () => {
    console.log("Çıkış yapılıyor (Mock)...");
    await delay(500);
    return { success: true };
  },

  // POST /api/v1/auth/ForgotPassword
  forgotPassword: async (email) => {
    console.log("Şifre sıfırlama linki gönderiliyor (Mock):", email);
    await delay(1000);
    return { success: true, message: "Doğrulama kodu e-postanıza gönderildi." };
  },

  // POST /api/v1/auth/ResetPassword (Mock Doğrulama)
  verifyCode: async (code) => {
    console.log("Kod doğrulanıyor (Mock):", code);
    await delay(1000);
    if (code && code.length >= 4) {
       return { success: true, message: "Kod başarıyla doğrulandı." };
    }
    throw new Error("Hatalı doğrulama kodu girdiniz.");
  },

  // POST /api/v1/auth/GoogleLogin
  googleLogin: async (idToken) => {
    console.log("Google ile giriş yapılıyor (Mock):", idToken);
    await delay(1000);
    return { success: true, accessToken: "google_mock_token" };
  }
};