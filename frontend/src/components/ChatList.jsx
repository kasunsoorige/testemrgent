import React, { useState, useEffect } from 'react';
import { Search, Menu, MoreVertical, Pin } from 'lucide-react';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';
import { useAuth } from '../contexts/AuthContext';
import chatService from '../services/chatService';
import { toast } from '../hooks/use-toast';

const ChatList = ({ onChatSelect, selectedChatId }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [chats, setChats] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {
    try {
      setIsLoading(true);
      const chatsData = await chatService.getChats();
      setChats(chatsData);
    } catch (error) {
      console.error('Failed to load chats:', error);
      toast({
        title: "Error",
        description: "Failed to load chats. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMs = now - date;
    const diffInMins = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInMins < 60) {
      return `${diffInMins}m`;
    } else if (diffInHours < 24) {
      return `${diffInHours}h`;
    } else if (diffInDays < 7) {
      return `${diffInDays}d`;
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  const getParticipant = (chat) => {
    if (chat.participant_details && chat.participant_details.length > 0) {
      return chat.participant_details[0];
    }
    return null;
  };

  const filteredChats = chats.filter(chat => {
    const participant = getParticipant(chat);
    return participant?.name.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const sortedChats = [...filteredChats].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1;
    if (!a.is_pinned && b.is_pinned) return 1;
    
    const aTime = a.last_message ? new Date(a.last_message.timestamp) : new Date(a.created_at);
    const bTime = b.last_message ? new Date(b.last_message.timestamp) : new Date(b.created_at);
    return bTime - aTime;
  });

  if (isLoading) {
    return (
      <div className="flex flex-col h-screen bg-white">
        <div className="flex items-center justify-between p-4 border-b border-gray-200" style={{ backgroundColor: '#E90062' }}>
          <div className="flex items-center space-x-3">
            <Avatar className="h-8 w-8">
              <AvatarFallback>{user?.name?.[0] || 'U'}</AvatarFallback>
            </Avatar>
            <h1 className="text-xl font-semibold text-white">PayPhone</h1>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200" style={{ backgroundColor: '#E90062' }}>
        <div className="flex items-center space-x-3">
          <Avatar className="h-8 w-8">
            <AvatarImage src={user?.avatar} alt={user?.name} />
            <AvatarFallback>{user?.name?.[0] || 'U'}</AvatarFallback>
          </Avatar>
          <h1 className="text-xl font-semibold text-white">PayPhone</h1>
        </div>
        <div className="flex items-center space-x-2">
          <button className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-full transition-colors">
            <Search size={20} />
          </button>
          <button className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-full transition-colors">
            <MoreVertical size={20} />
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="p-4 border-b border-gray-100">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search chats..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-pink-500 focus:bg-white transition-colors"
          />
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto">
        {sortedChats.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="mb-4">
              <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ backgroundColor: '#E90062' }}>
                <span className="text-2xl text-white">💬</span>
              </div>
            </div>
            <p className="text-lg font-medium">No chats yet</p>
            <p className="text-sm text-center px-8">
              {searchTerm ? 'No chats match your search' : 'Start a conversation with someone'}
            </p>
          </div>
        ) : (
          sortedChats.map((chat) => {
            const participant = getParticipant(chat);
            if (!participant) return null;

            const isSelected = selectedChatId === chat.id;
            const isOwnMessage = chat.last_message?.sender_id === user?.id;
            
            // Calculate unread count (simplified)
            const unreadCount = 0; // This would be calculated from messages

            return (
              <div
                key={chat.id}
                onClick={() => onChatSelect(chat)}
                className={`flex items-center p-4 border-b border-gray-100 cursor-pointer transition-colors hover:bg-gray-50 ${
                  isSelected ? 'bg-pink-50' : ''
                }`}
              >
                <div className="relative">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src={participant.avatar} alt={participant.name} />
                    <AvatarFallback>{participant.name[0]}</AvatarFallback>
                  </Avatar>
                  {participant.is_online && (
                    <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
                  )}
                </div>

                <div className="flex-1 ml-3 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-semibold text-gray-900 truncate">{participant.name}</h3>
                      {chat.is_pinned && (
                        <Pin size={14} className="text-gray-500" />
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500">
                        {chat.last_message ? formatTime(chat.last_message.timestamp) : formatTime(chat.created_at)}
                      </span>
                      {unreadCount > 0 && (
                        <Badge 
                          variant="secondary" 
                          className="bg-pink-500 text-white min-w-[20px] h-5 text-xs flex items-center justify-center rounded-full"
                        >
                          {unreadCount}
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center mt-1">
                    {isOwnMessage && chat.last_message && (
                      <span className="text-gray-500 mr-1">
                        {chat.last_message.status === 'sent' && '✓'}
                        {chat.last_message.status === 'delivered' && '✓✓'}
                        {chat.last_message.status === 'read' && <span className="text-blue-500">✓✓</span>}
                      </span>
                    )}
                    <p className="text-gray-600 text-sm truncate">
                      {chat.last_message ? chat.last_message.text : 'New chat'}
                    </p>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ChatList;