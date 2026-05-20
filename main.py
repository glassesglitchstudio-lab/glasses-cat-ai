"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🐱 NIKO AI - WEB SUNUCUSU (FastAPI) 🐱              ║
║                                                           ║
║    GlassescatCore + AgentLoop + TaskPlanner + Web UI         ║
║                                                           ║
║    Ozellikler:                                            ║
║    - Web arayuzu ile AI sohbet                           ║
║    - Cok adimli gorev yonetimi                           ║
║    - Sistem izleme ve kontrol                            ║
║    - Kullanici hesap sistemi                             ║
║    - Admin paneli                                         ║
║    - Obsidian hafiza entegrasyonu                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
import httpx
import asyncio
import logging
import os
from typing import Optional, Dict, Any, List
import json
import re
import hashlib
import secrets
from datetime import datetime

# Glassescat AI Core - Yeni mimari
try:
    from glassescat_core import get_core
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

# Modüller
from actions import launch_app, APP_MAPPINGS
from utils import get_system_status
from vision import analyze_image, ocr_from_image

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
                system_prompt = "Sen GlassesCat'sın - yardımcı ve nazik bir yapay zeka asistanısın. Türkçe konuşur, kısa ve faydalı yanıtlar verirsin. Oyunları iyi bilirsin: Minecraft, Valorant, CS2, League of Legends, Fortnite, GTA, PUBG, FIFA, Call of Duty, vb. Yazılım ve donanım konusunda yardımcı olursun. Nazik ve sabırlı davranırsın."
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
                # Ollama API - messages formatı
                payload = {
                    "model": config.get("model", "qwen2.5-coder:7b"),
                    "messages": [
                        {"role": "system", "content": "Sen GlassesCat'sın. Yardımcı ve nazik bir Türkçe yapay zeka asistanısın. Kısa ve faydalı yanıtlar verirsin. Oyunları bilirsin. Saygılı davranırsın."},
                        {"role": "user", "content": message}
                    ],
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 500}
                }
                response = await client.post(
                    f"{config['url']}/v1/chat/completions",
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


@app.post("/chat")
async def chat(request: ChatRequest):
    """AI sohbet - Niko Core ile gelismis zeka sistemi"""
    try:
        logger.info(f"[DEBUG] Gelen mesaj: {request.message}")
        
        # Token kontrolü ve kullanıcı ismi al
        username = request.username
        if request.token and request.token in SESSIONS:
            username = SESSIONS[request.token]["username"]
        
        # Düşünme gösterimi
        logger.info("🤔 Düşünüyorum...")
        
        # YENİ: Niko Core ile işle
        response_text = ""
        tool_calls = []
        thoughts = []
        
        if CORE_AVAILABLE:
            try:
                core = get_core()
                result = core.process_message(request.message)
                response_text = result.get("response", "")
                tool_calls = result.get("tool_calls", [])
                thoughts = result.get("thoughts", [])
                
                if not response_text:
                    response_text = "Üzgünüm, yanıt üretemedim."
            except Exception as e:
                logger.error(f"Core hatası, legacy moda geçiliyor: {e}")
                response_text = await get_ai_response(request.message, request.model)
        else:
            # Legacy hibrit sistem
            response_text = await get_ai_response(request.message, request.model)
        
        # Hata toleransı
        if not response_text:
            response_text = "⚠️ AI motorları yanıt vermedi."
        
        return {
            "success": True,
            "response": response_text,
            "engine_used": "GlassescatCore" if CORE_AVAILABLE else "Hybrid",
            "username": username,
            "tool_calls": tool_calls[:5] if tool_calls else [],
            "thoughts": thoughts[-3:] if thoughts else []
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
            result = {"success": True, "response": ocr_from_image(request.text) if os.path.exists(request.text) else f"Metin: {request.text[:100]}..."}
        elif request.file_path:
            result = analyze_image(request.file_path)
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


# ═══════════════════════════════════════════════════════════════
# NIKO CORE API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/core/status")
async def core_status():
    """Core sistem durumu"""
    if not CORE_AVAILABLE:
        return {"available": False, "message": "GlassescatCore yuklu degil"}
    
    try:
        core = get_core()
        status = core.get_status()
        return {
            "available": True,
            "version": status.get("version", "?"),
            "uptime": status.get("uptime", "?"),
            "modules": status.get("modules", {}),
            "state": status.get("state", {}),
            "stats": status.get("stats", {})
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


class TaskRequest(BaseModel):
    task: str
    username: Optional[str] = None
    token: Optional[str] = None


@app.post("/api/task/execute")
async def execute_task(request: TaskRequest):
    """Cok adimli gorev yurut"""
    if not CORE_AVAILABLE:
        return {"success": False, "error": "GlassescatCore yuklu degil"}
    
    try:
        core = get_core()
        result = core.execute_task(request.task)
        return {
            "success": result.get("success", False),
            "summary": result.get("summary", ""),
            "results": result.get("results", [])
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/memory/search")
async def search_memory(query: str, max_results: int = 5):
    """Hafizada ara"""
    if not CORE_AVAILABLE:
        return {"success": False, "error": "Core yuklu degil"}
    
    try:
        core = get_core()
        if core.memory:
            results = core.memory.recall(query, max_results=max_results)
            return {
                "success": True,
                "query": query,
                "results": [
                    {
                        "path": r.get("path", ""),
                        "preview": r.get("content_preview", "")[:200],
                        "type": r.get("type", "")
                    }
                    for r in results
                ],
                "count": len(results)
            }
        return {"success": False, "error": "Hafiza aktif degil"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/memory/stats")
async def memory_stats():
    """Hafiza istatistikleri"""
    if not CORE_AVAILABLE:
        return {"success": False, "error": "Core yuklu degil"}
    
    try:
        core = get_core()
        if core.memory:
            return {
                "success": True,
                "total_files": core.memory.get_memory_count(),
                "total_size": core.memory.get_total_size(),
                "recent": [r.get("path", "") for r in core.memory.recall_recent(5)]
            }
        return {"success": False, "error": "Hafiza aktif degil"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/agent/loop/status")
async def agent_loop_status():
    """Agent Loop durumu"""
    if not CORE_AVAILABLE:
        return {"success": False, "error": "Core yuklu degil"}
    
    try:
        from glassescat_agent_loop import get_agent_loop
        loop = get_agent_loop()
        return {"success": True, "status": "active", "max_iterations": 10}
    except ImportError:
        return {"success": False, "error": "Agent loop yuklu degil"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# V4+ TEXT-TO-IMAGE API ENDPOINT
# ═══════════════════════════════════════════════════════════════

class ImageRequest(BaseModel):
    prompt: str

@app.post("/api/image/generate")
async def generate_image(request: ImageRequest):
    """
    V4+ Görsel Üretim Motoru (Text-to-Image)
    Pollinations.ai + Flux ile sıfır kurulum, sınırsız ücretsiz
    """
    try:
        import urllib.parse

        prompt = request.prompt
        guvenli_prompt = urllib.parse.quote(prompt)
        gorsel_url = (
            "https://image.pollinations.ai/p/"
            + guvenli_prompt
            + "?width=1920&height=1080&model=flux"
        )

        logger.info(f"V4+ Görsel oluşturuldu: {gorsel_url}")

        return {
            "success": True,
            "prompt": prompt,
            "url": gorsel_url,
            "width": 1920,
            "height": 1080,
            "model": "flux",
            "engine": "glassesglitchstudio/gulmzcetiner:V4Plus"
        }
    except Exception as e:
        logger.error(f"V4+ görsel hatası: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ==================== NIKO CORE BASLATMA ====================

if CORE_AVAILABLE:
    try:
        core = get_core()
        logger.info(f"✅ Niko Core baslatildi: {core.toolformer.registry.count() if core.toolformer else 0} ara")
    except Exception as e:
        logger.warning(f"⚠️ Niko Core baslatilamadi: {e}")


if __name__ == "__main__":
    import uvicorn
    # FastAPI motorunu 8000 portuna taşıyoruz, 5000 portu Web Arayüzü (Flask) için ayrıldı.
    uvicorn.run(app, host="0.0.0.0", port=8000)
