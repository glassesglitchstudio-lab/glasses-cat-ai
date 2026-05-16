#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
Venv UI-Previewer v1.0.0
=========================
UI-PRO-MAX-ENGINE önizleme sunucusu.
.venv sanal ortamında, Root Mode gerektirmeden çalışır.
Obsidian hafıza ile entegredir.

Kullanım:
    python scripts/preview.py              # Varsayılan port 3456
    python scripts/preview.py --port 8080  # Özel port
    python scripts/preview.py --build      # Build + preview

Mühür: Admin (Berkay) - 2026-05-14
"""

import http.server
import socketserver
import os
import sys
import json
import webbrowser
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# === KONFİGÜRASYON ===
DEFAULT_PORT = 3456
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SKILL_DIR = PROJECT_ROOT / '.opencode' / 'skills' / 'ui-pro-max-engine'
PREVIEW_DIR = SKILL_DIR / 'preview'
TEMPLATES_DIR = SKILL_DIR / 'templates'

# === OBSIDIAN HAFIZA ENTEGRASYONU ===
def log_to_obsidian(action, details=""):
    """Önizleme aktivitelerini Obsidian hafızaya kaydet."""
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from obsidian_memory import get_obsidian_memory
        m = get_obsidian_memory()
        m.save_memory(
            f"UI-Preview_{datetime.now().strftime('%H%M%S')}",
            f"**{action}**: {details}",
            tags=["ui-pro-max-engine", "preview", "venv"]
        )
    except Exception as e:
        print(f"[Obsidian] Log atlandı: {e}")

# === HTTP SUNUCU ===
class UIPreviewHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        os.makedirs(str(PREVIEW_DIR), exist_ok=True)
        super().__init__(*args, directory=str(PREVIEW_DIR), **kwargs)

    def do_GET(self):
        if self.path == '/api/health':
            self._send_json({
                'status': 'ok',
                'engine': 'UI-PRO-MAX-ENGINE',
                'version': '1.0.0',
                'mode': '.venv preview',
                'rootless': True,
                'capabilities': [
                    'framer-motion-architect',
                    'tailwind-neon-orange-stylist',
                    'glassmorphism-master',
                    'venv-ui-previewer'
                ],
                'sealed_by': 'Admin (Berkay)',
                'sealed_date': '2026-05-14'
            })
            return
        
        if self.path == '/api/capabilities':
            self._send_json({
                'framer-motion': {
                    'status': 'ready',
                    'spring_defaults': {'stiffness': 260, 'damping': 20}
                },
                'neon-orange': {
                    'primary': '#FF6B00',
                    'status': 'ready'
                },
                'glassmorphism': {
                    'blur': '16px',
                    'opacity': '0.08',
                    'status': 'ready'
                }
            })
            return
        
        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else b'{}'
        
        if self.path == '/api/preview':
            try:
                data = json.loads(body)
                html = self._generate_preview_html(data)
                preview_file = PREVIEW_DIR / 'generated_preview.html'
                with open(str(preview_file), 'w', encoding='utf-8') as f:
                    f.write(html)
                self._send_json({
                    'success': True,
                    'url': f'http://localhost:{self.server.server_address[1]}/generated_preview.html'
                })
                log_to_obsidian("preview_generated", f"Component preview: {data.get('type', 'unknown')}")
            except Exception as e:
                self._send_json({'success': False, 'error': str(e)}, 500)
            return
        
        self.send_error(404)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _generate_preview_html(self, data):
        """Dinamik UI önizleme HTML'i oluştur."""
        component_type = data.get('type', 'glass-card')
        neon_color = data.get('neonColor', '#FF6B00')
        blur_level = data.get('blur', '16px')
        
        return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UI-PRO-MAX-ENGINE Preview</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        neon: {{ orange: '{neon_color}', 'orange-light': '#FF8C38', 'orange-dark': '#CC5500' }},
                        dark: {{ bg: '#0A0A0F', card: '#12121A', surface: '#1A1A26' }}
                    }},
                    boxShadow: {{
                        'neon-orange': '0 0 15px rgba(255, 107, 0, 0.3), 0 0 30px rgba(255, 107, 0, 0.1)',
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{
            background: #0A0A0F;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }}
        .glass {{
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur({blur_level});
            -webkit-backdrop-filter: blur({blur_level});
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        }}
        .glass-neon {{
            background: linear-gradient(135deg, rgba(255, 107, 0, 0.12), rgba(255, 255, 255, 0.06), rgba(255, 107, 0, 0.04));
            backdrop-filter: blur({blur_level});
            border: 1px solid rgba(255, 107, 0, 0.2);
        }}
        .neon-glow {{
            box-shadow: 0 0 15px rgba(255, 107, 0, 0.3), 0 0 30px rgba(255, 107, 0, 0.1);
        }}
        @keyframes neon-pulse {{
            0%, 100% {{ box-shadow: 0 0 5px rgba(255, 107, 0, 0.3), 0 0 10px rgba(255, 107, 0, 0.1); }}
            50% {{ box-shadow: 0 0 15px rgba(255, 107, 0, 0.5), 0 0 30px rgba(255, 107, 0, 0.2); }}
        }}
        .animate-neon {{ animation: neon-pulse 2s ease-in-out infinite; }}
        .gradient-top {{
            background: linear-gradient(90deg, transparent, {neon_color}, transparent);
        }}
    </style>
</head>
<body>
    <div class="w-full max-w-4xl p-8 space-y-8">
        <!-- Header -->
        <div class="glass-neon p-6 text-center">
            <div class="gradient-top h-0.5 w-full mb-4" style="width: 100%; height: 2px;"></div>
            <h1 class="text-3xl font-bold text-white mb-2">UI-PRO-MAX-ENGINE</h1>
            <p class="text-gray-400">Admin (Berkay) için mühürlendi • 2026-05-14</p>
        </div>

        <!-- Ana İçerik -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Glass Kart -->
            <div class="glass p-8 hover:scale-[1.02] transition-transform duration-300 cursor-pointer">
                <div class="gradient-top h-0.5 w-1/3 mb-4" style="height: 2px;"></div>
                <h2 class="text-xl font-bold text-white mb-2">✨ Glassmorphism</h2>
                <p class="text-gray-400 text-sm">Buzlu cam efekti • blur({blur_level})</p>
                <div class="mt-4 flex gap-2">
                    <span class="px-3 py-1 rounded-full bg-white/5 text-xs text-neon-orange border border-neon-orange/20">glass</span>
                    <span class="px-3 py-1 rounded-full bg-white/5 text-xs text-gray-400 border border-white/10">modern</span>
                </div>
            </div>

            <!-- Neon Kart -->
            <div class="glass-neon p-8 animate-neon hover:scale-[1.02] transition-transform duration-300 cursor-pointer">
                <div class="gradient-top h-0.5 w-1/3 mb-4" style="height: 2px;"></div>
                <h2 class="text-xl font-bold text-white mb-2">🔥 Neon Orange</h2>
                <p class="text-gray-400 text-sm">Renk: {neon_color} • Neon parıltı</p>
                <button class="mt-4 px-6 py-2 rounded-xl bg-neon-orange text-white font-semibold neon-glow hover:brightness-110 transition-all duration-300">
                    Neon Buton
                </button>
            </div>

            <!-- Derinlik Kartı -->
            <div class="glass p-8 relative overflow-hidden group cursor-pointer">
                <div class="absolute inset-0 bg-gradient-to-b from-neon-orange/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <div class="relative z-10">
                    <h2 class="text-xl font-bold text-white mb-2">📐 Derinlik Efekti</h2>
                    <p class="text-gray-400 text-sm">Hover'da neon gradient katman</p>
                </div>
            </div>

            <!-- Animasyon Kartı -->
            <div class="glass p-8 group cursor-pointer">
                <h2 class="text-xl font-bold text-white mb-2">🎯 Spring Animasyon</h2>
                <p class="text-gray-400 text-sm">Framer-Motion hazır (stiffness: 260, damping: 20)</p>
                <div class="mt-4 w-12 h-12 rounded-lg bg-neon-orange/20 border border-neon-orange/30 group-hover:translate-x-20 transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]"></div>
            </div>
        </div>

        <!-- Statü Bar -->
        <div class="glass p-4 flex items-center justify-between text-sm">
            <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                <span class="text-gray-400">.venv Preview • Rootless Mode</span>
            </div>
            <span class="text-gray-500">UI-PRO-MAX-ENGINE v1.0.0</span>
        </div>
    </div>
</body>
</html>"""

    def log_message(self, format, *args):
        status = args[1]
        icon = "✅" if status.startswith("2") else "⚠️" if status.startswith("3") else "❌"
        print(f"  {icon} [{self.address_string()}] {args[0]} {status}")


# === ANA ÇALIŞTIRICI ===
def ensure_dependencies():
    """Gerekli bağımlılıkları kontrol et."""
    print("🔍 Bağımlılıklar kontrol ediliyor...")
    
    # Node modülleri kontrol
    node_modules = PROJECT_ROOT / 'node_modules'
    if not (node_modules / 'framer-motion').exists():
        print("  ⚠️  framer-motion bulunamadı. 'npm install framer-motion' önerilir.")
    else:
        print("  ✅ framer-motion hazır")
    
    print()

def create_default_preview():
    """Varsayılan preview HTML'ini oluştur."""
    os.makedirs(str(PREVIEW_DIR), exist_ok=True)
    
    preview_html = PREVIEW_DIR / 'index.html'
    if not preview_html.exists():
        # Kendi endpoint'imizi kullanarak varsayılan sayfayı oluştur
        handler = UIPreviewHandler
        html = handler._generate_preview_html(handler, {})
        with open(str(preview_html), 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  📄 Varsayılan preview oluşturuldu: {preview_html}")

def start_server(port):
    """Sunucuyu başlat."""
    print(f"""
╔══════════════════════════════════════════════════╗
║         🚀 UI-PRO-MAX-ENGINE PREVIEW            ║
║──────────────────────────────────────────────────║
║  • Port:       {port}                               ║
║  • Mode:       .venv (Rootless)                    ║
║  • Engine:     UI-PRO-MAX-ENGINE v1.0.0            ║
║  • Mühür:      Admin (Berkay) • 2026-05-14         ║
║──────────────────────────────────────────────────║
║  🔗 http://localhost:{port}                        ║
║  💚 Health: http://localhost:{port}/api/health      ║
║──────────────────────────────────────────────────║
║  Yetenekler:                                      ║
║  ✅ Framer-Motion Architect                       ║
║  ✅ Tailwind Neon-Orange Stylist                  ║
║  ✅ Glassmorphism Master                          ║
║  ✅ Venv UI-Previewer                             ║
╚══════════════════════════════════════════════════╝
    """)
    
    log_to_obsidian("server_started", f"UI-PRO-MAX-ENGINE preview başlatıldı (port: {port})")
    
    with socketserver.TCPServer(("", port), UIPreviewHandler) as httpd:
        webbrowser.open(f'http://localhost:{port}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  👋 Sunucu durduruldu.")
            log_to_obsidian("server_stopped", "UI preview sunucusu durduruldu")
            httpd.shutdown()


def main():
    parser = argparse.ArgumentParser(description='UI-PRO-MAX-ENGINE Preview Server')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Sunucu portu (varsayılan: {DEFAULT_PORT})')
    parser.add_argument('--build', action='store_true', help='UI build al ve preview yap')
    args = parser.parse_args()
    
    print("🛠️  UI-PRO-MAX-ENGINE başlatılıyor...")
    ensure_dependencies()
    create_default_preview()
    start_server(args.port)


if __name__ == "__main__":
    main()
