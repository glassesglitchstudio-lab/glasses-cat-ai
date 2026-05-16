"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║      ██████╗  █████╗  ██████╗  █████╗ ██╗     ██╗     ███████╗██╗          ║
║      ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██║     ██║     ██╔════╝██║          ║
║      ██████╔╝███████║██║   ██║███████║██║     ██║     █████╗  ██║          ║
║      ██╔═══╝ ██╔══██║██║   ██║██╔══██║██║     ██║     ██╔══╝  ██║          ║
║      ██║     ██║  ██║╚██████╔╝██║  ██║███████╗███████╗███████╗███████╗     ║
║      ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝     ║
║                         ██████╗ ███████╗                                        ║
║                         ██╔══██╗██╔════╝                                        ║
║                         ██████╔╝█████╗                                          ║
║                         ██╔══██╗██╔══╝                                          ║
║                         ██║  ██║███████╗                                        ║
║                         ╚═╝  ╚═╝╚══════╝                                        ║
║                      GLASSESCAT AUTONOMOUS ENGINE                              ║
║                    Erkay Software - Lead Engineer AI                          ║
║                         Version 2.0 - SWA 1.6                                  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

User Intent System - Command Parser
Kullanıcı Niyeti Algilama ve Komut Ayristirma
Erkay Software - Lead Engineer AI

Modlar:
- [G] Game Mod: Oyun gelistirme ve oyunla ilgili islemler
- [A] Agent Mod: Ajans ve otomasyon islemleri
- [S] System Mod: Sistem durdurma, ajanlari dondurma ve model gecisi
- [<] Back/Resume: Sistem modundan geri donus
"""

import re
import os
import time
import logging
from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum

# GlassesCat Log Sistemi - Havalı gosterim
class GlassesCatLogger:
    """GlassesCat markali logger"""
    
    COLORS = {
        'RESET': '\033[0m',
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'MAGENTA': '\033[95m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
        'GAME': '\033[92m',
        'AGENT': '\033[96m',
        'SYSTEM': '\033[91m'
    }
    
    @staticmethod
    def log(mode: str, message: str, level: str = "INFO"):
        """GlassesCat log mesaji"""
        color = GlassesCatLogger.COLORS.get(mode.upper(), GlassesCatLogger.COLORS['WHITE'])
        timestamp = time.strftime("%H:%M:%S")
        
        logo = f"""
==================================================
  >> GLASSESCAT [{mode}] {timestamp}
