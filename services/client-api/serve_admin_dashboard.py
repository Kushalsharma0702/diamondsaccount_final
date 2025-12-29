#!/usr/bin/env python3
"""
Simple HTTP server for admin dashboard with API proxy
Serves static files and proxies API requests to backend
"""
import http.server
import socketserver
import urllib.parse
import urllib.request
import json
import os
from pathlib import Path

# Configuration
PORT = 8080
ADMIN_API_URL = "http://localhost:8002"  # Admin backend API
DASHBOARD_DIR = Path(__file__).parent / "admin-dashboard"


class AdminDashboardHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom handler that:
    1. Serves static files from admin-dashboard directory
    2. Proxies /admin/api/* requests to the admin backend
    3. Adds proper CORS headers
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)
    
    def end_headers(self):
        """Override to prevent duplicate CORS headers - backend handles CORS"""
        # DO NOT add CORS headers here - backend middleware handles them
        # Adding headers here causes double CORS headers and conflicts
        super().end_headers()
    
    def do_OPTIONS(self):
        """Proxy OPTIONS preflight to backend - backend handles CORS"""
        if self.path.startswith('/admin/api/'):
            # Proxy OPTIONS to backend so it can handle CORS properly
            self.proxy_request('OPTIONS')
        else:
            # For static files, just return 200 OK
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        # Proxy API requests to backend
        if self.path.startswith('/admin/api/'):
            self.proxy_request('GET')
        else:
            # Serve static files
            # If root path, serve diamonds-admin.html
            if self.path == '/' or self.path == '/login':
                self.path = '/diamonds-admin.html'
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path.startswith('/admin/api/'):
            self.proxy_request('POST')
        else:
            self.send_error(404)
    
    def do_PUT(self):
        """Handle PUT requests"""
        if self.path.startswith('/admin/api/'):
            self.proxy_request('PUT')
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        if self.path.startswith('/admin/api/'):
            self.proxy_request('DELETE')
        else:
            self.send_error(404)
    
    def do_PATCH(self):
        """Handle PATCH requests"""
        if self.path.startswith('/admin/api/'):
            self.proxy_request('PATCH')
        else:
            self.send_error(404)
    
    def proxy_request(self, method):
        """Proxy request to admin backend API"""
        try:
            # Remove /admin prefix from path for backend
            backend_path = self.path.replace('/admin', '', 1)
            backend_url = f"{ADMIN_API_URL}{backend_path}"
            
            # Read request body for POST/PUT/PATCH
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create request
            req = urllib.request.Request(
                backend_url,
                data=body,
                method=method
            )
            
            # Copy headers
            for header in ['Content-Type', 'Authorization']:
                if header in self.headers:
                    req.add_header(header, self.headers[header])
            
            # Make request to backend
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    # Send response back to client
                    self.send_response(response.status)
                    
                    # Copy response headers
                    for header, value in response.headers.items():
                        if header.lower() not in ['transfer-encoding', 'connection']:
                            self.send_header(header, value)
                    
                    self.end_headers()
                    
                    # Send response body
                    self.wfile.write(response.read())
            
            except urllib.error.HTTPError as e:
                # Forward error response
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(e.read())
        
        except Exception as e:
            print(f"Error proxying request: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({"error": str(e)})
            self.wfile.write(error_response.encode())
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start the server"""
    # Check if dashboard directory exists
    if not DASHBOARD_DIR.exists():
        print(f"❌ Error: Dashboard directory not found: {DASHBOARD_DIR}")
        print(f"   Please ensure admin-dashboard directory exists")
        return
    
    # Check if diamonds-admin.html exists
    admin_html = DASHBOARD_DIR / "diamonds-admin.html"
    if not admin_html.exists():
        print(f"❌ Error: diamonds-admin.html not found in {DASHBOARD_DIR}")
        return
    
    print("=" * 60)
    print("🚀 Admin Dashboard Server Starting...")
    print("=" * 60)
    print(f"📁 Serving from: {DASHBOARD_DIR}")
    print(f"🌐 Dashboard URL: http://localhost:{PORT}")
    print(f"🔗 API Proxy: {ADMIN_API_URL}")
    print("=" * 60)
    print(f"\n✅ Server running on port {PORT}")
    print(f"   Open http://localhost:{PORT} in your browser")
    print("\n📋 Available endpoints:")
    print(f"   - http://localhost:{PORT}/ (Dashboard login)")
    print(f"   - http://localhost:{PORT}/admin/api/* (API proxy)")
    print("\n💡 Press Ctrl+C to stop the server\n")
    
    try:
        with socketserver.TCPServer(("", PORT), AdminDashboardHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {PORT} is already in use")
            print(f"   Please stop the other process or use a different port")
        else:
            print(f"\n❌ Error starting server: {e}")


if __name__ == "__main__":
    main()
