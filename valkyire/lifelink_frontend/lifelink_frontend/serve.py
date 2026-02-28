import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "."

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print("="*60)
    print(f"🌐 Frontend Server Running")
    print(f"📱 Open: http://localhost:{PORT}/dashboard.html")
    print(f"🤖 Chatbot: http://localhost:{PORT}/../../lifelink_backend/lifelink_backend/chatbot.html")
    print("="*60)
    print("Press Ctrl+C to stop")
    httpd.serve_forever()