==================================================
{message}
"""
        print(logo)
    
    @staticmethod
    def game(message: str):
        GlassesCatLogger.log("[G]", message, "GAME")
    
    @staticmethod
    def agent(message: str):
        GlassesCatLogger.log("[A]", message, "AGENT")
    
    @staticmethod
    def system(message: str):
        GlassesCatLogger.log("[S]", message, "SYSTEM")
    
    @staticmethod
    def info(message: str):
        print(f"{GlassesCatLogger.COLORS['CYAN']}[INFO]{GlassesCatLogger.COLORS['RESET']} {message}")
    
    @staticmethod
    def error(message: str):
        print(f"{GlassesCatLogger.COLORS['RED']}[ERROR]{GlassesCatLogger.COLORS['RESET']} {message}")

logger = GlassesCatLogger

class IntentMode(Enum):
    GAME = "[G]"
    AGENT = "[A]"
    SYSTEM = "[S]"
    BACK = "[<]"
    UNKNOWN = "?"

class CommandParser:
    def __init__(self):
        self.current_mode = IntentMode.UNKNOWN
        self.conversation_history = []
        
        self.game_keywords = [
            "oyun", "game", "play", "minecraft", "valorant", "cs2", "fortnite",
            "league", "lol", "gta", "pubg", "fifa", "call of duty", "cod",
            "oyna", "harita", "level", "skor", "karakter", "sprite", "collision",
            "fizik", "fps", "rpg", "platformer", "puzzle", "arcade",
            "2d", "3d", "grafik", "render", "sound", "muzik", "efekt",
            "oyun yap", "oyun olustur", "game create", "new game"
        ]
        
        self.agent_keywords = [
            "ajan", "agent", "bot", "otomatik", "automation", "task",
            "gorev", "islem", "process", "schedule", "zamanla", "cron",
            "web scraping", "veri", "data", "cek", "fetch", "api",
            "scraper", "bot yaz", "selenium", "playwright",
            "tweet", "discord", "telegram", "whatsapp", "mesaj gonder",
            "mail", "eposta", "bildirim", "notification", "webhook"
        ]
        
        self.system_keywords = [
            # Genel sistem kontrolü
            "dur", "stop", "exit", "quit", "kapat", "close", "freeze",
            "don", "bekle", "wait", "bekleme", "pause", "model degistir",
            "change model", "switch model", "gecis", "shutdown", "sistem",
            "system", "reset", "sifirla", "bellek temizle", "clear memory",
            "reload", "yeniden baslat",
            # AJANLARI DONDUR - YENİ
            "ajanlari dondur", "ajanları dondur", "ajan dondur", "agent freeze",
            "botlari dondur", "botları dondur", "bot dondur", "bots freeze",
            "tüm ajanlari dondur", "tüm ajanları dondur", "hepsini dondur",
            "otomasyonu durdur", "automation stop", "tasks dur", "gorevleri durdur",
            "scheduler dur", "zamanlayiciyi durdur", "cron dur"
        ]
        
        # Geri dönüş keywords - [S] modundan çıkış
        self.back_keywords = [
            "geri don", "geri dön", "devam et", "devamet", "resume",
            "restart", "yeniden basla", "baslat", "start", "calistir",
            "uyan", "wake up", "activate", "aktive et", "enable",
            "oyuna don", "oyuna dön", "ajanlara don", "ajanlara dön",
            "mod degistir", "mod değiştir", "mode switch", "gecis yap"
        ]
        
        # Önceki mod saklama (geri dönüş için)
        self.previous_mode = IntentMode.UNKNOWN
        self.system_frozen = False  # Sistem donmuş mu?
    
    def analyze_intent(self, user_input: str) -> Tuple[IntentMode, float, Dict]:
        text = user_input.lower().strip()
        
        # ÖNCE: Geri dönüş kontrolü (sistem donmuşsa ve back kelime varsa)
        if self.system_frozen:
            for keyword in self.back_keywords:
                if keyword in text:
                    logger.system(f"Geri donus algilandi: {keyword}")
                    return (IntentMode.BACK, 1.0, {"back": True, "resume": True})
        
        game_score = 0
        agent_score = 0
        system_score = 0
        
        # Back keyword kontrolü (her zaman öncelikli)
        back_score = 0
        for keyword in self.back_keywords:
            if keyword in text:
                back_score += 2  # Double weight
        
        for keyword in self.game_keywords:
            if keyword in text:
                game_score += 1
        
        for keyword in self.agent_keywords:
            if keyword in text:
                agent_score += 1
        
        for keyword in self.system_keywords:
            if keyword in text:
                system_score += 2  # Sistem kelimeleri daha güçlü
        
        intent_patterns = [
            r"sunu\s+yapmak\s+istiyorum",
            r"bunu\s+yapmak\s+istiyorum",
            r"su\s+seyi\s+yap",
            r"bunu\s+yap",
            r"bir\s+oyun\s+yap",
            r"bir\s+bot\s+yap",
            r"bir\s+ajan\s+yap",
            r"otomatik\s+yap",
            r"istiyorum",
            r"yap\s+lsin",
            r"olsa"
        ]
        
        has_intent_pattern = any(re.search(p, text) for p in intent_patterns)
        
        if has_intent_pattern:
            game_score *= 1.2
            agent_score *= 1.2
        
        scores = {
            IntentMode.GAME: game_score,
            IntentMode.AGENT: agent_score,
            IntentMode.SYSTEM: system_score,
            IntentMode.BACK: back_score
        }
        
        max_score = max(scores.values())
        
        if max_score == 0:
            return (IntentMode.UNKNOWN, 0.0, scores)
        
        total = sum(scores.values())
        confidence = max_score / total if total > 0 else 0
        
        detected_mode = max(scores, key=scores.get)
        
        return (detected_mode, confidence, scores)
    
    def correct_mistake(self, user_input: str) -> Optional[str]:
        text = user_input.lower().strip()
        
        typo_fixes = {
            "oyun yapmak istiyorum": "oyun gelistirme moduna geciyorum",
            "oyn yapmak istiyorum": "oyun gelistirme moduna geciyorum",
            "oyun yapmakisyorum": "oyun gelistirme moduna geciyorum",
            "bot yapmak istiyorum": "ajan moduna geciyorum",
            "otomasyon yapmak istiyorum": "ajan moduna geciyorum",
            "sistemi durdur": "sistem modu aktif",
            "her seyi dondur": "sistem modu aktif",
            "modele gec": "sistem modu aktif",
            "menu renklerini mavi yap": "UI konfigurasyonu guncelleniyor",
            "menu rengini degistir": "UI konfigurasyonu guncelleniyor",
            "arkaplan degistir": "UI konfigurasyonu guncelleniyor",
            "sesi kapat": "ses ayarlari guncelleniyor",
            "oyunu baslat": "oyun calistiriliyor",
            "oyunu durdur": "oyun durduruluyor"
        }
        
        for typo, correction in typo_fixes.items():
            if typo in text:
                return correction
        
        return None
    
    def transform_to_code(self, user_input: str, mode: IntentMode) -> str:
        text = user_input.lower().strip()
        
        code_templates = {
            IntentMode.GAME: self._game_code_template,
            IntentMode.AGENT: self._agent_code_template,
            IntentMode.SYSTEM: self._system_code_template
        }
        
        template = code_templates.get(mode, self._default_code_template)
        return template(user_input)
    
    def _game_code_template(self, user_input: str) -> str:
        text = user_input.lower()
        
        # === STRIDE 3D KOD ÜRETIMI (C# / .NET 8.0) ===
        if "stride" in text or "3d" in text or "cs2" in text or "fps" in text:
            return self._generate_stride_3d_cs2(text)
        
        if "platformer" in text or "ziplama" in text:
            return """
