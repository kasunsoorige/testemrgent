import api from './api';

class ChatService {
  async getChats() {
    try {
      const response = await api.get('/chats');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch chats');
    }
  }

  async createChat(participants, type = 'private') {
    try {
      const response = await api.post('/chats', {
        participants,
        type
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create chat');
    }
  }

  async getChat(chatId) {
    try {
      const response = await api.get(`/chats/${chatId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch chat');
    }
  }

  async deleteChat(chatId) {
    try {
      await api.delete(`/chats/${chatId}`);
      return true;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete chat');
    }
  }

  async pinChat(chatId) {
    try {
      const response = await api.put(`/chats/${chatId}/pin`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to pin chat');
    }
  }

  async getMessages(chatId, limit = 50, offset = 0) {
    try {
      const response = await api.get(`/chats/${chatId}/messages`, {
        params: { limit, offset }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch messages');
    }
  }

  async sendMessage(chatId, text, messageType = 'text') {
    try {
      const response = await api.post(`/chats/${chatId}/messages`, {
        text,
        message_type: messageType
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send message');
    }
  }

  async updateMessageStatus(messageId, status) {
    try {
      const response = await api.put(`/chats/messages/${messageId}/status`, {
        status
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update message status');
    }
  }

  async getUnreadCount() {
    try {
      const response = await api.get('/chats/messages/unread-count');
      return response.data.unread_count;
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
      return 0;
    }
  }
}

export default new ChatService();