import api from './api';

class UserService {
  async getUsers(search = '', limit = 50, offset = 0) {
    try {
      const response = await api.get('/users', {
        params: { search, limit, offset }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch users');
    }
  }

  async getUserById(userId) {
    try {
      const response = await api.get(`/users/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch user');
    }
  }

  async updateUserStatus(userId, isOnline) {
    try {
      const response = await api.put(`/users/${userId}/status`, null, {
        params: { is_online: isOnline }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update status');
    }
  }

  async searchContacts(query, limit = 20) {
    try {
      const response = await api.get('/users/search/contacts', {
        params: { q: query, limit }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to search contacts');
    }
  }
}

export default new UserService();