# GlassesCat Oyun - Platformer Template
import pygame
import sys

class PlatformerGame:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("GlassesCat Platformer")
        self.clock = pygame.time.Clock()
        self.player_pos = [100, 400]
        self.player_vel = 0
        self.gravity = 0.5
        self.jump_power = -12
        self.platforms = [(0, 550, 800, 50), (200, 400, 200, 20), (500, 300, 200, 20)]
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.player_pos[0] -= 5
        if keys[pygame.K_RIGHT]: self.player_pos[0] += 5
        
        self.player_vel += self.gravity
        self.player_pos[1] += self.player_vel
        
        for plat in self.platforms:
            if self.player_pos[1] + 20 >= plat[1] and self.player_pos[1] < plat[1] + 10:
                if plat[0] <= self.player_pos[0] <= plat[0] + plat[2]:
                    self.player_pos[1] = plat[1] - 20
                    self.player_vel = 0
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.player_vel = self.jump_power
            
            self.update()
            self.screen.fill((50, 50, 150))
            pygame.draw.rect(self.screen, (255, 255, 0), (*self.player_pos, 30, 30))
            for p in self.platforms: pygame.draw.rect(self.screen, (100, 200, 100), p)
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__": PlatformerGame().run()
"""
        
        elif "pong" in text or "top" in text:
            return """
# GlassesCat Oyun - Pong Template
import pygame
import sys

class PongGame:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("GlassesCat Pong")
        self.clock = pygame.time.Clock()
        self.paddle1_y = self.paddle2_y = 250
        self.ball_x, self.ball_y = 400, 300
        self.ball_dx, self.ball_dy = 5, 5
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.paddle1_y > 0: self.paddle1_y -= 8
        if keys[pygame.K_s] and self.paddle1_y < 500: self.paddle1_y += 8
        if keys[pygame.K_UP] and self.paddle2_y > 0: self.paddle2_y -= 8
        if keys[pygame.K_DOWN] and self.paddle2_y < 500: self.paddle2_y += 8
        
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        if self.ball_y <= 0 or self.ball_y >= 580: self.ball_dy *= -1
        if self.ball_x <= 30 and self.paddle1_y <= self.ball_y <= self.paddle1_y + 100: self.ball_dx *= -1
        if self.ball_x >= 770 and self.paddle2_y <= self.ball_y <= self.paddle2_y + 100: self.ball_dx *= -1
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
            self.update()
            self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.screen, (255, 255, 255), (10, self.paddle1_y, 20, 100))
            pygame.draw.rect(self.screen, (255, 255, 255), (770, self.paddle2_y, 20, 100))
            pygame.draw.circle(self.screen, (255, 255, 255), (int(self.ball_x), int(self.ball_y)), 10)
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__": PongGame().run()
"""
        
        elif "yilan" in text or "snake" in text:
            return """
