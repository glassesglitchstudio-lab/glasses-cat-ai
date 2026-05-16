"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          NIKO AI - HERMES PC AJANI                        ║
║          Desktop Application v2.0                         ║
║                                                           ║
║    Full-Featured Personal AI Assistant                    ║
║    JARVIS • HERMES • FRIDAY Style                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
import threading
import queue
import time
import datetime
import os
import sys
import subprocess
import webbrowser
import json
import re
from pathlib import Path

# System modules
try:
    import pyautogui
    PYAUTOGUI_OK = True
except:
    PYAUTOGUI_OK = False

try:
    import psutil
    PSUTIL_OK = True
except:
    PSUTIL_OK = False

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# App paths
USER_HOME = Path.home()
DESKTOP = USER_HOME / "Desktop"
DOCUMENTS = USER_HOME / "Documents"
DOWNLOADS = USER_HOME / "Downloads"

# APP paths
APP_PATHS = {
    'chrome': r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    'vscode': r"C:\Users\ErCuM\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    'discord': r"C:\Users\ErCuM\AppData\Local\Discord\Update.exe",
    'spotify': r"C:\Users\ErCuM\AppData\Roaming\Spotify\Spotify.exe",
    'telegram': r"C:\Users\ErCuM\AppData\Roaming\Telegram Desktop\Telegram.exe",
    'notepad': r"C:\Windows\System32\notepad.exe",
    'explorer': r"C:\Windows\explorer.exe",
    'cmd': r"C:\Windows\System32\cmd.exe",
    'powershell': r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
}


