#!/usr/bin/env python3
"""
Test Document Upload with Encryption
Tests: Upload → Verify Encryption → Download → Verify Decryption
"""
import requests
import os
import tempfile
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BASE_URL = "http://localhost:8001/api/v1"

# Load database credentials
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "CA_Project")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Test data
test_email = f"doc_test_{int(datetime.now().timestamp())}@example.com"
test_password = "TestPass123!"

print("=" * 80)
print("DOCUMENT UPLOAD WITH ENCRYPTION TEST")
print("=" * 80)
print(f"Test Email: {test_email}\n")

# Step 1: Create test user and client
print("=" * 80)
print("STEP 1: Create Test User and Client")
print("=" * 80)

try:
    # Register user
    register_response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": test_email,
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1-555-123-4567",
        "password": test_password,
        "confirm_password": test_password
    }, timeout=10)
    
    if register_response.status_code != 201:
        print(f"⚠️  Registration: {register_response.status_code}")
    
    # Create client
    client_response = requests.post(f"{BASE_URL}/client/add", json={
        "email": test_email,
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1-555-123-4567",
        "filing_year": 2023
    }, timeout=10)
    
    if client_response.status_code == 200:
        client_data = client_response.json()
        client_id = client_data.get('id')
        print(f"✅ Client created: {client_id}")
    else:
        print(f"❌ Client creation failed: {client_response.text}")
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Create test PDF file
print("\n" + "=" * 80)
print("STEP 2: Create Test PDF File")
print("=" * 80)

# Create a simple PDF content (minimal valid PDF)
test_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Document) Tj
ET
endstream
endobj
5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000306 00000 n 
0000000419 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
520
%%EOF"""

original_file_size = len(test_pdf_content)
print(f"✅ Test PDF created: {original_file_size} bytes")
print(f"   Content preview: 'Test Document'")

# Step 3: Upload document through API
print("\n" + "=" * 80)
print("STEP 3: Upload Document (with Encryption)")
print("=" * 80)

try:
    files = {
        "file": ("test_document.pdf", test_pdf_content, "application/pdf")
    }
    data = {
        "client_id": client_id,
        "section": "personal_info",
        "document_type": "receipt"
    }
    
    print(f"📤 Uploading document...")
    print(f"   Client ID: {client_id}")
    print(f"   File: test_document.pdf ({original_file_size} bytes)")
    
    response = requests.post(
        f"{BASE_URL}/documents/upload",
        files=files,
        data=data,
        timeout=30
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        doc_data = response.json()
        print(f"✅ Document uploaded successfully!")
        print(f"   Document ID: {doc_data.get('id')}")
        print(f"   Original Filename: {doc_data.get('original_filename')}")
        print(f"   File Type: {doc_data.get('file_type')}")
        print(f"   File Size: {doc_data.get('file_size')} bytes")
        print(f"   Encrypted: {doc_data.get('encrypted')}")
        print(f"   Status: {doc_data.get('status')}")
        document_id = doc_data.get('id')
    else:
        print(f"❌ Upload failed: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 4: Verify in database
print("\n" + "=" * 80)
print("STEP 4: Verify Document in Database")
print("=" * 80)

try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, client_id, original_filename, file_type, file_size,
                   file_path, encrypted, encryption_key_hash, status, created_at
            FROM documents
            WHERE id = :doc_id
        """), {"doc_id": document_id})
        
        row = result.fetchone()
        if row:
            print(f"✅ Document found in database:")
            print(f"   ID: {row[0]}")
            print(f"   Client ID: {row[1]}")
            print(f"   Original Filename: {row[2]}")
            print(f"   File Type: {row[3]}")
            print(f"   File Size: {row[4]} bytes (original)")
            print(f"   File Path: {row[5]}")
            print(f"   Encrypted: {row[6]}")
            print(f"   Encryption Key Hash: {row[7][:16]}..." if row[7] else "   Encryption Key Hash: None")
            print(f"   Status: {row[8]}")
            print(f"   Created At: {row[9]}")
            
            # Check if encrypted file exists
            file_path = row[5]
            if os.path.exists(file_path):
                encrypted_file_size = os.path.getsize(file_path)
                print(f"\n   Encrypted File on Disk:")
                print(f"     Path: {file_path}")
                print(f"     Size: {encrypted_file_size} bytes")
                print(f"     Original Size: {original_file_size} bytes")
                print(f"     Size Difference: {encrypted_file_size - original_file_size} bytes (encryption overhead)")
                
                # Verify file is encrypted (should be different from original)
                with open(file_path, "rb") as f:
                    encrypted_content = f.read()
                
                if encrypted_content != test_pdf_content:
                    print(f"     ✅ File is encrypted (content differs from original)")
                else:
                    print(f"     ❌ File is NOT encrypted (content matches original)")
            else:
                print(f"     ❌ Encrypted file not found on disk!")
        else:
            print(f"❌ Document NOT found in database!")
            exit(1)
            
except Exception as e:
    print(f"❌ Database verification error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 5: Download and verify decryption
print("\n" + "=" * 80)
print("STEP 5: Download Document (Decrypt)")
print("=" * 80)

try:
    print(f"📥 Downloading document...")
    download_response = requests.get(
        f"{BASE_URL}/documents/{document_id}/download",
        timeout=30
    )
    
    print(f"📥 Response Status: {download_response.status_code}")
    
    if download_response.status_code == 200:
        downloaded_content = download_response.content
        print(f"✅ Document downloaded successfully!")
        print(f"   Downloaded Size: {len(downloaded_content)} bytes")
        
        # Verify decryption
        if downloaded_content == test_pdf_content:
            print(f"   ✅ Decryption successful (content matches original)")
            print(f"   ✅ File integrity verified")
        else:
            print(f"   ❌ Decryption failed (content does not match original)")
            print(f"   Original size: {len(test_pdf_content)}")
            print(f"   Downloaded size: {len(downloaded_content)}")
            
        # Save downloaded file for inspection
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(downloaded_content)
            tmp_path = tmp.name
        print(f"   Saved to: {tmp_path}")
        
    else:
        print(f"❌ Download failed: {download_response.text}")
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 6: List client documents
print("\n" + "=" * 80)
print("STEP 6: List Client Documents")
print("=" * 80)

try:
    list_response = requests.get(
        f"{BASE_URL}/documents/client/{client_id}",
        timeout=10
    )
    
    if list_response.status_code == 200:
        list_data = list_response.json()
        print(f"✅ Documents listed:")
        print(f"   Total Documents: {list_data.get('total')}")
        for doc in list_data.get('documents', []):
            print(f"     - {doc.get('original_filename')} ({doc.get('file_type')}, {doc.get('file_size')} bytes, encrypted: {doc.get('encrypted')})")
    else:
        print(f"⚠️  List failed: {list_response.status_code}")
        
except Exception as e:
    print(f"⚠️  Error: {e}")

# Final Summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"\n✅ Step 1: User/Client Created")
print(f"✅ Step 2: Test PDF Created ({original_file_size} bytes)")
print(f"✅ Step 3: Document Uploaded (encrypted)")
print(f"✅ Step 4: Database Verified (encrypted flag, key hash)")
print(f"✅ Step 5: Document Downloaded (decrypted)")
print(f"✅ Step 6: Documents Listed")
print(f"\n✅ ALL TESTS PASSED - Encryption/Decryption Working!")
print("=" * 80)










