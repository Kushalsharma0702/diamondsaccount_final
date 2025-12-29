# Chat & Communication API Documentation

## Overview

The Chat API enables real-time communication between clients and admins. Messages are stored in the database and can be retrieved, marked as read, and counted for unread notifications.

## API Endpoints

### 1. Send Message

**POST** `/api/v1/chat/send`

Send a chat message from client or admin.

**Request Body:**
```json
{
  "client_id": "uuid",
  "message": "Hello, I have a question about my tax return.",
  "sender_role": "client"  // or "admin"
}
```

**Response:**
```json
{
  "id": "uuid",
  "sender_role": "client",
  "message": "Hello, I have a question about my tax return.",
  "created_at": "2025-12-24T08:00:00",
  "read_by_client": true,
  "read_by_admin": false
}
```

### 2. Get Messages

**GET** `/api/v1/chat/{client_id}`

Get all chat messages for a client, ordered by creation time.

**Response:**
```json
{
  "messages": [
    {
      "id": "uuid",
      "sender_role": "client",
      "message": "Hello",
      "created_at": "2025-12-24T08:00:00",
      "read_by_client": true,
      "read_by_admin": false
    },
    {
      "id": "uuid",
      "sender_role": "admin",
      "message": "Hi! How can I help?",
      "created_at": "2025-12-24T08:05:00",
      "read_by_client": false,
      "read_by_admin": true
    }
  ],
  "total": 2
}
```

### 3. Mark Messages as Read

**PUT** `/api/v1/chat/{client_id}/mark-read?role={role}`

Mark all messages as read for a specific role (client or admin).

**Query Parameters:**
- `role` - Either "client" or "admin"

**Response:**
```json
{
  "message": "Messages marked as read for client"
}
```

### 4. Get Unread Count

**GET** `/api/v1/chat/{client_id}/unread-count?role={role}`

Get count of unread messages for a specific role.

**Query Parameters:**
- `role` - Either "client" or "admin"

**Response:**
```json
{
  "unread_count": 3
}
```

## Flutter Integration

### Chat API Service

Located at: `lib/features/chat/data/chat_api.dart`

**Usage:**
```dart
import 'package:tax_ease_app_client/features/chat/data/chat_api.dart';

// Send a message
final message = await ChatApi.sendMessage(
  clientId: clientId,
  message: "Hello!",
  senderRole: 'client',
);

// Get all messages
final messages = await ChatApi.getMessages(clientId);

// Mark as read
await ChatApi.markAsRead(
  clientId: clientId,
  role: 'client',
);

// Get unread count
final unreadCount = await ChatApi.getUnreadCount(
  clientId: clientId,
  role: 'client',
);
```

### Chat Screen

Located at: `lib/features/chat/presentation/pages/chat_page.dart`

**Navigation:**
```dart
// Navigate to chat
context.go('/chat?clientId=$clientId');

// Or with email (will resolve clientId automatically)
context.go('/chat?email=$userEmail');
```

**Features:**
- Real-time message display
- Auto-refresh every 5 seconds
- Mark messages as read when viewing
- Send messages with send button
- Pull-to-refresh
- Empty state handling
- Error handling

## Database Schema

**Table:** `chat_messages`

- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users table
- `sender_role` (VARCHAR) - "client", "admin", or "superadmin"
- `message` (TEXT) - Message content
- `read_by_client` (BOOLEAN) - Whether client has read
- `read_by_admin` (BOOLEAN) - Whether admin has read
- `created_at` (TIMESTAMP) - Creation time

## Features

### Auto-Refresh

The Flutter chat screen automatically refreshes every 5 seconds to show new messages.

### Read Status

- Messages are marked as read when the chat screen is opened
- Separate read status for client and admin
- Unread count available for notifications

### Message Ordering

Messages are ordered by `created_at` ascending (oldest first).

## Testing

Run the test script:

```bash
python3 backend/test_chat_api.py
```

This tests:
1. Getting client ID
2. Sending message as client
3. Sending message as admin
4. Retrieving all messages
5. Getting unread count
6. Marking messages as read

## Notes

- Client ID can be obtained from `/api/v1/admin/clients` endpoint
- Messages are linked to users via `user_id` (from client's user_id)
- In production, `sender_role` should be extracted from JWT token
- Consider adding WebSocket support for real-time updates




