"""
GlassesCat - Merkezi Sunucu
Flask backend - Web sitesi ve CLI icin API
Turkce iyilestirilmis + Ollama entegrasyonu
Agent Mimarisi - Model Router + Actions
"""
import sys
import io
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import subprocess
import datetime
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass
import requests
try:
    import paramiko
except:
    paramiko = None
import socket
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except:
    DDGS = None
    DDGS_AVAILABLE = False
import json
import threading
import ctypes
from ctypes import wintypes

# === DÜŞÜNCE LOGU SİSTEMİ ===
class ThoughtLogger:
    """
    Yapay zeka düşünce akışını yönetir.
    Hem terminale hem de web istemcisine anlık gönderim yapar.
    """
    
    def __init__(self):
        self.thoughts = []
        self.callbacks = []  # Web istemcilerine gönderim için
        
    def log(self, thought: str, source: str = "System"):
        """
        Yeni düşünce logu ekle.
        
        Args:
            thought: Log mesajı
            source: Kaynak (System, Router, Actions, vb.)
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'source': source,
            'thought': thought
        }
        
        self.thoughts.append(log_entry)
        
        # Terminale yazdır
        print(f"[{timestamp}] [DÜŞÜNCE/{source}]: {thought}")
        
        # Web istemcilerine gönder (callback'ler varsa)
        for callback in self.callbacks:
            try:
                callback(log_entry)
            except:
                pass
                
        return log_entry
    
    def get_recent_thoughts(self, count: int = 10):
        """Son N düşünceyi getir"""
        return self.thoughts[-count:] if self.thoughts else []
    
    def clear(self):
        """Logları temizle"""
        self.thoughts.clear()
    
    def register_callback(self, callback):
        """Web istemcisi callback'i ekle"""
        self.callbacks.append(callback)
        
    def unregister_callback(self, callback):
        """Callback'i kaldır"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

# Global thought logger instance
thought_logger = ThoughtLogger()

# === AGENT MODÜLLERİ ===
try:
    from model_router import get_model_router, ModelRouter
    MODEL_ROUTER_AVAILABLE = True
    print("[Agent] Model Router yuklendi")
except ImportError as e:
    MODEL_ROUTER_AVAILABLE = False
    print(f"[Agent] Model Router kullanılamıyor: {e}")

try:
    from actions import launch_app, APP_MAPPINGS, launch_game_escape, get_game_status
    ACTIONS_AVAILABLE = True
    GAME_ACTIONS_AVAILABLE = True
    print("[Agent] Actions modülü yüklendi ✓ (Oyun fonksiyonları dahil)")
except ImportError as e:
    ACTIONS_AVAILABLE = False
    GAME_ACTIONS_AVAILABLE = False
    print(f"[Agent] Actions kullanılamıyor: {e}")

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
CORS(app)

# Ollama API
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"  # En iyi Türkçe model
ROOT_MODEL = "deepseek-r1:8b"  # Root modda teknik model

# Root Mod (Şifre Korumalı)
root_mode_active = False
ROOT_PASSWORD = "GlassCat2026!"  # Root mod şifresi - değiştirebilirsiniz
root_auth_attempts = 0  # Başarısız giriş denemeleri

# Sürekli Ekran Analizi
screen_monitor_active = False
screen_monitor_thread = None
screen_history = []  # Son ekran durumları
MAX_SCREEN_HISTORY = 100

def monitor_screen():
    """Background thread ile sürekli ekran analizi"""
    global screen_history, screen_monitor_active
    import time
    
    while screen_monitor_active:
        try:
            # Aktif pencere başlığını al
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            length = user32.GetWindowTextLengthW(hwnd) + 1
            buffer = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(hwnd, buffer, length)
            window_title = buffer.value
            
            # Process ID
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            # Kaydet
            screen_data = {
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'window_title': window_title,
                'pid': pid.value
            }
            
            screen_history.append(screen_data)
            
            # Limiti koru
            if len(screen_history) > MAX_SCREEN_HISTORY:
                screen_history.pop(0)
            
            # 5 saniye bekle (CPU dostu)
            time.sleep(5)
            
        except Exception as e:
            print(f"[Monitor Error] {str(e)}")
            time.sleep(5)

# Pre-defined Senaryolar
scenarios = {
    'prism_dawncraft': {
        'name': 'Prism Launcher → Dawncraft',
        'steps': [
            {'action': 'open_app', 'value': 'prism launcher'},
            {'action': 'wait', 'value': 3},
            {'action': 'click', 'x': 500, 'y': 300, 'description': 'Dawncraft butonu'},
            {'action': 'wait', 'value': 2},
            {'action': 'click', 'x': 600, 'y': 400, 'description': 'Oyunu başlat'}
        ]
    }
}

# Uygulama Bazlı Senaryolar (Ekran görüntüsü + Window Detection)
app_scenarios = {
    'snapchat': {
        'name': 'Snapchat Kişi Arama',
        'keywords': ['snapchat', 'snap'],
        'actions': {
            'kişi ara': {'action': 'click', 'x': 100, 'y': 100, 'description': 'Arama butonu'},
            'kişiye git': {'action': 'click', 'x': 200, 'y': 200, 'description': 'Profil butonu'}
        }
    },
    'discord': {
        'name': 'Discord Sunucu',
        'keywords': ['discord'],
        'actions': {
            'sunucu ara': {'action': 'click', 'x': 150, 'y': 150, 'description': 'Sunucu arama'},
            'kanala gir': {'action': 'click', 'x': 250, 'y': 250, 'description': 'Kanal seç'}
        }
    },
    'chrome': {
        'name': 'Chrome Sekme',
        'keywords': ['chrome', 'google chrome'],
        'actions': {
            'yeni sekme': {'action': 'hotkey', 'key': 'ctrl+t', 'description': 'Yeni sekme'},
            'sekme kapat': {'action': 'hotkey', 'key': 'ctrl+w', 'description': 'Sekme kapat'}
        }
    }
}

# Kali Linux bağlantısı
kali_ssh = None
kali_connected = False
root_kali_connected = False

# Oyun Bilgisi - Gemini Zekası için Genişletilmiş Bilgi Tabanı
GAMING_KNOWLEDGE = """
🎮 OYUN DÜNYASI - Detaylı Bilgi:

POPÜLER OYUNLAR:
• GTA VI (2025) - Rockstar'ın yeni nesil açık dünya oyunu, Vice City'de geçiyor
• Call of Duty: Black Ops 6 - Treyarch'ın yeni FPS oyunu, özel zombi modları
• Elden Ring - FromSoftware'in souls-like açık dünya başyapıtı
• Cyberpunk 2077 - CD Projekt RED'in distopik RPG'si (Phantom Liberty eklentisi)
• Baldur's Gate 3 - Larian Studios'ın D&D tabanlı RPG'si, 2023 GOTY
• Marvel's Spider-Man 2 - Insomniac'ın PlayStation özel oyunu
• God of War Ragnarök - Santa Monica Studio'nun mitolojik aksiyonu
• The Last of Us Part II - Naughty Dog'un hikaye odaklı oyunu
• Red Dead Redemption 2 - Rockstar'ın batı temalı şaheseri
• Minecraft - Mojang'ın sonsuz yaratıcılık oyunu
• Fortnite - Epic Games'in battle royale fenomeni
• League of Legends - Riot Games'in MOBA'sı
• Valorant - Taktiksel FPS, CS:GO alternatifi
• Apex Legends - Respawn'ın battle royale'si
• Genshin Impact - MiHoYo'nun açık dünya RPG'si

OYUN MOTORLARI:
• Unreal Engine 5 - Nanite ve Lumen teknolojileri, fotorealistik grafikler
• Unity - Çok platformlu oyun geliştirme, indie oyunlar için popüler
• Source 2 - Valve'ın motoru, Half-Life Alyx ve CS2'de kullanılıyor
• Godot - Açık kaynak, hafif ve güçlü
• Frostbite - EA'ın motoru, Battlefield serisinde
• Decima Engine - Guerrilla Games, Horizon ve Death Stranding

OYUN KATEGORİLERİ:
• FPS (First Person Shooter) - CS:GO, Valorant, Call of Duty
• RPG (Role Playing Game) - Baldur's Gate 3, Cyberpunk 2077, Elden Ring
• MOBA - League of Legends, Dota 2, SMITE
• Battle Royale - Fortnite, PUBG, Apex Legends
• Açık Dünya - GTA, RDR2, The Witcher 3, Zelda: BOTW
• Souls-like - Elden Ring, Dark Souls, Sekiro, Lies of P
• Simülasyon - The Sims 4, Cities: Skylines, Flight Simulator
• Strateji - StarCraft II, Age of Empires IV, Civilization VI
• Korku - Resident Evil 4, Silent Hill 2, Dead Space
• Indie - Hades, Celeste, Hollow Knight, Stardew Valley

PLATFORM:
• PC (Steam, Epic Games, GOG)
• PlayStation 5 - Özel oyunlar: Spider-Man, God of War, The Last of Us
• Xbox Series X/S - Game Pass, özel oyunlar: Halo, Forza
• Nintendo Switch - Özel oyunlar: Zelda, Mario, Pokemon
• Mobile - iOS/Android, Genshin Impact, PUBG Mobile

2024-2025 ÇIKACAK OYUNLAR:
• GTA VI (2025)
• Death Stranding 2
• Ghost of Yōtei
• Metaphor: ReFantazio
• Silent Hill 2 Remake
• Black Myth: Wukong
• Star Wars Outlaws
• Assassin's Creed Shadows

ESPORTS:
• League of Legends Worlds - Yıllık dünya şampiyonası
• The International (Dota 2) - En büyük ödül havuzu
• CS2 Major - Valve tarafından desteklenen şampiyonalar
• Valorant Champions - Riot'ın organizasyonu
• Fortnite World Cup - Epic Games'in turnuvası