class NikoAIApp(ctk.CTk):
    """Glassescat AI - Hermes Style Desktop Application"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Glassescat AI - Personal Assistant")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Make window frameless with custom titlebar
        self.overrideredirect(True)
        self.configure(fg_color=["#1a1a2e", "#16213e"])
        
        # Variables
        self.message_queue = queue.Queue()
        self.processing = False
        self.command_history = []
        self.history_index = -1
        self.voice_enabled = ctk.BooleanVar(value=True)
        self.minimized_to_tray = False
        
        # Build UI
        self._create_ui()
        
        # Start message processor
        self.after(100, self._process_messages)
        
        # Welcome message
        self._add_message("system", "Glassescat AI", "Merhaba! Ben Niko, kişisel asistanınız. Size nasıl yardımcı olabilirim?\n\nKomutlar için 'yardım' yazabilirsiniz.")
        
        # AI Chat Function
        self._init_ai()
    
    def _create_ui(self):
        """Create the UI components"""
        
        # Title bar
        self.title_bar = ctk.CTkFrame(self, height=40, fg_color="#0f0f23", corner_radius=0)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.title_bar, 
            text="  Glassescat AI - Personal Assistant",
            font=("Segoe UI", 14, "bold"),
            text_color="#00d4ff"
        )
        self.title_label.pack(side="left", padx=15, pady=5)
        
        # Window controls
        self.btn_min = ctk.CTkButton(
            self.title_bar, text="─", width=40, height=30,
            fg_color="transparent", hover_color="#2a2a4a",
            command=self._minimize_window, text_color="#ffffff"
        )
        self.btn_min.pack(side="right", padx=2)
        
        self.btn_max = ctk.CTkButton(
            self.title_bar, text="□", width=40, height=30,
            fg_color="transparent", hover_color="#2a2a4a",
            command=self._maximize_window, text_color="#ffffff"
        )
        self.btn_max.pack(side="right")
        
        self.btn_close = ctk.CTkButton(
            self.title_bar, text="✕", width=40, height=30,
            fg_color="transparent", hover_color="#ff4444",
            command=self._close_app, text_color="#ffffff"
        )
        self.btn_close.pack(side="right")
        
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left sidebar
        self.sidebar = ctk.CTkFrame(self.main_container, width=200, fg_color="#1a1a2e")
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Sidebar buttons
        sidebar_buttons = [
            ("🏠 Ana Sayfa", self._show_home),
            ("💻 Sistem", self._show_system),
            ("📁 Dosyalar", self._show_files),
            ("🎮 Oyunlar", self._show_games),
            ("⚙️ Ayarlar", self._show_settings),
        ]
        
        for text, cmd in sidebar_buttons:
            btn = ctk.CTkButton(
                self.sidebar, text=text, height=45,
                fg_color="#252545", hover_color="#353565",
                anchor="w", command=cmd,
                font=("Segoe UI", 12)
            )
            btn.pack(fill="x", padx=10, pady=5)
        
        # Quick actions
        ctk.CTkLabel(self.sidebar, text="Hızlı İşlemler", font=("Segoe UI", 11, "bold")).pack(pady=(20, 10))
        
        quick_actions = [
            ("🌐 Web Aç", lambda: self._quick_action("web")),
            ("📝 Not Al", lambda: self._quick_action("note")),
            ("📸 Screenshot", lambda: self._quick_action("screenshot")),
            ("🔊 Ses Kapa/Aç", lambda: self._quick_action("voice")),
        ]
        
        for text, cmd in quick_actions:
            btn = ctk.CTkButton(
                self.sidebar, text=text, height=35,
                fg_color="#2a2a4a", hover_color="#3a3a5a",
                anchor="w", command=cmd,
                font=("Segoe UI", 10)
            )
            btn.pack(fill="x", padx=10, pady=3)
        
        # Chat area (right side)
        self.chat_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.chat_frame.pack(side="right", fill="both", expand=True)
        
        # Messages area
        self.messages_frame = ctk.CTkScrollableFrame(
            self.chat_frame, fg_color="transparent",
            scrollbar_button_color="#2a2a4a"
        )
        self.messages_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Input area
        self.input_frame = ctk.CTkFrame(self.chat_frame, height=60, fg_color="#1a1a2e")
        self.input_frame.pack(fill="x", side="bottom")
        self.input_frame.pack_propagate(False)
        
        self.input_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Niko'ya bir şey sorun veya komut verin...",
            font=("Segoe UI", 12),
            fg_color="#252545",
            border_color="#3a3a5a",
            height=45
        )
        self.input_entry.pack(fill="x", padx=10, pady=10, side="left", expand=True)
        self.input_entry.bind("<Return>", self._send_message)
        self.input_entry.bind("<Up>", self._history_up)
        self.input_entry.bind("<Down>", self._history_down)
        
        self.send_btn = ctk.CTkButton(
            self.input_frame, text="Gönder", width=80, height=45,
            fg_color="#00d4ff", hover_color="#00b8dd",
            command=lambda: self._send_message(None),
            font=("Segoe UI", 12, "bold")
        )
        self.send_btn.pack(side="right", padx=10, pady=10)
        
        # Status bar
        self.status_bar = ctk.CTkFrame(self, height=25, fg_color="#0f0f23", corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_bar, text="  Hazır", 
            font=("Segoe UI", 10),
            text_color="#888888"
        )
        self.status_label.pack(side="left")
        
        # Voice toggle
        self.voice_toggle = ctk.CTkCheckBox(
            self.status_bar, text="Ses", variable=self.voice_enabled,
            font=("Segoe UI", 10), checkbox_height=15, checkbox_width=15
        )
        self.voice_toggle.pack(side="right", padx=10)
    
    def _add_message(self, msg_type, sender, content):
        """Add a message to the chat"""
        self.message_queue.put((msg_type, sender, content))
    
    def _process_messages(self):
        """Process messages from queue"""
        try:
            while True:
                msg_type, sender, content = self.message_queue.get_nowait()
                
                # Create message widget
                msg_frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
                
                if msg_type == "user":
                    msg_frame.pack(fill="x", pady=5, anchor="e")
                    bubble = ctk.CTkFrame(
                        msg_frame, 
                        fg_color="#00d4ff",
                        corner_radius=15
                    )
                    label = ctk.CTkLabel(
                        bubble, text=content, wraplength=500,
                        font=("Segoe UI", 11), text_color="#000000",
                        padx=15, pady=10
                    )
                    label.pack()
                    bubble.pack(side="right", padx=(50, 0))
                    
                elif msg_type == "system":
                    msg_frame.pack(fill="x", pady=5)
                    bubble = ctk.CTkFrame(
                        msg_frame,
                        fg_color="#252545",
                        corner_radius=15
                    )
                    header = ctk.CTkLabel(
                        bubble, text=sender,
                        font=("Segoe UI", 10, "bold"), text_color="#00d4ff",
                        padx=15, pady=(10, 0)
                    )
                    header.pack(anchor="w", padx=15)
                    label = ctk.CTkLabel(
                        bubble, text=content, wraplength=550,
                        font=("Segoe UI", 11), text_color="#ffffff",
                        padx=15, pady=10
                    )
                    label.pack(anchor="w", padx=15, pady=(0, 10))
                    bubble.pack(side="left", padx=(0, 50))
                    
                elif msg_type == "ai":
                    msg_frame.pack(fill="x", pady=5)
                    bubble = ctk.CTkFrame(
                        msg_frame,
                        fg_color="#2a2a4a",
                        corner_radius=15
                    )
                    header = ctk.CTkLabel(
                        bubble, text=f"Glassescat AI - {sender}",
                        font=("Segoe UI", 10, "bold"), text_color="#00ff88",
                        padx=15, pady=(10, 0)
                    )
                    header.pack(anchor="w", padx=15)
                    label = ctk.CTkLabel(
                        bubble, text=content, wraplength=550,
                        font=("Segoe UI", 11), text_color="#ffffff",
                        padx=15, pady=10
                    )
                    label.pack(anchor="w", padx=15, pady=(0, 10))
                    bubble.pack(side="left", padx=(0, 50))
                
                # Scroll to bottom
                self.messages_frame.after_idle(
                    lambda: self.messages_frame._parent_canvas.yview_moveto(1.0)
                )
                
        except queue.Empty:
            pass
        
        self.after(50, self._process_messages)
    
    def _send_message(self, event):
        """Send user message"""
        text = self.input_entry.get().strip()
        if not text:
            return
        
        # Add to history
        self.command_history.append(text)
        self.history_index = len(self.command_history)
        
        # Clear input
        self.input_entry.delete(0, "end")
        
        # Add user message
        self._add_message("user", "Siz", text)
        
        # Process command
        threading.Thread(target=self._process_command, args=(text,), daemon=True).start()
    
    def _process_command(self, text):
        """Process user command"""
        self._update_status("İşleniyor...")
        text_lower = text.lower()
        
        # Help command
        if text_lower in ['yardım', 'yardim', 'help', 'komutlar']:
            self._show_help()
            return
        
        # System info
        if text_lower in ['sistem bilgi', 'system info', 'bilgi']:
            self._show_system_info()
            return
        
        # Time
        if text_lower in ['saat kaç', 'saat kac', 'time', 'saat']:
            self._add_message("ai", "Sistem", f"Saat: {datetime.datetime.now().strftime('%H:%M:%S')}")
            return
        
        # Date
        if text_lower in ['tarih', 'date', 'bugün', 'bugun']:
            self._add_message("ai", "Sistem", f"Tarih: {datetime.datetime.now().strftime('%Y-%m-%d %A')}")
            return
        
        # Screenshot
        if 'screenshot' in text_lower or 'ekran görüntüsü' in text_lower or 'ekran goruntusu' in text_lower:
            self._take_screenshot()
            return
        
        # Open app
        if text_lower.startswith('aç ') or text_lower.startswith('ac ') or text_lower.startswith('baslat ') or text_lower.startswith('baslat '):
            app_name = text.split(' ', 1)[1] if ' ' in text else ""
            self._open_app(app_name)
            return
        
        # Search web
        if text_lower.startswith('ara ') or text_lower.startswith('search ') or text_lower.startswith('google '):
            query = text.split(' ', 1)[1] if ' ' in text else ""
            self._search_web(query)
            return
        
        # Note
        if text_lower.startswith('not al ') or text_lower.startswith('not ekle '):
            note_text = text.split(' ', 2)[2] if len(text.split(' ', 2)) > 2 else ""
            self._add_note(note_text)
            return
        
        # Exit
        if text_lower in ['çıkış', 'cikis', 'exit', 'kapat']:
            self._close_app()
            return
        
        # AI Chat (Ollama)
        self._ai_chat(text)
    
    def _show_help(self):
        """Show help message"""
        help_text = """