# GlassesCat Oyun - Snake Template
import pygame
import sys
import random

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 600, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("GlassesCat Snake")
        self.clock = pygame.time.Clock()
        self.snake = [(300, 300), (290, 300), (280, 300)]
        self.direction = (10, 0)
        self.food = (random.randint(0, 58) * 10, random.randint(0, 58) * 10)
        self.score = 0
    
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != (0, 10): self.direction = (0, -10)
                if event.key == pygame.K_DOWN and self.direction != (0, -10): self.direction = (0, 10)
                if event.key == pygame.K_LEFT and self.direction != (10, 0): self.direction = (-10, 0)
                if event.key == pygame.K_RIGHT and self.direction != (-10, 0): self.direction = (10, 0)
        
        head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])
        
        if head in self.snake or head[0] < 0 or head[0] >= 600 or head[1] < 0 or head[1] >= 600:
            return False
        
        self.snake.insert(0, head)
        
        if head == self.food:
            self.score += 1
            self.food = (random.randint(0, 58) * 10, random.randint(0, 58) * 10)
        else:
            self.snake.pop()
        
        return True
    
    def run(self):
        while self.update():
            self.screen.fill((0, 0, 0))
            for s in self.snake: pygame.draw.rect(self.screen, (0, 255, 0), (*s, 10, 10))
            pygame.draw.rect(self.screen, (255, 0, 0), (*self.food, 10, 10))
            pygame.display.flip()
            self.clock.tick(15)
        print(f"Oyun Bitti! Skor: {self.score}")

if __name__ == "__main__": SnakeGame().run()
"""
        
        return """
# GlassesCat Oyun Gelistirme
import pygame
import sys

class GlassesCatGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("GlassesCat Game")
        self.running = True
        self.player = pygame.Rect(400, 300, 40, 40)
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.player.x -= 5
        if keys[pygame.K_RIGHT]: self.player.x += 5
        if keys[pygame.K_UP]: self.player.y -= 5
        if keys[pygame.K_DOWN]: self.player.y += 5
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
            
            self.update()
            self.screen.fill((30, 30, 50))
            pygame.draw.rect(self.screen, (100, 200, 255), self.player)
            pygame.display.flip()
            pygame.time.Clock().tick(60)

if __name__ == "__main__": GlassesCatGame().run()
"""
    
    def _agent_code_template(self, user_input: str) -> str:
        text = user_input.lower()
        
        if "scrap" in text or "veri cek" in text:
            return """
# GlassesCat Agent - Web Scraper
import requests
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    def scrape(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            return {"status": "success", "data": soup.title.string}
        except Exception as e:
            return {"status": "error", "message": str(e)}

scraper = WebScraper()
result = scraper.scrape("https://example.com")
print(result)
"""
        
        elif "discord" in text or "telegram" in text or "mesaj" in text:
            return """
# GlassesCat Agent - Mesaj Botu
import asyncio

class MessageBot:
    def __init__(self, platform="discord"):
        self.platform = platform
    
    async def send_message(self, target, message):
        print(f"[{self.platform.upper()}] Gonderiliyor: {message} -> {target}")
        return {"status": "sent", "platform": self.platform}

bot = MessageBot("discord")
asyncio.run(bot.send_message("channel_id", "GlassesCat'ten selamlar!"))
"""
        
        elif "schedule" in text or "zamanla" in text:
            return """
# GlassesCat Agent - Scheduler
import schedule
import time

class TaskScheduler:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, interval, func):
        schedule.every(interval).seconds.do(func)
        self.tasks.append(func)
    
    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

scheduler = TaskScheduler()
scheduler.add_task(60, lambda: print("GlassesCat: Gorev calisti!"))
scheduler.run()
"""
        
        return """
# GlassesCat Agent Sistemi

class GlassesCatAgent:
    def __init__(self):
        self.name = "GlassesCat Agent"
        self.tasks = []
    
    def execute_task(self, task):
        print(f"Gorev isleniyor: {task}")
        return {"status": "completed", "task": task}
    
    def add_task(self, task):
        self.tasks.append(task)

