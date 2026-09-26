// src/services/authService.js

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
    if (email === "baha@KariyerAI.com" && password === "password123") {
      // Başarılı girişte sahte token'lar dönüyoruz
      return { 
        success: true, 
        accessToken: "mock_access_token_12345", 
        refreshToken: "mock_refresh_token_67890" 
      };
    }
    throw new Error("Hatalı e-posta veya şifre!");
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

  // POST /api/v1/auth/GoogleLogin
  googleLogin: async (idToken) => {
    console.log("Google ile giriş yapılıyor (Mock):", idToken);
    await delay(1000);
    return { success: true, accessToken: "google_mock_token" };
  }
};