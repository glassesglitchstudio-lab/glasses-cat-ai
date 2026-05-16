#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI-PRO-MAX-ENGINE Preview Server
Rootless .venv modunda çalışır.
Mühür: Admin (Berkay) - 2026-05-14
"""
import sys, os, io, json, socketserver, http.server, webbrowser
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PORT = 3456
PROJECT = r'C:\Users\ErCuM\CascadeProjects\niko_ai'
PREVIEW_DIR = os.path.join(PROJECT, '.opencode', 'skills', 'ui-pro-max-engine', 'preview')
INDEX_FILE = os.path.join(PREVIEW_DIR, 'index.html')

os.makedirs(PREVIEW_DIR, exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PREVIEW_DIR, **kwargs)

    def send_head(self):
        path = self.translate_path(self.path)
        if self.path == '/' or self.path == '/index.html':
            if os.path.exists(INDEX_FILE):
                try:
                    with open(INDEX_FILE, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', len(content))
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.end_headers()
                    return content
                except:
                    pass
        return super().send_head()

    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            data = {
                'status': 'ok',
                'engine': 'UI-PRO-MAX-ENGINE',
                'version': '1.0.0',
                'mode': '.venv preview',
                'rootless': True,
                'sealed_by': 'Admin (Berkay)',
                'sealed_date': '2026-05-14'
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
        return super().do_GET()

    def log_message(self, format, *args):
        status = str(args[1])
        icon = 'OK' if status.startswith('2') else 'RD' if status.startswith('3') else 'ER'
        method = args[0]
        path = args[2]
        print(f'  [{icon}] {method} {path} -> {status}')

print(f'''
{"=" * 52}
  UI-PRO-MAX-ENGINE PREVIEW SERVER
  Port: {PORT}
  Mode: .venv (Rootless)
  Status: RUNNING
  URL: http://localhost:{PORT}
{"=" * 52}
  Admin (Berkay) icin muehurlendi - 2026-05-14
{"=" * 52}
''')

try:
    webbrowser.open(f'http://localhost:{PORT}')
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print('\nServer durduruldu.')
