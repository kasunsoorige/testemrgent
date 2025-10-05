// Mock data for PayPhone app

export const mockUsers = [
  {
    id: '1',
    name: 'Alice Johnson',
    phone: '+1 234 567 8901',
    email: 'alice@example.com',
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b2c5?w=150&h=150&fit=crop&crop=face',
    status: 'Hey there! I am using PayPhone.',
    isOnline: true,
    lastSeen: new Date().toISOString()
  },
  {
    id: '2',
    name: 'Bob Smith',
    phone: '+1 234 567 8902',
    email: 'bob@example.com',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
    status: 'Busy at work',
    isOnline: false,
    lastSeen: new Date(Date.now() - 30 * 60 * 1000).toISOString()
  },
  {
    id: '3',
    name: 'Carol Davis',
    phone: '+1 234 567 8903',
    email: 'carol@example.com',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
    status: 'Available',
    isOnline: true,
    lastSeen: new Date().toISOString()
  },
  {
    id: '4',
    name: 'David Wilson',
    phone: '+1 234 567 8904',
    email: 'david@example.com',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
    status: 'Love to travel!',
    isOnline: false,
    lastSeen: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
  },
  {
    id: '5',
    name: 'Emma Brown',
    phone: '+1 234 567 8905',
    email: 'emma@example.com',
    avatar: 'https://images.unsplash.com/photo-1544725176-7c40e5a71c5e?w=150&h=150&fit=crop&crop=face',
    status: 'Coffee lover ☕',
    isOnline: true,
    lastSeen: new Date().toISOString()
  }
];

export const mockChats = [
  {
    id: '1',
    participantId: '2',
    lastMessage: {
      text: 'Hey! How are you doing?',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      senderId: '2',
      status: 'delivered'
    },
    unreadCount: 2,
    isPinned: false
  },
  {
    id: '2',
    participantId: '3',
    lastMessage: {
      text: 'Thanks for the help yesterday!',
      timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      senderId: '1',
      status: 'read'
    },
    unreadCount: 0,
    isPinned: true
  },
  {
    id: '3',
    participantId: '1',
    lastMessage: {
      text: 'Are we still meeting tomorrow?',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      senderId: '1',
      status: 'sent'
    },
    unreadCount: 0,
    isPinned: false
  },
  {
    id: '4',
    participantId: '4',
    lastMessage: {
      text: 'Check out this amazing place I visited!',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      senderId: '4',
      status: 'delivered'
    },
    unreadCount: 1,
    isPinned: false
  },
  {
    id: '5',
    participantId: '5',
    lastMessage: {
      text: 'Good morning! ☀️',
      timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
      senderId: '5',
      status: 'read'
    },
    unreadCount: 0,
    isPinned: false
  }
];

export const mockMessages = {
  '1': [
    {
      id: '1',
      text: 'Hi Bob! How\'s your day going?',
      senderId: '1',
      timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
      status: 'read'
    },
    {
      id: '2',
      text: 'Hey Alice! It\'s been pretty good. Just finished a big project at work.',
      senderId: '2',
      timestamp: new Date(Date.now() - 58 * 60 * 1000).toISOString(),
      status: 'read'
    },
    {
      id: '3',
      text: 'That\'s awesome! Congratulations 🎉',
      senderId: '1',
      timestamp: new Date(Date.now() - 55 * 60 * 1000).toISOString(),
      status: 'read'
    },
    {
      id: '4',
      text: 'Thanks! How about you? Any exciting plans for the weekend?',
      senderId: '2',
      timestamp: new Date(Date.now() - 50 * 60 * 1000).toISOString(),
      status: 'read'
    },
    {
      id: '5',
      text: 'Planning to go hiking with some friends. Want to join us?',
      senderId: '1',
      timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
      status: 'read'
    },
    {
      id: '6',
      text: 'Hey! How are you doing?',
      senderId: '2',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      status: 'delivered'
    }
  ],
  '2': [
    {
      id: '7',
      text: 'Carol, thanks so much for your help with the presentation yesterday!',
      senderId: '1',
      timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      status: 'read'
    },
    {
      id: '8',
      text: 'You\'re welcome! It turned out great. How did the client meeting go?',
      senderId: '3',
      timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
      status: 'read'
    },
    {
      id: '9',
      text: 'They loved it! We got the project 🙌',
      senderId: '1',
      timestamp: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
      status: 'read'
    }
  ]
};

export const currentUser = {
  id: '1',
  name: 'You',
  phone: '+1 234 567 8900',
  email: 'you@example.com',
  avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face',
  status: 'Hey there! I am using PayPhone.',
  isOnline: true
};

export const emojis = [
  '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇',
  '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚',
  '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩',
  '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '😣', '😖',
  '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯',
  '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓', '🤗', '🤔',
  '🤭', '🤫', '🤥', '😶', '😐', '😑', '😬', '🙄', '😯', '😦',
  '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐', '🥴',
  '🤢', '🤮', '🤧', '😷', '🤒', '🤕', '🤑', '🤠', '😈', '👿',
  '👹', '👺', '🤡', '💩', '👻', '💀', '👽', '👾', '🤖', '🎃'
];