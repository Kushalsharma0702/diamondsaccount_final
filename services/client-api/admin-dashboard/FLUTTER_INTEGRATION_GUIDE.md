# Flutter Integration Guide for Diamonds Accounts Admin System

## Overview
This guide explains how to seamlessly integrate the admin dashboard with Flutter client applications for real-time data synchronization.

## Real-Time Sync Features Implemented

### 1. BroadcastChannel API
- **Purpose**: Cross-tab and cross-window communication
- **Channel Name**: `diamonds-admin-sync`
- **Message Format**:
```javascript
{
  type: 'CLIENT_UPDATED' | 'CLIENT_ADDED' | 'ADMIN_UPDATED' | 'DOCUMENT_STATUS_CHANGED' | 'PAYMENT_STATUS_CHANGED',
  data: { /* relevant data object */ },
  timestamp: Date.now(),
  source: 'admin-dashboard'
}
```

### 2. localStorage Persistence
- **Keys Used**:
  - `diamonds-clients`: Array of client objects
  - `diamonds-admins`: Array of admin objects  
  - `diamonds-next-id`: Next client ID counter

### 3. Real-Time Event Handlers
- `handleClientUpdate(clientData)`: Updates existing client data
- `handleAdminUpdate(adminData)`: Updates existing admin data
- `handleClientAdded(clientData)`: Adds new client to system
- `handleDocumentStatusChange(data)`: Updates document submission status
- `handlePaymentStatusChange(data)`: Updates payment status

## Flutter App Integration Methods

### Method 1: WebView Integration
```dart
// In Flutter app
WebViewController webController = WebViewController()
  ..setJavaScriptMode(JavaScriptMode.unrestricted)
  ..addJavaScriptChannel(
    'admin_dashboard_update',
    onMessageReceived: (JavaScriptMessage message) {
      // Handle admin dashboard updates
      final data = jsonDecode(message.message);
      handleAdminUpdate(data);
    },
  );

// Send data to admin dashboard
webController.runJavaScript('''
  window.postMessage({
    type: 'CLIENT_STATUS_UPDATE',
    payload: {
      clientId: $clientId,
      status: '$newStatus'
    },
    source: 'flutter-app'
  }, '*');
''');
```

### Method 2: HTTP API Integration
```dart
// Flutter HTTP client
class AdminAPI {
  static const String baseUrl = 'http://localhost:3000/api';
  
  // Get client data
  static Future<Map<String, dynamic>> getClient(int clientId) async {
    final response = await http.get(Uri.parse('$baseUrl/clients/$clientId'));
    return jsonDecode(response.body);
  }
  
  // Update client status
  static Future<bool> updateClientStatus(int clientId, String status) async {
    final response = await http.put(
      Uri.parse('$baseUrl/clients/$clientId/status'),
      body: jsonEncode({'status': status}),
      headers: {'Content-Type': 'application/json'},
    );
    return response.statusCode == 200;
  }
  
  // Update document status
  static Future<bool> updateDocumentStatus(int clientId, String docType, bool submitted) async {
    final response = await http.put(
      Uri.parse('$baseUrl/clients/$clientId/documents/$docType'),
      body: jsonEncode({'submitted': submitted}),
      headers: {'Content-Type': 'application/json'},
    );
    return response.statusCode == 200;
  }
}
```

### Method 3: WebSocket Integration
```dart
// Real-time WebSocket connection
class AdminWebSocket {
  late WebSocketChannel channel;
  
  void connect() {
    channel = WebSocketChannel.connect(Uri.parse('ws://localhost:8080/admin-sync'));
    
    channel.stream.listen((message) {
      final data = jsonDecode(message);
      handleRealTimeUpdate(data);
    });
  }
  
  void sendUpdate(Map<String, dynamic> update) {
    channel.sink.add(jsonEncode(update));
  }
  
  void handleRealTimeUpdate(Map<String, dynamic> data) {
    switch (data['type']) {
      case 'CLIENT_UPDATED':
        // Update local client data
        updateLocalClient(data['payload']);
        break;
      case 'DOCUMENT_STATUS_CHANGED':
        // Update document status in UI
        updateDocumentStatus(data['payload']);
        break;
      case 'PAYMENT_STATUS_CHANGED':
        // Update payment status
        updatePaymentStatus(data['payload']);
        break;
    }
  }
}
```

## Admin Dashboard API Endpoints

The admin system provides window-level API endpoints for Flutter integration:

```javascript
// Available API methods
window.adminAPI = {
  getClients: () => AdminSystem.clients,
  getClient: (id) => AdminSystem.clients.find(c => c.id === id),
  updateClient: (id, data) => AdminSystem.updateClient(id, data),
  getDocumentStatus: (clientId) => AdminSystem.getClientDocuments(clientId),
  updateDocumentStatus: (clientId, docType, submitted) => AdminSystem.toggleDocumentStatus(clientId, docType),
  updatePaymentStatus: (clientId, paid) => AdminSystem.updatePaymentStatus(clientId, paid)
};
```

## Real-Time Sync Workflow

### Client Updates from Flutter App:
1. Flutter app makes change (document upload, status update)
2. Flutter sends message to admin dashboard via WebView/API
3. Admin dashboard processes update and triggers `handleFlutterMessage()`
4. Dashboard updates local data and broadcasts change via BroadcastChannel
5. All connected admin tabs receive update and refresh UI
6. Change persisted to localStorage for consistency

### Admin Updates from Dashboard:
1. Admin makes change in dashboard
2. Dashboard updates local data immediately
3. Change broadcasted via BroadcastChannel
4. Flutter app receives message and updates local state
5. Flutter UI refreshes to show new data
6. Change persisted for offline access

