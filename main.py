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

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
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
import uuid
import io
import csv

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

# Modüler route'ları dahil et
try:
    from routes import router as api_router
    app.include_router(api_router)
    logger.info("Modüler route'lar yüklendi")
except Exception as e:
    logger.debug(f"Route yükleme hatası: {e}")

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
    stream: Optional[bool] = False


class SkillHuntRequest(BaseModel):
    query: str
    source: str = "both"


class SkillInstallRequest(BaseModel):
    command: str


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
    """Ana sayfa - Claude tarzı sohbet arayüzü"""
    try:
        return templates.TemplateResponse(
            request=request,
            name="chat.html",
            context={"request": request}
        )
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        return HTMLResponse(content="<h1>GlassesCat AI</h1><p>Template yüklenemedi</p>")

@app.get("/docs", response_class=HTMLResponse)
async def docs_page(request: Request):
    """Dokümantasyon sayfası - static HTML"""
    try:
        docs_path = os.path.join(os.path.dirname(__file__), "docs", "index.html")
        if os.path.exists(docs_path):
            with open(docs_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>GlassesCat AI</h1><p>Doküman bulunamadı</p>")
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {str(e)}")
        return HTMLResponse(content="<h1>GlassesCat AI</h1><p>Template yüklenemedi</p>")


@app.get("/status")
def status():
    """Sistem durumu - CPU, RAM, sıcaklık"""
    return get_system_status()


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
        
        # Model seçimi: frontend'den gelen modele göre yönlendir
        model_choice = (request.model or "X_OPUS").upper()
        
        # ── STREAMING MODU ──
        if request.stream:
            def sse(data: dict):
                return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            async def stream_gen():
                try:
                    if model_choice in ("X_GLITCH_OPUS", "X_FABLE_CODER"):
                        from xopus_router import get_xopus, GLITCH_MODEL, CODE_MODEL
                        xopus = get_xopus()
                        override = GLITCH_MODEL if model_choice == "X_GLITCH_OPUS" else CODE_MODEL
                        for ch in xopus.chat_stream(
                            message=request.message,
                            system_prompt=None,
                            model=override
                        ):
                            yield sse(ch)
                        yield sse({"done": True})
                    elif CORE_AVAILABLE:
                        import threading
                        from glassescat_agent_loop import extract_answer
                        holder = {}
                        def run_core():
                            try:
                                core = get_core()
                                res = core.process_message(request.message)
                                holder["text"] = res.get("response", "")
                            except Exception as e:
                                holder["error"] = str(e)
                        th = threading.Thread(target=run_core, daemon=True)
                        th.start()
                        th.join(timeout=120)
                        if holder.get("error"):
                            yield sse({"error": holder["error"]})
                            return
                        text = holder.get("text", "")
                        if isinstance(text, dict):
                            text = text.get("response") or text.get("text") or text.get("error") or str(text)
                        elif isinstance(text, str) and text.startswith("{") and ("'response'" in text[:80] or "'error'" in text[:80]):
                            try:
                                inner = json.loads(text.replace("'", '"'))
                                if isinstance(inner, dict):
                                    text = inner.get("response") or inner.get("text") or inner.get("error") or str(inner)
                            except Exception:
                                pass
                        text = extract_answer(text or "")
                        yield sse({"token": text, "done": False})
                        yield sse({"done": True})
                    else:
                        text = await get_ai_response(request.message, request.model)
                        yield sse({"token": text, "done": False})
                        yield sse({"done": True})
                except Exception as e:
                    logger.error(f"Stream hatasi: {e}")
                    yield sse({"error": str(e)})
            
            return StreamingResponse(
                stream_gen(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
            )
        
        # Düşünme gösterimi
        logger.info("🤔 Düşünüyorum...")
        
        # YENİ: Niko Core ile işle
        response_text = ""
        tool_calls = []
        thoughts = []
        
        # Model seçimi: frontend'den gelen modele göre yönlendir
        model_choice = (request.model or "X_OPUS").upper()
        
        if model_choice in ("X_GLITCH_OPUS", "X_FABLE_CODER"):
            try:
                from xopus_router import get_xopus, GLITCH_MODEL, CODE_MODEL
                xopus = get_xopus()
                override = GLITCH_MODEL if model_choice == "X_GLITCH_OPUS" else CODE_MODEL
                result = xopus.chat(
                    message=request.message,
                    system_prompt=None,
                    model=override
                )
                response_text = result.get("response", "")
                if result.get("routing"):
                    thoughts = [result["routing"]]
                if not response_text:
                    response_text = f"Üzgünüm, {model_choice} yanıt üretemedi: {result.get('error', 'bilinmeyen hata')}"
            except ImportError:
                response_text = "X_OPUS modülü bulunamadı. `xopus_router.py` eksik."
            except Exception as e:
                logger.error(f"X_OPUS hatası: {e}")
                response_text = f"⚠️ {model_choice} hatası: {e}"
        elif CORE_AVAILABLE:
            try:
                core = get_core()
                result = core.process_message(request.message)
                response_text = result.get("response", "")
                
                # Güvenlik ağı: response dict/dict-repr gelirse metni ayıkla
                if isinstance(response_text, dict):
                    response_text = response_text.get("response") or response_text.get("text") or response_text.get("error") or str(response_text)
                elif isinstance(response_text, str) and response_text.startswith("{") and ("'response'" in response_text[:80] or "'error'" in response_text[:80]):
                    try:
                        import ast
                        inner = ast.literal_eval(response_text)
                        if isinstance(inner, dict):
                            response_text = inner.get("response") or inner.get("text") or inner.get("error") or str(inner)
                    except Exception:
                        pass
                
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
            "engine_used": model_choice,
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


# ─────────────────────────────────────────────────────────────
# DOSYA YÜKLEME VE İŞLEME
# ─────────────────────────────────────────────────────────────

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "storage", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf": "document",
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".gif": "image", ".webp": "image", ".svg": "image",
    ".py": "code", ".js": "code", ".ts": "code", ".jsx": "code", ".tsx": "code",
    ".html": "code", ".css": "code", ".json": "code", ".xml": "code", ".yaml": "code", ".yml": "code",
    ".md": "code", ".txt": "code", ".csv": "data", ".tsv": "data",
    ".docx": "document", ".doc": "document"
}

def parse_uploaded_file(file_path: str, ext: str) -> dict:
    ext = ext.lower()
    content = ""
    preview = ""
    file_type = ALLOWED_EXTENSIONS.get(ext, "unknown")
    try:
        if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
            with open(file_path, "rb") as f:
                import base64
                b64 = base64.b64encode(f.read()).decode()
                preview = f"data:image/{ext.lstrip('.')};base64,{b64[:100]}..."
                content = f"[Image: {os.path.basename(file_path)}]"
        elif ext == ".pdf":
            try:
                import PyPDF2
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    pages = [p.extract_text() for p in reader.pages[:10]]
                    content = "\n\n".join(pages)
                    preview = content[:500]
            except ImportError:
                content = f"[PDF: {os.path.basename(file_path)} (PyPDF2 gerekli)]"
                preview = content
        elif ext == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[:30]
                content = "".join(lines)
                preview = content[:500]
        elif ext == ".docx":
            try:
                from docx import Document
                doc = Document(file_path)
                paras = [p.text for p in doc.paragraphs[:50]]
                content = "\n".join(paras)
                preview = content[:500]
            except ImportError:
                content = f"[DOCX: {os.path.basename(file_path)} (python-docx gerekli)]"
                preview = content
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                preview = content[:500]
    except Exception as e:
        content = f"[Dosya okunamadı: {e}]"
        preview = content
    return {"content": content, "preview": preview, "type": file_type, "extension": ext}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), project_id: str = Form(default="")):
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return {"success": False, "error": f"Desteklenmeyen dosya türü: {ext}. İzin verilenler: {', '.join(ALLOWED_EXTENSIONS.keys())}"}

        file_id = uuid.uuid4().hex[:8]
        safe_name = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)

        content_bytes = await file.read()
        with open(file_path, "wb") as f:
            f.write(content_bytes)

        parsed = parse_uploaded_file(file_path, ext)
        file_info = {
            "id": file_id,
            "name": file.filename,
            "path": file_path,
            "size": len(content_bytes),
            "type": parsed["type"],
            "extension": ext,
            "preview": parsed["preview"][:300]
        }

        if project_id:
            from glassescat_core import get_core
            c = get_core()
            if c.get_project(project_id):
                c.add_file_to_project(project_id, file_info)

        return {
            "success": True,
            "file": file_info,
            "content": parsed["content"],
            "message": f"{file.filename} yüklendi ({len(content_bytes)} bayt)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/upload/{file_id}")