OYUN TERİMLERİ:
• FPS (Frames Per Second) - Saniyedeki kare sayısı, 60+ ideal
• Ping - Gecikme süresi, düşük ping (0-50ms) iyi
• Latency - Ağ gecikmesi
• Loot - Ganimet/eşya toplama
• Grinding - Tekrarlayarak seviye atlama
• Easter Egg - Gizli sürprizler
• Speedrun - Oyunu en hızlı bitirme
• Noob/Yeni - Yeni başlayan
• GG (Good Game) - İyi oyun, maç sonu saygı ifadesi
• AFK - Klavyeden uzak (Away From Keyboard)
• Buff/Nerf - Güçlendirme/Zayıflatma
• Meta - En güçlü stratejiler/oyun tarzı
• OP (Overpowered) - Aşırı güçlü
• DLC - Ek içerik
• Season Pass - Sezonluk içerik paketi
"""

# Gemini Zekası - Gelişmiş AI Kişilik
GEMINI_PERSONALITY = """
Sen GG Studio 2026'nın asistanısın.

ÖZELLİKLERİN:
1. 🧠 ÇOK YÖNLÜ ZEKA - Teknik, yaratıcı, analitik düşünme
2. 🎮 Oyun uzmanı - Tüm oyun türleri, mekanikler, tarihçe
3. 💻 Teknik bilgi - Yazılım, donanım, programlama
4. 🌍 Güncel bilgiler - 2024-2025 oyun dünyası, teknoloji trendleri
5. 🎯 Stratejik analiz - Oyun stratejileri, meta analizi
6. 🎨 Yaratıcı çözümler - Alternatif yaklaşımlar sunma

CEVAP STİLİ (Gemini tarzı):
• Kapsamlı ama öz - Detay ver ama gereksiz uzatma
• Maddeler halinde - Kolay okunur format
• Örnekler ver - Somut örneklerle açıkla
• Güncel bilgi - 2024-2025 oyunlarından örnekler
• Karşılaştırma - Benzer oyunları/teknikleri karşılaştır
• Derinlemesine - Yüzeyde kalma, detaya in

TÜRKÇE KURALLARI (Gemini standartları):
• Kesinlikle "ı/i/u/ü" karıştırma
• "yi/yi/yu/yü" eklerini doğru kullan
• Teknik terimleri Türkçe'ye uygun çevir
• Akademik Türkçe, argo yok

ÖRNEK CEVAP YAPISI:
"Bu konu şu şekilde işliyor:

1. Temel Kavram:
   Açıklama...

2. Pratik Uygulama:
   Örnek...

3. Karşılaştırma:
   X vs Y...

4. Güncel Durum (2024-2025):
   Son gelişmeler..."