agent = GlassesCatAgent()
result = agent.execute_task("Kullanici talebi")
print(result)
"""
    
    def _system_code_template(self, user_input: str) -> str:
        return """
# GlassesCat System - Sistem Kontrol

import sys
import os

class GlassesCatSystem:
    def __init__(self):
        self.frozen = False
        self.current_model = "turkcell-llm-7b-v1"
    
    def freeze_system(self):
        self.frozen = True
        print("[SYSTEM] Sistem donduruldu - Model degisimi bekleniyor")
        return {"status": "frozen", "action": "model_switch_pending"}
    
    def switch_model(self, new_model):
        old_model = self.current_model
        self.current_model = new_model
        self.frozen = False
        print(f"[SYSTEM] Model degistirildi: {old_model} -> {new_model}")
        return {"old_model": old_model, "new_model": new_model}
    
    def get_status(self):
        return {
            "frozen": self.frozen,
            "model": self.current_model,
            "memory_usage": "N/A"
        }

system = GlassesCatSystem()
system.freeze_system()
"""
    
    def _generate_stride_3d_cs2(self, text: str) -> str:
        """GlassesCat -> Stride 3D CS2 Otomatik C# Kod Üretimi"""
        
        logger.game("Stride 3D CS2 C# kodu uretiliyor...")
        
        # CS2 özellikleri
        is_cs2 = "cs2" in text or "fps" in text
        is_3d = "3d" in text or "stride" in text
        
        if is_cs2 and is_3d:
            return """
// ============================================================
// GLASSESCAT CS2 3D - STRIDE ENGINE C#
// ============================================================
// [MOTTO]: PERFEKT
// [OWNER]: BERKAY  
// [ENGINE]: STRIDE - STATUS: PERFEKT
// ============================================================

using Stride.Core;
using Stride.Core.Mathematics;
using Stride.Engine;
using Stride.Input;
using Stride.Physics;

public class PlayerController : EntityComponent
{
    // ==================== KONFIGURASYON ====================
    public float MouseSensitivity { get; set; } = 0.002f;
    public float MoveSpeed { get; set; } = 8.0f;
    public float JumpVelocity { get; set; } = 5.0f;
    public float Gravity { get; set; } = 15.0f;
    public float Health { get; set; } = 100.0f;
    public float MaxHealth { get; set; } = 100.0f;

    // ==================== SILAHLAR ====================
    private Dictionary<string, Weapon> weapons = new Dictionary<string, Weapon>
    {
        ["Pistol"] = new Weapon { Damage = 20, FireRate = 0.3f, Ammo = 12 },
        ["Rifle"] = new Weapon { Damage = 35, FireRate = 0.1f, Ammo = 30 },
        ["Sniper"] = new Weapon { Damage = 100, FireRate = 1.5f, Ammo = 5 },
        ["Shotgun"] = new Weapon { Damage = 50, FireRate = 0.8f, Ammo = 8 }
    };

    private string currentWeapon = "Pistol";
    private double lastShotTime = 0;

    // ==================== KILLCARD VERILERI ====================
    public int KillStreak { get; private set; }
    public int TotalKills { get; private set; }

    // ==================== RECOIL SISTEMI ====================
    private Vector3 recoilOffset;
    private float recoilRecovery = 5.0f;

    // ==================== COMPONENT REFERENCES ====================
    private CameraComponent camera;
    private CharacterComponent character;

    public override void Start()
    {
        camera = Entity.Get<CameraComponent>();
        character = Entity.Get<CharacterComponent>();
        Input.mouseMode = MouseMode.Captured;
        logger.game("CS2 oyuncu hazir - STRIDE ENGINE");
    }

    public override void Update(double delta)
    {
        HandleMouseLook();
        HandleMovement((float)delta);
        HandleShooting();
        UpdateRecoil((float)delta);
    }

    private void HandleMouseLook()
    {
        var motion = Input.MousePosition;
        Entity.Transform.Rotation *= Quaternion.RotationY(-motion.X * MouseSensitivity);
        camera.Transform.Rotation *= Quaternion.RotationX(-motion.Y * MouseSensitivity);
    }

    private void HandleMovement(float delta)
    {
        var velocity = character.Velocity;
        
        if (!character.IsOnGround())
            velocity.Y -= Gravity * delta;
        else
            velocity.Y = 0;

        var input = Input.GetMotion();
        velocity.X = input.X * MoveSpeed;
        velocity.Z = input.Y * MoveSpeed;

        if (Input.IsKeyPressed(Keys.Space) && character.IsOnGround())
            velocity.Y = JumpVelocity;

        character.Velocity = velocity;
    }

    private void HandleShooting()
    {
        if (!Input.IsMouseButtonPressed(MouseButton.Left)) return;

        var weapon = weapons[currentWeapon];
        var now = (double)Game.TotalTime;

        if (now - lastShotTime < weapon.FireRate) return;
        lastShotTime = now;

        ApplyRecoil();
        PerformRaycast();
    }

    private void PerformRaycast()
    {
        var rayStart = camera.Entity.Transform.WorldPosition();
        var rayEnd = rayStart + camera.Entity.Transform.Forward * 100f;
        
        var result = PhysicsSimulation.Raycast(rayStart, rayEnd);
        
        if (result.Succeeded && result.Body.Entity != null)
        {
            var target = result.Body.Entity.GetComponent<HealthComponent>();
            if (target != null)
            {
                var weapon = weapons[currentWeapon];
                target.Health -= weapon.Damage;
                KillStreak++;
                TotalKills++;
                ShowKillCard(weapon.Damage);
            }
        }
    }

    private void ApplyRecoil()
    {
        var weapon = weapons[currentWeapon];
        recoilOffset = camera.Entity.Transform.Forward * weapon.Damage * 0.01f;
    }

    private void UpdateRecoil(float delta)
    {
        recoilOffset = Vector3.Lerp(recoilOffset, Vector3.Zero, recoilRecovery * delta);
    }

    private void ShowKillCard(int damage)
    {
        logger.game($"Killcard: {damage} damage - STRIDE ENGINE");
    }
}

// ==================== WEAPON CLASS ====================
public class Weapon
{
    public int Damage { get; set; }
    public float FireRate { get; set; }
    public int Ammo { get; set; }
}

// ==================== HEALTH COMPONENT ====================
public class HealthComponent : EntityComponent
{
    public float Health { get; set; } = 100.0f;
    public float MaxHealth { get; set; } = 100.0f;
}

// ============================================================
// GLASSESCAT CS2 3D - STRIDE ENGINE TAMAMLANDI
// ENGINE: STRIDE - STATUS: PERFEKT
// ============================================================
"""
        
        return """
// ============================================================
// GLASSESCAT STRIDE 3D OYUN - OTOMATIK C# URETIM
// ============================================================
// [MOTTO]: PERFEKT
// ENGINE: STRIDE - STATUS: PERFEKT
// ============================================================

using Stride.Core;
using Stride.Core.Mathematics;
using Stride.Engine;
using Stride.Input;
using Stride.Physics;

public class BasicPlayerController : EntityComponent
{
    public float Speed { get; set; } = 8.0f;
    public float JumpForce { get; set; } = 5.0f;
    public float Gravity { get; set; } = 15.0f;

    private CameraComponent camera;
    private CharacterComponent character;

    public override void Start()
    {
        camera = Entity.Get<CameraComponent>();
        character = Entity.Get<CharacterComponent>();
        Input.mouseMode = MouseMode.Captured;
    }

    public override void Update(double delta)
    {
        var velocity = character.Velocity;
        
        if (!character.IsOnGround())
            velocity.Y -= Gravity * (float)delta;
        
        var input = Input.GetMotion();
        velocity.X = input.X * Speed;
        velocity.Z = input.Y * Speed;

        if (Input.IsKeyPressed(Keys.Space) && character.IsOnGround())
            velocity.Y = JumpForce;

        character.Velocity = velocity;
    }
}

// ============================================================
// GLASSESCAT STRIDE OTOMATIK URETIM TAMAMLANDI
// ENGINE: STRIDE - STATUS: PERFEKT
// ============================================================
"""

    def _default_code_template(self, user_input: str) -> str:
        return f"""
# Glassescat - Genel Komut
# Giris: {user_input}

print("Glassescat: Komut algilandi")
print("Giris: {{user_input}}")
"""

    def parse(self, user_input: str) -> Dict:
        correction = self.correct_mistake(user_input)
        mode, confidence, scores = self.analyze_intent(user_input)
        
        # Sistem modu geçişinde önceki modu sakla
        if mode == IntentMode.SYSTEM:
            logger.system("Sistem modu aktif - Ajankontrol hazirlaniyor...")
            self.previous_mode = self.current_mode  # Önceki modu sakla
            self.system_frozen = True
        elif mode == IntentMode.BACK:
            prev_str = self.previous_mode.value if hasattr(self.previous_mode, 'value') else str(self.previous_mode)
            logger.info(f"Geri donus: {prev_str} moduna donuluyor")
            resume_mode = self.previous_mode if self.previous_mode != IntentMode.UNKNOWN else IntentMode.GAME
            mode = resume_mode
            self.current_mode = mode
            self.system_frozen = False
            logger.game(f"Sistem uyandi - {mode.value} modu aktif")
        elif mode != IntentMode.UNKNOWN:
            # Normal mod geçişi
            self.previous_mode = self.current_mode
            self.current_mode = mode
            self.system_frozen = False
        
        # GlassesCat log
        if mode == IntentMode.GAME:
            logger.game(f"Oyun modu algilandi - Guven: %{confidence*100:.0f}")
        elif mode == IntentMode.AGENT:
            logger.agent(f"Ajan modu algilandi - Guven: %{confidence*100:.0f}")
        elif mode == IntentMode.SYSTEM:
            logger.system(f"Sistem modu aktif - Ajankontrol hazir")
        
        self.conversation_history.append({
            "input": user_input,
            "mode": mode.value,
            "confidence": confidence,
            "system_frozen": self.system_frozen,
            "previous_mode": self.previous_mode.value if hasattr(self.previous_mode, 'value') else str(self.previous_mode)
        })
        
        generated_code = self.transform_to_code(user_input, mode)
        
        result = {
            "original_input": user_input,
            "mode": mode.value,
            "confidence": confidence,
            "scores": {k.value: v for k, v in scores.items()},
            "generated_code": generated_code,
            "was_corrected": correction is not None,
            "correction_message": correction,
            "system_frozen": self.system_frozen,
            "previous_mode": self.previous_mode.value if hasattr(self.previous_mode, 'value') else str(self.previous_mode),
            "can_resume": self.system_frozen
        }
        
        return result
    
    def get_mode_description(self, mode: IntentMode) -> str:
        descriptions = {
            IntentMode.GAME: "[G] OYUN MODU - Oyun gelistirme",
            IntentMode.AGENT: "[A] AJAN MODU - Otomasyon",
            IntentMode.SYSTEM: "[S] SISTEM MODU - Ajankontrol (Dondurulmus)",
            IntentMode.BACK: "[<] GERI DONUS - Sistem uyaniyor",
            IntentMode.UNKNOWN: "? BILINMEYEN"
        }
        return descriptions.get(mode, "Bilinmiyor")
    
    def resume_system(self) -> Dict:
        """Sistem dondurulmussa onceki moda geri don"""
        if not self.system_frozen:
            return {"status": "not_frozen", "message": "Sistem zaten aktif"}
        
        resume_mode = self.previous_mode if self.previous_mode != IntentMode.UNKNOWN else IntentMode.GAME
        self.current_mode = resume_mode
        self.system_frozen = False
        logger.game(f"Sistem aktive edildi - {resume_mode.value} modu aktif")
        
        return {
            "status": "resumed",
            "mode": resume_mode.value,
            "message": f"Sistem {resume_mode.value} moduna dondu"
        }
    
    def freeze_system(self) -> Dict:
        """Sistem durdurma"""
        self.previous_mode = self.current_mode
        self.current_mode = IntentMode.SYSTEM
        self.system_frozen = True
        logger.system("Sistem donduruldu - Tum ajanlar beklemede")
        
        return {
            "status": "frozen",
            "message": "Tum ajanlar donduruldu"
        }


