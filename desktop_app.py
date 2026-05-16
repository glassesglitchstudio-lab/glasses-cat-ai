"""
GlassesCat BETA - Glass Morphism Desktop
#121212 + #00FFAB Neon + Normal Pencere + /Komutlar
"""

import customtkinter as ctk
import tkinter as tk
import threading
import time
import subprocess
import asyncio
import httpx
import psutil
import webbrowser
import pyautogui
import pygetwindow as gw
from ctypes import windll

# Tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# === RENKLER ===
COLORS = {
    "bg_dark": "#121212",
    "bg_medium": "#1E1E1E", 
    "bg_light": "#2D2D2D",
    "neon": "#00FFAB",
    "neon_hover": "#008855",
    "text": "#FFFFFF",
    "text_secondary": "#888888",
    "danger": "#FF4444",
    "warning": "#FFAA00",
}


class GlassesCatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Normal pencere (daha güvenilir)
        self.title("GlassesCat - SWA 1.6")
        self.geometry("1100x720")
        self.configure(fg_color=COLORS["bg_dark"])
        
        # AI - qwen sohbet için, deepseek kodlama için
        self.ollama_url = "http://localhost:11434"
        self.model = "qwen2.5-coder:7b"  # Sohbet için
        self.code_model = "deepseek-r1:8b"  # Kodlama için
        self.root_mode = False
        self.monitoring = True
        self.is_max = False
        
        # Modeller
        self.models = ["qwen2.5-coder:7b", "llama3.1:latest", "llama3.2:latest", "deepseek-r1:8b"]
        
        self.create_ui()
        self.start_monitoring()
        self.welcome()
        
        # Orb animasyon
        self.orb_scale = 1.0
        self.orb_dir = 1
        self.animate_orb()

    def create_ui(self):
        # Ana container
        self.main_container = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"])
        self.main_container.pack(fill="both", expand=True)
        
        # Sol nav panel
        self.nav = ctk.CTkFrame(self.main_container, width=160, fg_color=COLORS["bg_medium"], corner_radius=0)
        self.nav.pack(side="left", fill="y")
        self.nav.pack_propagate(False)
        
        # Nav butonları
        nav_items = [("🏠", "Ana Sayfa"), ("💬", "Sohbet"), ("🖥️", "Kontrol"), ("⚙️", "Ayarlar")]
        for icon, txt in nav_items:
            ctk.CTkButton(self.nav, text=f"{icon}  {txt}", fg_color="transparent", 
                         hover_color=COLORS["neon_hover"], anchor="w", height=42, 
                         command=lambda t=txt: self.nav_click(t),
                         text_color=COLORS["text"]).pack(fill="x", padx=8, pady=2)
        
        # Sağ içerik
        self.content = ctk.CTkFrame(self.main_container, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)
        
        # Sistem widget
        self.sys_widget()
        
        # Başlık
        self.header = ctk.CTkLabel(self.content, text="GlassesCat", font=ctk.CTkFont(size=20, weight="bold"), 
                                   text_color=COLORS["neon"])
        self.header.pack(anchor="w", padx=20, pady=(12, 8))
        
        # Chat
        self.chat = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        self.chat.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Input
        inp = ctk.CTkFrame(self.content, fg_color=COLORS["bg_medium"], height=55)
        inp.pack(fill="x", side="bottom", pady=0)
        inp.pack_propagate(False)
        
        self.entry = ctk.CTkEntry(inp, placeholder_text="/komut veya mesaj...", placeholder_text_color=COLORS["text_secondary"],
                                  fg_color=COLORS["bg_dark"], border_color=COLORS["neon"], text_color=COLORS["text"],
                                  font=ctk.CTkFont(size=13), height=38)
        self.entry.pack(side="left", fill="both", expand=True, padx=(12, 8), pady=8)
        self.entry.bind("<Return>", lambda e: self.send())
        
        ctk.CTkButton(inp, text="Gönder", width=75, height=38, fg_color=COLORS["neon"], 
                      hover_color=COLORS["neon_hover"], command=self.send, text_color=COLORS["bg_dark"]).pack(side="right", padx=(0, 12), pady=8)

    def sys_widget(self):
        """GPU/RAM widget"""
        w = ctk.CTkFrame(self.content, fg_color=COLORS["bg_light"], corner_radius=12)
        w.pack(fill="x", padx=18, pady=(8, 6))
        
        # GPU
        f = ctk.CTkFrame(w, fg_color="transparent")
        f.pack(fill="x", padx=12, pady=(10, 5))
        ctk.CTkLabel(f, text="🎮 GPU", text_color=COLORS["neon"], font=ctk.CTkFont(size=11)).pack(side="left")
        self.gpu_lbl = ctk.CTkLabel(f, text="--%", text_color=COLORS["text"], font=ctk.CTkFont(size=12, weight="bold"))
        self.gpu_lbl.pack(side="right")
        self.gpu_bar = ctk.CTkProgressBar(f, progress_color=COLORS["neon"], fg_color=COLORS["bg_medium"], height=7)
        self.gpu_bar.pack(fill="x", pady=(5, 8))
        self.gpu_bar.set(0)
        
        # RAM
        f2 = ctk.CTkFrame(w, fg_color="transparent")
        f2.pack(fill="x", padx=12, pady=(0, 10))
        ctk.CTkLabel(f2, text="💾 RAM", text_color=COLORS["neon"], font=ctk.CTkFont(size=11)).pack(side="left")
        self.ram_lbl = ctk.CTkLabel(f2, text="--%", text_color=COLORS["text"], font=ctk.CTkFont(size=12, weight="bold"))
        self.ram_lbl.pack(side="right")
        self.ram_bar = ctk.CTkProgressBar(f2, progress_color=COLORS["neon"], fg_color=COLORS["bg_medium"], height=7)
        self.ram_bar.pack(fill="x", pady=(5, 8))
        self.ram_bar.set(0)

    def start_monitoring(self):
        def mon():
            while self.monitoring:
                try:
                    r = psutil.virtual_memory()
                    self.after(0, lambda: self.ram_bar.set(r.percent/100))
                    self.after(0, lambda: self.ram_lbl.configure(text=f"{r.percent:.0f}%"))
                    
                    c = psutil.cpu_percent()
                    self.after(0, lambda: self.gpu_bar.set(c/100))
                    self.after(0, lambda: self.gpu_lbl.configure(text=f"{c:.0f}%"))
                except: pass
                time.sleep(2)
        threading.Thread(target=mon, daemon=True).start()

    def welcome(self):
        self.add("GlassesCat", "👋 GlassesCat AI'ya hoş geldin!\n\n📋 /komutlar:\n/youtube - YouTube\n/discord - Discord\n/snapchat - Snapchat\n/wsp - WhatsApp\n/ss - Screenshot\n/kilit - Kilitle\n/ses+ /ses- - Ses\n\n🔴 /root admin123")

    def nav_click(self, t):
        if t == "Ana Sayfa": self.header.configure(text="GlassesCat"); self.clear(); self.welcome()
        elif t == "Sohbet": self.header.configure(text="💬 Sohbet"); self.clear(); self.add("GlassesCat", "Sohbet başladı!")
        elif t == "Kontrol": self.header.configure(text="🖥️ Kontrol"); self.clear(); self.add("GlassesCat", "📋 /ss /kilit /uyku /ses+ /ses-")
        elif t == "Ayarlar": self.header.configure(text="⚙️ Ayarlar"); self.clear(); self.show_settings()

    def show_settings(self):
        ctk.CTkLabel(self.chat, text="Model:", text_color=COLORS["text"]).pack(anchor="w", pady=(10,3))
        self.model_combo = ctk.CTkComboBox(self.chat, values=self.models, button_color=COLORS["neon"])
        self.model_combo.set(self.model)
        self.model_combo.pack(fill="x", padx=10)

    def send(self):
        msg = self.entry.get()
        if not msg: return
        self.add("Sen", msg)
        self.entry.delete(0, "end")
        
        if msg.startswith("/"): self.run_cmd(msg)
        else: self.ai_resp(msg)

    def run_cmd(self, c):
        c = c.lower().strip()
        cmds = {
            "/youtube": ("web", "https://youtube.com"),
            "/discord": ("web", "https://discord.com"),
            "/snapchat": ("web", "https://snapchat.com"),
            "/wsp": ("web", "https://web.whatsapp.com"),
            "/whatsapp": ("web", "https://web.whatsapp.com"),
            "/twitter": ("web", "https://twitter.com"),
            "/instagram": ("web", "https://instagram.com"),
            "/tiktok": ("web", "https://tiktok.com"),
            "/telegram": ("web", "https://web.telegram.org"),
            "/spotify": ("web", "https://open.spotify.com"),
            "/netflix": ("web", "https://netflix.com"),
            "/steam": ("exe", "steam"),
            "/vscode": ("exe", "code"),
            "/notepad": ("exe", "notepad"),
            "/calc": ("exe", "calc"),
            "/ss": ("ctrl", "ss"), "/screenshot": ("ctrl", "ss"),
            "/kilit": ("ctrl", "lock"), "/lock": ("ctrl", "lock"),
            "/uyku": ("ctrl", "sleep"), "/sleep": ("ctrl", "sleep"),
            "/ses+": ("ctrl", "vup"), "/ses-": ("ctrl", "vdown"),
            "/root": ("sys", "root"), "/help": ("sys", "help"),
            "/clear": ("sys", "clear"),
            # Oyun oluşturma
            "/oyun": ("oyun", "menu"), "/game": ("oyun", "menu"),
        }
        
        if c in cmds:
            t, v = cmds[c]
            if t == "web": 
                webbrowser.open(v)
                self.add("GlassesCat", f"✅ {c} açılıyor")
            elif t == "exe":
                try: 
                    subprocess.Popen(v, shell=True)
                    self.add("GlassesCat", f"✅ {c}")
                except: 
                    self.add("GlassesCat", f"❌ Hata")
            elif t == "ctrl": 
                self.do_ctrl(v)
            elif t == "sys":
                if v == "root": self.add("GlassesCat", "🔴 /root admin123")
                elif v == "help": self.add("GlassesCat", "📋 /youtube /discord /snapchat /ss /kilit /ses+")
                elif v == "clear": self.clear()
        else: 
            self.add("GlassesCat", f"❌ Bilinmeyen: {c}\n/help yaz")

    def do_ctrl(self, a):
        try:
            if a == "ss":
                import datetime
                pyautogui.screenshot(f"ss_{datetime.now().strftime('%H%M%S')}.png")
                self.add("GlassesCat", "📸 Screenshot alındı")
            elif a == "lock": 
                subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
                self.add("GlassesCat", "🔒")
            elif a == "sleep": 
                subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
                self.add("GlassesCat", "💤")
            elif a == "vup": 
                [pyautogui.press("volumeup") for _ in range(5)]
                self.add("GlassesCat", "🔊")
            elif a == "vdown": 
                [pyautogui.press("volumedown") for _ in range(5)]
                self.add("GlassesCat", "🔉")
        except Exception as e: 
            self.add("GlassesCat", f"❌ {e}")

    def create_game(self, game_type, user_request=""):
        """Oyun oluşturma sistemi"""
        import os
        games_dir = os.path.join(os.path.dirname(__file__), "games")
        os.makedirs(games_dir, exist_ok=True)
        
        game_templates = {
            "minecraft": self.get_minecraft_code,
            "fps": self.get_fps_code,
            "pong": self.get_pong_code,
            "snake": self.get_snake_code,
            "platformer": self.get_platformer_code,
            "rpg": self.get_rpg_code,
        }
        
        # Oyun türünü algıla
        req = user_request.lower()
        if "minecraft" in req or "blok" in req or "kazı" in req:
            game_type = "minecraft"
        elif "fps" in req or "silah" in req or "cs" in req or "savaş" in req:
            game_type = "fps"
        elif "pong" in req or "top" in req:
            game_type = "pong"
        elif "yılan" in req or "snake" in req:
            game_type = "snake"
        elif "platform" in req or "zıpla" in req:
            game_type = "platformer"
        elif "rpg" in req or "macera" in req or "rol" in req:
            game_type = "rpg"
        
        # Kod üret
        if game_type in game_templates:
            code = game_templates[game_type]()
            filename = f"user_{game_type}_{int(time.time())}.py"
            filepath = os.path.join(games_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            
            self.add("GlassesCat", f"🎮 {game_type.upper()} oyunu oluşturuldu!\n📁 {filename}\n⏳ Başlatılıyor...")
            
            # Oyunu çalıştır
            try:
                subprocess.Popen(f'start cmd /k "cd {games_dir} && python {filename}"', shell=True)
            except Exception as e:
                self.add("GlassesCat", f"❌ Oyun başlatılamadı: {e}")
        else:
            # AI'ya kod üret
            self.ai_resp(f"Bir {game_type} oyunu için Python Tkinter kodu yazar mısın? Çalışır ve eğlenceli olsun.")

    def get_minecraft_code(self):
        return '''"""
GlassesCat - Minecraft Tarzı Blok Oyunu
"""
import tkinter as tk
import random

root = tk.Tk()
root.title("GlassesCat Minecraft")
root.geometry("800x600")

canvas = tk.Canvas(root, bg="#1a1a2e", width=800, height=600)
canvas.pack()

# Oyuncu
player = {"x": 400, "y": 300, "size": 20}
blocks = []

# Blok tipi seç
current_block = "toprak"

def draw_player():
    canvas.delete("player")
    canvas.create_rectangle(
        player["x"]-player["size"]//2, player["y"]-player["size"]//2,
        player["x"]+player["size"]//2, player["y"]+player["size"]//2,
        fill="#00FFAB", outline="", tags="player"
    )

def draw_blocks():
    canvas.delete("block")
    for b in blocks:
        color = {"toprak": "#8B4513", "taş": "#808080", "çim": "#228B22", "odun": "#A0522D"}.get(b["type"], "#FFF")
        canvas.create_rectangle(
            b["x"], b["y"], b["x"]+30, b["y"]+30,
            fill=color, outline="", tags="block"
        )

def on_key(event):
    if event.keysym == "w": player["y"] -= 10
    if event.keysym == "s": player["y"] += 10
    if event.keysym == "a": player["x"] -= 10
    if event.keysym == "d": player["x"] += 10
    if event.keysym == "space":
        blocks.append({"x": player["x"], "y": player["y"]-30, "type": current_block})
    draw_player()
    draw_blocks()

root.bind("<Key>", on_key)

# Başlangıç blokları
for _ in range(20):
    blocks.append({
        "x": random.randint(0, 750),
        "y": random.randint(350, 550),
        "type": random.choice(["toprak", "taş", "çim", "odun"])
    })

draw_player()
draw_blocks()
root.mainloop()
'''

    def get_fps_code(self):
        return '''"""
GlassesCat - FPS Savaş Oyunu
"""
import tkinter as tk
import random
import math

root = tk.Tk()
root.title("GlassesCat FPS")
root.geometry("800x600")

canvas = tk.Canvas(root, bg="#121212", width=800, height=600)
canvas.pack()

# Oyuncu
player = {"x": 400, "y": 500, "angle": 0}
bullets = []
enemies = []
score = 0

def draw():
    canvas.delete("all")
    # Yer
    canvas.create_rectangle(0, 550, 800, 600, fill="#2D2D2D")
    # Oyuncu
    canvas.create_oval(380, 480, 420, 520, fill="#00FFAB")
    # Silah
    mx, my = root.winfo_pointerx(), root.winfo_pointery()
    player["angle"] = math.atan2(my-500, mx-400)
    canvas.create_line(400, 500, 400+math.cos(player["angle"])*50, 500+math.sin(player["angle"])*50, fill="#FF4444", width=5)
    # Düşmanlar
    for e in enemies:
        canvas.create_oval(e["x"]-15, e["y"]-15, e["x"]+15, e["y"]+15, fill="#FF4444")
    # Mermiler
    for b in bullets:
        canvas.create_oval(b["x"]-3, b["y"]-3, b["x"]+3, b["y"]+3, fill="#FFFF00")
    # Skor
    canvas.create_text(50, 30, text=f"Skor: {score}", fill="#00FFAB", font=("Arial", 16))

def update():
    global score
    # Düşman hareketi
    for e in enemies:
        e["y"] += e["speed"]
        if e["y"] > 600:
            enemies.remove(e)
    # Mermi hareketi
    for b in bullets:
        b["x"] += b["vx"]
        b["y"] += b["vy"]
        # Çarpışma
        for e in enemies[:]:
            if abs(b["x"]-e["x"])<20 and abs(b["y"]-e["y"])<20:
                enemies.remove(e)
                bullets.remove(b)
                score += 10
                break
        if b["x"]<0 or b["x"]>800 or b["y"]<0 or b["y"]>600:
            if b in bullets: bullets.remove(b)
    # Yeni düşman
    if random.random() < 0.02:
        enemies.append({"x": random.randint(50, 750), "y": -20, "speed": random.randint(1, 3)})
    draw()
    root.after(30, update)

def shoot(event):
    mx, my = root.winfo_pointerx(), root.winfo_pointery()
    angle = math.atan2(my-500, mx-400)
    bullets.append({"x": 400, "y": 500, "vx": math.cos(angle)*10, "vy": math.sin(angle)*10})

root.bind("<Button-1>", shoot)
update()
root.mainloop()
'''

    def get_pong_code(self):
        return '''"""
GlassesCat - Pong Oyunu
"""
import tkinter as tk

root = tk.Tk()
root.title("GlassesCat Pong")
root.geometry("600x400")

canvas = tk.Canvas(root, bg="#121212", width=600, height=400)
canvas.pack()

ball = {"x": 300, "y": 200, "vx": 4, "vy": 4}
paddle1 = {"y": 150}
paddle2 = {"y": 150, "ai_y": 150}
score = {"p1": 0, "p2": 0}

def draw():
    canvas.delete("all")
    canvas.create_line(300, 0, 300, 400, fill="#00FFAB40", dash=(10,10))
    canvas.create_rectangle(10, paddle1["y"], 20, paddle1["y"]+100, fill="#00FFAB")
    canvas.create_rectangle(580, paddle2["y"], 590, paddle2["y"]+100, fill="#FF4444")
    canvas.create_oval(ball["x"]-10, ball["y"]-10, ball["x"]+10, ball["y"]+10, fill="#FFFFFF")
    canvas.create_text(150, 30, text=f"{score['p1']}", fill="#00FFAB", font=("Arial", 24))
    canvas.create_text(450, 30, text=f"{score['p2']}", fill="#FF4444", font=("Arial", 24))

def update():
    global ball, score
    ball["x"] += ball["vx"]
    ball["y"] += ball["vy"]
    
    if ball["y"] < 10 or ball["y"] > 390:
        ball["vy"] *= -1
    
    # Paddle 1
    if 10 <= ball["x"] <= 30 and paddle1["y"] <= ball["y"] <= paddle1["y"]+100:
        ball["vx"] *= -1.1
    
    # Paddle 2 (AI basit)
    if paddle2["ai_y"] + 50 > ball["y"]:
        paddle2["ai_y"] -= 3
    else:
        paddle2["ai_y"] += 3
    
    if 570 <= ball["x"] <= 590 and paddle2["y"] <= ball["y"] <= paddle2["y"]+100:
        ball["vx"] *= -1.1
    
    # Skor
    if ball["x"] < 0:
        score["p2"] += 1
        ball = {"x": 300, "y": 200, "vx": 4, "vy": 4}
    if ball["x"] > 600:
        score["p1"] += 1
        ball = {"x": 300, "y": 200, "vx": -4, "vy": 4}
    
    draw()
    root.after(20, update)

def on_key(event):
    if event.keysym == "w": paddle1["y"] = max(0, paddle1["y"]-20)
    if event.keysym == "s": paddle1["y"] = min(300, paddle1["y"]+20)

root.bind("<Key>", on_key)
update()
root.mainloop()
'''

    def get_snake_code(self):
        return '''"""
GlassesCat - Yılan Oyunu
"""
import tkinter as tk
import random

root = tk.Tk()
root.title("GlassesCat Snake")
root.geometry("400x420")

canvas = tk.Canvas(root, bg="#121212", width=400, height=400)
canvas.pack()

snake = [{"x": 200, "y": 200}]
food = {"x": 0, "y": 0}
direction = {"x": 10, "y": 0}
score = 0
game_over = False

def draw():
    canvas.delete("all")
    for s in snake:
        canvas.create_rectangle(s["x"], s["y"], s["x"]+10, s["y"]+10, fill="#00FFAB")
    canvas.create_oval(food["x"], food["y"], food["x"]+10, food["y"]+10, fill="#FF4444")
    canvas.create_text(200, 15, text=f"Skor: {score}", fill="#FFFFFF", font=("Arial", 12))
    if game_over:
        canvas.create_text(200, 200, text="OYUN BİTTİ!", fill="#FF4444", font=("Arial", 24))

def update():
    global snake, food, score, game_over
    if game_over: return
    
    # Hareket
    head = {"x": snake[0]["x"] + direction["x"], "y": snake[0]["y"] + direction["y"]}
    
    # Duvara çarpma
    if head["x"] < 0 or head["x"] > 390 or head["y"] < 0 or head["y"] > 390:
        game_over = True
        draw()
        return
    
    # Kendine çarpma
    for s in snake:
        if head["x"] == s["x"] and head["y"] == s["y"]:
            game_over = True
            draw()
            return
    
    snake.insert(0, head)
    
    # Yemek
    if head["x"] == food["x"] and head["y"] == food["y"]:
        score += 1
        food = {"x": random.randint(0, 39)*10, "y": random.randint(0, 39)*10}
    else:
        snake.pop()
    
    draw()
    root.after(100, update)

def on_key(event):
    global direction
    if event.keysym == "Up" and direction["y"] == 0: direction = {"x": 0, "y": -10}
    if event.keysym == "Down" and direction["y"] == 0: direction = {"x": 0, "y": 10}
    if event.keysym == "Left" and direction["x"] == 0: direction = {"x": -10, "y": 0}
    if event.keysym == "Right" and direction["x"] == 0: direction = {"x": 10, "y": 0}

root.bind("<Key>", on_key)
update()
root.mainloop()
'''

    def get_platformer_code(self):
        return '''"""
GlassesCat - Platformer Oyunu
"""
import tkinter as tk

root = tk.Tk()
root.title("GlassesCat Platformer")
root.geometry("600x400")

canvas = tk.Canvas(root, bg="#1a1a2e", width=600, height=400)
canvas.pack()

player = {"x": 50, "y": 300, "vx": 0, "vy": 0, "on_ground": False}
platforms = [
    {"x": 0, "y": 380, "w": 600},
    {"x": 100, "y": 300, "w": 100},
    {"x": 250, "y": 250, "w": 100},
    {"x": 400, "y": 200, "w": 100},
    {"x": 150, "y": 150, "w": 80},
]
coins = [{"x": 140, "y": 270}, {"x": 290, "y": 220}, {"x": 440, "y": 170}]
score = 0

def draw():
    canvas.delete("all")
    for p in platforms:
        canvas.create_rectangle(p["x"], p["y"], p["x"]+p["w"], p["y"]+20, fill="#00FFAB")
    for c in coins:
        canvas.create_oval(c["x"], c["y"], c["x"]+15, c["y"]+15, fill="#FFFF00")
    canvas.create_rectangle(player["x"], player["y"], player["x"]+30, player["y"]+30, fill="#FF4444")
    canvas.create_text(30, 20, text=f"Skor: {score}", fill="#FFFFFF")

def update():
    global player, score
    player["vy"] += 0.5
    player["y"] += player["vy"]
    player["x"] += player["vx"]
    
    # Platform çarpışma
    player["on_ground"] = False
    for p in platforms:
        if p["x"] <= player["x"]+30 <= p["x"]+p["w"] and p["y"] <= player["y"]+30 <= p["y"]+20:
            player["y"] = p["y"]-30
            player["vy"] = 0
            player["on_ground"] = True
    
    # Yemek toplama
    for c in coins[:]:
        if abs(player["x"]+15-c["x"])<20 and abs(player["y"]+15-c["y"])<20:
            coins.remove(c)
            score += 10
    
    # Sınırlar
    if player["x"] < 0: player["x"] = 0
    if player["x"] > 570: player["x"] = 570
    if player["y"] > 400: player["y"] = 300; player["vy"] = 0
    
    draw()
    root.after(20, update)

def on_key(event):
    global player
    if event.keysym == "a": player["vx"] = -5
    if event.keysym == "d": player["vx"] = 5
    if event.keysym == "space" and player["on_ground"]: player["vy"] = -12
    if event.keysym in ["a","d"] and event.type == "2": player["vx"] = 0

root.bind("<Key>", on_key)
update()
root.mainloop()
'''

    def get_rpg_code(self):
        return '''"""
GlassesCat - RPG Macera Oyunu
"""
import tkinter as tk
import random

root = tk.Tk()
root.title("GlassesCat RPG")
root.geometry("600x500")

canvas = tk.Canvas(root, bg="#0a0a0f", width=600, height=500)
canvas.pack()

# Karakter
player = {"x": 300, "y": 400, "hp": 100, "level": 1, "xp": 0, "gold": 0}
enemies = []
inventory = []

def draw():
    canvas.delete("all")
    # Harita
    for x in range(0, 600, 50):
        for y in range(0, 400, 50):
            canvas.create_rectangle(x, y, x+50, y+50, outline="#1a1a2e")
    # Düşmanlar
    for e in enemies:
        canvas.create_oval(e["x"]-15, e["y"]-15, e["x"]+15, e["y"]+15, fill="#FF4444")
        canvas.create_text(e["x"], e["y"]-20, text=f"{e['hp']}HP", fill="#FFF", font=("Arial", 8))
    # Oyuncu
    canvas.create_oval(player["x"]-20, player["y"]-20, player["x"]+20, player["y"]+20, fill="#00FFAB")
    # UI
    canvas.create_rectangle(0, 400, 600, 500, fill="#1E1E1E")
    canvas.create_text(50, 420, text=f"Can: {player['hp']}", fill="#FF4444")
    canvas.create_text(50, 450, text=f"Seviye: {player['level']}", fill="#00FFAB")
    canvas.create_text(150, 420, text=f"XP: {player['xp']}", fill="#FFFF00")
    canvas.create_text(150, 450, text=f"Altın: {player['gold']}", fill="#FFD700")
    canvas.create_text(500, 420, text=f"Envanter: {len(inventory)}", fill="#888")
    canvas.create_text(500, 450, text="WASD-Hareket, T-Saldır", fill="#666")

def update():
    global enemies, player
    # Düşman üret
    if len(enemies) < 3 and random.random() < 0.02:
        enemies.append({"x": random.randint(50, 550), "y": random.randint(50, 350), "hp": 30})
    # Düşman hareket
    for e in enemies:
        if abs(e["x"]-player["x"]) > 30 or abs(e["y"]-player["y"]) > 30:
            e["x"] += random.choice([-1, 1])
            e["y"] += random.choice([-1, 1])
        else:
            player["hp"] -= 1
    
    if player["hp"] <= 0:
        canvas.create_text(300, 250, text="ÖLDÜN!", fill="#FF4444", font=("Arial", 40))
        return
    
    draw()
    root.after(100, update)

def on_key(event):
    global player
    if event.keysym == "w": player["y"] = max(30, player["y"]-20)
    if event.keysym == "s": player["y"] = min(370, player["y"]+20)
    if event.keysym == "a": player["x"] = max(30, player["x"]-20)
    if event.keysym == "d": player["x"] = min(570, player["x"]+20)
    if event.keysym == "t":
        for e in enemies[:]:
            if abs(e["x"]-player["x"])<50 and abs(e["y"]-player["y"])<50:
                e["hp"] -= 20
                if e["hp"] <= 0:
                    enemies.remove(e)
                    player["xp"] += 10
                    player["gold"] += random.randint(5, 15)
                    if player["xp"] >= player["level"]*50:
                        player["level"] += 1
                        player["hp"] = 100

root.bind("<Key>", on_key)
update()
root.mainloop()
'''

    def ai_resp(self, msg):
        # Kodlama isteklerinde deepseek kullan
        msg_lower = msg.lower()
        kod_anahtarlari = ['kod', 'code', 'python', 'oyun', 'game', '3d', 'fps', 'cs2', 'script', 'yaz', 'program']
        secilen_model = self.code_model if any(k in msg_lower for k in kod_anahtarlari) else self.model
        
        self.thinking = ctk.CTkLabel(self.chat, text="🤔 Düşünüyorum...", text_color=COLORS["warning"], font=ctk.CTkFont(size=12, slant="italic"))
        self.thinking.pack(anchor="w", pady=3)
        
        def fetch():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                async def call():
                    async with httpx.AsyncClient(timeout=90.0) as cl:
                        # System prompt - kodlama için farklı
                        if secilen_model == self.code_model:
                            system = "Sen GlassesCat'sın. 3D oyun geliştirme uzmanısın. CS2 tarzı FPS oyun kodları yazarsın. Temiz, çalışır kod verirsin. Türkçe açıkla."
                        else:
                            system = "Sen GlassesCat'sın. Yardımcı ve nazik bir Türkçe yapay zeka asistanısın. Kısa ve faydalı yanıtlar verirsin."
                        
                        p = {
                            "model": secilen_model,
                            "messages": [
                                {"role": "system", "content": system},
                                {"role": "user", "content": msg}
                            ],
                            "stream": False,
                            "options": {"temperature": 0.5, "num_predict": 1000}
                        }
                        r = await cl.post(f"{self.ollama_url}/v1/chat/completions", json=p)
                        return r.json().get("choices", [{}])[0].get("message", {}).get("content", "Yanıt yok") if r.status_code == 200 else f"Hata: {r.status_code}"
                resp = loop.run_until_complete(call())
                loop.close()
                self.after(0, lambda: self.got_ai(resp, msg))
            except Exception as e: 
                self.after(0, lambda: self.add("GlassesCat", f"❌ {e}"))
        threading.Thread(target=fetch, daemon=True).start()

    def got_ai(self, resp, orig):
        if hasattr(self, 'thinking'): 
            self.thinking.destroy()
        if "/root admin123" in orig.lower(): 
            self.root_mode = True
            self.add("GlassesCat", "🔴 ROOT!")
        elif self.root_mode and "root off" in resp.lower(): 
            self.root_mode = False
            self.add("GlassesCat", "🟢 Normal")
        else: 
            self.add("GlassesCat", resp)

    def add(self, sender, txt):
        f = ctk.CTkFrame(self.chat, fg_color=COLORS["bg_light"] if sender == "Sen" else COLORS["bg_medium"], corner_radius=12)
        f.pack(anchor="e" if sender == "Sen" else "w", pady=4, padx=25, fill="x")
        ctk.CTkLabel(f, text=f"{'👤' if sender == 'Sen' else '🤖'} {txt}", text_color=COLORS["neon"] if sender == "Sen" else COLORS["text"],
                    font=ctk.CTkFont(size=13), wraplength=550, justify="left" if sender != "Sen" else "right").pack(padx=14, pady=10)
        self.chat._parent_canvas.yview_moveto(1)

    def clear(self):
        for w in self.chat.winfo_children(): 
            w.destroy()

    def animate_orb(self):
        self.orb_scale += 0.008 * self.orb_dir
        if self.orb_scale >= 1.1: 
            self.orb_dir = -1
        elif self.orb_scale <= 1.0: 
            self.orb_dir = 1
        self.after(50, self.animate_orb)

    def toggle_maximize(self):
        if not self.is_max:
            self.attributes('-zoomed', True)
            self.is_max = True
        else:
            self.attributes('-zoomed', False)
            self.is_max = False


if __name__ == "__main__":
    app = GlassesCatApp()
    app.mainloop()