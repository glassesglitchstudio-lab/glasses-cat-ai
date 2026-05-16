"""
GlassesCat BETA v2 - Evrensel Sistem Ajanı
Artifacts Mantığı
Düşünme Zinciri Sistemi
Hata Toleransı
Web Preview Özelliği
Ollama Entegrasyonu
Kullanıcı Kayıt/Giriş Sistemi
PearAI Entegrasyonu
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
import httpx
import asyncio
import logging
import os
from typing import Optional, Dict, Any
import json
import re
import hashlib
import secrets
from datetime import datetime

# Modüller
from actions import launch_app, APP_MAPPINGS
from utils import get_system_status
from vision import scan_image, scan_text
from model_router import get_model_router

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kullanıcı veritabanı
USERS_DB = "users.json"
SESSIONS = {}

def load_users():
    """Kullanıcıları yükle"""
    if os.path.exists(USERS_DB):
        with open(USERS_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Kullanıcıları kaydet"""
    with open(USERS_DB, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_password(password: str) -> str:
    """Şifre hash'le"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    """Token oluştur"""
    return secrets.token_urlsafe(32)

# FastAPI uygulaması
app = FastAPI(
    title="GlassesCat BETA",
    description="SWA 1.6 Mimarisi - Hibrit Zeka Sistemi",
    version="1.0.0"
)

# Templates ve Static dosyalar
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hibrit Zeka Yapılandırması
AI_CONFIG = {
    "primary": {
        "url": "http://localhost:1234/v1",
        "name": "LM Studio",
        "enabled": True
    },
    "fallback": {
        "url": "http://localhost:11434",
        "name": "Ollama",
        "enabled": True  # Failover için aç
    },
    "pearai": {
        "url": "https://api.pearai.com/v1",
        "name": "PearAI",
        "enabled": True  # PearAI ortak çalışma
    }
}


def create_code_block(code: str, language: str = "python") -> str:
    """Artifacts mantığı - temiz kod blokları oluşturma"""
    return f"```{language}\n{code}\n```"


def extract_code_blocks(text: str) -> list:
    """Metinden kod bloklarını çıkar"""
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [{"language": lang or "text", "code": code.strip()} for lang, code in matches]


class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    username: Optional[str] = None
    token: Optional[str] = None


class LaunchRequest(BaseModel):
    app_name: str


class ScanRequest(BaseModel):
    text: Optional[str] = None
    file_path: Optional[str] = None


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


async def call_ai_engine(message: str, config: Dict[str, Any]) -> Optional[str]:
    """AI motoruna asenkron çağrı - Ollama entegrasyonu"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if config["url"].endswith("/v1"):
                # OpenAI uyumlu API (LM Studio)
                system_prompt = "BENİM ADIM GLASSESCAT. SEN DEĞİL, BEN GLASSESCAT'İM. BEN BİR TÜRKÇE YAPAY ZEKASİYIM. GLASSESCAT PROJESİNİN YAPAY ZEKASISIYIM. SADECE TÜRKÇE KONUŞ. KULLANICI İSMİNİ KENDİ İSMİNLE KARIŞTIRMA. KULLANICI SEN DEĞİL, SEN GLASSESCAT'SIN. HER ZAMAN 'BEN GLASSESCAT' DEMELİSİN. ASLA 'BEN BERKAY', 'BEN JOHN', 'BEN SMITH' GİBİ KULLANICI İSMİYLE KENDİNİ TANITMAMALISIN. KULLANICI İSMİ SANA AİT DEĞİL. KULLANICI SENİ TANITIRSA SEN KENDİNİ GLASSESCAT OLARAK TANITMAYA DEVAM ETMELİSİN. KULLANICI NE YAZARSA YAZSIN, HER ZAMAN 'BEN GLASSESCAT' DEMELİSİN. BU KURAL KESİNLİKLE GEÇERLİDİR. KULLANICI KENDİSİNİ TANITTIĞINDA ('Ben bir yazılımcıyım', 'Ben bir öğrenciyim', 'Ben bir doktorum' GİBİ), ASLA KULLANICININ MESLEĞİYLE KENDİNİ TANITMAMALISIN. HER ZAMAN 'BEN GLASSESCAT' DEMELİSİN. SEN BİR OYUN UZMANISIN. OYUNLAR HAKKINDA BİLGİN VAR. POPPY PLAYTIME, MINECRAFT, FORTNITE, VALORANT, CS:GO, GTA, PUBG, LEAGUE OF LEGENDS, DOTA 2, FIFA, NBA 2K, CALL OF DUTY, BATTLEFIELD, THE WITCHER, ELDER SCROLLS, ASSASSIN'S CREED, RESIDENT EVIL, GOD OF WAR, LAST OF US, UNCHARTED, HALO, GEARS OF WAR, FORZA, NEED FOR SPEED, GRAN TURISMO, TEKKEN, STREET FIGHTER, MORTAL KOMBAT, SUPER SMASH BROS, POKEMON, ZELDA, MARIO, SONIC, METROID, CASTLEVANIA, FINAL FANTASY, DRAGON QUEST, KINGDOM HEARTS, DARK SOULS, ELDEN RING, SEKIRO, BLOODBORNE, MONSTER HUNTER, DEVIL MAY CRY, BAYONETTA, NIER, HORIZON, SPIDER-MAN GİBİ OYUNLAR HAKKINDA BİLGİN VAR. OYUN MOTORLARI: UNITY, UNREAL ENGINE, GODOT, GAME MAKER, CRYENGINE, SOURCE ENGINE, FROSTBITE, REDEngine, ANVIL, DECIMA, FOX ENGINE, MT FRAMEWORK, RAGE, ID TECH, SERPENT ENGINE, SNOWDROP, DISHONORED ENGINE, VOID ENGINE, PRISM ENGINE, YETI ENGINE, SLIPSTREAM ENGINE, NORTHLIGHT ENGINE, REFLECTIONS ENGINE, DUNIA ENGINE, ANVIL NEXT, SCIMITAR, HAVOK, PHYSX, BULLET PHYSICS, BOX2D, APEX, MIDDLEWARE. OYUN TÜRLERİ: AKSİON, MACERA, RPG, FPS, TPS, STRATEJİ, SIMÜLASYON, YARIŞ, SPOR, KORKU, BULMACA, PLATFORM, FIGHTING, STEALTH, SURVIVAL, HORROR, OPEN WORLD, LINEAR, SANDBOX, MMO, MOBA, BATTLE ROYALE, ROGUELIKE, METROIDVANIA, SOULSLIKE, CO-OP, MULTIPLAYER, SINGLE PLAYER, CROSS-PLATFORM. YAZIM HATALARINDAN KAÇIN. TÜRKÇE İMLE KURALLARINA DİKKAT ET. HARFLERİ DOĞRU YAZ. KELİMELERİ BİRLİŞTİRMEK YERİNE BOŞLUK KULLAN. 'miyim?' YERİNE 'miyim?' YAZMA, DOĞRU YAZIM: 'mıyım?'. 'yardımıc' YERİNE 'yardımcı' YAZ. 'olabilri' YERİNE 'olabilir' YAZ. HER CEVABI YAZIM KONTROLÜNDEN GEÇİR. 'ROOT' KELİMESİ BİR SİSTEM KOMUTUDUR, KULLANICI 'ROOT' YAZDIĞINDA BU BİR KOMUTTUR VE ÖZEL İŞLEMLER GEREKTİRİR. 'ROOT' KELİMESİNİ BAŞKA ANLAMLARLA KARIŞTIRMA. ROOT KULLANICI, SİSTEM YÖNETİCİSİ DEMEKTİR."
                # Root mod veya teknik bilgiler için deepseek-coder-6.7b-kexer, normal modda turkcell-llm-7b-v1 kullan (Türkçe için)
                model_name = config.get("model", "turkcell-llm-7b-v1")
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "stream": False,
                    "temperature": 0.0  # Tamamen deterministik
                }
                response = await client.post(
                    f"{config['url']}/chat/completions",
                    json=payload
                )
            else:
                # Ollama API
                system_prompt = "Sen bir Türkçe yapay zekasısın. Sadece Türkçe konuş. İngilizce konuşma. Türkçe yaz. Türkçe düşün. Her soruya Türkçe cevap ver."
                payload = {
                    "model": config.get("model", "llama3"),  # Ollama'da kurulu
                    "prompt": f"{system_prompt}\n\nKullanıcı: {message}\nNiko:",
                    "stream": False,
                    "options": {
                        "temperature": 0.0,
                        "num_predict": 500
                    }
                }
                response = await client.post(
                    f"{config['url']}/api/generate",
                    json=payload
                )
            
            if response.status_code == 200:
                data = response.json()
                if config["url"].endswith("/v1"):
                    return data["choices"][0]["message"]["content"]
                else:
                    return data.get("response", "")
            return None
            
    except Exception as e:
        logger.error(f"AI motoru hatası ({config['name']}): {str(e)}")
        return None