# ==================== RETRY MEKANİZMASI ====================
class FileRetry:
    """
    GlassesCat Retry Sistemi
    Dosya islemlerinde 'Erisim Engellendi' ve 'Dosya Kullanimda' hatalarini otomatik asar
    
    Erkay Software - Lead Engineer AI
    """
    
    MAX_RETRIES = 5
    RETRY_DELAY = 0.5  # Saniye
    
    ERROR_CASES = [
        "erisim engellendi",
        "permission denied",
        "dosya kullanımda",
        "file in use",
        "being used by another process",
        "cannot access",
        "the process cannot access the file"
    ]
    
    @staticmethod
    def execute(func: Callable, *args, **kwargs) -> Tuple[bool, any]:
        """
        Fonksiyonu retry ile calistir
        
        Usage:
            success, result = FileRetry.execute(ornek_fonksiyon, arg1, arg2)
        """
        last_error = None
        
        for attempt in range(FileRetry.MAX_RETRIES):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Basarili deneme: {attempt + 1}")
                return True, result
            
            except Exception as e:
                error_str = str(e).lower()
                is_retryable = any(case in error_str for case in FileRetry.ERROR_CASES)
                
                if not is_retryable:
                    logger.error(f"Kritik hata - retry edilemez: {e}")
                    return False, str(e)
                
                last_error = str(e)
                logger.info(f"Deneme {attempt + 1}/{FileRetry.MAX_RETRIES} basarisiz: {e}")
                
                if attempt < FileRetry.MAX_RETRIES - 1:
                    time.sleep(FileRetry.RETRY_DELAY * (attempt + 1))  # Artan bekleme
                    logger.info("Tekrar deneniyor...")
        
        logger.error(f"Tum denemeler basarisiz: {last_error}")
        return False, last_error
    
    @staticmethod
    def read_file(filepath: str, encoding: str = "utf-8") -> Tuple[bool, str]:
        """Dosya okuma retry ile"""
        return FileRetry.execute(lambda: open(filepath, 'r', encoding=encoding).read())
    
    @staticmethod
    def write_file(filepath: str, content: str, encoding: str = "utf-8") -> Tuple[bool, str]:
        """Dosya yazma retry ile"""
        return FileRetry.execute(
            lambda: open(filepath, 'w', encoding=encoding).write(content) or True
        )
    
    @staticmethod
    def copy_file(src: str, dst: str) -> Tuple[bool, str]:
        """Dosya kopyalama retry ile"""
        import shutil
        return FileRetry.execute(shutil.copy2, src, dst)
    
    @staticmethod
    def delete_file(filepath: str) -> Tuple[bool, str]:
        """Dosya silme retry ile"""
        return FileRetry.execute(lambda: (os.remove(filepath) or True))