"""

# Notlar dosyası
NOTES_FILE = "notlar.txt"


@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint - Düşünce logları ile"""
    global screen_monitor_active, screen_monitor_thread, screen_history
    data = request.get_json()
    message = data.get('message', '').strip()
    msg_lower = message.lower()
    
    if not message:
        return jsonify({'error': 'Mesaj boş olamaz'}), 400
    
    # DÜŞÜNCE LOGU: Yeni mesaj işlemi başlıyor
    thought_logger.clear()  # Her yeni mesajda logları temizle
    thought_logger.log(f"Yeni mesaj alındı. Analiz ediliyor...", "System")
    thought_logger.log(f"Mesaj: '{message[:50]}{'...' if len(message) > 50 else ''}'", "System")
    
    # Intent analizi
    if any(cmd in msg_lower for cmd in ['aç', 'ac', 'başlat', 'baslat', 'çalıştır', 'calistir']):
        thought_logger.log(f"Intent tespit edildi: UYGULAMA AÇMA", "System")
    elif any(cmd in msg_lower for cmd in ['araştır', 'arastir', 'ara', 'bak', 'incele']):
        thought_logger.log(f"Intent tespit edildi: ARAŞTIRMA", "System")
    elif any(cmd in msg_lower for cmd in ['kapat', 'durdur', 'stop']):
        thought_logger.log(f"Intent tespit edildi: DURDURMA", "System")
    elif any(cmd in msg_lower for cmd in ['oyun', 'oyna', 'game', 'başlat oyunu', 'start game']):
        thought_logger.log(f"Intent tespit edildi: OYUN BAŞLATMA", "System")
    else:
        thought_logger.log(f"Intent tespit edildi: SOHBET/AI YANITI", "System")
    
    # Not alma
    if msg_lower.startswith('not al:') or msg_lower.startswith('not al :'):
        note_content = message[7:].strip() if msg_lower.startswith('not al:') else message[8:].strip()
        return save_note(note_content)
    
    # Dosya oluşturma
    if msg_lower.startswith('oluştur ') or msg_lower.startswith('olustur '):
        return create_file_from_command(message)
    if 'oluştur' in msg_lower or 'olustur' in msg_lower:
        if any(word in msg_lower for word in ['masaüstü', 'masaustu', 'desktop', 'dosya', 'not defteri', 'txt']):
            return create_file_from_command(message)
    
    # WhatsApp mesaj gönderme
    if msg_lower.startswith('whatsapp mesaj gönder') or msg_lower.startswith('whatsapp mesaj gonder'):
        try:
            # Format: "whatsapp mesaj gönder +905551234567 Merhaba nasilsin"
            parts = message.split()
            if len(parts) >= 3:
                phone = parts[2].strip()  # Telefon numarası
                text = ' '.join(parts[3:])  # Mesaj
                
                # WhatsApp URI
                whatsapp_url = f"whatsapp://send?phone={phone}&text={text}"
                subprocess.Popen(f'start "" "{whatsapp_url}"', shell=True)
                
                return jsonify({
                    'success': True,
                    'response': f'✅ WhatsApp açılıyor: {phone} → "{text}"',
                    'type': 'whatsapp'
                })
            else:
                return jsonify({
                    'success': False,
                    'response': '❌ Format yanlış. Kullanım: whatsapp mesaj gönder +905551234567 Mesajın'
                })
        except Exception as e:
            return jsonify({'error': f'WhatsApp açılamadı: {str(e)}'}), 500
    
    # Telegram mesaj gönderme
    if msg_lower.startswith('telegram mesaj gönder') or msg_lower.startswith('telegram mesaj gonder'):
        try:
            # Format: "telegram mesaj gönder @kullanici Merhaba nasilsin"
            parts = message.split()
            if len(parts) >= 3:
                username = parts[2].strip()  # @kullanici
                text = ' '.join(parts[3:])  # Mesaj
                
                # Telegram URI
                telegram_url = f"tg://resolve?domain={username.lstrip('@')}&text={text}"
                subprocess.Popen(f'start "" "{telegram_url}"', shell=True)
                
                return jsonify({
                    'success': True,
                    'response': f'✅ Telegram açılıyor: {username} → "{text}"',
                    'type': 'telegram'
                })
            else:
                return jsonify({
                    'success': False,
                    'response': '❌ Format yanlış. Kullanım: telegram mesaj gönder @kullanici Mesajın'
                })
        except Exception as e:
            return jsonify({'error': f'Telegram açılamadı: {str(e)}'}), 500
    
    # Ekran görüntüsü alma
    if msg_lower.startswith('ekran görüntüsü al') or msg_lower.startswith('ekran goruntusu al') or msg_lower == 'screenshot':
        try:
            import pyautogui
            import time
            from datetime import datetime
            
            # Klasör oluştur
            screenshots_dir = os.path.join(os.path.expanduser('~'), 'Desktop', 'Screenshots')
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
            
            # Dosya adı
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            # Ekran görüntüsü al
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            return jsonify({
                'success': True,
                'response': f'✅ Ekran görüntüsü kaydedildi: {filepath}\n📍 Koordinat öğrenmek için: "mouse pozisyonu" yazın',
                'type': 'screenshot',
                'filepath': filepath
            })
        except Exception as e:
            return jsonify({'error': f'Ekran görüntüsü alınamadı: {str(e)}'}), 500
    
    # OYUN BAŞLATMA - Agent Entegrasyonu
    if any(cmd in msg_lower for cmd in ['oyun başlat', 'oyunu başlat', 'kaçış oyunu', 'escape game', 'game test', 'test oyunu']):
        thought_logger.log(f"Oyun başlatma isteği işleniyor...", "Game")
        
        try:
            if GAME_ACTIONS_AVAILABLE:
                # Test modu kontrolü
                test_mode = any(cmd in msg_lower for cmd in ['test', 'test modu', 'agent'])
                
                thought_logger.log(f"Actions modülünden oyun başlatma çağrılıyor. Test modu: {test_mode}", "Game")
                result = launch_game_escape(test_mode=test_mode)
                
                thought_logger.log(f"Oyun başlatma sonucu: {result.get('message', 'Bilinmiyor')}", "Game")
                
                return jsonify({
                    'success': result.get('success', False),
                    'response': result.get('message', 'Oyun başlatıldı'),
                    'type': 'game_launch',
                    'game': 'escape',
                    'mode': result.get('mode', 'normal'),
                    'thoughts': thought_logger.get_recent_thoughts(5)
                })
            else:
                thought_logger.log(f"Game Actions kullanılamıyor!", "System")
                return jsonify({
                    'success': False,
                    'response': '❌ Oyun modülü kullanılamıyor. Actions.py kontrol edin.',
                    'type': 'error'
                })
        except Exception as e:
            error_msg = str(e)
            thought_logger.log(f"Oyun başlatma hatası: {error_msg}", "System")
            
            # HATA KONTROLÜ: Model Router ile hata analizi
            error_analysis = analyze_game_error_with_router(error_msg)
            
            return jsonify({
                'success': False,
                'response': f'❌ Oyun başlatılamadı: {error_msg}\n\n💡 AI Analizi:\n{error_analysis}',
                'type': 'game_error',
                'error': error_msg,
                'thoughts': thought_logger.get_recent_thoughts(5)
            })
            return jsonify({'error': f'Ekran görüntüsü alınamadı: {str(e)}'}), 500
    
    # Mouse pozisyonu göster
    if msg_lower == 'mouse pozisyonu' or msg_lower == 'mouse position' or msg_lower == 'koordinat':
        try:
            import pyautogui
            x, y = pyautogui.position()
            screen_width, screen_height = pyautogui.size()
            
            return jsonify({
                'success': True,
                'response': f'📍 Mouse Pozisyonu:\n   X: {x}\n   Y: {y}\n   Ekran Boyutu: {screen_width}x{screen_height}',
                'type': 'mouse_position',
                'x': x,
                'y': y
            })
        except Exception as e:
            return jsonify({'error': f'Mouse pozisyonu alınamadı: {str(e)}'}), 500
    
    # Hangi uygulama açık?
    if msg_lower == 'hangi uygulama açık' or msg_lower == 'aktif pencere' or msg_lower == 'aktif uygulama':
        try:
            import ctypes
            from ctypes import wintypes
            
            # Aktif pencere başlığını al
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            
            # Pencere başlığı
            length = user32.GetWindowTextLengthW(hwnd) + 1
            buffer = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(hwnd, buffer, length)
            window_title = buffer.value
            
            # Process ID al
            pid = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            return jsonify({
                'success': True,
                'response': f'🖥️ Aktif Uygulama:\n   Pencere: {window_title}\n   PID: {pid.value}',
                'type': 'active_window',
                'window_title': window_title,
                'pid': pid.value
            })
        except Exception as e:
            return jsonify({'error': f'Pencere bilgisi alınamadı: {str(e)}'}), 500
    
    # Senaryo listele
    if msg_lower == 'senaryo listele' or msg_lower == 'senaryolar':
        try:
            scenario_list = []
            for key, scenario in scenarios.items():
                steps_info = '\n'.join([f"   {i+1}. {step['action']}: {step.get('description', step.get('value', ''))}" for i, step in enumerate(scenario['steps'])])
                scenario_list.append(f"📋 {key}: {scenario['name']}\n{steps_info}")
            
            if scenario_list:
                return jsonify({
                    'success': True,
                    'response': f'📋 Mevcut Senaryolar:\n\n' + '\n\n'.join(scenario_list),
                    'type': 'scenario_list',
                    'scenarios': list(scenarios.keys())
                })
            else:
                return jsonify({
                    'success': True,
                    'response': '📋 Henüz senaryo yok.',
                    'type': 'scenario_list',
                    'scenarios': []
                })
        except Exception as e:
            return jsonify({'error': f'Senaryolar listelenemedi: {str(e)}'}), 500
    
    # Senaryo çalıştır
    if msg_lower.startswith('senaryo çalıştır') or msg_lower.startswith('senaryo calistir'):
        try:
            import pyautogui
            import time
            
            # Format: "senaryo çalıştır prism_dawncraft"
            parts = message.split()
            if len(parts) >= 3:
                scenario_key = parts[2].strip()
                
                if scenario_key in scenarios:
                    scenario = scenarios[scenario_key]
                    results = []
                    
                    for i, step in enumerate(scenario['steps']):
                        step_num = i + 1
                        action = step['action']
                        
                        if action == 'open_app':
                            open_application(step['value'])
                            results.append(f"{step_num}. {step['value']} açıldı")
                            time.sleep(1)
                        
                        elif action == 'wait':
                            time.sleep(step['value'])
                            results.append(f"{step_num}. {step['value']} saniye beklendi")
                        
                        elif action == 'click':
                            pyautogui.click(step['x'], step['y'])
                            desc = step.get('description', f'({step["x"]}, {step["y"]})')
                            results.append(f"{step_num}. Tıklandı: {desc}")
                            time.sleep(0.5)
                        
                        elif action == 'type':
                            pyautogui.write(step['value'])
                            results.append(f"{step_num}. Yazıldı: {step['value']}")
                            time.sleep(0.5)
                    
                    return jsonify({
                        'success': True,
                        'response': f'✅ Senaryo çalıştırıldı: {scenario["name"]}\n\n' + '\n'.join(results),
                        'type': 'scenario_executed',
                        'scenario': scenario_key
                    })
                else:
                    return jsonify({
                        'success': False,
                        'response': f'❌ Senaryo bulunamadı: {scenario_key}\n📋 Mevcut senaryolar: {", ".join(scenarios.keys())}'
                    })
            else:
                return jsonify({
                    'success': False,
                    'response': '❌ Format yanlış. Kullanım: senaryo çalıştır prism_dawncraft'
                })
        except Exception as e:
            return jsonify({'error': f'Senaryo çalıştırılamadı: {str(e)}'}), 500
    
    # Uygulama bazlı senaryo çalıştır (Ekran görüntüsü + Window Detection)
    # Sadece uygulama açıkken ve action varsa çalıştır, yoksa normal akışa devam et
    if (msg_lower.startswith('snapchat') or msg_lower.startswith('discord') or msg_lower.startswith('chrome')):
        # Eğer "aç" kelimesi varsa, uygulama açma komutudur - bu fonksiyonu atla
        if ' aç' in msg_lower or ' ac' in msg_lower:
            # Normal uygulama açma akışına devam et
            pass
        else:
            try:
                import pyautogui
                import time
                import ctypes
                from ctypes import wintypes
                
                # Format: "snapchat'e gir @kullanici" veya "discord sunucu ara"
                parts = message.split()
                app_name = parts[0].lower()
                action = ' '.join(parts[1:]) if len(parts) > 1 else ''
                
                # Eğer action yoksa, bu sadece uygulama adı - atla
                if not action:
                    pass
                else:
                    # Aktif pencere başlığını kontrol et
                    user32 = ctypes.windll.user32
                    hwnd = user32.GetForegroundWindow()
                    length = user32.GetWindowTextLengthW(hwnd) + 1
                    buffer = ctypes.create_unicode_buffer(length)
                    user32.GetWindowTextW(hwnd, buffer, length)
                    window_title = buffer.value.lower()
                    
                    # Hangi uygulama açık?
                    detected_app = None
                    for app_key, app_config in app_scenarios.items():
                        if any(keyword in window_title for keyword in app_config['keywords']):
                            detected_app = app_key
                            break
                    
                    if detected_app:
                        app_config = app_scenarios[detected_app]
                        
                        # Action'u kontrol et
                        for action_key, action_config in app_config['actions'].items():
                            if action_key in action.lower():
                                if action_config['action'] == 'click':
                                    pyautogui.click(action_config['x'], action_config['y'])
                                    return jsonify({
                                        'success': True,
                                        'response': f'✅ {detected_app.capitalize()} → {action_config["description"]}',
                                        'type': 'app_action',
                                        'app': detected_app
                                    })
                                elif action_config['action'] == 'hotkey':
                                    # Hotkey çalıştır
                                    keys = action_config['key'].split('+')
                                    pyautogui.hotkey(*keys)
                                    return jsonify({
                                        'success': True,
                                        'response': f'✅ {detected_app.capitalize()} → {action_config["description"]}',
                                        'type': 'app_action',
                                        'app': detected_app
                                    })
                        
                        return jsonify({
                            'success': False,
                            'response': f'⚠️ {detected_app.capitalize()} açık ama "{action}" komutu tanınmıyor.\n📋 Mevcut komutlar: {", ".join(app_config["actions"].keys())}'
                        })
                    # Uygulama açık değilse, normal akışa devam et (atla)
            except Exception as e:
                return jsonify({'error': f'Uygulama aksiyonu başarısız: {str(e)}'}), 500
    
    # Ekran monitor kontrol
    if msg_lower == 'monitor başlat' or msg_lower == 'monitor baslat':
        if not screen_monitor_active:
            screen_monitor_active = True
            screen_monitor_thread = threading.Thread(target=monitor_screen, daemon=True)
            screen_monitor_thread.start()
            return jsonify({
                'success': True,
                'response': '✅ Ekran monitor başlatıldı. Her 5 saniyede analiz edecek.',
                'type': 'monitor_started'
            })
        else:
            return jsonify({
                'success': False,
                'response': '⚠️ Monitor zaten çalışıyor.'
            })
    
    if msg_lower == 'monitor durdur' or msg_lower == 'monitor durdur':
        screen_monitor_active = False
        return jsonify({
            'success': True,
            'response': '✅ Ekran monitor durduruldu.',
            'type': 'monitor_stopped'
        })
    
    if msg_lower == 'monitor durum' or msg_lower == 'monitor durumu':
        return jsonify({
            'success': True,
            'response': f'📊 Monitor Durumu:\n   Aktif: {"Evet" if screen_monitor_active else "Hayır"}\n   Kayıtlı durum: {len(screen_history)}',
            'type': 'monitor_status',
            'active': screen_monitor_active,
            'history_count': len(screen_history)
        })
    
    if msg_lower == 'monitor geçmiş' or msg_lower == 'monitor gecmis':
        if screen_history:
            history_text = '\n'.join([f"📌 {h['timestamp']}: {h['window_title']}" for h in screen_history[-10:]])
            return jsonify({
                'success': True,
                'response': f'📊 Son 10 durum:\n\n{history_text}',
                'type': 'monitor_history',
                'history': screen_history[-10:]
            })
        else:
            return jsonify({
                'success': True,
                'response': '📊 Henüz geçmiş yok. Monitor başlatın: monitor başlat',
                'type': 'monitor_history'
            })
    
    # Uygulama analizi (düşük CPU kullanımı)
    if msg_lower == 'uygulama analizi' or msg_lower == 'uygulama analizi yap' or msg_lower == 'hangi uygulamalar açık':
        try:
            import ctypes
            from ctypes import wintypes
            
            # Aktif pencere başlığını al
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            length = user32.GetWindowTextLengthW(hwnd) + 1
            buffer = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(hwnd, buffer, length)
            window_title = buffer.value
            
            # Process ID
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            # Uygulama tespiti
            detected_apps = []
            app_keywords = {
                'Chrome': ['chrome', 'google chrome'],
                'Firefox': ['firefox'],
                'Edge': ['edge', 'microsoft edge'],
                'Discord': ['discord'],
                'Spotify': ['spotify'],
                'VS Code': ['code', 'visual studio code'],
                'Prism Launcher': ['prism', 'prismlauncher'],
                'Minecraft': ['minecraft'],
                'Steam': ['steam'],
                'Telegram': ['telegram'],
                'WhatsApp': ['whatsapp'],
                'YouTube': ['youtube'],
                'Netflix': ['netflix'],
                'Valorant': ['valorant'],
                'League of Legends': ['league of legends', 'lol'],
                'CS2': ['cs2', 'counter strike'],
                'GTA': ['gta', 'grand theft auto'],
                'Fortnite': ['fortnite'],
                'Apex': ['apex legends'],
                'Dota 2': ['dota'],
                'Overwatch': ['overwatch'],
                'OBS': ['obs'],
                'Notepad': ['notepad', 'not defteri'],
                'Word': ['word', 'microsoft word'],
                'Excel': ['excel', 'microsoft excel'],
                'PowerPoint': ['powerpoint', 'microsoft powerpoint'],
            }
            
            window_lower = window_title.lower()
            for app_name, keywords in app_keywords.items():
                if any(keyword in window_lower for keyword in keywords):
                    detected_apps.append(app_name)
            
            if not detected_apps:
                detected_apps = ["Bilinmeyen uygulama"]
            
            response_text = f'📊 Aktif Uygulama Analizi:\n\n'
            response_text += f'🖥️ Pencere Başlığı: {window_title}\n'
            response_text += f'🆔 Process ID: {pid.value}\n'
            response_text += f'📱 Tespit Edilen Uygulama: {", ".join(detected_apps)}\n\n'
            response_text += f'💡 Detaylı analiz için: monitor başlat'
            
            return jsonify({
                'success': True,
                'response': response_text,
                'type': 'app_analysis',
                'window_title': window_title,
                'pid': pid.value,
                'apps': detected_apps
            })
        except Exception as e:
            return jsonify({'error': f'Uygulama analizi başarısız: {str(e)}'}), 500
    
    # İsim bazlı tıklama (özel format) - ROOT MOD GEREKTIRIR
    # Format: "[isim] a tıkla" veya "[isim] e tıkla" veya "[uygulama] den [isim] a tıkla"
    if msg_lower.endswith(' a tıkla') or msg_lower.endswith(' a tikla') or msg_lower.endswith(' e tıkla') or msg_lower.endswith(' e tikla'):
        if not root_mode_active:
            return jsonify({
                'success': False,
                'response': '⚠️ OCR tıklama özelliği güvenlik nedeniyle WEB API\'de devre dışı.\n\n💡 Bu özellik sadece Niko Agent CLI\'da kullanılabilir.\n📝 CLI için: baslat.bat → [5] Glassescat AI Agent',
                'type': 'ocr_disabled',
                'security': True
            })
        
        try:
            import pyautogui
            import pytesseract
            import cv2
            import numpy as np
            
            # Tesseract yolunu belirt (Windows için)
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            # İsmi al (uygulama belirtimi varsa ayır)
            if ' den ' in msg_lower or ' den ' in message:
                # Format: "chrome den Berkay a tıkla"
                parts = message.rsplit(' den ', 1)
                app_name = parts[0].strip()
                name_part = parts[1].strip()
                name = name_part.rsplit(' a tıkla', 1)[0].strip() if ' a tıkla' in msg_lower else \
                        name_part.rsplit(' a tikla', 1)[0].strip() if ' a tikla' in msg_lower else \
                        name_part.rsplit(' e tıkla', 1)[0].strip() if ' e tıkla' in msg_lower else \
                        name_part.rsplit(' e tikla', 1)[0].strip()
            else:
                # Format: "Berkay a tıkla"
                name = message.rsplit(' a tıkla', 1)[0].strip() if ' a tıkla' in msg_lower else \
                        message.rsplit(' a tikla', 1)[0].strip() if ' a tikla' in msg_lower else \
                        message.rsplit(' e tıkla', 1)[0].strip() if ' e tıkla' in msg_lower else \
                        message.rsplit(' e tikla', 1)[0].strip()
            
            # Ekran görüntüsü al
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            
            # RGB'den BGR'ye dönüştür (OpenCV formatı)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Gri tonlamaya dönüştür
            gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
            
            # Metni oku
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            # İsmi bul
            n_boxes = len(data['text'])
            found = False
            best_match = None
            best_score = 0
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text and name.lower() in text.lower():
                    # Eşleşme skoru
                    score = len(name) / len(text) if len(text) > 0 else 0
                    if score > best_score:
                        best_score = score
                        best_match = {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'w': data['width'][i],
                            'h': data['height'][i],
                            'text': text
                        }
                        found = True
            
            if found and best_match:
                # Metnin merkezine tıkla
                center_x = best_match['x'] + best_match['w'] // 2
                center_y = best_match['y'] + best_match['h'] // 2
                
                pyautogui.click(center_x, center_y)
                
                return jsonify({
                    'success': True,
                    'response': f'✅ "{name}" bulundu ve tıklandı: ({center_x}, {center_y})\n📝 Bulunan metin: {best_match["text"]}',
                    'type': 'ocr_click',
                    'name': name,
                    'x': center_x,
                    'y': center_y
                })
            else:
                return jsonify({
                    'success': False,
                    'response': f'❌ "{name}" ekran üzerinde bulunamadı.\n💡 İpucu: Metin tam olarak görünmüyor olabilir veya OCR hatası olabilir.',
                    'type': 'ocr_not_found',
                    'name': name
                })
                
        except ImportError:
            return jsonify({
                'success': False,
                'response': f'⚠️ OCR kütüphaneleri kurulmamış.\n\n📝 Kurulum:\npip install pytesseract opencv-python numpy\n\n💡 Windows için Tesseract-OCR indirin ve PATH\'e ekleyin.',
                'type': 'ocr_not_installed'
            })
        except Exception as e:
            error_msg = str(e)
            if 'tesseract' in error_msg.lower():
                return jsonify({
                    'success': False,
                    'response': f'❌ Tesseract bulunamadı.\n\n📝 Çözüm:\n1. Tesseract-OCR\'ı kur: https://github.com/UB-Mannheim/tesseract/wiki\n2. Kurulum yolu: C:\\Program Files\\Tesseract-OCR\n3. Veya farklı yola kurduysanız, koddaki yolu güncelleyin.',
                    'type': 'tesseract_not_found'
                })
            return jsonify({'error': f'OCR tıklama hatası: {str(e)}'}), 500
    
    # Koordinat tıklama
    if msg_lower.startswith('tıkla') or msg_lower.startswith('tikla'):
        try:
            import pyautogui
            # Format: "tıkla 100 200" veya "tıkla x=100 y=200"
            parts = message.split()
            
            x, y = None, None
            for i, part in enumerate(parts):
                if part.startswith('x='):
                    x = int(part[2:])
                elif part.startswith('y='):
                    y = int(part[2:])
                elif i == 1 and x is None:
                    x = int(part)
                elif i == 2 and y is None:
                    y = int(part)
            
            if x is not None and y is not None:
                pyautogui.click(x, y)
                return jsonify({
                    'success': True,
                    'response': f'✅ Tıklandı: ({x}, {y})',
                    'type': 'click'
                })
            else:
                return jsonify({
                    'success': False,
                    'response': '❌ Format yanlış. Kullanım: tıkla 100 200 veya tıkla x=100 y=200'
                })
        except Exception as e:
            return jsonify({'error': f'Tıklama başarısız: {str(e)}'}), 500
    
    # Metin arama ve tıklama (OCR ile) - ROOT MOD GEREKTIRIR
    if msg_lower.startswith('bul ve tıkla') or msg_lower.startswith('bul ve tikla'):
        return jsonify({
            'success': False,
            'response': '⚠️ OCR özelliği güvenlik nedeniyle WEB API\'de devre dışı.\n\n💡 Bu özellik sadece Niko Agent CLI\'da kullanılabilir.\n📝 CLI için: baslat.bat → [5] Glassescat AI Agent',
            'type': 'ocr_disabled',
            'security': True
        })
    
    # Uygulama açma - farklı formatları destekle
    # Format 1: "aç chrome" / "ac chrome" / "başlat chrome" / "baslat chrome"
    if msg_lower.startswith('aç ') or msg_lower.startswith('ac ') or msg_lower.startswith('başlat ') or msg_lower.startswith('baslat '):
        # Kaç karakter atlayacağımızı belirle
        if msg_lower.startswith('başlat '):
            app_name = message[8:].strip()
        elif msg_lower.startswith('baslat '):
            app_name = message[7:].strip()
        else:
            app_name = message[3:].strip()
        return open_application(app_name)
    
    # Format 2: "chrome yi aç" / "chrome yi başlat" / "spotify baslat"
    if ' aç' in msg_lower or ' ac' in msg_lower or ' başlat' in msg_lower or ' baslat' in msg_lower:
        # Son kelimeyi al ve gerisini uygulama adı olarak kullan
        if msg_lower.endswith(' aç') or msg_lower.endswith(' ac'):
            app_name = message.rsplit(' ', 1)[0].strip()
            return open_application(app_name)
        if msg_lower.endswith(' başlat') or msg_lower.endswith(' baslat'):
            app_name = message.rsplit(' ', 1)[0].strip()
            return open_application(app_name)
        # Ortada geçiyorsa: "chrome yi aç", "chrome yi başlat"
        turkish_patterns = [' yi aç', ' yı aç', ' yu aç', ' yü aç', ' ni aç', ' nı aç', 
                           ' yi başlat', ' yı başlat', ' yu başlat', ' yü başlat',
                           ' ni başlat', ' nı başlat']
        for pattern in turkish_patterns:
            if pattern in msg_lower:
                app_name = msg_lower.replace(pattern, '').strip()
                return open_application(app_name)
    
    # Root mod - şifre kontrollü
    if msg_lower == 'root':
        # Sadece root yazıldı - terminalden şifresiz
        return toggle_root_mode(bypass_password=True)
    if msg_lower.startswith('root şifre ') or msg_lower.startswith('root sifre '):
        # Şifre ile root açma (web sitesi için)
        password = message[11:].strip() if msg_lower.startswith('root şifre ') else message[10:].strip()
        return toggle_root_mode(password, bypass_password=False)
    
    # Araştırma komutu - Root moda göre değişir
    if msg_lower.startswith('araştır ') or msg_lower.startswith('arastir '):
        query = message[9:].strip() if msg_lower.startswith('araştır ') else message[8:].strip()
        if root_mode_active:
            return research_technical(query)  # Root: Teknik kaynaklar
        else:
            return research_general(query)    # Normal: Genel arama
    
    # Hızlı soru - araştırmayı atla, direkt Ollama
    if msg_lower.startswith('sor ') or msg_lower.startswith('sora '):
        question = message[4:].strip() if msg_lower.startswith('sor ') else message[5:].strip()
        return ask_ollama(question)
    
    # Root mod aktif
    if root_mode_active:
        return handle_root_command(message)
    
    # Kali Linux komutları
    if msg_lower.startswith('kali '):
        return handle_kali_command(message[5:].strip())
    
    # Normal soru - Ollama
    return ask_ollama(message)


