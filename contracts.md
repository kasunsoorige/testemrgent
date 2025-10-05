# PayPhone Backend Contracts

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login 
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/profile` - Update user profile

### Users
- `GET /api/users` - Get all users (for contacts)
- `GET /api/users/:id` - Get specific user
- `PUT /api/users/:id/status` - Update user status/presence

### Chats
- `GET /api/chats` - Get user's chat list
- `POST /api/chats` - Create new chat
- `GET /api/chats/:id` - Get specific chat details
- `DELETE /api/chats/:id` - Delete chat

### Messages
- `GET /api/chats/:chatId/messages` - Get chat messages
- `POST /api/chats/:chatId/messages` - Send new message
- `PUT /api/messages/:id/status` - Update message status (delivered/read)

### Real-time (WebSocket)
- `message:sent` - New message sent
- `message:delivered` - Message delivered
- `message:read` - Message read
- `user:online` - User came online
- `user:offline` - User went offline

## Database Models

### User Model
```javascript
{
  _id: ObjectId,
  name: String,
  email: String,
  phone: String,
  password: String (hashed),
  avatar: String (URL),
  status: String,
  isOnline: Boolean,
  lastSeen: Date,
  createdAt: Date,
  updatedAt: Date
}
```

### Chat Model
```javascript
{
  _id: ObjectId,
  participants: [ObjectId], // User IDs
  type: String, // 'private' or 'group'
  lastMessage: {
    text: String,
    senderId: ObjectId,
    timestamp: Date,
    status: String // 'sent', 'delivered', 'read'
  },
  isPinned: Boolean,
  createdAt: Date,
  updatedAt: Date
}
```

### Message Model
```javascript
{
  _id: ObjectId,
  chatId: ObjectId,
  senderId: ObjectId,
  text: String,
  timestamp: Date,
  status: String, // 'sent', 'delivered', 'read'
  messageType: String, // 'text', 'image', 'file'
  createdAt: Date,
  updatedAt: Date
}
```

## Mock Data to Replace

### From mock.js - Replace with Backend APIs:

1. **mockUsers** → `/api/users` endpoint
2. **mockChats** → `/api/chats` endpoint  
3. **mockMessages** → `/api/chats/:chatId/messages` endpoint
4. **currentUser** → `/api/auth/me` endpoint

### Frontend Integration Changes:

1. **AuthScreen.jsx**
   - Replace mock authentication with real API calls
   - Add JWT token management
   - Add proper error handling

2. **ChatList.jsx** 
   - Fetch chats from `/api/chats`
   - Update with real-time chat updates
   - Handle loading states

3. **ChatWindow.jsx**
   - Fetch messages from `/api/chats/:chatId/messages`
   - Send messages via `/api/chats/:chatId/messages`
   - Real-time message updates via WebSocket
   - Update message status (delivered/read)

4. **App.js**
   - Add authentication state management
   - JWT token persistence
   - Protected routes

## Implementation Priority

### Phase 1: Core Backend
1. User authentication (register/login)
2. User management
3. Chat CRUD operations
4. Message CRUD operations

### Phase 2: Real-time Features
1. WebSocket integration
2. Real-time messaging
3. Online/offline status
4. Message status updates

### Phase 3: Frontend Integration
1. Replace all mock data with API calls
2. Add authentication context
3. Implement WebSocket client
4. Error handling and loading states

## Authentication Flow
1. User registers/logs in → JWT token returned
2. Token stored in localStorage
3. All API requests include Authorization header
4. Protected routes check for valid token
5. WebSocket connection authenticated with token

## Real-time Messaging Flow
1. User sends message → POST to API → WebSocket broadcast
2. Message delivered → Status update → WebSocket broadcast  
3. Message read → Status update → WebSocket broadcast
4. User online/offline → Status update → WebSocket broadcast