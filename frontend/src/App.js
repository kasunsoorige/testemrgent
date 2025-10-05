import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { Toaster } from "./components/ui/toaster";
import AuthScreen from "./components/AuthScreen";
import ChatList from "./components/ChatList";
import ChatWindow from "./components/ChatWindow";

const MainApp = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const [selectedChat, setSelectedChat] = useState(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleChatSelect = (chat) => {
    setSelectedChat(chat);
  };

  const handleBackToChats = () => {
    setSelectedChat(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading PayPhone...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthScreen />;
  }

  return (
    <div className="h-screen bg-gray-100">
      {isMobile ? (
        // Mobile Layout
        <div className="h-full">
          {selectedChat ? (
            <ChatWindow 
              chat={selectedChat} 
              onBack={handleBackToChats}
            />
          ) : (
            <ChatList 
              onChatSelect={handleChatSelect}
              selectedChatId={selectedChat?.id}
            />
          )}
        </div>
      ) : (
        // Desktop Layout
        <div className="flex h-full">
          <div className="w-1/3 min-w-[320px] max-w-md border-r border-gray-300">
            <ChatList 
              onChatSelect={handleChatSelect}
              selectedChatId={selectedChat?.id}
            />
          </div>
          <div className="flex-1">
            {selectedChat ? (
              <ChatWindow 
                chat={selectedChat} 
                onBack={handleBackToChats}
              />
            ) : (
              <div className="flex items-center justify-center h-full bg-gray-50">
                <div className="text-center">
                  <div className="mb-4">
                    <div className="mx-auto w-16 h-16 rounded-full flex items-center justify-center" style={{ backgroundColor: '#E90062' }}>
                      <span className="text-2xl text-white">💬</span>
                    </div>
                  </div>
                  <h2 className="text-xl font-semibold text-gray-700 mb-2">
                    Welcome to PayPhone
                  </h2>
                  <p className="text-gray-500">
                    Select a chat to start messaging
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const App = () => {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <MainApp />
          <Toaster />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
};

export default App;