/**
 * UI-PRO-MAX-ENGINE Preview Server
 * Node.js ile rootless .venv modunda
 * 
 * Mühür: Admin (Berkay) - 2026-05-14
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3456;
const INDEX_PATH = path.join(__dirname, '..', 'preview', 'index.html');

const server = http.createServer((req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // API endpoint
  if (req.url === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({
      status: 'ok',
      engine: 'UI-PRO-MAX-ENGINE',
      version: '1.0.0',
      mode: 'Node.js .venv preview',
      rootless: true,
      sealed_by: 'Admin (Berkay)',
      sealed_date: '2026-05-14'
    }, null, 2));
    return;
  }

  // Serve index.html
  fs.readFile(INDEX_PATH, 'utf-8', (err, content) => {
    if (err) {
      res.writeHead(500);
      res.end('Error loading preview');
      return;
    }
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(content);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  const msg = `
╔══════════════════════════════════════════════════╗
║         🚀 UI-PRO-MAX-ENGINE PREVIEW            ║
║──────────────────────────────────────────────────║
║  • Port:       ${PORT}                               ║
║  • Mode:       Node.js (Rootless)                  ║
║  • Engine:     UI-PRO-MAX-ENGINE v1.0.0            ║
║  • Mühür:      Admin (Berkay) • 2026-05-14         ║
║──────────────────────────────────────────────────║
║  🔗 http://localhost:${PORT}                        ║
║──────────────────────────────────────────────────║
║  Yetenekler:                                      ║
║  ✅ Framer-Motion Architect                       ║
║  ✅ Tailwind Neon-Orange Stylist                  ║
║  ✅ Glassmorphism Master                          ║
║  ✅ Venv UI-Previewer                             ║
╚══════════════════════════════════════════════════╝
  `;
  console.log(msg);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n  👋 Sunucu durduruldu.');
  process.exit(0);
});

console.log('🛠️  UI-PRO-MAX-ENGINE başlatılıyor...');