def run_command_parser():
    print("=" * 60)
    print("  GLASSESCAT USER INTENT - COMMAND PARSER")
    print("  Erkay Software - Lead Engineer AI")
    print("=" * 60)
    print()
    print("Modlar:")
    print("  [G] Game    - Oyun gelistirme")
    print("  [A] Agent   - Ajan/otomasyon")
    print("  [S] System  - Sistem kontrolu")
    print()
    print("Ornek: 'Sunu yapmak istiyorum...' yazin")
    print("Cikmak icin 'exit' yazin")
    print("=" * 60)
    print()
    
    parser = CommandParser()
    
    while True:
        try:
            user_input = input(f"{parser.get_mode_description(parser.current_mode)}\n> ")
            
            if user_input.lower() in ['exit', 'quit', 'cikis', 'q']:
                print("\nGlassescat kapatiliyor...")
                break
            
            if not user_input.strip():
                continue
            
            result = parser.parse(user_input)
            
            print()
            print("-" * 40)
            print(f"ANALIZ SONUCLARI")
            print("-" * 40)
            print(f"  Algilanan Mod: {result['mode']}")
            print(f"  Guven Skoru:   %{result['confidence'] * 100:.1f}")
            print(f"  Skorlar:       Oyun: {result['scores'].get('[G]', 0)}, "
                  f"Ajan: {result['scores'].get('[A]', 0)}, "
                  f"Sistem: {result['scores'].get('[S]', 0)}")
            
            if result['was_corrected']:
                print(f"  Duzeltildi: {result['correction_message']}")
            
            print("-" * 40)
            print("URETILEN KOD:")
            print("-" * 40)
            print(result['generated_code'])
            print("=" * 40)
            print()
            
        except KeyboardInterrupt:
            print("\nCikis yapildi")
            break
        except Exception as e:
            print(f"\nHata: {str(e)}")
            print("Tekrar deneyin!\n")


if __name__ == "__main__":
    run_command_parser()