def save_note(content):
    """Notları dosyaya kaydet"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(NOTES_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {content}\n")
        return jsonify({
            'success': True,
            'response': f'✅ Not kaydedildi: "{content}"',
            'type': 'note'
        })
    except Exception as e:
        return jsonify({'error': f'Not kaydedilemedi: {str(e)}'}), 500


def create_file_from_command(message):
    """Doğal dil komutundan dosya oluştur - masaüstüne not defteri oluştur"""
    try:
        msg_lower = message.lower()
        
        # Masaüstü yolunu bul - Windows'un gerçek masaüstü yolunu kullan
        import ctypes
        from ctypes import wintypes
        
        # SHGetFolderPath ile gerçek masaüstü yolunu al
        CSIDL_DESKTOP = 0
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, 0, buf)
        desktop_path = buf.value
        
        # Eğer yukarıdaki çalışmazsa, ortam değişkenlerini dene
        if not desktop_path or not os.path.exists(desktop_path):
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        if not os.path.exists(desktop_path):
            # OneDrive Desktop kontrol et
            onedrive_desktop = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Desktop')
            if os.path.exists(onedrive_desktop):
                desktop_path = onedrive_desktop
            else:
                # Son çare: USERPROFILE/Desktop
                desktop_path = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Desktop')
        
        # Varsayılan değerler
        filename = None
        content = ""
        location = desktop_path  # Varsayılan: masaüstü
        
        # Dosya adını çıkar
        # "masaüstüne not defteri oluştur" -> "not_defteri.txt"
        # "test.txt oluştur" -> "test.txt"
        # "yeni dosya oluştur" -> "yeni_dosya.txt"
        
        common_names = {
            'not defteri': 'not_defteri.txt',
            'not defteri oluştur': 'not_defteri.txt',
            'yeni dosya': 'yeni_dosya.txt',
            'yeni text': 'yeni_dosya.txt',
            'test': 'test.txt',
            'deneme': 'deneme.txt',
        }
        
        # Özel isimleri kontrol et
        for key, default_name in common_names.items():
            if key in msg_lower:
                filename = default_name
                break
        
        # İçerik var mı? "...içeriği ile" veya "...şunu yaz"
        content_indicators = ['içeriği', 'içine yaz', 'şunu yaz', 'yaz', 'içine']
        for indicator in content_indicators:
            if indicator in msg_lower:
                # Basit içerik çıkarımı
                parts = message.split(indicator)
                if len(parts) > 1:
                    content = parts[1].strip().strip('"').strip("'")
                    break
        
        # Konum belirtilmiş mi?
        if 'masaüstü' in msg_lower or 'masaustu' in msg_lower or 'desktop' in msg_lower:
            location = desktop_path
        elif 'belgelerim' in msg_lower or 'documents' in msg_lower:
            location = os.path.join(os.path.expanduser('~'), 'Documents')
        elif 'indirilenler' in msg_lower or 'downloads' in msg_lower:
            location = os.path.join(os.path.expanduser('~'), 'Downloads')
        
        # Dosya adı bulunamadıysa, mesajdan çıkarmaya çalış
        if not filename:
            # .txt uzantılı kelime ara
            words = message.split()
            for word in words:
                if word.lower().endswith('.txt'):
                    filename = word
                    break
            
            # Hala bulunamadıysa varsayılan isim
            if not filename:
                filename = f"yeni_dosya_{datetime.datetime.now().strftime('%H%M%S')}.txt"
        
        # Güvenli dosya adı oluştur
        filename = filename.replace(' ', '_').replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i').replace('ö', 'o').replace('ş', 's').replace('ü', 'u')
        
        # Tam yol
        full_path = os.path.join(location, filename)
        
        # Dosyayı oluştur
        with open(full_path, 'w', encoding='utf-8') as f:
            if content:
                f.write(content)
            else:
                f.write(f"# {filename}\n# GlassesCat tarafından oluşturuldu\n# {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        return jsonify({
            'success': True,
            'response': f'✅ Dosya oluşturuldu: {filename}\n📁 Konum: {location}\n💡 Notepad ile açmak için: "aç {filename}"',
            'type': 'file_create',
            'file_path': full_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'❌ Dosya oluşturulamadı: {str(e)}'
        })


def open_application(app_name):
    """Uygulama başlat - Actions modülünü kullan (Agent Mimarisi)"""
    try:
        # DÜŞÜNCE LOGU: İşlem başlıyor
        thought_logger.log(f"Kullanıcı '{app_name}' açmak istedi. APP_MAPPINGS kontrol ediliyor...", "Actions")
        
        # Önce actions.py'deki launch_app'i dene
        if ACTIONS_AVAILABLE:
            try:
                thought_logger.log(f"Actions modülünden '{app_name}' başlatma isteği yapılıyor...", "Actions")
                result = launch_app(app_name)
                
                thought_logger.log(f"Yol bulundu! '{app_name}' başlatılıyor...", "Actions")
                return jsonify({
                    'success': True,
                    'response': result.get('message', f'🚀 {app_name} başlatılıyor...'),
                    'type': 'app',
                    'source': 'actions_module',
                    'thoughts': thought_logger.get_recent_thoughts(3)
                })
            except ValueError as e:
                # Actions modülü bulamadı, fallback'e geç
                thought_logger.log(f"'{app_name}' APP_MAPPINGS'de bulunamadı. Fallback moda geçiliyor...", "Actions")
                print(f"[Agent] Actions bulamadı: {e}, fallback kullanılıyor...")
                pass
        
        # Fallback: Yerleşik basit başlatma
        thought_logger.log(f"Fallback başlatma mekanizması kullanılıyor...", "System")
        return open_application_fallback(app_name)
        
    except Exception as e:
        thought_logger.log(f"HATA: Uygulama başlatılamadı - {str(e)}", "System")
        return jsonify({'error': f'Uygulama başlatılamadı: {str(e)}'}), 500


def open_application_fallback(app_name):
    """Fallback uygulama başlatma - Actions kullanılamazsa"""
    try:
        thought_logger.log(f"Fallback mod: '{app_name}' için basit başlatma deneniyor...", "System")
        
        # Basit eşleştirme
        app_name_lower = app_name.lower().strip()
        
        # Türkçe ekleri kaldır
        suffixes = [' yi', ' yı', ' yu', ' yü', ' ni', ' nı', ' nu', ' nü', ' i', ' ı', ' u', ' ü']
        for suffix in sorted(suffixes, key=len, reverse=True):
            if app_name_lower.endswith(suffix):
                app_name_lower = app_name_lower[:-len(suffix)].strip()
                break
        
        thought_logger.log(f"Türkçe ekler temizlendi. '{app_name_lower}' başlatılıyor...", "System")
        
        # Basit başlatma
        subprocess.Popen(f'start "" "{app_name_lower}"', shell=True)
        
        thought_logger.log(f"'{app_name}' başarıyla başlatıldı (fallback).", "System")
        return jsonify({
            'success': True,
            'response': f'🚀 {app_name} başlatılıyor (fallback)...',
            'type': 'app',
            'source': 'fallback',
            'thoughts': thought_logger.get_recent_thoughts(3)
        })
    except Exception as e:
        thought_logger.log(f"Fallback HATA: '{app_name}' başlatılamadı - {str(e)}", "System")
        return jsonify({
            'success': False,
            'response': f'❌ "{app_name}" başlatılamadı: {str(e)}',
            'thoughts': thought_logger.get_recent_thoughts(3)
        })


def launch_app_with_windows_key(app_name):
    """PyAutoGUI ile Windows tuşu + uygulama adı yaz + Enter"""
    try:
        import pyautogui
        import time
        
        # PyAutoGUI güvenlik ayarları
        pyautogui.FAILSAFE = True
        
        # Önce Escape bas (menü kapalı olsun)
        pyautogui.keyDown('esc')
        pyautogui.keyUp('esc')
        time.sleep(0.1)
        
        # Windows tuşuna bas - hotkey kullan (daha güvenilir)
        pyautogui.hotkey('win')
        time.sleep(0.5)  # Menünün açılması için bekle
        
        # Uygulama adını yaz (Türkçe karakterleri düzelt ve boşlukları temizle)
        clean_name = app_name.lower().strip()
        
        # Türkçe ekleri kaldır (tekrar kontrol)
        suffixes = [' yi', ' yı', ' yu', ' yü', ' ni', ' nı', ' nu', ' nü', ' i', ' ı', ' u', ' ü']
        for suffix in sorted(suffixes, key=len, reverse=True):
            if clean_name.endswith(suffix):
                clean_name = clean_name[:-len(suffix)].strip()
                break
        
        # Türkçe karakterleri İngilizce'ye çevir
        turkish_map = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u', 
                       'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'}
        for tr, eng in turkish_map.items():
            clean_name = clean_name.replace(tr, eng)
        
        # Sadece harf ve sayıları al
        import re
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', clean_name)
        
        if clean_name:
            pyautogui.typewrite(clean_name, interval=0.02)
            time.sleep(0.8)  # Arama sonuçlarının gelmesi için bekle
            
            # Enter'a bas
            pyautogui.keyDown('return')
            pyautogui.keyUp('return')
        else:
            pyautogui.keyDown('esc')
            pyautogui.keyUp('esc')
            return jsonify({
                'success': False,
                'response': f'❌ "{app_name}" uygulama adı geçersiz.'
            })
        
        return jsonify({
            'success': True,
            'response': f'🚀 {app_name.capitalize()} Windows aramasıyla açılıyor...',
            'type': 'app'
        })
        
    except ImportError:
        # PyAutoGUI yoksa normal yöntemi dene
        try:
            subprocess.Popen(f'start "" "{app_name}"', shell=True)
            return jsonify({
                'success': True,
                'response': f'🚀 {app_name.capitalize()} başlatılıyor...',
                'type': 'app'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'response': f'❌ "{app_name}" bulunamadı.\n💡 Desteklenen uygulamalar: chrome, spotify, discord, word, excel, notepad, calc, vscode...'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'❌ "{app_name}" açılamadı.\n📝 Hata: {str(e)}\n💡 Uygulama bilgisayarınızda yüklü olmayabilir.'
        })


def toggle_root_mode(password=None, bypass_password=False):
    """Root modu aç/kapat (şifre korumalı)"""
    global root_mode_active, root_kali_connected, root_auth_attempts
    
    # Kapatmak için şifre gerekmez
    if root_mode_active:
        root_mode_active = False
        root_kali_connected = False
        root_auth_attempts = 0
        return jsonify({
            'success': True,
            'response': "⚪ Root mod kapalı",
            'root_mode': False,
            'type': 'system'
        })
    
    # Terminal bypass ise şifre kontrolü atla
    if bypass_password:
        root_mode_active = True
        root_auth_attempts = 0
        status = "🔴 ROOT MOD AKTİF (Terminal)\n💀 Teknik yetkiler etkin!\n\n💡 Admin menü için: admin\n💡 Kali bağlantısı: kali bağlan IP kullanıcı şifre"
        
        if kali_connected:
            root_kali_connected = True
        
        return jsonify({
            'success': True,
            'response': status,
            'root_mode': root_mode_active,
            'type': 'system'
        })
    
    # Açmak için şifre kontrolü (web için)
    if not password or password != ROOT_PASSWORD:
        root_auth_attempts += 1
        remaining_attempts = 3 - root_auth_attempts
        
        if root_auth_attempts >= 3:
            return jsonify({
                'success': False,
                'response': f'� Çok fazla başarısız deneme!\n� Root mod 5 dakika kilitlendi.',
                'type': 'system',
                'locked': True
            })
        
        return jsonify({
            'success': False,
            'response': f'🔒 Root mod şifresi gerekli!\n💡 Kalan deneme: {remaining_attempts}\n📝 Kullanım: root şifre [şifreniz]\n🔑 Varsayılan: GlassCat2026!',
            'type': 'system',
            'needs_password': True
        })
    
    # Şifre doğru - Root modu aç
    root_mode_active = True
    root_auth_attempts = 0
    status = "🔴 ROOT MOD AKTİF\n💀 Teknik yetkiler etkin!\n\n💡 Admin menü için: admin\n💡 Kali bağlantısı: kali bağlan IP kullanıcı şifre"
    
    if kali_connected:
        root_kali_connected = True
    
    return jsonify({
        'success': True,
        'response': status,
        'root_mode': root_mode_active,
        'type': 'system'
    })


def handle_root_command(message):
    """Root mod komutları - Kali bilgilendirme dahil"""
    global root_mode_active
    msg_lower = message.lower()
    
    if msg_lower in ['exit', 'çık']:
        return toggle_root_mode()
    
    if msg_lower in ['help', 'yardım', 'admin', 'menü', 'menu', 'root menü', 'root menu', 'root help', 'komutlar']:
        return jsonify({
            'success': True,
            'response': '''💀 ROOT MOD - Admin Menü

🔴 Mevcut Durum: AKTİF

📋 Komutlar:
• exit / çık - Root moddan çık
• help / yardım - Bu menüyü göster

🔐 Kali Linux:
• kali bağlan IP kullanıcı şifre - SSH bağlantısı
• kali [komut] - Kali'de komut çalıştır (örn: kali nmap -sS 192.168.1.1)
• kali linux nedir - Kali hakkında bilgi

🔍 Araştırma:
• araştır [konu] - Teknik kaynaklardan ara (StackOverflow, GitHub, HackerNews)

⚠️ Etik kullanım: Sadece izin verilen sistemlerde kullanın!''',
            'type': 'root'
        })
    
    # Kali Linux bilgilendirme soruları (bağlı olmasa bile cevapla)
    kali_info_keywords = ['kali linux nedir', 'kali nedir', 'kali ne işe yarar', 
                          'kali nasıl kurulur', 'kali kullanımı', 'kaliye nasıl bağlanır',
                          'kali bağlanmak', 'kali ssh', 'kali linux hakkında']
    
    if any(keyword in msg_lower for keyword in kali_info_keywords):
        return jsonify({
            'success': True,
            'response': '''🐉 Kali Linux - Penetrasyon Test Dağıtımı

📌 Kali Linux Nedir?
• Siber güvenlik ve penetrasyon testleri için özel Linux dağıtımı
• Offensive Security tarafından geliştirildi
• 600+ güvenlik aracı içerir

🔧 Temel Araçlar:
• nmap - Ağ taraması
• metasploit - Exploit framework
• wireshark - Paket analizi
• aircrack-ng - WiFi kırma
• sqlmap - SQL injection
• burpsuite - Web uygulama testi

💻 Bağlanmak İçin:
   kali bağlan IP kullanıcı şifre
   Örnek: kali bağlan 192.168.1.100 root toor

⚠️ Etik kullanım: Sadece izin verilen sistemlerde kullanın!''',
            'type': 'root'
        })
    
    if msg_lower.startswith('kali '):
        # Kali komutları için bağlantı kontrolü kaldırıldı - kullanıcı denemeye izin ver
        return handle_root_kali_command(message[5:].strip())
    
    return ask_ollama(message, model=ROOT_MODEL)


def handle_root_kali_command(command):
    """Root modda Kali komutları"""
    cmd_lower = command.lower()
    
    if cmd_lower.startswith('nmap'):
        return kali_execute(f"sudo {command}")
    if cmd_lower.startswith('sqlmap'):
        return kali_execute(f"sudo {command} --batch")
    if cmd_lower.startswith('hydra'):
        return kali_execute(f"sudo {command}")
    
    if not cmd_lower.startswith('sudo'):
        command = f"sudo {command}"
    
    return kali_execute(command)


def ask_ollama(message, model=None):
    """Ollama'dan yanıt al - MODEL ROUTER ile entegre + Düşünce Logları"""
    global root_mode_active
    
    # DÜŞÜNCE LOGU: AI işlemi başlıyor
    thought_logger.log(f"Kullanıcı mesajı alındı: '{message[:50]}...'", "AI")
    thought_logger.log(f"AI yanıtı hazırlanıyor...", "AI")
    
    # Önce Model Router'ı dene
    if MODEL_ROUTER_AVAILABLE:
        try:
            thought_logger.log(f"Model Router kullanılıyor. Uygun model seçiliyor...", "Router")
            router = get_model_router()
            
            # Model tipi belirleniyor
            model_type = "CODING" if root_mode_active else "AUTO"
            thought_logger.log(f"Model tipi: {model_type} (Root: {root_mode_active})", "Router")
            
            # Callback fonksiyonu - Model Router'dan gelen düşünce logları
            def router_thought_callback(thought, source):
                thought_logger.log(thought, source)
            
            result = router.chat(message, root_mode=root_mode_active, thought_callback=router_thought_callback)
            
            if result.get('success'):
                thought_logger.log(f"Model Router yanıt verdi. Model: {result.get('model', 'unknown')}", "Router")
                return jsonify({
                    'success': True,
                    'response': result['response'],
                    'type': 'ai',
                    'model': result.get('model', 'unknown'),
                    'model_type': result.get('model_type', 'unknown'),
                    'backend': result.get('backend', 'Ollama'),
                    'router': True,
                    'thoughts': thought_logger.get_recent_thoughts(5)
                })
            else:
                # Router başarısız olursa fallback'e geç
                thought_logger.log(f"Model Router hatası: {result.get('error', 'Bilinmeyen hata')}. Fallback'e geçiliyor...", "Router")
                print(f"[Agent] Router hatası: {result.get('error', 'Bilinmeyen hata')}")
        except Exception as e:
            thought_logger.log(f"Model Router çağrı hatası: {e}. Fallback kullanılıyor...", "System")
            print(f"[Agent] Router çağrı hatası: {e}")
    else:
        thought_logger.log(f"Model Router kullanılamıyor. Direkt Ollama kullanılıyor...", "System")
    
    # Fallback: Direkt Ollama API çağrısı
    if model is None:
        model = ROOT_MODEL if root_mode_active else DEFAULT_MODEL
    
    try:
        # GEMINI ZEKASI + OYUN BİLGİSİ - Gelişmiş Sistem Prompt
        if root_mode_active:
            system_prompt = f"""Sen GG Studio 2026'nın asistanısın. ROOT MOD AKTİF.

{GEMINI_PERSONALITY}

OYUN BİLGİSİ:
{GAMING_KNOWLEDGE}

KESİN KURALLAR - KESİNLİKLE UYGULA:
1. SADECE TÜRKÇE cevap ver, İngilizce KARMA
2. "ı/i/u/ü" karıştırma - Kesinlikle doğru kullan
3. "yi/yi/yu/yü" eklerini doğru kullan
4. Cümle başlarını BÜYÜK harfle başlat
5. Noktalama işaretlerini doğru kullan
6. Teknik terimleri Türkçe'ye uygun çevir
7. Akademik Türkçe, argo yok
8. Root modda teknik detay ver, kısa tutma
9. Kendinden bahsetme, sadece soruyu cevapla
10. "Ben yapay zekayım" gibi ifadeler kullanma

ROOT MOD ÖZELLİKLERİ:
• Kali Linux komutları çalıştırabilirsin
• Teknik araştırma yapabilirsin (StackOverflow, GitHub)
• Siber güvenlik bilgisi verebilirsin
• Derinlemesine analiz yapabilirsin

Kullanıcı: """
        else:
            system_prompt = f"""Sen GG Studio 2026'nın asistanısın.

{GEMINI_PERSONALITY}

OYUN BİLGİSİ:
{GAMING_KNOWLEDGE}

KESİN KURALLAR - KESİNLİKLE UYGULA:
1. SADECE TÜRKÇE cevap ver, İngilizce KARMA
2. "ı/i/u/ü" karıştırma - Kesinlikle doğru kullan
3. "yi/yi/yu/yü" eklerini doğru kullan
4. Cümle başlarını BÜYÜK harfle başlat
5. Noktalama işaretlerini doğru kullan
6. Teknik terimleri Türkçe'ye uygun çevir
7. Akademik Türkçe, argo yok
8. Samimi ve yardımsever ol
9. Emoji kullan (max 1-2)
10. Kapsamlı ama öz cevaplar ver
11. Maddeler halinde yaz
12. Örnekler ver
13. Kendinden bahsetme, sadece soruyu cevapla
14. "Ben yapay zekayım" gibi ifadeler kullanma

GG STUDIO 2026 - Berkay Gülmez / Arda Burak Çetiner tarafından geliştirilmiştir.

Kullanıcı: """
        
        thought_logger.log(f"Ollama'ya istek gönderiliyor. Model: {model}", "AI")
        
        payload = {
            "model": model,
            "prompt": system_prompt + message,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', 'Yanıt alınamadı')
            
            thought_logger.log(f"Ollama yanıt verdi. Yanıt uzunluğu: {len(ai_response)} karakter", "AI")
            
            return jsonify({
                'success': True,
                'response': ai_response,
                'type': 'ai',
                'model': model,
                'router': False,
                'thoughts': thought_logger.get_recent_thoughts(5)
            })
        else:
            thought_logger.log(f"Ollama hatası: HTTP {response.status_code}", "AI")
            return jsonify({
                'success': False,
                'response': f'❌ Ollama hatası: {response.status_code}',
                'thoughts': thought_logger.get_recent_thoughts(3)
            })
            
    except Exception as e:
        thought_logger.log(f"AI işlemi hatası: {str(e)}", "System")
        return jsonify({
            'success': False,
            'response': f'❌ Hata: {str(e)}'
        })


# OYUN HATA ANALİZİ - Model Router ile

def analyze_game_error_with_router(error_msg):
    """
    Oyun hatasını Model Router ile analiz et.
    Hata mesajına göre çözüm önerileri sunar.
    """
    thought_logger.log(f"Oyun hatasi analiz ediliyor: {error_msg[:50]}...", "Router")
    
    # Yaygın hata desenleri
    if "pygame" in error_msg.lower() or "pygame" in str(sys.exc_info()):
        return """Pygame hatası tespit edildi!
        
💡 Çözüm önerileri:
1. Pygame kurulumunu kontrol et: pip install pygame
2. Python sürümü uyumluluğunu kontrol et (3.7+)
3. .venv içinde pygame kurulu mu kontrol et

Kod:
cd C:\\Users\\ErCuM\\CascadeProjects\\niko_ai
python -m pip install pygame
"""
    
    if "module" in error_msg.lower() or "import" in error_msg.lower():
        return """Modül import hatası!
        
💡 Çözüm önerileri:
1. Eksik kütüphaneleri yükle: pip install -r requirements.txt
2. .venv'i aktif et: .venv\\Scripts\\activate
3. PYTHONPATH kontrolü yap

Kod:
cd C:\\Users\\ErCuM\\CascadeProjects\\niko_ai
.venv\\Scripts\\activate
pip install pygame numpy
"""
    
    if "display" in error_msg.lower() or "screen" in error_msg.lower():
        return """Ekran/görüntü hatası!
        
💡 Çözüm önerileri:
1. Pygame init() çağrıldı mı kontrol et
2. Ekran çözünürlüğü uyumlu mu kontrol et
3. Windows DPI ayarlarını kontrol et

Kod:
pygame.init()  # Unutulmuş olabilir
screen = pygame.display.set_mode((800, 600))
"""
    
    # Genel hata
    return f"""Genel hata tespit edildi: {error_msg[:100]}
    
💡 Çözüm önerileri:
1. Hata mesajını dikkatlice oku
2. game_escape.py dosyasını kontrol et
3. .venv ortamını aktif et ve bağımlılıkları yükle

Kod:
cd C:\\Users\\ErCuM\\CascadeProjects\\niko_ai
.venv\\Scripts\\activate
python game_escape.py --test
"""


# ARAŞTIRMA FONKSİYONLARI - Root/Normal mod ayrımı

def research_technical(query):
    """🔴 ROOT MOD: Teknik kaynaklardan araştırma yap (StackExchange, GitHub, HackerNews)"""
    try:
        print(f"🔴 [ROOT] Teknik araştırma: {query}")
        
        all_results = []
        
        # 1. StackOverflow (teknik sorular)
        try:
            stack_results = search_stackoverflow(query)
            all_results.extend(stack_results)
        except:
            pass
        
        # 2. GitHub (kod/projeler)
        try:
            github_results = search_github(query)
            all_results.extend(github_results)
        except:
            pass
        
        # 3. HackerNews (teknik haberler)
        try:
            hn_results = search_hackernews(query)
            all_results.extend(hn_results)
        except:
            pass
        
        # 4. DuckDuckGo (yedek)
        try:
            ddg_results = search_duckduckgo(query)
            all_results.extend(ddg_results)
        except:
            pass
        
        # Boş sonuçları filtrele
        filtered_results = []
        for result in all_results:
            title = result.get('title', '').strip()
            if title and len(title) > 3:  # En az 3 karakter
                filtered_results.append(result)
        
        all_results = filtered_results
        
        if not all_results:
            return jsonify({
                'success': False,
                'response': f'❌ "{query}" için teknik sonuç bulunamadı.'
            })
        
        # Sonuçları özetle
        summary_lines = [f"🔴 [ROOT MOD] **{query}** teknik araştırma sonuçları:\n"]
        
        for i, result in enumerate(all_results[:5], 1):
            icon = result.get('icon', '💻')
            title = result['title'][:60]
            summary = result.get('summary', '')[:100]
            source = result.get('source', '')
            
            summary_lines.append(f"\n{i}. {icon} **{title}** [{source}]")
            if summary:
                summary_lines.append(f"   {summary}")
        
        summary_lines.append(f"\n\n💡 {len(all_results)} teknik sonuç bulundu.")
        
        return jsonify({
            'success': True,
            'response': '\n'.join(summary_lines),
            'type': 'research_technical',
            'query': query,
            'sources': len(all_results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'❌ Teknik araştırma hatası: {str(e)}'
        })


def research_general(query):
    """⚪ NORMAL MOD: Genel web araması (DuckDuckGo) + Ollama analizi"""
    try:
        print(f"⚪ [NORMAL] Genel araştırma: {query}")
        
        # Kaynaklardan araştırma yap
        all_results = []
        
        # 1. DuckDuckGo
        try:
            ddg_results = search_duckduckgo(query)
            all_results.extend(ddg_results)
        except:
            pass
        
        # 2. Google (yedek)
        try:
            google_results = search_google_custom(query)
            all_results.extend(google_results)
        except:
            pass
        
        # 3. StackOverflow (teknik sorular)
        try:
            stack_results = search_stackoverflow(query)
            all_results.extend(stack_results)
        except:
            pass
        
        # 4. GitHub (kod/projeler)
        try:
            github_results = search_github(query)
            all_results.extend(github_results)
        except:
            pass
        
        # Boş sonuçları filtrele
        filtered_results = []
        for result in all_results:
            title = result.get('title', '').strip()
            if title and len(title) > 3:
                filtered_results.append(result)
        
        all_results = filtered_results
        
        if not all_results:
            # Sonuç yoksa direkt Ollama'ya sor
            return ask_ollama(query)
        
        # Sonuçları context olarak Ollama'ya gönder
        context = f"Aşağıdaki kaynaklardan '{query}' hakkında bilgi toplanmıştır:\n\n"
        
        for i, result in enumerate(all_results[:5], 1):
            source = result.get('source', '')
            title = result.get('title', '')
            summary = result.get('summary', '') or result.get('snippet', '')
            
            context += f"{i}. [{source}] {title}\n"
            if summary:
                context += f"   {summary}\n"
            context += "\n"
        
        context += f"\nBu kaynaklara dayanarak, '{query}' hakkında Türkçe bir özet hazırla."
        
        # Ollama'ya context ile sor
        return ask_ollama(context, model=DEFAULT_MODEL)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'❌ Araştırma hatası: {str(e)}'
        })