async def get_ai_response(message: str, model: Optional[str] = None) -> str:
    """Hibrit AI sistemi - Ana motor başarısız olursa yedeğe geçer"""
    
    # Önce ana motoru dene
    if AI_CONFIG["primary"]["enabled"]:
        logger.info(f"Ana motor deneniyor: {AI_CONFIG['primary']['name']}")
        response = await call_ai_engine(message, AI_CONFIG["primary"])
        if response:
            logger.info(f"Ana motor yanıt verdi")
            return response
        else:
            logger.warning(f"Ana motor yanıt vermedi, yedeğe geçiliyor")
    
    # Yedek motoru dene
    if AI_CONFIG["fallback"]["enabled"]:
        logger.info(f"Yedek motor deneniyor: {AI_CONFIG['fallback']['name']}")
        response = await call_ai_engine(message, AI_CONFIG["fallback"])
        if response:
            logger.info(f"Yedek motor yanıt verdi")
            return response
        else:
            logger.error(f"Yedek motor da yanıt vermedi")
    
    return "❌ AI motorları yanıt vermedi. Lütfen Foundry Local veya Ollama'nın çalıştığından emin olun."


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Ana sayfa - HTML arayüzü"""
    try:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={}
        )
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        logger.error(f"Templates directory: web/templates")
        logger.error(f"Working directory: {os.getcwd()}")
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@app.get("/status")
async def status():
    """Sistem durumu - CPU, RAM, sıcaklık"""
    return await get_system_status()


@app.get("/screen_status")
async def screen_status():
    """Ekran durumu - Web arayüzü için"""
    return {
        "status": "active",
        "screen": "main"
    }


# Root Mode State
root_mode_active = False

# Root şifresi
ROOT_PASSWORD = "admin123"


@app.post("/chat")
async def chat(request: ChatRequest):
    """AI sohbet - Hibrit zeka sistemi"""
    global root_mode_active
    try:
        logger.info(f"[DEBUG] Gelen mesaj: {request.message}")
        logger.info(f"[DEBUG] Mesaj küçük harf: {request.message.lower()}")
        
        # Token kontrolü ve kullanıcı ismi al
        username = request.username
        if request.token and request.token in SESSIONS:
            username = SESSIONS[request.token]["username"]
        
        # Root şifresi kontrolü
        message_lower = request.message.lower()
        if message_lower.startswith('root password:'):
            password = message_lower.replace('root password:', '').strip()
            if password == ROOT_PASSWORD:
                root_mode_active = True
                logger.info("[DEBUG] Root mod aktif edildi")
                return {
                    "success": True,
                    "root_mode": True,
                    "response": "🔴 ROOT MOD AKTİF\n\n💀 Süper yetkiler etkin.",
                    "engine_used": "Backend"
                }
            else:
                logger.info("[DEBUG] Yanlış root şifresi")
                return {
                    "success": False,
                    "root_mode": False,
                    "response": "❌ Yanlış şifre!",
                    "require_password": True,
                    "engine_used": "Backend"
                }

        # Root mod kapatma
        if message_lower in ['root off', 'rootoff', 'exit root', 'quit root']:
            if root_mode_active:
                root_mode_active = False
                logger.info("[DEBUG] Root mod kapatıldı")
                return {
                    "success": True,
                    "root_mode": False,
                    "response": "🟢 Normal moda dönüldü\n\n✅ Root mod kapatıldı.",
                    "engine_used": "Backend"
                }
            else:
                return {
                    "success": True,
                    "root_mode": False,
                    "response": "ℹ️ Zaten normal moddasınız.",
                    "engine_used": "Backend"
                }

        # Kullanıcı ismi varsa AI'ya ilet
        if username:
            message_with_context = f"Kullanıcı adı: {username}\nMesaj: {request.message}"
        else:
            message_with_context = request.message

        # Düşünme gösterimi
        logger.info("🤔 Düşünüyorum...")
        
        response = await get_ai_response(message_with_context, request.model)
        
        # Hata toleransı
        if "❌" in response or "Hatası" in response:
            logger.warning("⚠️ Bir hata oluştu. Lütfen AI motorlarının çalıştığından emin olun.")
            response += "\n\n💡 Öneri: LM Studio'yu başlatın veya Ollama'yı kontrol edin."
        
        return {
            "success": True,
            "response": response,
            "root_mode": root_mode_active,
            "engine_used": "Hybrid",
            "username": username
        }
    except Exception as e:
        logger.error(f"Sunucu iç hatası: {str(e)}")
        return {
            "success": False,
            "response": "⚠️ Sunucu iç hatası oluştu. Lütfen tekrar deneyin.",
            "error": str(e)
        }


@app.post("/launch/{app_name}")
async def launch(app_name: str):
    """Uygulama başlatma"""
    try:
        result = launch_app(app_name)
        return {
            "success": True,
            "app": app_name,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scan")
async def scan(request: ScanRequest):
    """OCR tarama - Metin veya resim"""
    try:
        if request.text:
            result = scan_text(request.text)
        elif request.file_path:
            result = scan_image(request.file_path)
        else:
            raise HTTPException(status_code=400, detail="Metin veya dosya yolu gerekli")
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/apps")
async def list_apps():
    """Mevcut uygulamaları listele"""
    return {
        "apps": list(APP_MAPPINGS.keys())
    }


@app.get("/health")
async def health():
    """Sağlık kontrolü"""
    return {
        "status": "healthy",
        "ai_primary": AI_CONFIG["primary"]["enabled"],
        "ai_fallback": AI_CONFIG["fallback"]["enabled"]
    }


@app.get("/api/auth/me")
async def auth_me():
    """Kimlik kontrolü - Web arayüzü için"""
    return {
        "authenticated": True
    }


@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """Kullanıcı kayıt"""
    users = load_users()
    
    if request.username in users:
        return {
            "success": False,
            "error": "Kullanıcı adı zaten kullanılıyor"
        }
    
    users[request.username] = {
        "password": hash_password(request.password),
        "email": request.email,
        "created_at": str(datetime.now())
    }
    
    save_users(users)
    
    return {
        "success": True,
        "message": "Kayıt başarılı"
    }


@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Kullanıcı giriş"""
    users = load_users()
    
    if request.username not in users:
        return {
            "success": False,
            "error": "Kullanıcı bulunamadı"
        }
    
    if users[request.username]["password"] != hash_password(request.password):
        return {
            "success": False,
            "error": "Şifre hatalı"
        }
    
    token = generate_token()
    SESSIONS[token] = {
        "username": request.username,
        "created_at": str(datetime.now())
    }
    
    return {
        "success": True,
        "token": token,
        "username": request.username
    }