async def get_uploaded_file(file_id: str):
    try:
        for fname in os.listdir(UPLOAD_DIR):
            if fname.startswith(file_id):
                path = os.path.join(UPLOAD_DIR, fname)
                ext = os.path.splitext(fname)[1].lower()
                parsed = parse_uploaded_file(path, ext)
                return {"success": True, "file": {"name": fname, "path": path}, **parsed}
        return {"success": False, "error": "Dosya bulunamadı"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────
# KONUŞMA PAYLAŞMA LİNKİ
# ─────────────────────────────────────────────────────────────

SHARES: Dict[str, dict] = {}

@app.post("/api/share")
async def share_conversation(data: dict):
    try:
        share_id = uuid.uuid4().hex[:10]
        SHARES[share_id] = {
            "messages": data.get("messages", []),
            "title": data.get("title", "Paylaşılan Sohbet"),
            "created": datetime.now().isoformat()
        }
        return {"success": True, "share_id": share_id, "url": f"/share/{share_id}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/share/{share_id}")
async def get_share(share_id: str):
    share = SHARES.get(share_id)
    if not share:
        return {"success": False, "error": "Paylaşım bulunamadı"}
    return {"success": True, **share}

@app.get("/share/{share_id}", response_class=HTMLResponse)
async def share_page(share_id: str):
    share = SHARES.get(share_id)
    if not share:
        return HTMLResponse("<h1>Paylaşım bulunamadı</h1>")
    msgs_html = ""
    for m in share.get("messages", []):
        role = m.get("role", "user")
        content = m.get("content", "")
        label = "👤 Kullanıcı" if role == "user" else "🤖 GlassesCat"
        msgs_html += f'<div style="margin-bottom:16px;padding:12px;background:{ "#f5f5f5" if role=="user" else "#f3e8ff" };border-radius:8px"><strong>{label}</strong><p style="margin-top:4px">{content}</p></div>'
    return HTMLResponse(f"""<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{share["title"]} — GlassesCat</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet"><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Inter',sans-serif;background:#fafafa;color:#1a1a1a;padding:40px 24px;max-width:720px;margin:0 auto}}h1{{font-size:1.1rem;font-weight:600;margin-bottom:24px;color:#7c3aed}}.meta{{font-size:0.75rem;color:#888;margin-bottom:32px}}</style></head><body><h1>{share["title"]}</h1><div class="meta">{share.get("created","")} · Paylaşılan Sohbet</div>{msgs_html}</body></html>""")


# Admin Paneli Endpoint'leri
from dotenv import load_dotenv
load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Degistirilmeli123!")

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Admin paneli - basit dashboard"""
    return HTMLResponse(content=f"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Admin — GlassesCat</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:#0c0a09;color:#f5f0eb;padding:40px 24px}}
h1{{font-size:1.3rem;font-weight:600;margin-bottom:24px}}
.card{{background:#141110;border:1px solid #1e1b18;border-radius:6px;padding:20px;margin-bottom:16px;max-width:500px}}
.card h2{{font-size:0.9rem;font-weight:500;margin-bottom:8px;color:#a8a29e}}
.card p{{font-size:0.8rem;color:#6b6560}}
</style></head><body>
<h1>GlassesCat Admin</h1>
<div class="card"><h2>Dashboard</h2><p>Admin paneli yapım aşamasında.</p></div>
<div class="card"><h2>Sistem Durumu</h2><p id="status">Yükleniyor...</p></div>
<script>
fetch('/api/core/status').then(r=>r.json()).then(d=>{{document.getElementById('status').textContent='Sürüm: '+(d.version||'?')+' | Mod: '+((d.state&&d.state.mode)||'normal')}}).catch(()=>{{document.getElementById('status').textContent='Bağlantı kurulamadı'}})
</script>
</body></html>""")