🤖 NIKO AI KOMUTLARI:

📌 SİSTEM:
  • sistem bilgi - Bilgisayar bilgileri
  • saat kaç - Mevcut saat
  • tarih - Bugünün tarihi

📌 UYGULAMALAR:
  • aç [uygulama] - Uygulama aç
  • ara [kelime] - Web'de ara
  • google [kelime] - Google'da ara

📌 DOSYALAR:
  • not al [metin] - Not kaydet
  • screenshot - Ekran görüntüsü al

📌 AI:
  • sor [soru] - AI'ye sor
  • [herhangi bir şey] - AI sohbeti

📌 KONTROL:
  • çıkış - Uygulamayı kapat
  • yardım - Bu yardımı göster
"""
        self._add_message("ai", "Yardım", help_text)
    
    def _show_system_info(self):
        """Show system information"""
        info = f"💻 SİSTEM BİLGİLERİ\n\n"
        info += f"Bilgisayar: {os.environ.get('COMPUTERNAME', '?')}\n"
        info += f"Kullanıcı: {os.environ.get('USERNAME', '?')}\n"
        info += f"Python: {sys.version.split()[0]}\n"
        
        if PSUTIL_OK:
            info += f"\n📊 KAYNAKLAR:\n"
            info += f"CPU: %{psutil.cpu_percent()}\n"
            info += f"RAM: %{psutil.virtual_memory().percent}\n"
            info += f"Disk: %{psutil.disk_usage('/').percent}\n"
            
            battery = psutil.sensors_battery()
            if battery:
                info += f"Pil: %{battery.percent}" + (" (Şarjda)\n" if battery.power_plugged else " (Şarjsız)\n")
        
        info += f"\n⏰ Çalışma Süresi: {datetime.datetime.now().strftime('%H:%M:%S')}"
        
        self._add_message("ai", "Sistem", info)
    
    def _open_app(self, app_name):
        """Open an application"""
        if not app_name:
            self._add_message("ai", "Sistem", "Uygulama adı belirtin. Örnek: 'aç chrome'")
            return
        
        app_lower = app_name.lower().replace(' ', '')
        
        # Check predefined paths
        for key, path in APP_PATHS.items():
            if key in app_lower or app_lower in key:
                if os.path.exists(path):
                    try:
                        subprocess.Popen(f'"{path}"')
                        self._add_message("ai", "Sistem", f"✅ {app_name} başlatıldı")
                        return
                    except Exception as e:
                        self._add_message("ai", "Sistem", f"❌ Hata: {str(e)}")
                        return
        
        # Try system PATH
        try:
            result = subprocess.run(['where', app_lower], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                subprocess.Popen(f'"{path}"')
                self._add_message("ai", "Sistem", f"✅ {app_name} başlatıldı")
                return
        except:
            pass
        
        # Try start command
        try:
            subprocess.Popen(f'start "" "{app_name}"', shell=True)
            self._add_message("ai", "Sistem", f"✅ {app_name} başlatıldı")
            return
        except Exception as e:
            self._add_message("ai", "Sistem", f"❌ {app_name} bulunamadı: {str(e)}")
    
    def _search_web(self, query):
        """Search on web"""
        if not query:
            self._add_message("ai", "Sistem", "Arama kelimesi belirtin.")
            return
        
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        self._add_message("ai", "Sistem", f"🔍 '{query}' için Google'da arama yapılıyor...")
    
    def _add_note(self, text):
        """Add a note"""
        if not text:
            self._add_message("ai", "Sistem", "Not içeriği belirtin.")
            return
        
        try:
            notes_file = DOCUMENTS / "glassescat_notes.txt"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(notes_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {text}\n")
            self._add_message("ai", "Sistem", f"✅ Not kaydedildi:\n{text}")
        except Exception as e:
            self._add_message("ai", "Sistem", f"❌ Not kaydedilemedi: {str(e)}")
    
    def _take_screenshot(self):
        """Take screenshot"""
        if not PYAUTOGUI_OK:
            self._add_message("ai", "Sistem", "❌ pyautogui kurulu değil")
            return
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_dir = DESKTOP / "Screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            filepath = screenshot_dir / f"glassescat_screenshot_{timestamp}.png"
            
            img = pyautogui.screenshot()
            img.save(str(filepath))
            
            self._add_message("ai", "Sistem", f"✅ Ekran görüntüsü kaydedildi:\n{filepath}")
        except Exception as e:
            self._add_message("ai", "Sistem", f"❌ Hata: {str(e)}")
    
    def _ai_chat(self, message):
        """Chat with AI (Ollama)"""
        try:
            import requests
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3.2", "prompt": message, "stream": False},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', 'Yanıt alınamadı.')
                self._add_message("ai", "AI", ai_response)
            else:
                self._add_message("ai", "AI", f"Ollama hatası: {response.status_code}")
        
        except Exception as e:
            self._add_message("ai", "AI", f"AI şu anda kullanılamıyor. Hata: {str(e)}\n\nOllama'nın çalıştığından emin olun.")
        
        self._update_status("Hazır")
    
    def _init_ai(self):
        """Initialize AI connection"""
        self._update_status("AI bağlantısı kontrol ediliyor...")
        
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                self._update_status("Hazır - Ollama bağlı")
            else:
                self._update_status("Hazır - Ollama bağlı değil")
        except:
            self._update_status("Hazır - Ollama çevrimdışı")
    
    def _show_home(self):
        """Show home view"""
        pass  # Already showing chat
    
    def _show_system(self):
        """Show system view"""
        self._show_system_info()
    
    def _show_files(self):
        """Show files view"""
        self._add_message("ai", "Dosyalar", "Dosya yöneticisi yakında eklenecek.\n\nŞimdilik 'not al [metin]' komutunu kullanabilirsiniz.")
    
    def _show_games(self):
        """Show games view"""
        self._add_message("ai", "Oyunlar", "🎮 OYUNLAR:\n\n• Minecraft\n• Valorant\n• CS2\n• GTA V\n• Fortnite\n• Apex Legends\n\nOyun açmak için: 'aç [oyun adı]'")
    
    def _show_settings(self):
        """Show settings view"""
        self._add_message("ai", "Ayarlar", "⚙️ AYARLAR:\n\n• Ses: Açık/Kapalı\n• Tema: Koyu (Aktif)\n• AI: Ollama (localhost:11434)\n\nAyarlar yakında GUI'den düzenlenebilir olacak.")
    
    def _quick_action(self, action):
        """Handle quick actions"""
        if action == "web":
            self.input_entry.insert(0, "ara ")
            self.input_entry.focus()
        elif action == "note":
            self.input_entry.insert(0, "not al ")
            self.input_entry.focus()
        elif action == "screenshot":
            self._take_screenshot()
        elif action == "voice":
            self.voice_enabled.set(not self.voice_enabled.get())
            status = "açık" if self.voice_enabled.get() else "kapalı"
            self._add_message("ai", "Sistem", f"🔊 Ses: {status}")
    
    def _history_up(self, event):
        """Navigate command history up"""
        if not self.command_history:
            return
        if self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, self.command_history[self.history_index])
    
    def _history_down(self, event):
        """Navigate command history down"""
        if not self.command_history:
            return
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, self.command_history[self.history_index])
        else:
            self.history_index = len(self.command_history)
            self.input_entry.delete(0, "end")
    
    def _update_status(self, text):
        """Update status bar"""
        self.status_label.configure(text=f"  {text}")
    
    def _minimize_window(self):
        """Minimize window"""
        self.minimize()
    
    def _maximize_window(self):
        """Maximize/restore window"""
        if self.winfo_manager() == "iconic":
            self.deiconify()
        else:
            self.attributes("-fullscreen", not self.attributes("-fullscreen"))
    
    def _close_app(self):
        """Close application"""
        self.destroy()
        sys.exit(0)
    
    def _start_drag(self, event):
        """Start window drag"""
        self.x = event.x
        self.y = event.y
    
    def _drag(self, event):
        """Drag window"""
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        x = self.winfo_x() + delta_x
        y = self.winfo_y() + delta_y
        self.geometry(f"+{x}+{y}")


def main():
    """Main entry point"""
    app = NikoAIApp()
    
    # Add drag functionality to title bar
    app.title_bar.bind("<Button-1>", app._start_drag)
    app.title_bar.bind("<B1-Motion>", app._drag)
    app.title_label.bind("<Button-1>", app._start_drag)
    app.title_label.bind("<B1-Motion>", app._drag)
    
    app.mainloop()


if __name__ == "__main__":
    main()
