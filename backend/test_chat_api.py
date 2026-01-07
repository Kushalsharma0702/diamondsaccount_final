#!/usr/bin/env python3
"""
Test Chat API endpoints.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

print("=" * 80)
print("TESTING CHAT API")
print("=" * 80)
print()

# Use demo client
demo_email = "demo@taxease.com"

# Step 1: Get client ID
print("=" * 80)
print("STEP 1: Get Client ID")
print("=" * 80)

try:
    clients_response = requests.get(f"{BASE_URL}/admin/clients", timeout=10)
    if clients_response.status_code == 200:
        clients = clients_response.json()
        demo_client = next((c for c in clients if c.get("email") == demo_email), None)
        if demo_client:
            client_id = demo_client["id"]
            print(f"✅ Client ID: {client_id}")
        else:
            print("❌ Demo client not found")
            exit(1)
    else:
        print(f"❌ Failed to get clients: {clients_response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Send message as client
print()
print("=" * 80)
print("STEP 2: Send Message as Client")
print("=" * 80)

try:
    send_response = requests.post(
        f"{BASE_URL}/chat/send",
        json={
            "client_id": client_id,
            "message": "Hello, I have a question about my tax return.",
            "sender_role": "client"
        },
        timeout=10
    )
    
    if send_response.status_code == 201:
        message_data = send_response.json()
        print(f"✅ Message sent:")
        print(f"   ID: {message_data.get('id')}")
        print(f"   Message: {message_data.get('message')}")
        print(f"   Sender: {message_data.get('sender_role')}")
        print(f"   Created: {message_data.get('created_at')}")
    else:
        print(f"❌ Failed to send: {send_response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 3: Send message as admin
print()
print("=" * 80)
print("STEP 3: Send Message as Admin")
print("=" * 80)

try:
    send_response = requests.post(
        f"{BASE_URL}/chat/send",
        json={
            "client_id": client_id,
            "message": "Hello! I'm reviewing your tax return. I'll get back to you soon.",
            "sender_role": "admin"
        },
        timeout=10
    )
    
    if send_response.status_code == 201:
        message_data = send_response.json()
        print(f"✅ Admin message sent:")
        print(f"   Message: {message_data.get('message')}")
        print(f"   Sender: {message_data.get('sender_role')}")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 4: Get all messages
print()
print("=" * 80)
print("STEP 4: Get All Messages")
print("=" * 80)

try:
    messages_response = requests.get(
        f"{BASE_URL}/chat/{client_id}",
        timeout=10
    )
    
    if messages_response.status_code == 200:
        data = messages_response.json()
        messages = data.get('messages', [])
        print(f"✅ Retrieved {len(messages)} messages:")
        for msg in messages:
            sender = "👤 Client" if msg.get('sender_role') == 'client' else "👨‍💼 Admin"
            print(f"   {sender}: {msg.get('message')}")
            print(f"      Time: {msg.get('created_at')}")
    else:
        print(f"❌ Failed to get messages: {messages_response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 5: Get unread count
print()
print("=" * 80)
print("STEP 5: Get Unread Count")
print("=" * 80)

try:
    unread_response = requests.get(
        f"{BASE_URL}/chat/{client_id}/unread-count?role=client",
        timeout=10
    )
    
    if unread_response.status_code == 200:
        data = unread_response.json()
        print(f"✅ Unread messages (client): {data.get('unread_count')}")
except Exception as e:
    print(f"⚠️  Error: {e}")

# Step 6: Mark as read
print()
print("=" * 80)
print("STEP 6: Mark Messages as Read")
print("=" * 80)

try:
    mark_read_response = requests.put(
        f"{BASE_URL}/chat/{client_id}/mark-read?role=client",
        timeout=10
    )
    
    if mark_read_response.status_code == 200:
        print(f"✅ Messages marked as read")
except Exception as e:
    print(f"⚠️  Error: {e}")

print()
print("=" * 80)
print("TESTING COMPLETE")
print("=" * 80)







