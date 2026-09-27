import http.server
import socketserver
import os
import cgi
import json
import urllib.parse

PORT = 8085
DIRECTORY = "public"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/upload':
            # Parse the form data posted
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type'],
                         }
            )
            
            uploaded_files = []
            
            for field in form.keys():
                field_item = form[field]
                if field_item.filename:
                    # It's an uploaded file
                    filename = os.path.basename(field_item.filename)
                    # Determine folder based on mime type or extension
                    is_video = filename.lower().endswith(('.mp4', '.mov', '.webm', '.m4v'))
                    folder = 'videos' if is_video else 'photos'
                    filepath = os.path.join(DIRECTORY, folder, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(field_item.file.read())
                        
                    uploaded_files.append({
                        'filename': filename,
                        'folder': folder,
                        'path': f"{folder}/{filename}",
                        'is_video': is_video
                    })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'files': uploaded_files}).encode())
            return
            
        self.send_error(404, "Not Found")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with socketserver.TCPServer(("127.0.0.1", PORT), CustomHandler) as httpd:
    print(f"Serving at http://127.0.0.1:{PORT}")
    httpd.serve_forever()
