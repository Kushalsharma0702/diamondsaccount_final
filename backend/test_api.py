#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Tax-Ease Backend

Tests all endpoints following a complete user journey:
1. Client registration & OTP verification
2. Client login
3. Client add operation
4. Admin listing clients
5. Chat (client ↔ admin)
6. Document upload
7. T1 form submission
8. Client delete operation

Run: python backend/test_api.py
"""
import time
import sys
import json
from typing import Optional, Dict, Any
import requests
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"
STATIC_OTP = "123456"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.client_token: Optional[str] = None
        self.admin_token: Optional[str] = None
        self.test_user_email = f"testuser_{int(time.time())}@example.com"
        self.test_client_id: Optional[str] = None
        self.passed = 0
        self.failed = 0
        self.test_results = []

    def print_test(self, name: str):
        print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Testing: {name}{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

    def print_pass(self, message: str):
        print(f"{Colors.GREEN}✓ PASS: {message}{Colors.RESET}")
        self.passed += 1
        self.test_results.append(("PASS", message))

    def print_fail(self, message: str, error: str = ""):
        print(f"{Colors.RED}✗ FAIL: {message}{Colors.RESET}")
        if error:
            print(f"  {Colors.RED}Error: {error}{Colors.RESET}")
        self.failed += 1
        self.test_results.append(("FAIL", message, error))

    def print_info(self, message: str):
        print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

    def wait_for_server(self, max_retries: int = 30):
        """Wait for server to be ready."""
        self.print_test("Server Health Check")
        for i in range(max_retries):
            try:
                response = requests.get(f"http://localhost:8001/", timeout=2)
                if response.status_code == 200:
                    self.print_pass("Server is running")
                    return True
            except requests.exceptions.RequestException:
                pass
            if i < max_retries - 1:
                time.sleep(1)
        self.print_fail("Server is not responding")
        return False

    def test_register(self):
        """Test client registration."""
        self.print_test("Client Registration")
        try:
            payload = {
                "email": self.test_user_email,
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-123-4567",
                "password": "TestPassword123!",
                "confirm_password": "TestPassword123!"  # Must match password
            }
            response = requests.post(f"{self.base_url}/auth/register", json=payload, timeout=10)
            if response.status_code == 201:
                data = response.json()
                if "id" in data and data["email"] == self.test_user_email:
                    self.print_pass(f"User registered: {data['email']}")
                    return True
                else:
                    self.print_fail("Registration response missing expected fields")
            else:
                self.print_fail(f"Registration failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("Registration exception", str(e))
        return False

    def test_request_otp(self):
        """Test OTP request (static 123456)."""
        self.print_test("Request OTP")
        try:
            payload = {
                "email": self.test_user_email,
                "purpose": "email_verification"
            }
            response = requests.post(f"{self.base_url}/auth/request-otp", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") is True:
                    self.print_pass("OTP requested (static: 123456)")
                    return True
                else:
                    self.print_fail("OTP request response invalid")
            else:
                self.print_fail(f"OTP request failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("OTP request exception", str(e))
        return False

    def test_verify_otp(self):
        """Test OTP verification with static code."""
        self.print_test("Verify OTP (Static: 123456)")
        try:
            payload = {
                "email": self.test_user_email,
                "code": STATIC_OTP,
                "purpose": "email_verification"
            }
            response = requests.post(f"{self.base_url}/auth/verify-otp", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") is True:
                    self.print_pass("OTP verified successfully")
                    return True
                else:
                    self.print_fail("OTP verification response invalid")
            else:
                self.print_fail(f"OTP verification failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("OTP verification exception", str(e))
        return False

    def test_login(self):
        """Test client login."""
        self.print_test("Client Login")
        try:
            payload = {
                "email": self.test_user_email,
                "password": "TestPassword123!"
            }
            response = requests.post(f"{self.base_url}/auth/login", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.client_token = data["access_token"]
                    self.print_pass(f"Login successful, token received")
                    return True
                else:
                    self.print_fail("Login response missing access_token")
            else:
                self.print_fail(f"Login failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("Login exception", str(e))
        return False

    def test_add_client(self):
        """Test adding a client record."""
        self.print_test("Add Client")
        try:
            payload = {
                "email": self.test_user_email,
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-123-4567",
                "filing_year": 2024
            }
            response = requests.post(f"{self.base_url}/client/add", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_client_id = data["id"]
                    self.print_pass(f"Client added: {data['name']} (ID: {data['id']})")
                    return True
                else:
                    self.print_fail("Add client response missing ID")
            else:
                self.print_fail(f"Add client failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("Add client exception", str(e))
        return False

    def test_admin_list_clients(self):
        """Test admin listing all clients."""
        self.print_test("Admin: List Clients")
        try:
            response = requests.get(f"{self.base_url}/admin/clients", timeout=10)
            if response.status_code == 200:
                clients = response.json()
                if isinstance(clients, list):
                    found = any(c.get("email") == self.test_user_email for c in clients)
                    self.print_pass(f"Found {len(clients)} clients (including test client: {found})")
                    if found:
                        self.print_info(f"Test client in list: {self.test_user_email}")
                    return True
                else:
                    self.print_fail("Admin clients response is not a list")
            else:
                self.print_fail(f"Admin list clients failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("Admin list clients exception", str(e))
        return False

    def test_chat_send_client(self):
        """Test sending a chat message from client side."""
        self.print_test("Chat: Send Message (Client → Admin)")
        if not self.test_client_id:
            self.print_fail("No client ID available")
            return False
        try:
            payload = {
                "client_id": self.test_client_id,
                "message": "Hello from client! This is a test message.",
                "sender_role": "client"
            }
            headers = {}
            if self.client_token:
                headers["Authorization"] = f"Bearer {self.client_token}"
            response = requests.post(f"{self.base_url}/chat/send", json=payload, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                self.print_pass("Chat message sent from client")
                return True
            else:
                self.print_fail(f"Chat send failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("Chat send exception", str(e))
        return False

    def test_chat_send_admin(self):
        """Test sending a chat message from admin side."""
        self.print_test("Chat: Send Message (Admin → Client)")
        if not self.test_client_id:
            self.print_fail("No client ID available")
            return False
        try:
            payload = {
                "client_id": self.test_client_id,
                "message": "Hello from admin! We received your message.",
                "sender_role": "admin"
            }
            headers = {}
            if self.admin_token:
                headers["Authorization"] = f"Bearer {self.admin_token}"
            response = requests.post(f"{self.base_url}/chat/send", json=payload, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                self.print_pass("Chat message sent from admin")
                return True
            else:
                self.print_fail(f"Chat send failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("Chat send exception", str(e))
        return False

    def test_chat_get_messages(self):
        """Test retrieving chat messages for a client."""
        self.print_test("Chat: Get Messages")
        if not self.test_client_id:
            self.print_fail("No client ID available")
            return False
        try:
            headers = {}
            if self.client_token:
                headers["Authorization"] = f"Bearer {self.client_token}"
            response = requests.get(f"{self.base_url}/chat/{self.test_client_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                self.print_pass(f"Retrieved {len(messages)} chat messages")
                if messages:
                    self.print_info(f"Latest message: {messages[-1].get('message', 'N/A')[:50]}...")
                return True
            else:
                self.print_fail(f"Chat get failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("Chat get exception", str(e))
        return False

    def test_document_upload(self):
        """Test document upload."""
        self.print_test("Document Upload")
        if not self.test_client_id:
            self.print_fail("No client ID available")
            return False
        try:
            # Create a dummy PDF file content
            dummy_pdf = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
            files = {
                "file": ("test_document.pdf", dummy_pdf, "application/pdf")
            }
            data = {
                "client_id": self.test_client_id,
                "section": "personal_info",
                "document_type": "receipt"
            }
            headers = {}
            if self.client_token:
                headers["Authorization"] = f"Bearer {self.client_token}"
            response = requests.post(
                f"{self.base_url}/documents/upload",
                files=files,
                data=data,
                headers=headers,
                timeout=10
            )
            if response.status_code in [200, 201]:
                self.print_pass("Document uploaded successfully")
                return True
            else:
                self.print_fail(f"Document upload failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("Document upload exception", str(e))
        return False

    def test_t1_form_submit(self):
        """Test T1 form submission."""
        self.print_test("T1 Form Submission")
        if not self.test_client_id:
            self.print_fail("No client ID available")
            return False
        try:
            payload = {
                "formData": {
                    "id": f"T1_{int(time.time())}",
                    "status": "draft",
                    "personalInfo": {
                        "firstName": "John",
                        "lastName": "Doe",
                        "sin": "123456789",
                        "email": self.test_user_email,
                        "phoneNumber": "+1-555-123-4567",
                        "address": "123 Test St, Toronto, ON",
                        "maritalStatus": "single",
                        "isCanadianCitizen": True
                    },
                    "hasForeignProperty": False,
                    "hasMedicalExpenses": True,
                    "hasCharitableDonations": False,
                    "hasMovingExpenses": False,
                    "isSelfEmployed": False,
                    "isFirstHomeBuyer": False,
                    "wasStudentLastYear": False,
                    "isUnionMember": False,
                    "hasDaycareExpenses": False,
                    "uploadedDocuments": {},
                    "awaitingDocuments": False
                }
            }
            headers = {"Content-Type": "application/json"}
            if self.client_token:
                headers["Authorization"] = f"Bearer {self.client_token}"
            response = requests.post(
                f"{self.base_url}/client/tax-return",
                json=payload,
                headers=headers,
                timeout=10
            )
            if response.status_code in [200, 201]:
                self.print_pass("T1 form submitted successfully")
                return True
            else:
                self.print_fail(f"T1 form submission failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("T1 form submission exception", str(e))
        return False

    def test_delete_client(self):
        """Test deleting a client."""
        self.print_test("Delete Client")
        if not self.test_client_id:
            self.print_fail("No client ID available")
            return False
        try:
            response = requests.delete(f"{self.base_url}/client/{self.test_client_id}", timeout=10)
            if response.status_code in [200, 204]:
                self.print_pass("Client deleted successfully")
                return True
            else:
                self.print_fail(f"Delete client failed", f"Status: {response.status_code}, {response.text}")
        except Exception as e:
            self.print_fail("Delete client exception", str(e))
        return False

    def run_all_tests(self):
        """Run all tests in sequence."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}Tax-Ease Backend API Test Suite{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"\nTest User Email: {self.test_user_email}")
        print(f"Base URL: {self.base_url}\n")

        # Wait for server
        if not self.wait_for_server():
            print(f"\n{Colors.RED}Server is not running. Please start the backend first.{Colors.RESET}")
            print(f"{Colors.YELLOW}Run: uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001{Colors.RESET}")
            return

        # Core flow tests
        self.test_register()
        time.sleep(0.5)
        self.test_request_otp()
        time.sleep(0.5)
        self.test_verify_otp()
        time.sleep(0.5)
        self.test_login()
        time.sleep(0.5)
        self.test_add_client()
        time.sleep(0.5)
        self.test_admin_list_clients()
        time.sleep(0.5)

        # Chat tests
        self.test_chat_send_client()
        time.sleep(0.5)
        self.test_chat_send_admin()
        time.sleep(0.5)
        self.test_chat_get_messages()
        time.sleep(0.5)

        # Document and T1 tests
        self.test_document_upload()
        time.sleep(0.5)
        self.test_t1_form_submit()
        time.sleep(0.5)

        # Cleanup
        self.test_delete_client()

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Test Summary{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


if __name__ == "__main__":
    tester = APITester()
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)