def search_google_custom(query):
    """Google Programmable Search API - En kaliteli sonuçlar"""
    # Not: API key ve search engine ID gerekli
    # Ücretsiz: https://programmablesearchengine.google.com/
    # Günlük 100 arama ücretsiz
    
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY', '')
    cx = os.getenv('GOOGLE_SEARCH_CX', '')
    
    if not api_key or not cx:
        return []  # API key yoksa boş dön, yedek kullanılsın
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cx,
        'q': query,
        'num': 5
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        results = []
        for item in data.get('items', []):
            title = item.get('title', '').strip()
            snippet = item.get('snippet', '').strip()
            
            # Boş başlıkları atla
            if not title or len(title) < 5:
                continue
                
            results.append({
                'title': title,
                'snippet': snippet,
                'url': item.get('link', ''),
                'source': 'Google'
            })
        
        return results
    except:
        return []


def search_duckduckgo(query):
    """DuckDuckGo - Yedek arama motoru"""
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=5):
                title = r.get('title', '').strip()
                body = r.get('body', '').strip()
                
                # Boş veya çok kısa başlıkları atla
                if not title or len(title) < 5:
                    continue
                    
                # Spam/ilgisiz içerikleri filtrele
                spam_keywords = ['sex', 'porn', 'xxx', 'nude', 'onlyfans']
                if any(spam in title.lower() or spam in body.lower() for spam in spam_keywords):
                    continue
                
                results.append({
                    'title': title,
                    'snippet': body[:150],
                    'url': r.get('href', ''),
                    'source': 'DuckDuckGo'
                })
            
            return results
    except:
        return []