@app.get("/manage", response_class=HTMLResponse)
async def manage_panel(request: Request):
    """Yönetim paneli"""
    return HTMLResponse(content=f"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Yönetim — GlassesCat</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:#0c0a09;color:#f5f0eb;padding:40px 24px}}
h1{{font-size:1.3rem;font-weight:600;margin-bottom:24px}}
.card{{background:#141110;border:1px solid #1e1b18;border-radius:6px;padding:20px;margin-bottom:16px;max-width:500px}}
.card h2{{font-size:0.9rem;font-weight:500;margin-bottom:8px;color:#a8a29e}}
.card p{{font-size:0.8rem;color:#6b6560}}
</style></head><body>
<h1>GlassesCat Yönetim</h1>
<div class="card"><h2>Yönetim Paneli</h2><p>Yapım aşamasında.</p></div>
</body></html>""")


@app.post("/api/settings/mode")
async def set_mode(data: dict):
    """Agent modunu değiştir"""
    try:
        from glassescat_core import get_core
        c = get_core()
        mode = data.get("mode", "normal")
        c.set_mode(mode)
        return {"success": True, "mode": mode}
    except Exception as e:
        return {"success": False, "error": str(e)}


class SetModeRequest(BaseModel):
    mode: str


@app.post("/api/set_mode")
async def api_set_mode(req: SetModeRequest):
    """Agent modunu degistir: normal, developer, silent, game, memory_agent"""
    try:
        from glassescat_core import get_core
        c = get_core()
        ok = c.set_mode(req.mode)
        if ok:
            return {"success": True, "mode": req.mode}
        else:
            return {"success": False, "error": f"Gecersiz mode: {req.mode}. Gecerli modlar: normal, developer, silent, game, memory_agent"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/settings/style")
async def set_style(data: dict):
    """Yanıt stilini değiştir: normal, concise, explanatory, formal, code_first"""
    try:
        from glassescat_core import get_core, BUILTIN_STYLES, STYLES
        c = get_core()
        style = data.get("style", "normal")
        if style not in BUILTIN_STYLES:
            return {"success": False, "error": f"Geçersiz stil. Seçenekler: {', '.join(BUILTIN_STYLES)}"}
        c.set_style(style)
        return {"success": True, "style": style, "description": STYLES[style]}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/settings/style")
async def get_style():
    try:
        from glassescat_core import get_core
        c = get_core()
        return {"success": True, "style": c.get_style()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/settings/preferences")
async def set_preferences(data: dict):
    try:
        from glassescat_core import get_core
        c = get_core()
        text = data.get("text", "")
        c.set_personal_preferences(text)
        return {"success": True, "length": len(text)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/settings/preferences")
async def get_preferences():
    try:
        from glassescat_core import get_core
        c = get_core()
        return {"success": True, "text": c.get_personal_preferences()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/settings/extended-thinking")
async def set_extended_thinking(data: dict):
    try:
        from glassescat_core import get_core
        c = get_core()
        enabled = data.get("enabled", False)
        c.set_extended_thinking(enabled)
        return {"success": True, "enabled": enabled}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────
# PROJE YÖNETİMİ API
# ─────────────────────────────────────────────────────────────

@app.post("/api/projects")
async def create_project(data: dict):
    try:
        from glassescat_core import get_core
        c = get_core()
        proj = c.create_project(
            project_id=data.get("id", ""),
            name=data.get("name", ""),
            instructions=data.get("instructions", "")
        )
        return {"success": True, "project": proj}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/projects")
async def list_projects():
    try:
        from glassescat_core import get_core
        c = get_core()
        return {"success": True, "projects": c.list_projects()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    try:
        from glassescat_core import get_core
        c = get_core()
        proj = c.get_project(project_id)
        if not proj:
            return {"success": False, "error": "Proje bulunamadı"}
        return {"success": True, "project": proj}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/projects/{project_id}/activate")
async def activate_project(project_id: str):
    try:
        from glassescat_core import get_core
        c = get_core()
        success = c.set_active_project(project_id)
        return {"success": success, "active_project": project_id if success else None}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    try:
        from glassescat_core import get_core
        c = get_core()
        success = c.delete_project(project_id)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────
# MESAJ DÜZENLEME / BRANCHING API
# ─────────────────────────────────────────────────────────────

@app.post("/api/conversations/{conv_id}/edit")
async def edit_message(conv_id: str, data: dict):
    try:
        from glassescat_core import get_core
        c = get_core()
        msg_index = data.get("message_index", -1)
        new_content = data.get("new_content", "")
        branch_id = c.edit_message(conv_id, msg_index, new_content)
        return {"success": True, "branch_id": branch_id, "message": "Yeni branch oluşturuldu"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/conversations/{conv_id}/branches")
async def get_branches(conv_id: str):
    try:
        from glassescat_core import get_core
        c = get_core()
        branches = c.get_branches(conv_id)
        return {"success": True, "branches": branches}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/conversations/branches/{branch_id}/switch")
async def switch_branch(branch_id: str):
    try:
        from glassescat_core import get_core
        c = get_core()
        success = c.switch_branch(branch_id)
        msgs = []
        for m in c.conversation_history:
            msgs.append({"role": m.role, "content": m.content})
        return {"success": success, "messages": msgs}
    except Exception as e:
        return {"success": False, "error": str(e)}


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


@app.post("/api/artifacts/edit")
async def edit_artifact(req: dict):
    """Secili HTML elementi icin AI ile CSS duzenlemesi uretir"""
    selector = (req.get("selector") or "").strip()
    instruction = (req.get("instruction") or "").strip()
    html_src = (req.get("html") or "").strip()[:20000]
    if not selector or not instruction:
        return {"success": False, "error": "selector ve instruction gerekli"}
    if not CORE_AVAILABLE:
        return {"success": False, "error": "GlassescatCore yuklu degil"}
    
    prompt = (
        "Sen bir web tasarim asistanisin. Kullanici, olusturulan HTML sayfasinda tek bir elementi duzenlemek istiyor.\n"
        f"Secili element (CSS selector): `{selector}`\n"
        f"Kullanici talimati: {instruction}\n\n"
        "Sayfanin HTML'i:\n```html\n" + html_src + "\n```\n\n"
        "Sadece bu element icin bir CSS kural blogu dondur: `{ selector { property: value; } }` seklinde.\n"
        "Sayfanin geri kalanini degistirme. Aciklama yazma, markdown kullanma."
    )
    
    try:
        core = get_core()
        result = core.process_message(prompt)
        resp = (result.get("response") or "").strip()
    except Exception as e:
        return {"success": False, "error": f"AI motoru hatasi: {e}"}
    
    # Model yaniti gercek bir metin degilse (dict-string / hata / bos) fallback'e dus
    if (not resp or resp.startswith("{")
            or "Ollama baglantisi yok" in resp
            or "'success': False" in resp
            or '"success": false' in resp):
        css = fallback_element_css(selector, instruction)
        return {"success": True, "css": css, "engine_used": "FallbackCSS"}
    
    m = re.search(re.escape(selector) + r"\s*\{[\s\S]*\}", resp)
    if not m:
        m = re.search(r"[^{}\n]+\{[\s\S]*\}", resp)
    if not m:
        css = fallback_element_css(selector, instruction)
        return {"success": True, "css": css, "engine_used": "FallbackCSS"}
    
    css = m.group(0).strip()
    return {"success": True, "css": css, "engine_used": "GlassescatCore"}


# ─────────────────────────────────────────────
# SKILL AVCIISI — skillsllm.com + GitHub araştırması + terminal kurulumu
# ─────────────────────────────────────────────

def _gh_headers():
    return {"User-Agent": "glassescat-skill-hunter", "Accept": "application/vnd.github+json"}


def _hunt_skillsllm(query: str) -> List[Dict]:
    """skillsllm.com ana listesinden (yildiz sirali) aday toplar."""
    out = []
    try:
        resp = httpx.get("https://skillsllm.com/?sort=stars", timeout=30, follow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        if resp.status_code != 200:
            return out
        html = resp.text
        # Kartlar: github.com/owner/repo baglantilari + /skill/slug linkleri
        for m in re.finditer(r'github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)', html):
            repo = m.group(1).rstrip("/")
            if repo not in [c["repo"] for c in out]:
                out.append({"repo": repo, "source": "skillsllm", "stars": 0})
        # Yildiz sayilari: "234,966" formatinda
        stars = re.findall(r'([\d,]{4,9})\s*[Ss]tars?', html)
        # slug'lar
        slugs = re.findall(r'/skill/([A-Za-z0-9_.-]+)', html)
        if slugs:
            slug_map = {}
            for i, s in enumerate(slugs):
                slug_map.setdefault(s, stars[i] if i < len(stars) else 0)
            for c in out:
                slug = c["repo"].split("/")[-1]
                for s, st in slug_map.items():
                    if s == slug or s.replace("-", "") == slug.replace("-", ""):
                        c["stars"] = st
                        c["slug"] = s
                        break
                if "slug" not in c:
                    c["slug"] = slug
        for c in out:
            c.setdefault("slug", c["repo"].split("/")[-1])
        return out[:30]
    except Exception:
        return out


def _hunt_github(query: str) -> List[Dict]:
    """GitHub aramasi ile skill koleksiyonu repolari bulur."""
    out = []
    try:
        resp = httpx.get(
            "https://api.github.com/search/repositories",
            params={"q": f"{query} skill", "per_page": 10, "sort": "stars"},
            headers=_gh_headers(), timeout=30,
        )
        if resp.status_code == 200:
            for r in resp.json().get("items", []):
                out.append({
                    "repo": r["full_name"],
                    "stars": r.get("stargazers_count") or 0,
                    "updated_at": r.get("updated_at", ""),
                    "desc": (r.get("description") or "")[:200],
                    "source": "github",
                })
    except Exception:
        pass
    return out


def _skill_install_command(repo: str, slug: str = "") -> str:
    """Skill sayfasindaki / repo'daki kurulum komutunu bulur (npx, git clone vs)."""
    tries = []
    if slug:
        tries.append(f"https://skillsllm.com/skill/{slug}")
    tries.append(f"https://raw.githubusercontent.com/{repo}/main/SKILL.md")
    tries.append(f"https://raw.githubusercontent.com/{repo}/main/README.md")
    for url in tries:
        try:
            resp = httpx.get(url, timeout=20, follow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                continue
            text = resp.text
            # ``` bash/code bloklari icinde npx/git clone/curl komutu ara
            for m in re.finditer(r'```(?:bash|sh|shell|console)?\s*\n([\s\S]{0,600}?)```', text):
                block = m.group(1)
                for line in block.splitlines():
                    line = line.strip()
                    if re.match(r'^(npx|npm|git clone|curl|pip install|uv tool|brew install)', line):
                        return line
            # duz satirlarda da ara
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("npx ") or line.startswith("git clone https://github.com/" + repo):
                    return line
        except Exception:
            continue
    return f"git clone https://github.com/{repo}.git"


@app.post("/api/skills/hunt")
async def skills_hunt(req: SkillHuntRequest):
    """skillsllm.com + GitHub uzerinden skill arastirir, en iyi adaylari puanlar."""
    query = (req.query or "").strip()
    source = (req.source or "both").strip()
    if not query:
        return {"success": False, "error": "arama metni gerekli"}
    try:
        llm_candidates = []
        gh_candidates = []
        if source in ("both", "skillsllm"):
            llm_candidates = _hunt_skillsllm(query)
        if source in ("both", "github"):
            gh_candidates = _hunt_github(query)

        seen = set()
        merged = []
        for c in llm_candidates + gh_candidates:
            if c["repo"].lower() in seen:
                continue
            seen.add(c["repo"].lower())
            merged.append(c)

        # Puanla: yildiz + konu eslesmesi
        qw = [w for w in re.split(r"\W+", query.lower()) if len(w) >= 2]
        for c in merged:
            repo_l = c["repo"].lower()
            c["score"] = int(min(int(c.get("stars") or 0), 5000) / 50)
            c["keywords_hit"] = sum(1 for w in qw if w in repo_l)
            c["score"] += c["keywords_hit"] * 10
            c["score"] = min(c["score"], 100)

        merged.sort(key=lambda c: (c["score"], c.get("stars") or 0), reverse=True)
        top = merged[:8]

        for c in top:
            slug = c.get("slug", "")
            if not slug:
                slug = c["repo"].split("/")[-1]
                c["slug"] = slug
            c["install_command"] = _skill_install_command(c["repo"], slug)
            c["zip_url"] = f"https://github.com/{c['repo']}/archive/refs/heads/main.zip"

        return {"success": True, "query": query, "candidates": top}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/skills/install")
async def skills_install(req: SkillInstallRequest):
    """Verilen kurulum komutunu GlassesCat'in kendi terminalinde calistirir."""
    command = (req.command or "").strip()
    if not command:
        return {"success": False, "error": "komut gerekli"}
    if not re.match(r"^(git clone|npx\s|npm\s)", command):
        return {"success": False, "error": "Sadece 'git clone', 'npx' veya 'npm' komutlari calistirilabilir"}
    workdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded_skills")
    os.makedirs(workdir, exist_ok=True)
    try:
        import subprocess
        proc = subprocess.run(
            command, shell=True, cwd=workdir, capture_output=True, text=True,
            timeout=600, encoding="utf-8", errors="replace",
        )
        output = (proc.stdout or "")[-4000:]
        if proc.returncode != 0:
            return {"success": False, "error": (proc.stderr or output)[-2000:], "output": output}
        return {"success": True, "output": output, "workdir": workdir}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Komut 10 dakikada bitmedi"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def fallback_element_css(selector, instruction):
    """AI motoru yanit veremediginde kelime -> CSS kurali uretir"""
    l = instruction.lower()
    props = []
    colors = {
        "mor": "#7c3aed", "turuncu": "#ff6a00", "kirmizi": "#e11d48", "kırmızı": "#e11d48",
        "mavi": "#2563eb", "yesil": "#16a34a", "yeşil": "#16a34a", "siyah": "#111111",
        "beyaz": "#ffffff", "sari": "#eab308", "sarı": "#eab308", "pembe": "#ec4899"
    }
    for k, v in colors.items():
        if k in l:
            props.append(f"color: {v}")
            break
    if "büyüt" in l or "buyut" in l or "büyük" in l or "buyuk" in l or "artır" in l or "artir" in l:
        props.append("font-size: 2.2rem")
    if "küçült" in l or "kucult" in l or "küçük" in l or "kucuk" in l or "azalt" in l:
        props.append("font-size: 0.9rem")
    if "ortala" in l or "center" in l:
        props.append("text-align: center")
    if "kalın" in l or "kalin" in l or "bold" in l:
        props.append("font-weight: 700")
    if "gölge" in l or "golge" in l or "shadow" in l:
        props.append("box-shadow: 0 8px 24px rgba(0,0,0,0.15)")
    if "yuvarla" in l or "köşe" in l or "kose" in l or "radius" in l:
        props.append("border-radius: 12px")
    if "arkaplan" in l or "arka plan" in l or "background" in l or "zemin" in l:
        props.append("background-color: #f3e8ff")
    if not props:
        props.append("color: #7c3aed")
    return f"{selector} {{ {'; '.join(props)}; }}"


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
# SWARM SUBAGENT — Paralel Alt Ajan Sistemi
# ═══════════════════════════════════════════════════════════════

class SwarmRequest(BaseModel):
    message: str

@app.post("/api/swarm")
async def swarm_execute(request: SwarmRequest):
    """Swarm Agent — mesajı alt görevlere böl, paralel çalıştır, birleştir"""
    try:
        msg = request.message
        subtask_status = [
            {"name": "web_search", "label": "Web'de ara", "icon": "🌐", "status": "running"},
            {"name": "memory_search", "label": "Hafızada ara", "icon": "📚", "status": "running"},
            {"name": "ai_analyze", "label": "AI analiz", "icon": "🤖", "status": "running"},
            {"name": "code_gen", "label": "Kod üretimi", "icon": "💻", "status": "running"},
            {"name": "skill_matcher", "label": "Skill eşleştirme", "icon": "🎯", "status": "running"},
            {"name": "translate", "label": "Çeviri", "icon": "🌍", "status": "running"},
        ]

        # 6 alt ajanı paralel çalıştır
        web_task = _swarm_web_search(msg)
        memory_task = _swarm_memory_search(msg)
        ai_task = _swarm_ai_analyze(msg)
        code_task = _swarm_code_gen(msg)
        skill_task = _swarm_skill_matcher(msg)
        translate_task = _swarm_translate(msg)

        web_result, memory_result, ai_result, code_result, skill_result, translate_result = await asyncio.gather(
            web_task, memory_task, ai_task, code_task, skill_task, translate_task, return_exceptions=True
        )

        # Hataları temizle
        def clean(r):
            return "" if isinstance(r, Exception) else (r or "")
        web_result = clean(web_result)
        memory_result = clean(memory_result)
        ai_result = clean(ai_result)
        code_result = clean(code_result)
        skill_result = clean(skill_result)
        translate_result = clean(translate_result)

        # Subtask durumlarını güncelle
        for s in subtask_status:
            s["status"] = "done"

        # Birleştir
        combined = _swarm_combine(msg, web_result, memory_result, ai_result, code_result, skill_result, translate_result)

        # Tüm alt ajanlar boş döndüyse direkt AI'ya sor
        if not combined:
            direct = await get_ai_response(msg)
            if direct and "❌" not in direct:
                combined = (
                    f"🐝 **Swarm Agent** — Alt ajanlar veri bulamadı, direkt AI yanıtı:\n\n"
                    f"{direct}"
                )
            else:
                combined = "⚠️ Swarm Agent şu anda yanıt üretemedi. Lütfen tekrar dene."

        return {
            "success": True,
            "response": combined,
            "subtasks": subtask_status
        }
    except Exception as e:
        logger.error(f"Swarm hatası: {e}")
        return {"success": False, "error": str(e), "subtasks": []}


async def _swarm_web_search(query: str) -> str:
    """🌐 Web arama alt ajanı — DuckDuckGo üzerinden anlık bilgi toplar"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                headers={"User-Agent": "GlassesCat-Swarm/1.0"}
            )
            if resp.status_code == 200:
                data = resp.json()
                abstract = data.get("AbstractText", "") or ""
                source = data.get("AbstractSource", "") or ""
                if abstract:
                    result = abstract[:600]
                    if source:
                        result += f"\nKaynak: {source}"
                    return result
                # Fallback: İlgili başlıklar
                topics = data.get("RelatedTopics", [])
                if topics:
                    lines = []
                    for t in topics[:3]:
                        if isinstance(t, dict):
                            text = t.get("Text", "") or t.get("Result", "") or ""
                            if text:
                                lines.append(text[:200])
                    if lines:
                        return "\n".join(lines)
    except Exception as e:
        logger.warning(f"Swarm web_search hatası: {e}")
    return ""


async def _swarm_memory_search(query: str) -> str:
    """📚 Hafıza arama alt ajanı — Obsidian'dan ilgili bilgileri getirir"""
    if not CORE_AVAILABLE:
        return ""
    try:
        core = get_core()
        if core.memory:
            results = core.memory.recall(query, max_results=5)
            if results:
                parts = []
                seen = set()
                for r in results:
                    path = r.get("path", "")
                    if path in seen:
                        continue
                    seen.add(path)
                    preview = r.get("content_preview", "")[:200].replace("\n", " ").strip()
                    mtype = r.get("type", "not")
                    parts.append(f"{'📄' if mtype != 'konusma' else '💬'} {preview}")
                if parts:
                    return "\n".join(parts[:3])
    except Exception as e:
        logger.warning(f"Swarm memory_search hatası: {e}")
    return ""


async def _swarm_ai_analyze(query: str) -> str:
    """🤖 AI analiz alt ajanı — mesajı derinlemesine analiz eder"""
    try:
        analysis_prompt = (
            f"Kullanıcı şunu dedi: \"{query}\"\n\n"
            "Bunu analiz et:\n"
            "1. Bu ne tür bir istek/soru?\n"
            "2. Hangi alt başlıkları var?\n"
            "3. Kısa bir özet çıkar (2-3 cümle)\n\n"
            "Format:\n"
            "Tür: ...\n"
            "Özet: ..."
        )
        result = await get_ai_response(analysis_prompt)
        if result and "❌" not in result:
            return result[:400]
    except Exception as e:
        logger.warning(f"Swarm ai_analyze hatası: {e}")
    return ""


async def _swarm_code_gen(query: str) -> str:
    """💻 Kod üretim alt ajanı — kod taleplerini algılar, artifact hazırlar"""
    try:
        # Kod talebi var mı kontrol et
        code_keywords = ["yaz", "kod", "kodla", "fonksiyon", "program", "script", "python", "javascript", "html", "css", "yap", "oluştur", "üret"]
        ql = query.lower()
        if not any(k in ql for k in code_keywords):
            return ""

        code_prompt = (
            f"Kullanıcı şunu istedi: \"{query}\"\n\n"
            "Sadece kod üret. Açıklama yazma. Markdown kullanma.\n"
            "Dil: python, javascript, html veya uygun olan neyse.\n"
            "Kodu ```python veya ```javascript veya ```html blokları içinde döndür."
        )
        result = await get_ai_response(code_prompt)
        if result and "❌" not in result:
            # Kod bloğu yakala
            import re
            blocks = re.findall(r'```(\w+)?\n(.*?)```', result, re.DOTALL)
            if blocks:
                parts = []
                for lang, code in blocks[:2]:
                    lang_label = lang or "text"
                    code_clean = code.strip()[:300]
                    parts.append(f"```{lang_label}\n{code_clean}\n```")
                if parts:
                    return "\n\n".join(parts)
            return result[:500]
    except Exception as e:
        logger.warning(f"Swarm code_gen hatası: {e}")
    return ""


async def _swarm_skill_matcher(query: str) -> str:
    """🎯 Skill eşleştirme alt ajanı — mesaja en uygun skill'i bulur"""
    try:
        ql = query.lower()
        # Skill kontrolü (frontend'deki BUILTIN_SKILLS ile senkron)
        skills_db = [
            ("site-builder", "🛠️", ["site", "web sitesi", "web sayfası", "arayüz", "tasarım"], "Web sitesi ve arayüz geliştirme"),
            ("tailwind-css", "🎨", ["tailwind", "responsive tasarım", "css framework"], "Utility-first CSS framework"),
            ("ui-pro-max", "✨", ["animasyon", "glassmorphism", "neon stil", "ui"], "Animasyon motorları"),
            ("ui-ux-pro-max", "🧩", ["ui/ux", "tasarım zekası", "kullanıcı deneyimi"], "Tasarım zekası"),
        ]
        matches = []
        for sid, icon, keywords, desc in skills_db:
            if any(k in ql for k in keywords):
                matches.append(f"{icon} **{sid}** — {desc}")
        if matches:
            return "Eşleşen skill'ler:\n" + "\n".join(matches[:3])
    except Exception as e:
        logger.warning(f"Swarm skill_matcher hatası: {e}")
    return ""


async def _swarm_translate(query: str) -> str:
    """🌍 Çeviri alt ajanı — dil algılar ve çeviri yapar"""
    try:
        ql = query.lower()
        # Çeviri talebi kontrolü
        translate_triggers = ["çevir", "çeviri", "translate", "ingilizce", "türkçe", "english", "turkish", "şu metni"]
        if not any(t in ql for t in translate_triggers):
            return ""

        translate_prompt = (
            f"Kullanıcı mesajı: \"{query}\"\n\n"
            "Bu bir çeviri talebi. Şunları yap:\n"
            "1. Kaynak dili ve hedef dili tespit et\n"
            "2. Çeviriyi yap\n"
            "3. Çevrilen metni döndür\n\n"
            "Format:\n"
            "Dil: kaynak → hedef\n"
            "Çeviri: ..."
        )
        result = await get_ai_response(translate_prompt)
        if result and "❌" not in result:
            return result[:400]
    except Exception as e:
        logger.warning(f"Swarm translate hatası: {e}")
    return ""


def _swarm_combine(query: str, web: str, memory: str, ai: str, code: str = "", skill: str = "", translate: str = "") -> str:
    """Alt ajan sonuçlarını birleştirip tek bir yanıt oluşturur"""
    parts = []
    has_any = False

    if code:
        has_any = True
        parts.append(f"💻 **Kod Çıktısı**\n{code}")

    if skill:
        has_any = True
        parts.append(f"🎯 **Skill Eşleşmesi**\n{skill}")

    if translate:
        has_any = True
        parts.append(f"🌍 **Çeviri**\n{translate}")

    if memory:
        has_any = True
        parts.append(f"📚 **Hafızamdan Bulduklarım**\n{memory}")

    if web:
        has_any = True
        parts.append(f"🌐 **Web'den Anlık Bilgiler**\n{web}")

    if ai:
        has_any = True
        parts.append(f"🤖 **Analizim**\n{ai}")

    if not has_any:
        return ""

    return (
        f"🐝 **Swarm Agent — Paralel İşleme Tamamlandı**\n\n"
        f"Sorgun: _{query}_\n\n"
        + "\n\n".join(parts) +
        "\n\n---\n_Tüm alt ajanlar paralel çalıştırıldı ve sonuçlar birleştirildi._"
    )


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
