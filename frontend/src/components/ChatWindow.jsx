import React, { useState, useRef, useEffect } from 'react';
import { ArrowLeft, Phone, Video, MoreVertical, Smile, Send, Paperclip } from 'lucide-react';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Button } from './ui/button';
import { useAuth } from '../contexts/AuthContext';
import chatService from '../services/chatService';
import { toast } from '../hooks/use-toast';
import { emojis } from '../data/mock';

const ChatWindow = ({ chat, onBack }) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const { user } = useAuth();

  const participant = chat?.participant_details?.[0];

  useEffect(() => {
    if (chat?.id) {
      loadMessages();
    }
  }, [chat?.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      setIsLoading(true);
      const messagesData = await chatService.getMessages(chat.id);
      setMessages(messagesData);
    } catch (error) {
      console.error('Failed to load messages:', error);
      toast({
        title: "Error",
        description: "Failed to load messages. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatMessageTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const handleSendMessage = async () => {
    if (message.trim() && !isSending) {
      const messageText = message.trim();
      setMessage('');
      setIsSending(true);

      try {
        const newMessage = await chatService.sendMessage(chat.id, messageText);
        setMessages(prev => [...prev, newMessage]);
        
        // Simulate delivery and read status updates
        setTimeout(async () => {
          try {
            await chatService.updateMessageStatus(newMessage.id, 'delivered');
            setMessages(prev => 
              prev.map(msg => 
                msg.id === newMessage.id 
                  ? { ...msg, status: 'delivered' }
                  : msg
              )
            );
          } catch (error) {
            console.error('Failed to update message status:', error);
          }
        }, 1000);

        setTimeout(async () => {
          try {
            await chatService.updateMessageStatus(newMessage.id, 'read');
            setMessages(prev => 
              prev.map(msg => 
                msg.id === newMessage.id 
                  ? { ...msg, status: 'read' }
                  : msg
              )
            );
          } catch (error) {
            console.error('Failed to update message status:', error);
          }
        }, 3000);
        
      } catch (error) {
        console.error('Failed to send message:', error);
        toast({
          title: "Error",
          description: "Failed to send message. Please try again.",
          variant: "destructive",
        });
        // Restore the message if sending failed
        setMessage(messageText);
      } finally {
        setIsSending(false);
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const addEmoji = (emoji) => {
    setMessage(prev => prev + emoji);
    setShowEmojiPicker(false);
    inputRef.current?.focus();
  };

  if (!participant) return null;

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="flex items-center p-4 border-b border-gray-200" style={{ backgroundColor: '#E90062' }}>
        <button 
          onClick={onBack}
          className="p-2 mr-2 text-white hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
        >
          <ArrowLeft size={20} />
        </button>
        
        <Avatar className="h-10 w-10 mr-3">
          <AvatarImage src={participant.avatar} alt={participant.name} />
          <AvatarFallback>{participant.name[0]}</AvatarFallback>
        </Avatar>

        <div className="flex-1">
          <h2 className="font-semibold text-white">{participant.name}</h2>
          <p className="text-sm text-pink-100">
            {participant.is_online ? 'Online' : `Last seen ${formatMessageTime(participant.last_seen)}`}
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-full transition-colors">
            <Phone size={20} />
          </button>
          <button className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-full transition-colors">
            <Video size={20} />
          </button>
          <button className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-full transition-colors">
            <MoreVertical size={20} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-500"></div>
          </div>
        ) : (
          <>
            {messages.map((msg, index) => {
              const isOwn = msg.sender_id === user?.id;
              const showTimestamp = index === 0 || 
                new Date(messages[index - 1].timestamp).toDateString() !== new Date(msg.timestamp).toDateString();

              return (
                <div key={msg.id}>
                  {showTimestamp && (
                    <div className="flex justify-center my-4">
                      <span className="bg-white px-3 py-1 rounded-full text-xs text-gray-600 shadow-sm">
                        {new Date(msg.timestamp).toLocaleDateString('en-US', {
                          weekday: 'long',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </span>
                    </div>
                  )}
                  
                  <div className={`flex mb-3 ${isOwn ? 'justify-end' : 'justify-start'}`}>
                    <div 
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl shadow-sm ${
                        isOwn 
                          ? 'bg-pink-500 text-white rounded-br-sm' 
                          : 'bg-white text-gray-800 rounded-bl-sm'
                      }`}
                    >
                      <p className="text-sm">{msg.text}</p>
                      <div className="flex items-center justify-end mt-1 space-x-1">
                        <span className={`text-xs ${isOwn ? 'text-pink-100' : 'text-gray-500'}`}>
                          {formatMessageTime(msg.timestamp)}
                        </span>
                        {isOwn && (
                          <span className="text-pink-100">
                            {msg.status === 'sent' && '✓'}
                            {msg.status === 'delivered' && '✓✓'}
                            {msg.status === 'read' && <span className="text-white">✓✓</span>}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Emoji Picker */}
      {showEmojiPicker && (
        <div className="p-4 border-t bg-white max-h-48 overflow-y-auto">
          <div className="grid grid-cols-10 gap-2">
            {emojis.map((emoji, index) => (
              <button
                key={index}
                onClick={() => addEmoji(emoji)}
                className="text-2xl hover:bg-gray-100 rounded p-1 transition-colors"
              >
                {emoji}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Message Input */}
      <div className="flex items-center p-4 border-t bg-white space-x-3">
        <button 
          onClick={() => setShowEmojiPicker(!showEmojiPicker)}
          className="p-2 text-gray-500 hover:bg-gray-100 rounded-full transition-colors"
        >
          <Smile size={20} />
        </button>

        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            disabled={isSending}
            className="w-full px-4 py-2 bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-pink-500 focus:bg-white transition-colors disabled:opacity-50"
          />
        </div>

        <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-full transition-colors">
          <Paperclip size={20} />
        </button>

        <Button
          onClick={handleSendMessage}
          disabled={!message.trim() || isSending}
          className="p-2 bg-pink-500 hover:bg-pink-600 text-white rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          size="sm"
        >
          {isSending ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          ) : (
            <Send size={18} />
          )}
        </Button>
      </div>
    </div>
  );
};

export default ChatWindow;