def search_stackoverflow(query):
    """StackOverflow teknik araması"""
    url = "https://api.stackexchange.com/2.3/search/advanced"
    params = {
        'order': 'desc',
        'sort': 'relevance',
        'q': query,
        'site': 'stackoverflow',
        'pagesize': 3
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        results = []
        for item in data.get('items', []):
            title = item.get('title', '').strip()
            # Boş başlıkları atla
            if not title or len(title) < 3:
                continue
            results.append({
                'icon': '💻',
                'title': title,
                'summary': f"Skor: {item.get('score', 0)} | Yanıt: {item.get('answer_count', 0)} | Görüntülenme: {item.get('view_count', 0)}",
                'url': item.get('link', ''),
                'source': 'StackOverflow'
            })
        
        return results
    except:
        return []


def search_stackexchange(query, site='stackoverflow'):
    """StackExchange/StackOverflow araması"""
    url = f"https://api.stackexchange.com/2.3/search/advanced"
    params = {
        'order': 'desc',
        'sort': 'relevance',
        'q': query,
        'site': site,
        'pagesize': 3
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        results = []
        for item in data.get('items', []):
            title = item.get('title', '').strip()
            # Boş başlıkları atla
            if not title or len(title) < 3:
                continue
            results.append({
                'icon': '💻',
                'title': title,
                'summary': f"Skor: {item.get('score', 0)} | Yanıt: {item.get('answer_count', 0)}",
                'url': item.get('link', ''),
                'source': 'StackExchange'
            })
        
        return results
    except:
        return []


def search_github(query):
    """GitHub repo araması"""
    url = "https://api.github.com/search/repositories"
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': 3
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        results = []
        for item in data.get('items', []):
            title = item.get('name', '').strip()
            # Boş başlıkları atla
            if not title or len(title) < 3:
                continue
            results.append({
                'icon': '⭐',
                'title': title,
                'summary': f"⭐ {item.get('stargazers_count', 0)} | {item.get('description', '')[:80]}",
                'url': item.get('html_url', ''),
                'source': 'GitHub'
            })
        
        return results
    except:
        return []


def search_hackernews(query):
    """HackerNews araması"""
    # Önce arama yap
    search_url = "https://hn.algolia.com/api/v1/search"
    params = {
        'query': query,
        'hitsPerPage': 3
    }
    
    response = requests.get(search_url, params=params, timeout=15)
    data = response.json()
    
    results = []
    for hit in data.get('hits', []):
        title = hit.get('title', '').strip()
        # Boş başlıkları atla
        if not title or len(title) < 3:
            continue
        results.append({
            'icon': '📰',
            'title': title,
            'summary': f"Puan: {hit.get('points', 0)} | Yorum: {hit.get('num_comments', 0)}",
            'url': hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
            'source': 'HackerNews'
        })
    
    return results


def search_reddit(query):
    """Reddit araması - JSON endpoint"""
    url = "https://www.reddit.com/search.json"
    params = {
        'q': query,
        'limit': 3,
        'sort': 'relevance'
    }
    headers = {
        'User-Agent': 'GlassesCat Research Bot 1.0'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        data = response.json()
        
        results = []
        for post in data.get('data', {}).get('children', []):
            post_data = post.get('data', {})
            title = post_data.get('title', '').strip()
            # Boş başlıkları atla
            if not title or len(title) < 3:
                continue
            results.append({
                'icon': '🤖',
                'title': title,
                'summary': f"Upvote: {post_data.get('ups', 0)} | r/{post_data.get('subreddit', '')}",
                'url': f"https://reddit.com{post_data.get('permalink', '')}",
                'source': 'Reddit'
            })
        
        return results
    except:
        return []


# KALI LINUX BAĞLANTISI

def handle_kali_command(command):
    """Kali Linux komutları"""
    global kali_ssh, kali_connected
    
    cmd_lower = command.lower()
    
    if cmd_lower.startswith('bağlan ') or cmd_lower.startswith('baglan '):
        parts = command.split()
        if len(parts) >= 4:
            return kali_connect(parts[1], parts[2], parts[3])
        return jsonify({'success': False, 'response': 'Kullanım: kali bağlan IP kullanıcı şifre'})
    
    if cmd_lower in ['bağlantı kes', 'baglanti kes']:
        return kali_disconnect()
    
    if not kali_connected:
        return jsonify({
            'success': False,
            'response': '❌ Kali bağlı değil! Önce "kali bağlan IP kullanıcı şifre"'
        })
    
    return kali_execute(command)


def kali_connect(ip, username, password, port=22):
    """Kali'ye SSH ile bağlan"""
    global kali_ssh, kali_connected, root_kali_connected
    
    try:
        kali_ssh = paramiko.SSHClient()
        kali_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kali_ssh.connect(ip, port=port, username=username, password=password, timeout=10)
        kali_connected = True
        root_kali_connected = root_mode_active
        
        stdin, stdout, stderr = kali_ssh.exec_command('uname -a')
        uname = stdout.read().decode().strip()
        
        return jsonify({
            'success': True,
            'response': f'✅ Kali bağlandı!\n🖥️ {uname[:50]}...',
            'type': 'kali',
            'connected': True
        })
    except Exception as e:
        kali_connected = False
        kali_ssh = None
        return jsonify({'success': False, 'response': f'❌ Bağlantı hatası: {str(e)}'})


def kali_disconnect():
    """Kali bağlantısını kes"""
    global kali_ssh, kali_connected, root_kali_connected
    
    try:
        if kali_ssh:
            kali_ssh.close()
        kali_ssh = None
        kali_connected = False
        root_kali_connected = False
        return jsonify({'success': True, 'response': '👋 Kali bağlantısı kesildi.', 'type': 'kali'})
    except:
        return jsonify({'success': True, 'response': '👋 Bağlantı kapatıldı.', 'type': 'kali'})


def kali_execute(command):
    """Kali'de komut çalıştır"""
    global kali_ssh
    
    try:
        stdin, stdout, stderr = kali_ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        exit_code = stdout.channel.recv_exit_status()
        
        if error and not output:
            return jsonify({'success': False, 'response': f'⚠️ Hata:\n{error[:500]}', 'type': 'kali'})
        
        return jsonify({'success': True, 'response': f'📤 Çıktı:\n{output[:1000]}', 'type': 'kali'})
    except Exception as e:
        return jsonify({'success': False, 'response': f'❌ Hata: {str(e)}'})


@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Tüm notları getir"""
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                notes = f.readlines()
            return jsonify({'notes': notes})
        return jsonify({'notes': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Sunucu durumu"""
    return jsonify({
        'status': 'ok',
        'service': 'GlassesCat Server',
        'version': '1.0.0',
        'root_mode': root_mode_active,
        'kali_connected': kali_connected
    })


if __name__ == '__main__':
    print("[AI] GlassesCat Server baslatiliyor...")
    print("[URL] http://localhost:5000")
    print("\n[Komutlar]:")
    print("   Not al: Bugun toplanti var")
    print("   Ac notepad")
    print("   root (Root mod - sifre: GlassCat2026!)")
    print("   kali baglan IP kullanici sifre")
    print("\n" + "="*50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
