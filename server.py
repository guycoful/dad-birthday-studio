import http.server
import socketserver
import os
import json
import urllib.parse

PORT = 8085
DIRECTORY = "public"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path.startswith('/upload'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            filename = params.get('filename', ['uploaded_file'])[0]
            filename = os.path.basename(filename)
            
            is_video = filename.lower().endswith(('.mp4', '.mov', '.webm', '.m4v'))
            folder = 'videos' if is_video else 'photos'
            filepath = os.path.join(DIRECTORY, folder, filename)
            
            length = int(self.headers.get('content-length', 0))
            with open(filepath, 'wb') as f:
                f.write(self.rfile.read(length))
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            uploaded_files = [{
                'filename': filename,
                'folder': folder,
                'path': f"{folder}/{filename}",
                'is_video': is_video
            }]
            
            self.wfile.write(json.dumps({'success': True, 'files': uploaded_files}).encode())
            return
            
        self.send_error(404, "Not Found")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with socketserver.TCPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
    print(f"Serving at http://127.0.0.1:{PORT}")
    httpd.serve_forever()
