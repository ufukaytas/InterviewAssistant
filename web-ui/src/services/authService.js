import api from './api';

export const authService = {
  // POST /api/v1/auth/Register
  register: async (userData) => {
    const nameParts = userData.name ? userData.name.trim().split(' ') : ['Kullanıcı'];
    const firstName = nameParts[0];
    const lastName = nameParts.length > 1 ? nameParts.slice(1).join(' ') : 'Bilinmiyor';

    const payload = {
      FirstName: firstName,
      LastName: lastName,
      Email: userData.email,
      Password: userData.password
    };

    const response = await api.post('/auth/Register', payload);
    return response.data;
  },

  // POST /api/v1/auth/Login
  login: async (email, password) => {
    const response = await api.post('/auth/Login', { email, password });
    
    const result = response.data;
    if (result.isSuccessfull && result.data && result.data.accessToken) {
      localStorage.setItem('accessToken', result.data.accessToken);
      if (result.data.refreshToken) {
         localStorage.setItem('refreshToken', result.data.refreshToken);
      }
    }
    return result; 
  },

  // POST /api/v1/auth/Logout
  logout: async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      await api.post('/auth/Logout', { refreshToken });
    }
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    return { success: true };
  },

  // POST /api/v1/auth/ForgotPassword
  forgotPassword: async (email) => {
    const response = await api.post('/auth/ForgotPassword', { email });
    return response.data;
  },

  // POST /api/v1/auth/VerifyCode
  verifyCode: async (code) => {
    const response = await api.post('/auth/VerifyCode', { code }); 
    return response.data;
  },

  resetPassword: async (email, token, newPassword) => {
    const response = await api.post('/auth/ResetPassword', { 
      Email: email, 
      Token: token, 
      NewPassword: newPassword 
    });
    return response.data;
  },

  // POST /api/v1/auth/GoogleLogin
  googleLogin: async (idToken) => {
    const response = await api.post('/auth/GoogleLogin', { idToken });
    
    const result = response.data;
    if (result.isSuccessfull && result.data && result.data.accessToken) {
      localStorage.setItem('accessToken', result.data.accessToken);
      if (result.data.refreshToken) {
         localStorage.setItem('refreshToken', result.data.refreshToken);
      }
    }
    return result;
  }
};