## Data Synchronization Events

### Supported Event Types:
- `CLIENT_UPDATED`: Complete client data update
- `CLIENT_ADDED`: New client added to system  
- `CLIENT_DELETED`: Client removed from system
- `ADMIN_UPDATED`: Admin account changes
- `ADMIN_ADDED`: New admin account created
- `ADMIN_DELETED`: Admin account removed
- `DOCUMENT_STATUS_CHANGED`: Document submission status change
- `PAYMENT_STATUS_CHANGED`: Payment received status change

### Event Data Format:
```javascript
{
  type: 'EVENT_TYPE',
  data: {
    // Event-specific data
    clientId?: number,
    adminId?: number,
    docType?: string,
    submitted?: boolean,
    paymentReceived?: boolean
  },
  timestamp: number,
  source: 'admin-dashboard' | 'flutter-app'
}
```

## Flutter Client App Implementation Example

```dart
class ClientDashboard extends StatefulWidget {
  @override
  _ClientDashboardState createState() => _ClientDashboardState();
}

class _ClientDashboardState extends State<ClientDashboard> {
  late WebViewController _webController;
  Map<String, dynamic> clientData = {};
  
  @override
  void initState() {
    super.initState();
    setupWebView();
  }
  
  void setupWebView() {
    _webController = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..addJavaScriptChannel(
        'flutter_handler',
        onMessageReceived: handleAdminMessage,
      )
      ..loadRequest(Uri.parse('file:///admin-dashboard/diamonds-admin.html'));
  }
  
  void handleAdminMessage(JavaScriptMessage message) {
    final data = jsonDecode(message.message);
    
    switch (data['type']) {
      case 'CLIENT_UPDATED':
        setState(() {
          clientData = data['payload'];
        });
        showSnackBar('Your information has been updated');
        break;
        
      case 'DOCUMENT_STATUS_CHANGED':
        updateDocumentUI(data['payload']);
        break;
        
      case 'PAYMENT_STATUS_CHANGED':
        updatePaymentUI(data['payload']);
        break;
    }
  }
  
  void submitDocument(String docType, File document) async {
    // Upload document logic here
    
    // Notify admin dashboard
    _webController.runJavaScript('''
      window.postMessage({
        type: 'DOCUMENT_UPLOAD',
        payload: {
          clientId: ${widget.clientId},
          docType: '$docType',
          submitted: true
        },
        source: 'flutter-app'
      }, '*');
    ''');
  }
  
  void updateDocumentUI(Map<String, dynamic> data) {
    setState(() {
      // Update document status in UI
    });
    showSnackBar('Document status updated');
  }
  
  void updatePaymentUI(Map<String, dynamic> data) {
    setState(() {
      // Update payment status in UI  
    });
    showSnackBar('Payment status updated');
  }
}
```

## Testing Real-Time Sync

### Manual Testing:
1. Open admin dashboard in multiple tabs
2. Open Flutter app with WebView integration
3. Make changes in admin dashboard
4. Verify changes appear in other tabs and Flutter app
5. Make changes in Flutter app
6. Verify changes appear in admin dashboard

### Automated Testing:
```javascript
// Test sync functionality
function testRealTimeSync() {
  // Simulate Flutter app message
  window.postMessage({
    type: 'CLIENT_STATUS_UPDATE',
    payload: {
      clientId: 671,
      status: 'completed'
    },
    source: 'flutter-app'
  }, '*');
  
  // Check if admin dashboard updated
  setTimeout(() => {
    const client = AdminSystem.clients.find(c => c.id === 671);
    console.assert(client.status === 'completed', 'Client status not updated');
  }, 100);
}
```

## Security Considerations

1. **Origin Validation**: Verify message origins in production
2. **Data Sanitization**: Validate all incoming data
3. **Authentication**: Ensure proper authentication for API endpoints
4. **Rate Limiting**: Implement rate limiting for real-time updates

## Performance Optimization

1. **Debouncing**: Debounce rapid updates to prevent UI thrashing
2. **Selective Updates**: Only update changed fields instead of full objects
3. **Caching**: Cache frequently accessed data locally
4. **Connection Management**: Handle WebSocket reconnection gracefully

## Troubleshooting

### Common Issues:
1. **Messages not received**: Check origin validation and channel names
2. **Data not persisting**: Verify localStorage is available and not full
3. **UI not updating**: Ensure `refreshCurrentView()` is called after updates
4. **Performance issues**: Check for excessive update frequency

### Debug Tools:
```javascript
// Enable debug mode
AdminSystem.debugMode = true;

// Log all sync messages
AdminSystem.syncChannel.addEventListener('message', (event) => {
  console.log('Sync Message:', event.data);
});

// Check localStorage data
console.log('Clients:', JSON.parse(localStorage.getItem('diamonds-clients')));
console.log('Admins:', JSON.parse(localStorage.getItem('diamonds-admins')));
```

## Next Steps

1. **Implement WebView Integration**: Add WebView to Flutter app with JavaScript channels
2. **Create HTTP API Server**: Set up Express.js server for REST API endpoints  
3. **Add WebSocket Support**: Implement WebSocket server for real-time communication
4. **Database Integration**: Connect to PostgreSQL/MongoDB for persistent storage
5. **Authentication System**: Implement JWT-based authentication
6. **Push Notifications**: Add push notifications for important updates
7. **Offline Support**: Implement offline sync capabilities
8. **Testing Suite**: Create comprehensive test suite for all integrations

This real-time sync system ensures that changes made on the admin side are immediately reflected on the client side, providing a seamless user experience across all connected devices and applications.
