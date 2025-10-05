import api from './api';

class AuthService {
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData);
      
      if (response.data.token) {
        localStorage.setItem('payphone_token', response.data.token);
        localStorage.setItem('payphone_user', JSON.stringify(response.data.user));
      }
      
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  async login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials);
      
      if (response.data.token) {
        localStorage.setItem('payphone_token', response.data.token);
        localStorage.setItem('payphone_user', JSON.stringify(response.data.user));
      }
      
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  async logout() {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('payphone_token');
      localStorage.removeItem('payphone_user');
    }
  }

  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get user');
    }
  }

  async updateProfile(profileData) {
    try {
      const response = await api.put('/auth/profile', profileData);
      localStorage.setItem('payphone_user', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Profile update failed');
    }
  }

  getStoredUser() {
    const user = localStorage.getItem('payphone_user');
    return user ? JSON.parse(user) : null;
  }

  getStoredToken() {
    return localStorage.getItem('payphone_token');
  }

  isAuthenticated() {
    return !!this.getStoredToken();
  }
}

export default new AuthService();