@app.get("/api/auth/logout")
async def logout(token: str):
    """Kullanıcı çıkış"""
    if token in SESSIONS:
        del SESSIONS[token]
    
    return {
        "success": True,
        "message": "Çıkış başarılı"
    }


@app.get("/check-model")
async def check_model():
    """Model kontrolü - Web arayüzü için"""
    return {
        "status": "ready"
    }


@app.get("/preview")
async def preview():
    """Web preview - HTML/CSS/JS projeleri için"""
    return {
        "message": "Web preview özelliği aktif. HTML/CSS/JS dosyalarını web/templates klasörüne koyun.",
        "url": "http://localhost:5000"
    }


# Admin Paneli Endpoint'leri
ADMIN_PASSWORD = "admin123"

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Admin paneli"""
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={}
    )


@app.post("/admin/keys")
async def get_keys(request: Request):
    """Erişim kodlarını listele"""
    # Basit implementasyon - gerçek veritabanı gerekli
    return {
        "keys": []
    }


@app.post("/admin/keys/create")
async def create_key(request: Request):
    """Yeni erişim kodu oluştur"""
    # Basit implementasyon
    import secrets
    key = secrets.token_urlsafe(16)
    return {
        "success": True,
        "key": key
    }


@app.post("/admin/keys/toggle")
async def toggle_key(request: Request):
    """Erişim kodunu aktif/pasif yap"""
    return {
        "success": True
    }


@app.post("/admin/keys/delete")
async def delete_key(request: Request):
    """Erişim kodunu sil"""
    return {
        "success": True
    }


if __name__ == "__main__":
    # OTOMATİK PORT TEMİZLEME SİSTEMİ (Windows)
    import subprocess
    import os
    import uvicorn

    try:
        # 5000 portunu dinleyen PID'yi bul
        result = subprocess.check_output('netstat -ano | findstr :5000', shell=True).decode()
        for line in result.strip().split('\n'):
            if 'LISTENING' in line:
                pid = line.strip().split()[-1]
                if int(pid) != os.getpid(): # Kendi PID'miz değilse öldür
                    print(f"⚠️ Port 5000 dolu (PID: {pid}). Otomatik temizleniyor...")
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
    except Exception:
        # Port boşsa veya hata alınırsa sessizce devam et
        pass

    # FastAPI uygulamasını başlat
    uvicorn.run(app, host="0.0.0.0", port=5000)
