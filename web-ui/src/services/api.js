import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3010/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
            const res = await axios.post('http://localhost:3010/api/v1/auth/RefreshToken', { refreshToken });
                    
            const newAccessToken = res.data.data.accessToken;
            const newRefreshToken = res.data.data.refreshToken;

          localStorage.setItem('accessToken', newAccessToken);
          if (newRefreshToken) localStorage.setItem('refreshToken', newRefreshToken);

          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/'; 
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;