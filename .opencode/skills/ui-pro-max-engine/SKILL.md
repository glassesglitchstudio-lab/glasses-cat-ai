---
name: ui-pro-max-engine
description: >
  UI-PRO-MAX-ENGINE: Modern UI mimarisi için dört yetenekli motor.
  Framer-Motion spring animasyonları, Tailwind neon-turuncu stil,
  Glassmorphism buzlu cam efektleri ve .venv içinde önizleme.
---

# 🚀 UI-PRO-MAX-ENGINE

**Mühür Tarihi:** 2026-05-14
**Mühürleyen:** Admin (Berkay)
**Durum:** ✅ AKTİF

Modern UI mimarisi için 4 ana yetenekten oluşan motor.

---

## 📋 İçindekiler

1. [Framer-Motion Architect](#-framer-motion-architect)
2. [Tailwind Neon-Orange Stylist](#-tailwind-neon-orange-stylist)
3. [Glassmorphism Master](#-glassmorphism-master)
4. [Venv UI-Previewer](#-venv-ui-previewer)
5. [Kullanım Akışı](#-kullanım-akışı)
6. [Hızlı Başlangıç](#-hızlı-başlangıç)

---

## 🎯 Framer-Motion Architect

**Yay (Spring) efektli, pürüzsüz sayfa geçişleri ve element animasyonları.**

### Temel Animasyonlar

```jsx
// Spring geçişi - sayfa/page geçişleri için
const pageTransition = {
  type: "spring",
  stiffness: 260,
  damping: 20,
  mass: 1
}

// Element giriş animasyonu
const fadeInUp = {
  initial: { opacity: 0, y: 60 },
  animate: { opacity: 1, y: 0 },
  transition: { type: "spring", stiffness: 260, damping: 20 }
}

// Hover animasyonu - glassmorphism kartlar için
const glassHover = {
  whileHover: { scale: 1.02, backdropFilter: "blur(12px)" },
  transition: { type: "spring", stiffness: 400, damping: 10 }
}
```

### Sayfa Geçiş Şablonu

```jsx
// pages/_app.js veya layout.js
import { motion, AnimatePresence } from "framer-motion"

export default function App({ Component, pageProps, router }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={router.route}
        initial={{ opacity: 0, x: 100 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -100 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
      >
        <Component {...pageProps} />
      </motion.div>
    </AnimatePresence>
  )
}
```

### Kullanım Kılavuzu

| Animasyon Türü | Spring Değerleri | Kullanım Yeri |
|---------------|------------------|---------------|
| Sayfa Geçişi | stiffness: 260, damping: 20 | Route değişimleri |
| Kart Hover | stiffness: 400, damping: 10 | Glassmorphism kartlar |
| Liste Stagger | stiffness: 300, damping: 15 | Listeler, gridler |
| Modal Açılış | stiffness: 200, damping: 25 | Modal, drawer |
| Buton Press | stiffness: 500, damping: 5 | Buton, tıklanabilir |

---

## 🎨 Tailwind Neon-Orange Stylist

**Neon turuncu detaylarla süslenmiş, modern arayüz tasarımı.**

### Renk Paleti

```css
/* tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      colors: {
        neon: {
          orange: '#FF6B00',
          'orange-light': '#FF8C38',
          'orange-dark': '#CC5500',
          glow: '#FF6B00',
        },
        glass: {
          light: 'rgba(255, 255, 255, 0.15)',
          medium: 'rgba(255, 255, 255, 0.10)',
          heavy: 'rgba(255, 255, 255, 0.05)',
          border: 'rgba(255, 255, 255, 0.18)',
        },
        dark: {
          bg: '#0A0A0F',
          card: '#12121A',
          surface: '#1A1A26',
        }
      },
      boxShadow: {
        'neon-orange': '0 0 15px rgba(255, 107, 0, 0.3), 0 0 30px rgba(255, 107, 0, 0.1)',
        'neon-orange-sm': '0 0 8px rgba(255, 107, 0, 0.25)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.3)',
      }
    }
  }
}
```

### Neon Turuncu Bileşenler

```jsx
// Neon Buton
<button className="
  px-6 py-3 rounded-xl 
  bg-neon-orange text-white font-semibold
  shadow-neon-orange
  hover:bg-neon-orange-light hover:shadow-neon-orange
  transition-all duration-300
  cursor-pointer
">
  Neon Action
</button>

// Neon Vurgulu Kart
<div className="
  relative p-6 rounded-2xl
  bg-dark-card border border-glass-border
  backdrop-blur-xl
  before:absolute before:inset-0
  before:rounded-2xl before:opacity-0
  before:shadow-[inset_0_0_20px_rgba(255,107,0,0.05)]
  hover:before:opacity-100
  transition-all duration-300
">
  <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-neon-orange to-transparent" />
  {children}
</div>
```

### Neon Glow Efektleri

```css
/* Neon parıltı animasyonu */
@keyframes neon-pulse {
  0%, 100% { 
    box-shadow: 0 0 5px rgba(255, 107, 0, 0.3),
                0 0 10px rgba(255, 107, 0, 0.1); 
  }
  50% { 
    box-shadow: 0 0 15px rgba(255, 107, 0, 0.5),
                0 0 30px rgba(255, 107, 0, 0.2),
                0 0 45px rgba(255, 107, 0, 0.1); 
  }
}

.neon-pulse {
  animation: neon-pulse 2s ease-in-out infinite;
}
```

---

## 🪟 Glassmorphism Master

**Buzlu cam (frosted glass) efektli, modern derinlikte paneller.**

### Core Glassmorphism CSS

```css
/* Ana glassmorphism karışımı */
.glass {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

/* Yoğun glass - ön plan kartlar için */
.glass-heavy {
  background: rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* Hafif glass - arka plan katmanlar için */
.glass-light {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
```

### Gradient Glass Varyasyonları

```css
/* Neon turuncu gradient glass */
.glass-neon {
  background: linear-gradient(
    135deg,
    rgba(255, 107, 0, 0.12) 0%,
    rgba(255, 255, 255, 0.06) 50%,
    rgba(255, 107, 0, 0.04) 100%
  );
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 107, 0, 0.2);
}

/* Çift katmanlı glass (derinlik efekti) */
.glass-deep {
  position: relative;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
      180deg,
      rgba(255, 107, 0, 0.05) 0%,
      transparent 100%
    );
    border-radius: inherit;
    pointer-events: none;
  }
}
```

### Tailwind Glassmorphism Utility

```js
// tailwind.config.js - glassmorphism utilities ekle
module.exports = {
  theme: {
    extend: {
      backdropBlur: {
        'glass': '16px',
        'glass-heavy': '20px',
      }
    }
  },
  plugins: [
    function({ addUtilities }) {
      addUtilities({
        '.glass': {
          background: 'rgba(255, 255, 255, 0.08)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: '16px',
        },
        '.glass-neon': {
          background: 'linear-gradient(135deg, rgba(255, 107, 0, 0.12), rgba(255, 255, 255, 0.06), rgba(255, 107, 0, 0.04))',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 107, 0, 0.2)',
        }
      })
    }
  ]
}
```

---

## 🖥️ Venv UI-Previewer

**.venv sanal ortamında, Root Mode gerektirmeden UI önizlemesi.**

### Python Preview Sunucusu

```python
# scripts/preview.py
#!/usr/bin/env python3
"""
Venv UI-Previewer: .venv içinde canlı UI önizleme sunucusu.
Root Mode gerektirmez, doğrudan sanal ortamda çalışır.
"""
import http.server
import socketserver
import os
import sys
import json
import webbrowser
from pathlib import Path

PORT = 3456
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
UI_DIR = PROJECT_ROOT / '.opencode' / 'skills' / 'ui-pro-max-engine' / 'preview'

class UIPreviewHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)
    
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'engine': 'UI-PRO-MAX-ENGINE',
                'mode': '.venv preview',
                'rootless': True
            }).encode())
            return
        return super().do_GET()
    
    def log_message(self, format, *args):
        print(f"[UI-Previewer] {args[0]} {args[1]} {args[2]}")

def start_preview():
    """UI önizleme sunucusunu başlat."""
    os.makedirs(UI_DIR, exist_ok=True)
    
    with socketserver.TCPServer(("", PORT), UIPreviewHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"""
╔══════════════════════════════════════════════╗
║        UI-PRO-MAX-ENGINE PREVIEW            ║
║──────────────────────────────────────────────║
║  • Port:    {PORT}                             ║
║  • Mode:    .venv (Rootless)                  ║
║  • Status:  🟢 ÇALIŞIYOR                       ║
║──────────────────────────────────────────────║
║  {url}  ║
╚══════════════════════════════════════════════╝
        """)
        webbrowser.open(url)
        httpd.serve_forever()

if __name__ == "__main__":
    start_preview()
```

### Kullanım

```bash
# .venv ile UI önizleme başlat
python .opencode/skills/ui-pro-max-engine/scripts/preview.py

# Tarayıcıda aç: http://localhost:3456
```

---

## 🔧 Kullanım Akışı

### Bir UI Talebi Geldiğinde

```
1. KULLANICI İSTEĞİ
   ↓
2. ANALİZ: Gereksinimleri belirle (sayfa tipi, bileşenler, efektler)
   ↓
3. TASARIM: Glassmorphism + Neon Orange kombinasyonu
   ↓
4. ANİMASYON: Framer-Motion spring efektleri ekle
   ↓
5. ÖNİZLEME: Venv UI-Previewer ile çalıştır
   ↓
6. SUNUM: Kullanıcıya canlı önizleme göster
```

### Komutlar

| Komut | Açıklama |
|-------|----------|
| `python scripts/preview.py` | UI önizleme sunucusunu başlat |
| `npm run dev` | Next.js geliştirme sunucusu |
| `.venv/Scripts/activate` | Sanal ortamı etkinleştir |

---

## 🚀 Hızlı Başlangıç

### Proje Başlatma

```bash
# 1. Sanal ortamı etkinleştir
.venv\Scripts\activate

# 2. Bağımlılıkları yükle
npm install framer-motion
pip install -r requirements.txt  # varsa

# 3. UI önizleme sunucusunu başlat
python .opencode\skills\ui-pro-max-engine\scripts\preview.py
```

### Örnek Bileşen: Neon-Glass Kart

```jsx
import { motion } from "framer-motion"

export default function NeonGlassCard({ title, children }) {
  return (
    <motion.div
      className="glass-neon p-8 rounded-2xl cursor-pointer"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300, damping: 15 }}
    >
      <div className="absolute top-0 left-4 right-4 h-0.5 bg-gradient-to-r from-transparent via-neon-orange to-transparent" />
      <h3 className="text-xl font-bold text-white mb-4">{title}</h3>
      {children}
    </motion.div>
  )
}
```

---

## 📜 Mühür Kaydı

```yaml
skill: ui-pro-max-engine
version: 1.0.0
sealed_by: Admin (Berkay)
sealed_date: 2026-05-14
status: active
capabilities:
  - framer-motion-architect
  - tailwind-neon-orange-stylist
  - glassmorphism-master
  - venv-ui-previewer
integrations:
  - obsidian-memory
  - opencode-skills
```
