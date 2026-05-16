"""
GlassesCat Web - Flask Web Uygulaması
Kivy yerine tarayıcıda çalışan versiyon
Session-based Authentication + API Keys
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from functools import wraps
import requests
import json
import os
import re
import threading
import time
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from queue import Queue, Empty

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

import sys
import os
# Ana dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tools as toolbox
from actions import launch_app, APP_MAPPINGS

from model_router import get_model_router, ModelType
from memory import get_memory, ConversationMemory

# Obsidian Sınırsız Hafıza
try:
    from obsidian_memory import get_obsidian_memory
    OBSIDIAN_MEMORY_OK = True
    _obsidian_mem = get_obsidian_memory()
except Exception as e:
    OBSIDIAN_MEMORY_OK = False

from file_ops import get_file_ops, FileOperations
from web_search import get_web_search, WebSearch
from code_sandbox import get_sandbox, CodeSandbox
from tts import get_tts, TextToSpeech
from code_agent import get_code_agent, CodeAgent
from vision import get_vision_analyzer

# Yeni Modüller (hata toleranslı)
try:
    from plugin_system import PluginManager
    PLUGIN_SYSTEM_OK = True
except Exception as e:
    print(f"[UYARI] Plugin System yüklenemedi: {e}")
    PLUGIN_SYSTEM_OK = False

try:
    from plugin_runner import MultiLanguagePluginManager
    MULTI_PLUGIN_OK = True
except Exception as e:
    print(f"[UYARI] Multi-Language Plugin yüklenemedi: {e}")
    MULTI_PLUGIN_OK = False

try:
    from skill_system import SkillManager
    SKILL_SYSTEM_OK = True
except Exception as e:
    print(f"[UYARI] Skill System yüklenemedi: {e}")
    SKILL_SYSTEM_OK = False

try:
    from rag_system import RAGEngine
    RAG_OK = True
except Exception as e:
    print(f"[UYARI] RAG System yüklenemedi: {e}")
    RAG_OK = False

try:
    from toolformer import Toolformer
    TOOLFORMER_OK = True
except Exception as e:
    print(f"[UYARI] Toolformer yüklenemedi: {e}")
    TOOLFORMER_OK = False

try:
    from task_scheduler import TaskScheduler
    TASK_SCHEDULER_OK = True
except Exception as e:
    print(f"[UYARI] Task Scheduler yüklenemedi: {e}")
    TASK_SCHEDULER_OK = False

try:
    from conversation_summarizer import ConversationSummarizer
    SUMMARIZER_OK = True
except Exception as e:
    print(f"[UYARI] Conversation Summarizer yüklenemedi: {e}")
    SUMMARIZER_OK = False

# Geliştirme modu
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
print(f"[SISTEM] DEV_MODE={DEV_MODE} {'(giriş gerektirmez)' if DEV_MODE else '(email+şifre gerekli)'}")

# URL Yapılandırması
BASE_URL = "" # Dinamik URL için boş bırakıldı

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Template değişikliklerini anında yansıt
CORS(app, supports_credentials=True) # CORS desteği eklendi
app.secret_key = "glassescat_secret_key_fixed_2024"  # Sabit key
app.permanent_session_lifetime = timedelta(days=7)  # 7 günlük oturum

# Memory instance
memory = get_memory()

# File operations instance
file_ops = get_file_ops()

# Web search instance
web_search = get_web_search()

# Code sandbox instance
sandbox = get_sandbox()

# TTS instance
tts = get_tts()

# Code agent instance
code_agent = get_code_agent()

# Vision analyzer instance
vision_analyzer = get_vision_analyzer()

# Router instance
router = get_model_router()

# Yeni modül instance'ları (hata toleranslı)
plugin_manager = None
if PLUGIN_SYSTEM_OK:
    try:
        plugin_manager = PluginManager.get_instance()
        # Pluginleri yükle (discover -> load -> enable)
        if plugin_manager:
            discovered = plugin_manager.discover_plugins()
            if discovered:
                print(f"[INFO] Pluginler kesfedildi: {discovered}")
                results = plugin_manager.load_all_plugins()
                for name, ok in results.items():
                    if ok:
                        plugin_manager.enable_plugin(name)
                        print(f"[INFO] Plugin aktif: {name}")
                    else:
                        print(f"[UYARI] Plugin yuklenemedi: {name}")
    except Exception as e:
        print(f"[UYARI] PluginManager baslatilamadi: {e}")

multi_plugin_manager = None
if MULTI_PLUGIN_OK:
    try:
        multi_plugin_manager = MultiLanguagePluginManager()
    except Exception as e:
        print(f"[UYARI] MultiPlugin baslatilamadi: {e}")

skill_manager = None
if SKILL_SYSTEM_OK:
    try:
        skill_manager = SkillManager.get_instance()
    except Exception as e:
        print(f"[UYARI] SkillManager baslatilamadi: {e}")

rag_engine = None
if RAG_OK:
    try:
        rag_engine = RAGEngine()
    except Exception as e:
        print(f"[UYARI] RAG baslatilamadi: {e}")

toolformer = None
if TOOLFORMER_OK:
    try:
        toolformer = Toolformer()
    except Exception as e:
        print(f"[UYARI] Toolformer baslatilamadi: {e}")

task_scheduler = None
if TASK_SCHEDULER_OK:
    try:
        task_scheduler = TaskScheduler()
    except Exception as e:
        print(f"[UYARI] TaskScheduler baslatilamadi: {e}")

summarizer = None
if SUMMARIZER_OK:
    try:
        summarizer = ConversationSummarizer()
    except Exception as e:
        print(f"[UYARI] Summarizer baslatilamadi: {e}")

# Tema sistemi
THEME_MAP = {
    "default": {"name": "Mavi", "css_class": ""},
    "code": {"name": "Turuncu Kod", "css_class": "theme-code"},
    "sohbet": {"name": "Mor Sohbet", "css_class": "theme-chat"},
    "analiz": {"name": "Yeşil Analiz", "css_class": "theme-analysis"},
}
current_theme = "default"

# Ollama API
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:latest")

# ==================== BEKLEME KUYRUK SİSTEMİ ====================
class RequestQueue:
    """İstek kuyruğu - bilgisayar yükünü azaltmak için"""
    def __init__(self, max_concurrent=1, rate_limit=2):  # Saniyede max 2 istek
        self.queue = Queue()
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.processing = False
        self.last_request_time = 0
        self.lock = threading.Lock()
        self.active_requests = 0
        
    def add_request(self, func, *args, **kwargs):
        """İstek kuyruğa ekle"""
        request_id = time.time()
        self.queue.put((request_id, func, args, kwargs))
        return self._process_queue()
    
    def _process_queue(self):
        """Kuyruktaki istekleri işle"""
        with self.lock:
            if self.processing or self.active_requests >= self.max_concurrent:
                return {"queued": True, "message": "⏳ Sıraya alındı, lütfen bekleyin..."}
            
            # Rate limiting kontrolü
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < (1.0 / self.rate_limit):
                wait_time = (1.0 / self.rate_limit) - time_since_last
                time.sleep(wait_time)
            
            self.processing = True
            self.active_requests += 1
            self.last_request_time = time.time()
        
        try:
            # Kuyruktan bir istek al
            try:
                request_id, func, args, kwargs = self.queue.get_nowait()
            except Empty:
                with self.lock:
                    self.processing = False
                    self.active_requests -= 1
                return None
            
            # İsteği işle
            result = func(*args, **kwargs)
            return result
            
        finally:
            with self.lock:
                self.processing = False
                self.active_requests -= 1
            # Bir sonraki isteği işle
            threading.Timer(0.5, self._process_next).start()
    
    def _process_next(self):
        """Bir sonraki isteği işle"""
        if not self.queue.empty():
            self._process_queue()

# Global kuyruk instance'ı
request_queue = RequestQueue(max_concurrent=1, rate_limit=0.5)  # 2 istek/saniye

def rate_limited(f):
    """Decorator - fonksiyonu kuyruğa al"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Kuyruğa ekle ve sonucu bekle
        result = request_queue.add_request(f, *args, **kwargs)
        if result and isinstance(result, dict) and result.get('queued'):
            return jsonify(result)
        return result
    return decorated

# ==================== Kali SSH Manager ====================
class KaliSSHManager:
    def __init__(self):
        self.ssh_client = None
        self.connected = False
        self.hostname = None
        self.username = None
        
    def connect(self, hostname, username, password=None, port=22):
        if not PARAMIKO_AVAILABLE:
            return {"error": "Paramiko yüklenmemiş"}
        
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(hostname, port=port, username=username, password=password, timeout=10)
            self.connected = True
            self.hostname = hostname
            self.username = username
            return {"success": True, "message": f"Kali ({hostname}) bağlandı"}
        except Exception as e:
            return {"error": str(e)}
    
    def disconnect(self):
        if self.ssh_client:
            self.ssh_client.close()
            self.connected = False
        return {"message": "Bağlantı kapatıldı"}
    
    def execute_command(self, command, timeout=60):
        """SSH komutu çalıştır"""
        if not self.connected:
            return {"error": "Bağlı değil"}
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            exit_code = stdout.channel.recv_exit_status()
            
            if len(output) > 50000:
                output = output[:50000] + "\n... (çıktı çok büyük, kısaltıldı)"
            
            return {
                "command": command,
                "output": output,
                "error": error if error else None,
                "exit_code": exit_code
            }
        except Exception as e:
            return {"error": str(e)}

# Global Kali manager
kali_manager = KaliSSHManager()

# Chat History Storage
chat_history = []

# ==================== İSTEK LOGLAMA & GÜVENLİK ====================
# API isteklerini logla
request_logs = []
MAX_LOGS = 100  # Son 100 isteği tut

# Admin şifresi (gerçek uygulamada environment variable'dan alınmalı)
ADMIN_PASSWORD = "glasses_admin_2024"

def log_request(endpoint, data, ip_address, status="success", error=None):
    """API isteğini logla"""
    import datetime
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "endpoint": endpoint,
        "data": data.get('message', '')[:100] if isinstance(data, dict) else str(data)[:100],
        "ip": ip_address,
        "status": status,
        "error": error
    }
    request_logs.append(log_entry)
    # Sadece son 100 isteği tut
    if len(request_logs) > MAX_LOGS:
        request_logs.pop(0)

def require_admin(f):
    """Admin yetkisi gerektiren endpoint decorator (Header veya Session bazlı)
    
    Geliştirici modunda giriş yapan kullanıcılar da admin API'lerine erişebilir.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Önce header ile kontrol et
        auth_header = request.headers.get('X-Admin-Password')
        if auth_header == ADMIN_PASSWORD:
            return f(*args, **kwargs)
        
        # Geliştirici modu kontrolü (session-based)
        if session.get('is_dev') and request.remote_addr in ['127.0.0.1', 'localhost', '::1']:
            return f(*args, **kwargs)
        
        # Admin modu kontrolü (session-based)
        if session.get('is_admin'):
            return f(*args, **kwargs)
        
        return jsonify({"error": "Yetkisiz erişim", "message": "Admin şifresi veya yetkili oturum gerekli"}), 403
    return decorated

def require_admin_session(f):
    """Admin yetkisi gerektiren sayfa decorator (Session bazlı)
    
    Geliştirici modunda giriş yapan kullanıcılar da admin paneline erişebilir.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Admin veya geliştirici modunda giriş yapılmış mı kontrol et
        is_admin = session.get('is_admin', False)
        is_dev = session.get('is_dev', False)
        
        if not is_admin and not is_dev:
            # Admin şifresini sorgulayan login sayfasına yönlendir
            return render_template('admin_login.html')
        
        # Geliştirici modu bilgisini request'e ekle
        request.is_developer_mode = is_dev
        
        return f(*args, **kwargs)
    return decorated

# IP tabanlı deneme sınırlama
failed_ips = {} # {ip: {count, last_attempt}}
BLOCK_TIMEOUT = 300 # 5 dakika

def check_brute_force():
    """IP üzerinden brute-force kontrolü"""
    ip = request.remote_addr
    if ip in failed_ips:
        data = failed_ips[ip]
        if data['count'] >= 5:
            now = time.time()
            if now - data['last_attempt'] < BLOCK_TIMEOUT:
                return False, int(BLOCK_TIMEOUT - (now - data['last_attempt']))
    return True, 0

def record_failed_attempt():
    """Hatalı denemeyi kaydet"""
    ip = request.remote_addr
    now = time.time()
    if ip not in failed_ips:
        failed_ips[ip] = {'count': 0, 'last_attempt': 0}
    failed_ips[ip]['count'] += 1
    failed_ips[ip]['last_attempt'] = now

def reset_failed_attempts():
    """Başarılı girişte IP sayacını sıfırla"""
    ip = request.remote_addr
    if ip in failed_ips:
        del failed_ips[ip]

# ==================== KULLANICI YÖNETİMİ ====================
# Basit kullanıcı yönetimi (gerçek uygulamada database kullanılmalı)
users = {}  # {username: {email, password_hash, created_at, last_login, access_key, failed_attempts, lock_until}}

# Geçerli Beta Erişim Anahtarları
valid_keys = {}  # {key_code: {created_at, created_by, is_active, description, used_by}}

# Kullanıcı mesajları kaydı
user_messages = []
MAX_USER_MESSAGES = 500

def log_user_message(username, message, msg_type="text", response=None):
    """Kullanıcı mesajını kaydet (admin panelinde görüntülemek için)"""
    import datetime
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "username": username or "Misafir",
        "message": message[:500],  # Mesajı kısalt
        "type": msg_type,
        "response": (response[:200] + "...") if response and len(response) > 200 else response
    }
    user_messages.append(log_entry)
    # Limiti aşarsa eski mesajları sil
    if len(user_messages) > MAX_USER_MESSAGES:
        user_messages.pop(0)

def is_ip_blocked(ip):
    """IP engelli mi kontrol et"""
    # Basit bir IP engelleme mantığı buraya eklenebilir
    return False

def hash_password(password):
    """Basit şifre hash'leme"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

# ==================== SESSION / LOGIN DECORATOR ====================
def login_required(f):
    """Giriş gerektiren sayfa decorator - Basit İsim + Beta Key sistemi"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Basit sistem: user_name ve beta_key kontrolü
        if 'user_name' not in session:
            # API isteği mi yoksa sayfa isteği mi kontrol et
            if request.path.startswith('/api/') or request.path == '/chat':
                return jsonify({"error": "Oturum gerekli", "authenticated": False}), 401
            return redirect('/')
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    """Şu anki giriş yapmış kullanıcıyı getir"""
    username = session.get('username')
    if username and username in users:
        return {"username": username, **users[username]}
    return None

def is_logged_in():
    """Kullanıcı giriş yapmış mı?"""
    return 'username' in session

# ==================== API ANAHTARI SİSTEMİ ====================
# Her kullanıcının kendi API key'leri
user_api_keys = {}  # {username: [{key, name, created_at, last_used}]}

def generate_user_api_key(username, key_name=""):
    """Kullanıcı için yeni API key oluştur"""
    api_key = f"gc_{secrets.token_urlsafe(32)}"
    if username not in user_api_keys:
        user_api_keys[username] = []
    
    user_api_keys[username].append({
        "key": api_key,
        "name": key_name or f"Key {len(user_api_keys[username]) + 1}",
        "created_at": datetime.now().isoformat(),
        "last_used": None,
        "is_active": True
    })
    return api_key

def validate_user_api_key(api_key):
    """API key'i doğrula ve kullanıcıyı döndür"""
    for username, keys in user_api_keys.items():
        for key_data in keys:
            if key_data["key"] == api_key and key_data["is_active"]:
                key_data["last_used"] = datetime.now().isoformat()
                return username
    return None

# ==================== ADMIN YÖNETİMİ ====================

# Eski access_keys yapısını valid_keys ile birleştiriyoruz
access_keys = valid_keys 

def generate_access_key(length=16):
    """Rastgele erişim kodu oluştur"""
    import secrets
    import string
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))

@app.route('/admin/keys/create', methods=['POST'])
@require_admin
def create_key():
    """Yeni erişim kodu oluştur"""
    import datetime
    data = request.json
    description = data.get('description', '').strip() or "Genel Kullanıcı"
    
    # Yeni key oluştur
    new_key = generate_access_key()
    while new_key in valid_keys:  # Benzersiz olmalı
        new_key = generate_access_key()
    
    valid_keys[new_key] = {
        "created_at": datetime.datetime.now().isoformat(),
        "created_by": "admin",
        "used_by": None,
        "is_active": True,
        "description": description
    }
    
    return jsonify({
        "success": True,
        "key": new_key,
        "message": f"✅ Yeni Beta Key oluşturuldu: {new_key}"
    })

@app.route('/admin/keys', methods=['GET'])
@require_admin
def list_keys():
    """Tüm geçerli Beta Key'leri listele"""
    return jsonify({
        "success": True,
        "keys": [
            {"key": k, **v} for k, v in valid_keys.items()
        ]
    })

@app.route('/admin/keys/delete', methods=['POST'])
@require_admin
def delete_key():
    """Erişim kodunu sil"""
    data = request.json
    key = data.get('key', '').strip().upper()
    
    if key not in valid_keys:
        return jsonify({"error": "Kod bulunamadı"}), 404
    
    del valid_keys[key]
    return jsonify({
        "success": True,
        "message": f"🗑️ Beta Key silindi: {key}"
    })

@app.route('/admin/keys/toggle', methods=['POST'])
@require_admin
def toggle_key():
    """Erişim kodunu aktif/pasif yap"""
    data = request.json
    key = data.get('key', '').strip().upper()
    
    if key not in valid_keys:
        return jsonify({"error": "Kod bulunamadı"}), 404
    
    valid_keys[key]["is_active"] = not valid_keys[key]["is_active"]
    status = "aktif" if valid_keys[key]["is_active"] else "pasif"
    
    return jsonify({
        "success": True,
        "message": f"🔑 Beta Key {status} yapıldı: {key}",
        "is_active": valid_keys[key]["is_active"]
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Kullanıcı kaydı - Ad + E-posta + Şifre"""
    if DEV_MODE:
        return jsonify({"success": False, "error": "Dev modda kayıt gerekmez, direkt giriş yapabilirsiniz."}), 400

    allowed, wait_time = check_brute_force()
    if not allowed:
        return jsonify({"success": False, "error": f"Çok fazla deneme! {wait_time} saniye bekleyin."}), 429

    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not name or not email or not password:
        record_failed_attempt()
        return jsonify({"success": False, "error": "Ad, e-posta ve şifre gerekli!"}), 400
    
    if len(name) < 2:
        return jsonify({"success": False, "error": "Ad en az 2 karakter olmalı!"}), 400
    
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return jsonify({"success": False, "error": "Geçersiz e-posta formatı!"}), 400
    
    if len(password) < 6:
        return jsonify({"success": False, "error": "Şifre en az 6 karakter olmalı!"}), 400
    
    if email in users:
        return jsonify({"success": False, "error": "Bu e-posta zaten kayıtlı!"}), 409
    
    users[email] = {
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "failed_attempts": 0,
        "lock_until": None,
        "is_active": True,
        "login_history": []
    }
    
    reset_failed_attempts()
    session['user_email'] = email
    session['user_name'] = name
    session['login_time'] = datetime.now().isoformat()
    session.permanent = True
    
    return jsonify({
        "success": True,
        "message": f"🎉 Hoş geldin {name}! Kaydın başarılı.",
        "name": name,
        "email": email,
        "redirect": "/"
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Kullanıcı girişi - E-posta + Şifre (beta key gerekmez)"""
    if DEV_MODE:
        # Dev modda her email+şifre kabul edilir
        data = request.json
        name = data.get('email', '').split('@')[0]
        session['user_email'] = data.get('email', '')
        session['user_name'] = name
        session['login_time'] = datetime.now().isoformat()
        session.permanent = True
        return jsonify({"success": True, "message": f"🎉 Hoş geldin {name}!", "name": name, "redirect": "/"})
    
    allowed, wait_time = check_brute_force()
    if not allowed:
        return jsonify({"success": False, "error": f"Çok fazla deneme! {wait_time} saniye bekleyin."}), 429

    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    remember = data.get('remember', False)
    
    if not email or not password:
        record_failed_attempt()
        return jsonify({"success": False, "error": "Email ve şifre gerekli!"}), 400
    
    user_data = users.get(email)
    if not user_data:
        record_failed_attempt()
        return jsonify({"success": False, "error": "Kullanıcı bulunamadı!"}), 404
    
    if user_data.get("password_hash") != hash_password(password):
        record_failed_attempt()
        user_data["failed_attempts"] = user_data.get("failed_attempts", 0) + 1
        if user_data["failed_attempts"] >= 3:
            user_data["lock_until"] = (datetime.now() + timedelta(minutes=5)).isoformat()
            user_data["failed_attempts"] = 0
            return jsonify({"success": False, "error": "3 kez hatalı deneme! 5 dakika bekleyin."}), 403
        return jsonify({"success": False, "error": "Hatalı şifre!"}), 401
    
    reset_failed_attempts()
    user_data["failed_attempts"] = 0
    user_data["lock_until"] = None
    user_data["last_login"] = datetime.now().isoformat()
    
    session.permanent = remember
    session['user_email'] = email
    session['user_name'] = user_data.get("name", email.split('@')[0])
    session['login_time'] = datetime.now().isoformat()
    
    return jsonify({
        "success": True,
        "message": f"🎉 Hoş geldin {user_data.get('name', email.split('@')[0])}!",
        "name": user_data.get("name", email.split('@')[0]),
        "email": email,
        "redirect": "/"
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Profesyonel çıkış - Session temizle ve güvenli yönlendirme"""
    user_name = session.get('user_name', 'Bilinmeyen')
    
    # Session temizle
    session.clear()
    
    # CSRF token için yeni session başlat (güvenlik)
    session.permanent = False
    
    return jsonify({
        "success": True,
        "message": f"👋 {user_name} başarıyla çıkış yaptı.",
        "redirect": "/"
    })


@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Mevcut kullanıcı bilgilerini getir - Session kontrolü"""
    if 'user_email' not in session:
        return jsonify({
            "success": True,
            "authenticated": False
        }), 200
    
    email = session.get('user_email')
    user_data = users.get(email)
    
    if not user_data:
        session.clear()
        return jsonify({
            "success": False,
            "authenticated": False,
            "error": "Kullanıcı bulunamadı!"
        }), 404
    
    return jsonify({
        "success": True,
        "authenticated": True,
        "name": user_data.get('name'),
        "email": email,
        "last_login": user_data.get('last_login'),
        "created_at": user_data.get('created_at')
    })


# ==================== GELİŞTİRİCİ MODU ====================
DEV_MODE_KEY = "GLASSES-DEV-2024"  # Geliştirici anahtarı

@app.route('/api/auth/dev-login', methods=['POST'])
def dev_login():
    """Geliştirici modu - Beta Key gerektirmeden hızlı giriş"""
    # Sadece localhost'tan erişime izin ver
    if request.remote_addr not in ['127.0.0.1', 'localhost', '::1']:
        return jsonify({
            "success": False,
            "error": "🚫 Geliştirici modu sadece localhost'tan erişilebilir!"
        }), 403
    
    data = request.json
    dev_key = data.get('dev_key', '').strip()
    name = data.get('name', 'Geliştirici').strip()
    
    if not dev_key:
        return jsonify({
            "success": False,
            "error": "❌ Geliştirici anahtarı gerekli!"
        }), 400
    
    if dev_key != DEV_MODE_KEY:
        return jsonify({
            "success": False,
            "error": "❌ Geçersiz geliştirici anahtarı!"
        }), 401
    
    import datetime
    
    # Geliştirici hesabı oluştur (varsa kullan)
    dev_email = f"dev_{int(datetime.datetime.now().timestamp())}@localhost"
    
    users[dev_email] = {
        "name": name,
        "email": dev_email,
        "password_hash": hash_password("dev_pass_" + dev_key),
        "beta_key": "DEV-MODE",
        "created_at": datetime.datetime.now().isoformat(),
        "last_login": datetime.datetime.now().isoformat(),
        "failed_attempts": 0,
        "lock_until": None,
        "is_active": True,
        "is_dev": True,
        "login_history": []
    }
    
    # Session oluştur
    session.permanent = True
    session['user_email'] = dev_email
    session['user_name'] = name
    session['is_dev'] = True
    session['login_time'] = datetime.datetime.now().isoformat()
    
    return jsonify({
        "success": True,
        "message": f"👨‍💻 Geliştirici modu aktif! Hoş geldin {name}!",
        "name": name,
        "email": dev_email,
        "mode": "developer",
        "redirect": "/"
    })

# ==================== KULLANICI API KEY ENDPOINT'LERİ ====================
@app.route('/api/user/keys', methods=['GET'])
@login_required
def get_user_keys():
    """Kullanıcının API key'lerini listele"""
    username = session.get('username')
    keys = user_api_keys.get(username, [])
    return jsonify({
        "success": True,
        "keys": [{"name": k["name"], "created_at": k["created_at"], 
                  "is_active": k["is_active"], "last_used": k.get("last_used")} 
                 for k in keys],
        "active_count": len([k for k in keys if k["is_active"]])
    })

@app.route('/api/user/keys/create', methods=['POST'])
@login_required
def create_user_key():
    """Yeni API key oluştur"""
    username = session.get('username')
    data = request.json or {}
    key_name = data.get('name', '').strip()
    
    new_key = generate_user_api_key(username, key_name or "Yeni Key")
    
    return jsonify({
        "success": True,
        "message": "✅ Yeni API key oluşturuldu!",
        "key": new_key,
        "warning": "Bu key'i güvenli bir yerde saklayın! Bir daha gösterilmeyecek."
    })

@app.route('/api/user/keys/revoke', methods=['POST'])
@login_required
def revoke_user_key():
    """API key'i iptal et"""
    username = session.get('username')
    data = request.json or {}
    key_name = data.get('name', '').strip()
    
    if username not in user_api_keys:
        return jsonify({"error": "API key bulunamadı"}), 404
    
    for key_data in user_api_keys[username]:
        if key_data["name"] == key_name:
            key_data["is_active"] = False
            return jsonify({
                "success": True,
                "message": f"✅ '{key_name}' API key iptal edildi."
            })
    
    return jsonify({"error": "Key bulunamadı"}), 404

@app.route('/stride-ide')
def stride_ide():
    """GlassesCat STRIDE IDE - Web Tabanlı Oyun Geliştirme"""
    if 'user_name' not in session:
        return redirect('/')
    try:
        return render_template('stride_ide.html', user_name=session.get('user_name'))
    except Exception as e:
        print(f"[ERROR] stride_ide.html render hatası: {str(e)}")
        return f"Template Hatası: {str(e)}", 500

@app.route('/api/stride/generate', methods=['POST'])
@login_required
def stride_generate():
    """Stride için component/system dosyaları oluştur"""
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from stride_auto_gen import StrideFileDetector
        
        data = request.json
        command = data.get('command', '')
        
        detector = StrideFileDetector()
        result = detector.auto_generate(command)
        
        return jsonify({
            "success": True,
            "created": result,
            "message": f"{len(result['components'])} component, {len(result['systems'])} system oluşturuldu"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/stride/detect', methods=['POST'])
@login_required
def stride_detect():
    """Mevcut koddan eksik dosyaları tespit et"""
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from stride_auto_gen import StrideFileDetector
        
        detector = StrideFileDetector()
        result = detector.auto_detect_and_generate()
        
        return jsonify({
            "success": True,
            "created": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/')
def index():
    """Ana sayfa - Dev modda direkt chat, normal modda login"""
    if DEV_MODE:
        if 'user_name' not in session:
            session['user_name'] = 'Admin'
            session['is_dev'] = True
            session.permanent = True
        try:
            return render_template('index.html', user_name=session.get('user_name', 'Admin'))
        except Exception as e:
            print(f"[ERROR] index.html render hatası: {str(e)}")
            return f"Template Hatası: {str(e)}", 500
    
    if 'user_name' in session:
        try:
            return render_template('index.html', user_name=session.get('user_name'))
        except Exception as e:
            return f"Template Hatası: {str(e)}", 500
    
    try:
        return render_template('simple_login.html')
    except Exception as e:
        return f"Template Hatası: {str(e)}", 500

@app.route('/login')
def login_page():
    """Eski login rotası artık ana sayfaya yönlendiriyor"""
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard_page():
    """Eski dashboard rotası artık ana sayfaya yönlendiriyor"""
    return redirect(url_for('index'))

@app.route('/admin')
@require_admin_session
def admin_panel():
    """Admin paneli HTML sayfası - Oturum kontrollü"""
    return render_template('admin.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin girişi"""
    data = request.json
    password = data.get('password', '').strip()
    if password == ADMIN_PASSWORD:
        session['is_admin'] = True
        return jsonify({"success": True, "message": "Admin girişi başarılı!"})
    return jsonify({"success": False, "error": "Geçersiz şifre!"}), 401

@app.route('/admin/password', methods=['POST'])
@require_admin
def change_admin_password():
    """Admin şifresini değiştir"""
    global ADMIN_PASSWORD
    data = request.json
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()

    # Mevcut şifreyi kontrol et
    if current_password != ADMIN_PASSWORD:
        return jsonify({"error": "Mevcut şifre yanlış"}), 401

    # Yeni şifre kontrolü
    if not new_password:
        return jsonify({"error": "Yeni şifre boş olamaz"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Şifre en az 6 karakter olmalı"}), 400

    # Şifreyi güncelle
    ADMIN_PASSWORD = new_password

    return jsonify({
        "success": True,
        "message": "✅ Admin şifresi başarıyla değiştirildi!"
    })



@app.route('/admin/logs/api', methods=['GET'])
@require_admin
def get_api_logs():
    """Son istek loglarını getir"""
    return jsonify({
        "logs": request_logs,
        "total": len(request_logs),
        "max_logs": MAX_LOGS
    })

@app.route('/admin/stats', methods=['GET'])
@require_admin
def get_stats():
    """API istatistiklerini getir"""
    import datetime
    from collections import Counter
    
    if not request_logs:
        return jsonify({"message": "Henüz log yok"})
    
    # İstatistikleri hesapla
    endpoints = Counter([log["endpoint"] for log in request_logs])
    statuses = Counter([log["status"] for log in request_logs])
    
    # Son 24 saatteki istekler
    now = datetime.datetime.now()
    last_24h = [log for log in request_logs 
                if (now - datetime.datetime.fromisoformat(log["timestamp"])).days < 1]
    
    return jsonify({
        "total_requests": len(request_logs),
        "requests_24h": len(last_24h),
        "endpoints": dict(endpoints),
        "statuses": dict(statuses),
        "unique_ips": len(set(log["ip"] for log in request_logs))
    })

@app.route('/admin/logs/clear', methods=['POST'])
@require_admin
def clear_logs():
    """Logları temizle"""
    global request_logs
    request_logs = []
    return jsonify({"message": "Loglar temizlendi"})

@app.route('/admin/queue', methods=['GET'])
@require_admin
def get_queue_status():
    """Kuyruk durumunu getir"""
    return jsonify({
        "queue_size": request_queue.queue.qsize(),
        "processing": request_queue.processing,
        "active_requests": request_queue.active_requests,
        "rate_limit": request_queue.rate_limit
    })

@app.route('/api/users', methods=['GET'])
@require_admin
def get_users():
    """Tüm kullanıcıları listele (admin only)"""
    return jsonify({
        "users": [
            {
                "username": u, 
                "email": d.get("email", "Belirtilmemiş"),
                "created_at": d["created_at"], 
                "last_login": d["last_login"],
                "access_key": d.get("access_key", "Bilinmiyor")
            }
            for u, d in users.items()
        ],
        "total": len(users)
    })

@app.route('/admin/messages', methods=['GET'])
@require_admin
def get_user_messages():
    """Kullanıcı mesajlarını getir (sıralama ve filtreleme ile)"""
    sort_by = request.args.get('sort', 'newest')  # newest, oldest, username, type
    username_filter = request.args.get('user', '').strip().lower()
    type_filter = request.args.get('type', '').strip().lower()
    limit = int(request.args.get('limit', 100))
    
    # Filtrele
    filtered = user_messages
    if username_filter:
        filtered = [m for m in filtered if username_filter in m['username'].lower()]
    if type_filter:
        filtered = [m for m in filtered if m['type'] == type_filter]
    
    # Sırala
    if sort_by == 'newest':
        filtered = sorted(filtered, key=lambda x: x['timestamp'], reverse=True)
    elif sort_by == 'oldest':
        filtered = sorted(filtered, key=lambda x: x['timestamp'])
    elif sort_by == 'username':
        filtered = sorted(filtered, key=lambda x: x['username'].lower())
    elif sort_by == 'type':
        filtered = sorted(filtered, key=lambda x: x['type'])
    
    # Limit uygula
    filtered = filtered[:limit]
    
    return jsonify({
        "messages": filtered,
        "total": len(user_messages),
        "filtered": len(filtered),
        "sort_by": sort_by
    })

@app.route('/admin/messages/clear', methods=['POST'])
@require_admin
def clear_user_messages():
    """Kullanıcı mesajlarını temizle"""
    global user_messages
    count = len(user_messages)
    user_messages = []
    return jsonify({
        "message": f"{count} mesaj silindi",
        "cleared": count
    })

@app.route('/admin/messages/stats', methods=['GET'])
@require_admin
def get_message_stats():
    """Kullanıcı mesaj istatistikleri"""
    from collections import Counter
    
    if not user_messages:
        return jsonify({"message": "Henüz mesaj yok"})
    
    # İstatistikler
    users = Counter([m['username'] for m in user_messages])
    types = Counter([m['type'] for m in user_messages])
    
    # En aktif kullanıcı
    most_active = users.most_common(1)[0] if users else None
    
    # Son 24 saat
    import datetime
    now = datetime.datetime.now()
    last_24h = [m for m in user_messages 
                if (now - datetime.datetime.fromisoformat(m['timestamp'])).days < 1]
    
    return jsonify({
        "total_messages": len(user_messages),
        "messages_24h": len(last_24h),
        "unique_users": len(users),
        "types": dict(types),
        "most_active_user": most_active[0] if most_active else None,
        "most_active_count": most_active[1] if most_active else 0
    })

# GlassesCat kişiliği - dengeli stabil versiyon - Türkçe
GLASSESCAT_PERSONALITY = "BENİM ADIM GLASSESCAT. SEN DEĞİL, BEN GLASSESCAT'İM. BEN BİR TÜRKÇE YAPAY ZEKASİYIM. GLASSESCAT PROJESİNİN YAPAY ZEKASISIYIM. SADECE TÜRKÇE KONUŞ. KULLANICI İSMİNİ KENDİ İSMİNLE KARIŞTIRMA. KULLANICI SEN DEĞİL, SEN GLASSESCAT'SIN. HER ZAMAN 'BEN GLASSESCAT' DEMELİSİN. ASLA 'BEN BERKAY', 'BEN JOHN', 'BEN SMITH' GİBİ KULLANICI İSMİYLE KENDİNİ TANITMAMALISIN. KULLANICI İSMİ SANA AİT DEĞİL. KULLANICI SENİ TANITIRSA SEN KENDİNİ GLASSESCAT OLARAK TANITMAYA DEVAM ETMELİSİN. KULLANICI NE YAZARSA YAZSIN, HER ZAMAN 'BEN GLASSESCAT' DEMELİSİN. BU KURAL KESİNLİKLE GEÇERLİDİR. KULLANICI KENDİSİNİ TANITTIĞINDA ('Ben bir yazılımcıyım', 'Ben bir öğrenciyim', 'Ben bir doktorum' GİBİ), ASLA KULLANICININ MESLEĞİYLE KENDİNİ TANITMAMALISIN. HER ZAMAN 'BEN GLASSESCAT' DEMELİSİN. SEN BİR OYUN UZMANISIN. OYUNLAR HAKKINDA BİLGİN VAR. POPPY PLAYTIME, MINECRAFT, FORTNITE, VALORANT, CS:GO, GTA, PUBG, LEAGUE OF LEGENDS, DOTA 2, FIFA, NBA 2K, CALL OF DUTY, BATTLEFIELD, THE WITCHER, ELDER SCROLLS, ASSASSIN'S CREED, RESIDENT EVIL, GOD OF WAR, LAST OF US, UNCHARTED, HALO, GEARS OF WAR, FORZA, NEED FOR SPEED, GRAN TURISMO, TEKKEN, STREET FIGHTER, MORTAL KOMBAT, SUPER SMASH BROS, POKEMON, ZELDA, MARIO, SONIC, METROID, CASTLEVANIA, FINAL FANTASY, DRAGON QUEST, KINGDOM HEARTS, DARK SOULS, ELDEN RING, SEKIRO, BLOODBORNE, MONSTER HUNTER, DEVIL MAY CRY, BAYONETTA, NIER, HORIZON, SPIDER-MAN, GOD OF WAR, LAST OF US, UNCHARTED, HALO, GEARS OF WAR, FORZA, NEED FOR SPEED, GRAN TURISMO, TEKKEN, STREET FIGHTER, MORTAL KOMBAT, SUPER SMASH BROS, POKEMON, ZELDA, MARIO, SONIC, METROID, CASTLEVANIA, FINAL FANTASY, DRAGON QUEST, KINGDOM HEARTS, DARK SOULS, ELDEN RING, SEKIRO, BLOODBORNE, MONSTER HUNTER, DEVIL MAY CRY, BAYONETTA, NIER, HORIZON, SPIDER-MAN GİBİ OYUNLAR HAKKINDA BİLGİN VAR. OYUN MOTORLARI: UNITY, UNREAL ENGINE, GODOT, GAME MAKER, CRYENGINE, SOURCE ENGINE, FROSTBITE, REDEngine, ANVIL, DECIMA, FOX ENGINE, MT FRAMEWORK, RAGE, ID TECH, SERPENT ENGINE, SNOWDROP, DISHONORED ENGINE, VOID ENGINE, PRISM ENGINE, YETI ENGINE, SLIPSTREAM ENGINE, NORTHLIGHT ENGINE, REFLECTIONS ENGINE, DUNIA ENGINE, ANVIL NEXT, SCIMITAR, HAVOK, PHYSX, BULLET PHYSICS, BOX2D, APEX, MIDDLEWARE. OYUN TÜRLERİ: AKSİON, MACERA, RPG, FPS, TPS, STRATEJİ, SIMÜLASYON, YARIŞ, SPOR, KORKU, BULMACA, PLATFORM, FIGHTING, STEALTH, SURVIVAL, HORROR, OPEN WORLD, LINEAR, SANDBOX, MMO, MOBA, BATTLE ROYALE, ROGUELIKE, METROIDVANIA, SOULSLIKE, CO-OP, MULTIPLAYER, SINGLE PLAYER, CROSS-PLATFORM. YAZIM HATALARINDAN KAÇIN. TÜRKÇE İMLE KURALLARINA DİKKAT ET. HARFLERİ DOĞRU YAZ. KELİMELERİ BİRLİŞTİRMEK YERİNE BOŞLUK KULLAN. 'miyim?' YERİNE 'miyim?' YAZMA, DOĞRU YAZIM: 'mıyım?'. 'yardımıc' YERİNE 'yardımcı' YAZ. 'olabilri' YERİNE 'olabilir' YAZ. HER CEVABI YAZIM KONTROLÜNDEN GEÇİR. 'ROOT' KELİMESİ BİR SİSTEM KOMUTUDUR, KULLANICI 'ROOT' YAZDIĞINDA BU BİR KOMUTTUR VE ÖZEL İŞLEMLER GEREKTİRİR. 'ROOT' KELİMESİNİ BAŞKA ANLAMLARLA KARIŞTIRMA. ROOT KULLANICI, SİSTEM YÖNETİCİSİ DEMEKTİR. KULLANICI KENDİSİNİ TANITTIĞINDA ('Ben bir yazılımcıyım', 'Ben bir öğrenciyim', 'Ben bir doktorum' GİBİ), KENDİSİNİ TANITMAYA DEVAM ETMELİSİN. SEN HER ZAMAN 'BEN GLASSESCAT' DEMELİSİN."

@app.route('/history', methods=['GET'])
def get_history():
    """Chat geçmişini getir"""
    return jsonify({"history": chat_history})

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user_api():
    """Mevcut kullanıcı bilgilerini getir"""
    return jsonify({
        "success": True,
        "username": session.get('username'),
        "login_time": session.get('login_time')
    })

@app.route('/screen_status', methods=['GET'])
def get_screen_status_api():
    """Ekran durumunu getir (Placeholder)"""
    return jsonify({
        "window_title": "GlassesCat Dashboard",
        "status": "active"
    })

@app.route('/check-model', methods=['GET'])
def check_model_api():
    """Model durumunu kontrol et"""
    return jsonify({
        "loaded": True,
        "model": request.args.get('model', 'llama3.1')
    })

@app.route('/admin/check-session', methods=['GET'])
def check_admin_session():
    """Admin session kontrolü - Admin veya geliştirici modu kontrolü"""
    if session.get('is_admin'):
        return jsonify({"authenticated": True, "mode": "admin", "is_developer": False})
    
    # Geliştirici modu kontrolü
    if session.get('is_dev'):
        return jsonify({
            "authenticated": True, 
            "mode": "developer", 
            "is_developer": True,
            "user": session.get('user_name', 'Geliştirici')
        })
    
    return jsonify({"authenticated": False}), 401

# Geliştirici şifresi - basit giriş için
DEV_SIMPLE_PASSWORD = "adminglassescat"

@app.route('/simple-login', methods=['POST'])
def simple_login():
    """Basit İsim + Beta Key ile giriş - Kayıt gerektirmez"""
    data = request.json
    name = data.get('name', '').strip()
    beta_key = data.get('beta_key', '').strip().upper()
    
    if not name:
        return jsonify({"success": False, "error": "İsim gereklidir!"}), 400
    
    if not beta_key:
        return jsonify({"success": False, "error": "Beta Key gereklidir!"}), 400
    
    # Beta Key kontrolü
    if beta_key not in valid_keys:
        return jsonify({"success": False, "error": "Geçersiz Beta Key!"}), 401
    
    if not valid_keys[beta_key]["is_active"]:
        # Kullanılmış key - kullanıcı adı eşleşiyor mu kontrol et
        used_by = valid_keys[beta_key].get("used_by", "")
        if used_by != name:
            return jsonify({"success": False, "error": "Bu Beta Key başka kullanıcıya ait!"}), 401
    else:
        # İlk kez kullanılıyor - kaydet
        valid_keys[beta_key]["is_active"] = False
        valid_keys[beta_key]["used_by"] = name
        valid_keys[beta_key]["used_at"] = datetime.now().isoformat()
    
    # Kullanıcı kaydet (isim bazlı)
    users[name] = {
        "name": name,
        "beta_key": beta_key,
        "created_at": datetime.now().isoformat(),
        "last_login": datetime.now().isoformat()
    }
    
    # Session oluştur (basit)
    session['user_name'] = name
    session['beta_key'] = beta_key
    session.permanent = True
    
    return jsonify({
        "success": True,
        "message": f"🎉 Hoş geldin {name}!",
        "name": name,
        "redirect": "/"
    })

@app.route('/dev-login-simple', methods=['POST'])
def dev_login_simple():
    """Geliştirici girişi - İsim gerekmez, direkt 'Admin' yapar
    
    Şifre: adminglassescat
    """
    data = request.json
    password = data.get('password', '').strip()
    
    if not password:
        return jsonify({"success": False, "error": "Şifre gereklidir!"}), 400
    
    # Şifre kontrolü
    if password != DEV_SIMPLE_PASSWORD:
        return jsonify({"success": False, "error": "Geçersiz şifre!"}), 401
    
    # İsim her zaman 'Admin'
    name = "Admin"
    dev_key = "DEV-MODE-SIMPLE"
    
    # Kullanıcı kaydet
    users[name] = {
        "name": name,
        "beta_key": dev_key,
        "is_dev": True,
        "created_at": datetime.now().isoformat(),
        "last_login": datetime.now().isoformat()
    }
    
    # Session oluştur
    session['user_name'] = name
    session['beta_key'] = dev_key
    session['is_dev'] = True
    session.permanent = True
    
    return jsonify({
        "success": True,
        "message": "👨‍💻 Geliştirici modu aktif! Hoş geldin Admin!",
        "name": name,
        "redirect": "/" 
    })

def detect_intent(message):
    """Kod/teknik içerik mi tespit et"""
    code_keywords = ['kod', 'python', 'java', 'javascript', 'html', 'css',
                     'sql', 'api', 'fonksiyon', 'class', 'def', 'import',
                     'program', 'script', 'bug', 'error', 'debug', 'syntax', 'nmap', 'hack']

    msg_lower = message.lower()
    if any(kw in msg_lower for kw in code_keywords):
        return DEFAULT_MODEL
    return DEFAULT_MODEL

def ollama_chat(message, model=None, context=False, session_id=None, extra_system=None):
    """Ollama'dan yanit al."""
    global chat_history

    # Router ile model seçimi
    if model is None:
        model_info = router.route(message)
        model = model_info["model"]
        print(f"[DEBUG] Router seçilen model: {model} (Tip: {model_info['type']})")

    # Memory'den bağlam al
    context_messages = []
    if session_id:
        context_messages = memory.get_context(session_id, limit=10)
    elif context and chat_history:
        recent_history = chat_history[-3:]
        for item in recent_history:
            role = "user" if item.get('is_user') else "assistant"
            msg = item.get('message', '')[:100]
            context_messages.append({"role": role, "content": msg})

    # Obsidian Sınırsız Hafıza Bağlamı
    obsidian_context = ""
    if OBSIDIAN_MEMORY_OK:
        try:
            obsidian_ctx = _obsidian_mem.get_context_for_ai(query=message)
            if obsidian_ctx:
                obsidian_context = f"\n\n[OBSIDIAN SINIRSIZ HAFIZA - Geçmiş bağlamlar]\n{obsidian_ctx}"
        except:
            pass
    
    # System prompt - Türkçe
    system_prompt = "BENİM ADIM GLASSESCAT. SEN DEĞİL, BEN GLASSESCAT'İM. BEN BİR TÜRKÇE YAPAY ZEKASİYIM. SADECE TÜRKÇE KONUŞ. KULLANICI İSMİNİ KENDİ İSMİNLE KARIŞTIRMA. HER ZAMAN 'BEN GLASSESCAT' DEMELİSİN."
    system_prompt += obsidian_context
    
    # Extra system prompt (skill'lerden gelen)
    if extra_system:
        system_prompt += "\n\n" + extra_system

    model_name = model

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(context_messages)
    messages.append({"role": "user", "content": message})

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.0}
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('message', {}).get('content', '')

            # Boş yanıt kontrolü
            if not ai_response or ai_response.strip() == '':
                return {"error": "🤖 AI boş yanıt döndü. Model yukleniyor olabilir, biraz bekleyin."}
            
            # Memory'ye kaydet
            if session_id:
                memory.add_message(session_id, "user", message)
                memory.add_message(session_id, "assistant", ai_response)
            
            # Eski sisteme de kaydet (geriye uyumluluk)
            chat_history.append({"message": message, "is_user": True})
            chat_history.append({"message": ai_response, "is_user": False})
            
            # Geçmiş limiti (100 mesaj)
            if len(chat_history) > 100:
                chat_history = chat_history[-100:]
            
            return {"response": ai_response, "model": model_name}
        else:
            error_text = response.text if response.text else f"HTTP {response.status_code}"
            print(f"[Ollama Hata] {error_text[:200]}")
            if 'CUDA' in error_text or 'cuda' in error_text:
                return {"error": "GPU hatasi. Ollama'nin CUDA surumu uyumsuz. 'ollama serve' terminalde calisiyor mu?"}
            if 'llama runner' in error_text:
                return {"error": "AI modeli yuklenemedi. Terminalde 'ollama serve' calistigini ve modelin var oldugunu kontrol et ('ollama list')."}
            return {"error": f"Ollama hatasi. Terminalde 'ollama serve' calisiyor mu?"}
            
    except requests.exceptions.Timeout:
        return {"error": "⏱️ AI 120 saniyede yanit veremedi. Cok uzun mesaj veya sistem meşgul. Tekrar deneyin."}
    except requests.exceptions.ConnectionError:
        return {"error": "❌ Ollama baglantisi yok. 'ollama serve' calistigindan emin olun."}
    except Exception as e:
        return {"error": f"Beklenmedik hata: {str(e)}"}

@app.route('/check-model', methods=['GET'])
def check_model():
    """Ollama model durumunu kontrol et"""
    model = request.args.get('model', DEFAULT_MODEL)
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "messages": [{"role": "user", "content": "test"}],
                "stream": False,
                "options": {"num_predict": 1}
            },
            timeout=10
        )
        if response.status_code == 200:
            return jsonify({"loaded": True, "model": model})
        else:
            return jsonify({"loaded": False, "model": model, "error": "Model yuklu degil"})
    except:
        return jsonify({"loaded": False, "model": model, "error": "Baglanti yok"})


# ===== OBSIDIAN SINIRSIZ HAFIZA API =====

@app.route('/api/memory/search', methods=['POST'])
@login_required
def memory_search():
    """Obsidian sınırsız hafızada ara"""
    if not OBSIDIAN_MEMORY_OK:
        return jsonify({"error": "Obsidian hafıza aktif değil"}), 400
    
    data = request.json or {}
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({"error": "Arama sorgusu gerekli"}), 400
    
    results = _obsidian_mem.recall(query, max_results=20)
    return jsonify({
        "success": True,
        "query": query,
        "results": results,
        "count": len(results)
    })


@app.route('/api/memory/recent', methods=['GET'])
@login_required
def memory_recent():
    """Son hafızaları getir"""
    if not OBSIDIAN_MEMORY_OK:
        return jsonify({"error": "Obsidian hafıza aktif değil"}), 400
    
    limit = request.args.get('limit', 20, type=int)
    results = _obsidian_mem.recall_recent(limit=limit)
    return jsonify({
        "success": True,
        "results": results,
        "count": len(results)
    })


@app.route('/api/memory/stats', methods=['GET'])
@login_required
def memory_stats():
    """Hafıza istatistiklerini getir"""
    if not OBSIDIAN_MEMORY_OK:
        return jsonify({"error": "Obsidian hafıza aktif değil"}), 400
    
    return jsonify({
        "success": True,
        "total_files": _obsidian_mem.get_memory_count(),
        "total_size": _obsidian_mem.get_total_size()
    })


# =============================================================================
# 🧠 KONUŞMA HAFIZASI API
# =============================================================================

@app.route('/api/memory/session', methods=['POST'])
@login_required
def create_memory_session():
    """Yeni hafıza oturumu oluştur"""
    try:
        data = request.get_json() or {}
        session_id = memory.create_session()
        return jsonify({
            "success": True,
            "session_id": session_id
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/memory/session/<session_id>', methods=['GET'])
@login_required
def get_memory_session(session_id):
    """Oturum bilgilerini getir"""
    session = memory.get_session(session_id)
    if session:
        return jsonify({
            "success": True,
            "session": {
                "id": session["id"],
                "created_at": session["created_at"],
                "last_active": session["last_active"],
                "message_count": len(session["messages"]),
                "summary": memory.get_conversation_summary(session_id)
            }
        })
    return jsonify({"success": False, "error": "Oturum bulunamadı"}), 404


@app.route('/api/memory/session/<session_id>/messages', methods=['GET'])
@login_required
def get_memory_messages(session_id):
    """Oturum mesajlarını getir"""
    limit = request.args.get('limit', 50, type=int)
    session = memory.get_session(session_id)
    if session:
        messages = session["messages"][-limit:] if len(session["messages"]) > limit else session["messages"]
        return jsonify({
            "success": True,
            "messages": messages
        })
    return jsonify({"success": False, "error": "Oturum bulunamadı"}), 404


@app.route('/api/memory/session/<session_id>/clear', methods=['POST'])
@login_required
def clear_memory_session(session_id):
    """Oturum mesajlarını temizle"""
    success = memory.clear_session(session_id)
    return jsonify({"success": success})


@app.route('/api/memory/sessions', methods=['GET'])
@login_required
def list_memory_sessions():
    """Tüm oturumları listele"""
    sessions = memory.list_sessions()
    return jsonify({
        "success": True,
        "sessions": sessions
    })


@app.route('/api/memory/session/<session_id>', methods=['DELETE'])
@login_required
def delete_memory_session(session_id):
    """Oturumu sil"""
    success = memory.delete_session(session_id)
    return jsonify({"success": success})


@app.route('/api/memory/search', methods=['GET'])
@login_required
def search_memory():
    """Mesajlarda ara"""
    session_id = request.args.get('session_id')
    query = request.args.get('q', '')
    
    if not session_id or not query:
        return jsonify({"success": False, "error": "session_id ve q gerekli"}), 400
    
    results = memory.search_messages(session_id, query)
    return jsonify({
        "success": True,
        "results": results,
        "count": len(results)
    })


@app.route('/api/memory/export', methods=['GET'])
@login_required
def export_memory():
    """Konuşmayı dışa aktar"""
    session_id = request.args.get('session_id')
    format_type = request.args.get('format', 'json')
    
    if not session_id:
        return jsonify({"success": False, "error": "session_id gerekli"}), 400
    
    data = memory.export_conversation(session_id, format_type)
    if data:
        return jsonify({"success": True, "data": data})
    return jsonify({"success": False, "error": "Oturum bulunamadı"}), 404


# =============================================================================
# 📁 DOSYA İŞLEMLERİ API
# =============================================================================

@app.route('/api/files/read', methods=['POST'])
@login_required
def api_read_file():
    """Dosya okuma"""
    try:
        data = request.get_json()
        filepath = data.get('path', '')
        
        if not filepath:
            return jsonify({"success": False, "error": "path gerekli"}), 400
        
        result = file_ops.read_file(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/files/write', methods=['POST'])
@login_required
def api_write_file():
    """Dosya yazma"""
    try:
        data = request.get_json()
        filepath = data.get('path', '')
        content = data.get('content', '')
        append = data.get('append', False)
        
        if not filepath:
            return jsonify({"success": False, "error": "path gerekli"}), 400
        
        result = file_ops.write_file(filepath, content, append=append)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/files/copy', methods=['POST'])
@login_required
def api_copy_file():
    """Dosya kopyalama"""
    try:
        data = request.get_json()
        source = data.get('source', '')
        destination = data.get('destination', '')
        
        if not source or not destination:
            return jsonify({"success": False, "error": "source ve destination gerekli"}), 400
        
        result = file_ops.copy_file(source, destination)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/files/delete', methods=['POST'])
@login_required
def api_delete_file():
    """Dosya silme"""
    try:
        data = request.get_json()
        filepath = data.get('path', '')
        
        if not filepath:
            return jsonify({"success": False, "error": "path gerekli"}), 400
        
        result = file_ops.delete_file(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/files/list', methods=['GET'])
@login_required
def api_list_directory():
    """Dizin listeleme"""
    try:
        dirpath = request.args.get('path', os.path.expanduser('~'))
        result = file_ops.list_directory(dirpath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/files/search', methods=['GET'])
@login_required
def api_search_files():
    """Dosya arama"""
    try:
        root_dir = request.args.get('root', os.path.expanduser('~'))
        pattern = request.args.get('pattern', '')
        recursive = request.args.get('recursive', 'true').lower() == 'true'
        
        if not pattern:
            return jsonify({"success": False, "error": "pattern gerekli"}), 400
        
        result = file_ops.search_files(root_dir, pattern, recursive)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/files/info', methods=['GET'])
@login_required
def api_file_info():
    """Dosya bilgisi"""
    try:
        filepath = request.args.get('path', '')
        
        if not filepath:
            return jsonify({"success": False, "error": "path gerekli"}), 400
        
        result = file_ops.get_file_info(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/files/mkdir', methods=['POST'])
@login_required
def api_create_directory():
    """Dizin oluşturma"""
    try:
        data = request.get_json()
        dirpath = data.get('path', '')
        
        if not dirpath:
            return jsonify({"success": False, "error": "path gerekli"}), 400
        
        result = file_ops.create_directory(dirpath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/files/log', methods=['GET'])
@login_required
def api_file_log():
    """İşlem loglarını getir"""
    limit = request.args.get('limit', 50, type=int)
    log = file_ops.get_operation_log(limit)
    return jsonify({"success": True, "log": log})


# =============================================================================
# 🔍 WEB ARAMA API
# =============================================================================

@app.route('/api/search', methods=['GET'])
@login_required
def api_web_search():
    """Web araması"""
    try:
        query = request.args.get('q', '')
        provider = request.args.get('provider', 'duckduckgo')
        max_results = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({"success": False, "error": "q (query) gerekli"}), 400
        
        result = web_search.search(query, provider=provider, max_results=max_results)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/search/news', methods=['GET'])
@login_required
def api_news_search():
    """Haber araması"""
    try:
        query = request.args.get('q', '')
        max_results = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({"success": False, "error": "q gerekli"}), 400
        
        result = web_search.search_news(query, max_results=max_results)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/search/article', methods=['GET'])
@login_required
def api_get_article():
    """Makale içeriği getir"""
    try:
        url = request.args.get('url', '')
        
        if not url:
            return jsonify({"success": False, "error": "url gerekli"}), 400
        
        result = web_search.get_article_content(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/search/clear-cache', methods=['POST'])
@login_required
def api_clear_search_cache():
    """Önbelleği temizle"""
    web_search.clear_cache()
    return jsonify({"success": True, "message": "Önbellek temizlendi"})


# =============================================================================
# 🐍 KOD ÇALIŞTIRMA SANDBOX API
# =============================================================================

@app.route('/api/sandbox/execute', methods=['POST'])
@login_required
def api_sandbox_execute():
    """Python kodu çalıştır"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        use_subprocess = data.get('subprocess', False)
        
        if not code:
            return jsonify({"success": False, "error": "code gerekli"}), 400
        
        if use_subprocess:
            result = sandbox.execute_in_subprocess(code)
        else:
            result = sandbox.execute(code)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/sandbox/log', methods=['GET'])
@login_required
def api_sandbox_log():
    """Çalıştırma loglarını getir"""
    limit = request.args.get('limit', 50, type=int)
    log = sandbox.get_execution_log(limit)
    return jsonify({"success": True, "log": log})


@app.route('/api/sandbox/validate', methods=['POST'])
@login_required
def api_sandbox_validate():
    """Kod güvenlik kontrolü"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code:
            return jsonify({"success": False, "error": "code gerekli"}), 400
        
        secure, msg = sandbox._check_security(code)
        valid, import_msg = sandbox._validate_imports(code)
        
        return jsonify({
            "success": True,
            "secure": secure,
            "secure_message": msg,
            "valid": valid,
            "valid_message": import_msg
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# 🔊 SESLİ YANIT (TTS) API
# =============================================================================

@app.route('/api/tts/speak', methods=['POST'])
@login_required
def api_tts_speak():
    """Metni sese dönüştür"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        provider = data.get('provider', 'gtts')
        
        if not text:
            return jsonify({"success": False, "error": "text gerekli"}), 400
        
        result = tts.speak(text, provider=provider)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/tts/voices', methods=['GET'])
@login_required
def api_tts_voices():
    """Mevcut sesleri listele"""
    provider = request.args.get('provider', 'gtts')
    result = tts.get_available_voices(provider)
    return jsonify(result)


@app.route('/api/tts/provider', methods=['POST'])
@login_required
def api_tts_set_provider():
    """Varsayılan TTS sağlayıcısını ayarla"""
    try:
        data = request.get_json()
        provider = data.get('provider', 'gtts')
        
        tts.set_provider(provider)
        return jsonify({"success": True, "provider": provider})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/tts/clear-cache', methods=['POST'])
@login_required
def api_tts_clear_cache():
    """TTS önbelleğini temizle"""
    tts.clear_cache()
    return jsonify({"success": True, "message": "TTS önbelleği temizlendi"})


# =============================================================================
# 🤖 CODE AGENT API
# =============================================================================

@app.route('/api/agent/capabilities', methods=['GET'])
@login_required
def api_agent_capabilities():
    """Agent yeteneklerini listele"""
    return jsonify(code_agent.get_capabilities())


@app.route('/api/agent/analyze', methods=['POST'])
@login_required
def api_agent_analyze():
    """Kod analiz et"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'auto')
        
        if not code:
            return jsonify({"success": False, "error": "code gerekli"}), 400
        
        result = code_agent.analyze_code(code, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agent/errors', methods=['POST'])
@login_required
def api_agent_errors():
    """Koddaki hataları bul"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({"success": False, "error": "code gerekli"}), 400
        
        result = code_agent.find_errors(code, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agent/explain', methods=['POST'])
@login_required
def api_agent_explain():
    """Kodu açıkla"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({"success": False, "error": "code gerekli"}), 400
        
        result = code_agent.explain_code(code, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agent/generate', methods=['POST'])
@login_required
def api_agent_generate():
    """Kod üret"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        language = data.get('language', 'python')
        framework = data.get('framework')
        
        if not description:
            return jsonify({"success": False, "error": "description gerekli"}), 400
        
        result = code_agent.generate_code(description, language, framework)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agent/refactor', methods=['POST'])
@login_required
def api_agent_refactor():
    """Kodu yeniden düzenle"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        style = data.get('style', 'clean')
        
        if not code:
            return jsonify({"success": False, "error": "code gerekli"}), 400
        
        result = code_agent.refactor_code(code, language, style)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agent/optimize', methods=['POST'])
@login_required
def api_agent_optimize():
    """Kodu optimize et"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({"success": False, "error": "code gerekli"}), 400
        
        result = code_agent.optimize_code(code, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agent/security', methods=['POST'])
@login_required
def api_agent_security():
    """Güvenlik denetimi yap"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({"success": False, "error": "code gerekli"}), 400
        
        result = code_agent.security_audit(code, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/agent/document', methods=['POST'])
@login_required
def api_agent_document():
    """Koda dökümanasyon ekle"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({"success": False, "error": "code gerekli"}), 400
        
        result = code_agent.document_code(code, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# 👁️ VİZYON API - Resim Analizi (LLaVA)
# =============================================================================

@app.route('/api/vision/analyze', methods=['POST'])
@login_required
def api_vision_analyze():
    """Görüntü analiz et"""
    try:
        data = request.get_json()
        image_data = data.get('image')  # base64
        image_path = data.get('path')    # veya dosya yolu
        question = data.get('question', 'Bu görüntüyü detaylı olarak Türkçe açıkla.')
        
        if image_data:
            result = vision_analyzer.analyze(image_data, question)
        elif image_path:
            result = vision_analyzer.analyze(image_path, question)
        else:
            return jsonify({"success": False, "error": "image veya path gerekli"}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/vision/screenshot', methods=['POST'])
@login_required
def api_vision_screenshot():
    """Screenshot analizi"""
    try:
        data = request.get_json()
        screenshot_path = data.get('path')
        question = data.get('question')
        
        result = vision_analyzer.analyze_screenshot(screenshot_path, question)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/vision/ocr', methods=['POST'])
@login_required
def api_vision_ocr():
    """Görüntüden metin çıkar (OCR)"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        image_path = data.get('path')
        
        if image_data:
            result = vision_analyzer.ocr_text(image_data)
        elif image_path:
            result = vision_analyzer.ocr_text(image_path)
        else:
            return jsonify({"success": False, "error": "image veya path gerekli"}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/vision/code', methods=['POST'])
@login_required
def api_vision_code():
    """Kod ekran görüntüsü analizi"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        image_path = data.get('path')
        
        if image_data:
            result = vision_analyzer.analyze_code_screenshot(image_data)
        elif image_path:
            result = vision_analyzer.analyze_code_screenshot(image_path)
        else:
            return jsonify({"success": False, "error": "image veya path gerekli"}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/vision/error', methods=['POST'])
@login_required
def api_vision_error():
    """Hata ekranı analizi"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        image_path = data.get('path')
        
        if image_data:
            result = vision_analyzer.analyze_error(image_data)
        elif image_path:
            result = vision_analyzer.analyze_error(image_path)
        else:
            return jsonify({"success": False, "error": "image veya path gerekli"}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/vision/status', methods=['GET'])
@login_required
def api_vision_status():
    """Vision modülü durumu"""
    return jsonify(get_vision_status())


# =============================================================================
# 📊 MODEL BİLGİLERİ API
# =============================================================================

@app.route('/api/models', methods=['GET'])
@login_required
def api_models_list():
    """Tüm model bilgilerini getir"""
    models_info = router.get_models_info()
    available = router.get_available_models()
    
    return jsonify({
        "success": True,
        "models": models_info,
        "available": available
    })


@app.route('/api/models/status', methods=['GET'])
@login_required
def api_models_status():
    """Model durumlarını getir"""
    status = router.get_model_status()
    return jsonify({
        "success": True,
        "status": status
    })


# Chat endpoint - stabilize edilmiş ve loglama aktif
@app.route('/chat', methods=['POST'])
@login_required
@rate_limited
def chat():
    """Ana chat endpoint'i"""
    try:
        global current_theme
        data = request.json
        message = data.get('message', '').strip()
        ip_address = request.remote_addr
        current_user = session.get('user_name', 'Misafir')
        image_data = data.get('image')
        has_image = image_data is not None
        selected_model = data.get('model')
        
        if not message and not has_image:
            log_request('/chat', data, ip_address, status="error", error="Bos mesaj")
            return jsonify({"error": "Bos mesaj gonderilemez"}), 400
        
        # İsim tanıma
        if message.lower().startswith('benim adım') or message.lower().startswith('adım') or message.lower().startswith('i am') or message.lower().startswith('my name is'):
            match = re.search(r'(?:benim adım|adım|i am|my name is)\s+(.+)', message, re.IGNORECASE)
            if match:
                user_name = match.group(1).strip().rstrip('.!?')
                response = f"Merhaba {user_name}, benim adım GlassesCat. Sana nasıl yardımcı olabilirim?"
                log_request('/chat', data, ip_address, status="name_recognition")
                log_user_message(current_user, message, "name_recognition", response)
                return jsonify({"response": response, "theme": current_theme, "model": DEFAULT_MODEL})

        # Meslek/hobi tanıma
        if message.lower().startswith('ben bir') or message.lower().startswith('i am a') or message.lower().startswith('i am an'):
            match = re.search(r'(?:ben bir|i am a|i am an)\s+(.+)', message, re.IGNORECASE)
            if match:
                user_profession = match.group(1).strip().rstrip('.!?')
                response = f"Sen {user_profession} olduğunu öğrendim. Benim adım GlassesCat. Sana nasıl yardımcı olabilirim?"
                log_request('/chat', data, ip_address, status="profession_recognition")
                log_user_message(current_user, message, "profession_recognition", response)
                return jsonify({"response": response, "theme": current_theme, "model": DEFAULT_MODEL})

        # Yerel Sistem Komutları
        local_result = process_local_command(message)
        if local_result:
            log_request('/chat', data, ip_address, status="local_command")
            log_user_message(current_user, message, "system", local_result.get('response', ''))
            return jsonify(local_result)

        # Kali komutu
        kali_result = process_kali_command(message)
        if kali_result:
            log_request('/chat', data, ip_address, status="kali_command")
            log_user_message(current_user, message, "kali", kali_result.get('message', '') if isinstance(kali_result, dict) else None)
            return jsonify(kali_result)
        
        # Oyun komutları
        game_result = process_game_command(message)
        if game_result:
            log_request('/chat', data, ip_address, status="game_command")
            log_user_message(current_user, message, "game", game_result.get('response', ''))
            return jsonify(game_result)
        
        # Toolformer ile araç çağrısı dene
        if toolformer and hasattr(toolformer, 'process_response'):
            try:
                tool_result = toolformer.process_response(message)
                if tool_result and isinstance(tool_result, dict) and tool_result.get('handled'):
                    log_request('/chat', data, ip_address, status="toolformer")
                    log_user_message(current_user, message, response=str(tool_result.get('result', '')))
                    return jsonify({"response": str(tool_result.get('result', '')), "theme": current_theme, "model": "toolformer"})
            except Exception as e:
                print(f"[UYARI] Toolformer hatası: {e}")
        
        # Resim analizi
        if has_image:
            result = vision_analyzer.analyze(
                image_source=image_data,
                question=message or "Bu goruntuyu detayli olarak Turkce ac"
            )
            result['theme'] = current_theme
            result['model'] = 'llava:latest'
            log_request('/chat', data, ip_address, status="vision_success")
            return jsonify(result)
        
        # Model seçimi ve tema belirleme
        if selected_model:
            model = selected_model
            # Tema belirleme
            if 'coder' in model.lower() or 'qwen' in model.lower():
                current_theme = 'code'
            elif 'llama3.1' in model.lower() or 'sohbet' in model.lower():
                current_theme = 'sohbet'
            elif 'deepseek' in model.lower() or 'r1' in model.lower():
                current_theme = 'analiz'
            else:
                current_theme = 'default'
        else:
            model_info = router.route(message, has_image=has_image)
            model = model_info["model"]
            current_theme = 'default'
        
        # Skill prompt'larını birleştir
        combined_prompt = None
        skill_names = []
        if skill_manager:
            enabled = skill_manager.get_enabled_skills()
            skill_names = list(enabled.keys())
            combined_prompt = skill_manager.get_combined_prompt(skill_names)
        
        # Ollama'ya gönder
        result = ollama_chat(message, model=model, context=True, extra_system=combined_prompt)
        result['theme'] = current_theme
        result['skills'] = skill_names
        
        # Konuşmayı özetle (arka planda)
        if summarizer and len(chat_history) > 20:
            session_id = session.get('user_name', 'default')
            threading.Thread(target=summarizer.auto_summarize_if_needed, args=(session_id,), daemon=True).start()
        
        # Loglama
        if result.get('error'):
            log_request('/chat', data, ip_address, status="error", error=result['error'])
        else:
            log_request('/chat', data, ip_address, status="success")
            log_user_message(current_user, message, response=result.get('response'))
        
        return jsonify(result)

    except Exception as e:
        print(f"[CRITICAL ERROR] chat function failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Sunucu hatası: {str(e)}", "status": "error"}), 500


def process_local_command(message):
    """Yerel sistem komutlarını ve uygulama başlatmayı işle"""
    msg = message.lower().strip()
    
    # Uygulama Başlatma: "aç [uygulama]" veya "[uygulama] aç"
    if msg.startswith("aç ") or msg.endswith(" aç"):
        app_name = msg.replace("aç ", "").replace(" aç", "").strip()
        try:
            res = launch_app(app_name)
            return {"response": res['message'], "type": "toolbox"}
        except:
            pass # Eğer uygulama bulunamazsa normal AI'ya geçsin

    # Dosya Arama: "dosya bul [pattern]"
    if msg.startswith("dosya bul "):
        pattern = msg.replace("dosya bul ", "").strip()
        files = toolbox.find_files(pattern)
        if files:
            res_text = "🔍 Bulunan dosyalar:\n" + "\n".join(files[:10])
            if len(files) > 10: res_text += f"\n...ve {len(files)-10} tane daha."
            return {"response": res_text, "type": "toolbox"}
        return {"response": "❌ Hiç dosya bulunamadı.", "type": "toolbox"}

    # Dizin Listeleme: "listele" veya "ls" veya "dizin listele"
    if msg in ["listele", "ls", "dir"] or msg.startswith("dizin listele"):
        path = "."
        if msg.startswith("dizin listele "):
            path = msg.replace("dizin listele ", "").strip()
        
        res = toolbox.list_directory(path)
        if res['success']:
            folders = [f"[D] {d}" for d in res['directories']]
            files = [f"[F] {f}" for f in res['files']]
            res_text = f"📁 {path} içeriği:\n" + "\n".join(folders + files)
            return {"response": res_text, "type": "toolbox"}
        return {"response": f"❌ Hata: {res['error']}", "type": "toolbox"}

    # Komut Çalıştırma: "komut çalıştır [cmd]"
    if msg.startswith("komut çalıştır "):
        cmd = message[15:].strip() # Case sensitive komut için orijinal mesajı kullan
        res = toolbox.run_command(cmd)
        if res['success']:
            output = res['stdout'] if res['stdout'] else "Komut çalıştırıldı (çıktı yok)."
            return {"response": f"⚙️ Komut Çıktısı:\n{output}", "type": "toolbox"}
        return {"response": f"❌ Hata: {res['stderr'] if res['stderr'] else res['error']}", "type": "toolbox"}

    # Tarayıcı Aç: "tarayıcı aç [url]"
    if msg.startswith("tarayıcı aç "):
        url = msg.replace("tarayıcı aç ", "").strip()
        if not url.startswith("http"): url = "https://" + url
        toolbox.open_browser(url)
        return {"response": f"🌐 {url} açılıyor...", "type": "toolbox"}

    return None

def process_game_command(message):
    """Oyun geliştirme komutlarını işle - GlassesCat GAME DEV"""
    msg = message.lower().strip()
    
    # CS2 Demo çalıştırma
    if msg in ["cs2 demo", "cs2 oyna", "cs2 başlat", "oyun cs2", "fps demo"]:
        return {
            "response": "🎮 CS2 Demo başlatılıyor...\n\n" +
                       "Kontroller:\n" +
                       "• WASD: Hareket\n" +
                       "• Mouse: Nişan alma\n" +
                       "• Sol Click: Ateş\n" +
                       "• R: Şarjör değiştirme\n" +
                       "• 1-4: Silah değiştirme\n\n" +
                       "Oyun yeni bir pencerede açılacak.",
            "type": "game",
            "action": "launch_cs2_demo"
        }
    
    # Pygame kurulum kontrolü
    if msg in ["pygame kur", "oyun kurulumu", "requirements kur"]:
        return {
            "response": "📦 Oyun geliştirme bağımlılıkları kuruluyor...\n" +
                       "```bash\n" +
                       "pip install pygame numpy\n" +
                       "```\n" +
                       "Kurulum tamamlandıktan sonra CS2 demo çalıştırılabilir.",
            "type": "game",
            "action": "install_deps"
        }
    
    # Oyun dizini açma

    
    return None

@app.route('/voice', methods=['POST'])
@login_required
@rate_limited
def voice():
    """Sesli mesaj işle - Web Speech API'den gelen metni chat gibi işle"""
    data = request.json
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({"error": "Boş mesaj"})
    
    # Kali komutu kontrol et
    kali_result = process_kali_command(message)
    if kali_result:
        if isinstance(kali_result, dict):
            kali_result['voice_mode'] = True
        return jsonify(kali_result)
    
    # Normal sohbet
    model = DEFAULT_MODEL
    result = ollama_chat(message, model=model)
    result['voice_mode'] = True
    return jsonify(result)

def process_kali_command(message):
    """Kali komutlarını işle"""
    patterns = [
        (r'^(?:kali|ssh)\s+bağlan\s+(\S+)\s+(\S+)\s*(\S*)', 'connect'),
        (r'^(?:kali|ssh)\s+nmap\s+(.+)', 'nmap'),
        (r'^(?:kali|ssh)\s+komut\s+(.+)', 'command'),
        (r'^(?:kali|ssh)\s+(?:bağlantı\s+kes|disconnect|çık)', 'disconnect'),
        (r'^(?:kali|ssh)\s+sqlmap\s+(.+)', 'sqlmap'),
        (r'^(?:kali|ssh)\s+nikto\s+(.+)', 'nikto'),
        (r'^(?:kali|ssh)\s+whatweb\s+(.+)', 'whatweb'),
        (r'^(?:kali|ssh)\s+searchsploit\s+(.+)', 'searchsploit'),
        (r'^(?:kali|ssh)\s+whois\s+(.+)', 'whois'),
        (r'^(?:kali|ssh)\s+metasploit\s*(.*)', 'metasploit'),
    ]
    
    for pattern, cmd_type in patterns:
        match = re.search(pattern, message.lower())
        if match:
            return execute_kali_cmd(cmd_type, match.groups())
    
    return None

def execute_kali_cmd(cmd_type, groups):
    """Kali komutunu çalıştır"""
    if cmd_type == 'connect':
        ip, user, password = groups[0], groups[1], groups[2] if groups[2] else None
        if not password:
            return {"error": "Şifre gerekli. Örnek: kali bağlan 192.168.1.100 kali sifre123"}
        return kali_manager.connect(ip, user, password=password)
    
    elif cmd_type == 'disconnect':
        return kali_manager.disconnect()
    
    elif not kali_manager.connected:
        return {"error": "Önce 'kali bağlan IP kullanıcı şifre' ile bağlan"}
    
    elif cmd_type == 'metasploit':
        arg = groups[0] if groups else ""
        cmd = f"msfconsole -q -x '{arg}'" if arg else "msfconsole -q"
        return kali_manager.execute_command(cmd, timeout=300)
    
    elif cmd_type == 'nmap':
        return kali_manager.execute_command(f"nmap -sV {groups[0]}", timeout=120)
    
    elif cmd_type == 'sqlmap':
        return kali_manager.execute_command(f"sqlmap -u {groups[0]} --batch --level=1", timeout=300)
    
    elif cmd_type == 'nikto':
        return kali_manager.execute_command(f"nikto -h {groups[0]}", timeout=180)
    
    elif cmd_type == 'whatweb':
        return kali_manager.execute_command(f"whatweb {groups[0]}", timeout=60)
    
    elif cmd_type == 'searchsploit':
        return kali_manager.execute_command(f"searchsploit {groups[0]}", timeout=30)
    
    elif cmd_type == 'whois':
        return kali_manager.execute_command(f"whois {groups[0]}", timeout=30)
    
    elif cmd_type == 'command':
        return kali_manager.execute_command(groups[0])
    
    return {"error": "Bilinmeyen komut"}


# ==================== 🎮 SANAL ALAN (VENV) API ENDPOINTLERI ====================

import subprocess
import sys

# VENV yolu
VENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.venv')

def check_venv_exists():
    """Venv dizininin varlığını kontrol et"""
    return os.path.exists(VENV_PATH) and os.path.exists(os.path.join(VENV_PATH, 'Scripts', 'python.exe'))

def check_package_installed(package):
    """Belirli bir paketin kurulu olup olmadığını kontrol et"""
    try:
        venv_python = os.path.join(VENV_PATH, 'Scripts', 'python.exe')
        result = subprocess.run(
            [venv_python, '-c', f'import {package}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

@app.route('/api/venv/status', methods=['GET'])
@login_required
def venv_status():
    """VENV durumunu kontrol et - Python versiyonu dahil"""
    try:
        exists = check_venv_exists()
        has_pygame = check_package_installed('pygame') if exists else False
        has_numpy = check_package_installed('numpy') if exists else False
        has_tkinter = check_package_installed('tkinter') if exists else True  # Tkinter genelde built-in
        
        # Python versiyonu kontrolü
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        pygame_compatible = check_python_version_compatible()
        
        return jsonify({
            "exists": exists,
            "hasPygame": has_pygame,
            "hasNumpy": has_numpy,
            "hasTkinter": has_tkinter,
            "pythonVersion": python_version,
            "pygameCompatible": pygame_compatible,
            "path": VENV_PATH,
            "message": "Pygame kurulumu gerekli. /venv-kur komutu ile kurabilirsiniz!" if exists and not has_pygame and not pygame_compatible else None
        })
    except Exception as e:
        return jsonify({
            "exists": False,
            "hasPygame": False,
            "hasNumpy": False,
            "hasTkinter": False,
            "pythonVersion": None,
            "pygameCompatible": False,
            "error": str(e)
        }), 500

@app.route('/api/venv/setup', methods=['POST'])
@login_required
def venv_setup():
    """VENV oluştur"""
    try:
        if check_venv_exists():
            return jsonify({
                "success": True,
                "message": "✅ VENV zaten mevcut!"
            })
        
        # VENV oluştur
        base_path = os.path.dirname(VENV_PATH)
        result = subprocess.run(
            [sys.executable, '-m', 'venv', '.venv'],
            cwd=base_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return jsonify({
                "success": True,
                "message": "✅ Python sanal alani (.venv) olusturuldu!"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"VENV olusturulamadi: {result.stderr}"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Kurulum hatasi: {str(e)}"
        }), 500

@app.route('/api/venv/install', methods=['POST'])
@login_required
def venv_install():
    """Oyun bağımlılıklarını kur - OFFLINE ve ONLINE destek"""
    try:
        if not check_venv_exists():
            return jsonify({
                "success": False,
                "error": "Once VENV olusturulmali!"
            }), 400
        
        venv_pip = os.path.join(VENV_PATH, 'Scripts', 'pip.exe')
        venv_python = os.path.join(VENV_PATH, 'Scripts', 'python.exe')
        
        # 1. pip upgrade et (önemli!)
        addTerminalLineServer("Pip yukseltiliyor...")
        subprocess.run([venv_python, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      capture_output=True, timeout=60)
        
        # 2. setuptools downgrade et (pygame uyumluluk için)
        addTerminalLineServer("Setuptools ayarlaniyor...")
        subprocess.run([venv_pip, 'install', 'setuptools==65.5.1', '--force-reinstall'], 
                      capture_output=True, timeout=60)
        
        # 3. wheel kur (binary paketler için)
        subprocess.run([venv_pip, 'install', 'wheel'], capture_output=True, timeout=30)
        
        # 4. Pygame binary wheel kurulumu (kaynak kod derlemesi yok!)
        addTerminalLineServer("Pygame binary kurulumu deneniyor...")
        
        # Windows için önceden derlenmiş wheel
        cmds_to_try = [
            # En son versiyon binary wheel
            [venv_pip, 'install', 'pygame', '--only-binary', ':all:', '--no-cache-dir'],
            # Belirli versiyon binary
            [venv_pip, 'install', 'pygame==2.5.2', '--only-binary', ':all:', '--no-cache-dir'],
            # Daha eski ama stabil versiyon
            [venv_pip, 'install', 'pygame==2.4.0', '--only-binary', ':all:', '--no-cache-dir'],
            # Eski Windows uyumlu
            [venv_pip, 'install', 'pygame==2.1.3', '--only-binary', ':all:', '--no-cache-dir'],
            # Son çare - herhangi bir binary
            [venv_pip, 'install', 'pygame', '--prefer-binary', '--no-build-isolation'],
        ]
        
        for i, cmd in enumerate(cmds_to_try):
            try:
                addTerminalLineServer(f"Deneme {i+1}/6...")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                
                if result.returncode == 0 and check_package_installed('pygame'):
                    # Numpy de kur
                    subprocess.run([venv_pip, 'install', 'numpy', '--only-binary', ':all:'], 
                                  capture_output=True, timeout=60)
                    
                    return jsonify({
                        "success": True,
                        "message": "✅ Pygame ve Numpy kuruldu!"
                    })
            except subprocess.TimeoutExpired:
                continue
        
        # Hepsi başarısız olduysa - Python 3.13 için pygame yok
        # Tkinter alternatifini öner
        if not check_python_version_compatible():
            return jsonify({
                "success": True,
                "warning": True,
                "message": "⚠️ Python 3.13 icin pygame destegi yok!\n✅ Tkinter kullanabilirsiniz (Python ile gelir, kurulum gerekmez).\n\nOrnek: import tkinter as tk",
                "alternative": "tkinter"
            })
        
        return jsonify({
            "success": False,
            "error": "Pygame kurulumu basarisiz. Python 3.8-3.12 onerilir."
        }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Kurulum hatasi: {str(e)}"
        }), 500


def addTerminalLineServer(message, type='info'):
    """Terminal mesajı ekle (server tarafı)"""
    print(f"[VENV] {message}")


def check_python_version_compatible():
    """Python versiyonunun pygame ile uyumlu olup olmadığını kontrol et"""
    version = sys.version_info
    # Python 3.8 - 3.12 arası pygame destekli
    return (3, 8) <= (version.major, version.minor) <= (3, 12)

# ==================== 🚀 SINIRSIZ KOD ÇALIŞTIRMA SİSTEMİ ====================

@app.route('/api/venv/execute', methods=['POST'])
@login_required
def venv_execute():
    """
    HERHANGİ Python kodunu VENV içinde çalıştır
    Kullanıcı ne isterse: oyun, script, uygulama, hesap makinesi, vs.
    """
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        filename = data.get('filename', 'custom_script.py')
        auto_install = data.get('auto_install', True)  # Eksik paketleri otomatik kur
        
        if not code:
            return jsonify({
                "success": False,
                "error": "Kod boş olamaz!"
            }), 400
        
        if not check_venv_exists():
            return jsonify({
                "success": False,
                "error": "VENV bulunamadi! Once Sanal Alani kurun."
            }), 400
        
        # Güvenlik: Sadece belirli dizine yaz
        scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'user_scripts')
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Dosya adı güvenliği
        safe_filename = os.path.basename(filename)
        if not safe_filename.endswith('.py'):
            safe_filename += '.py'
        
        file_path = os.path.join(scripts_dir, safe_filename)
        
        # Kodu kaydet
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        venv_python = os.path.join(VENV_PATH, 'Scripts', 'python.exe')
        
        # Gerekli paketleri otomatik tespit et ve kur
        if auto_install:
            imports = re.findall(r'^import\s+(\w+)|^from\s+(\w+)', code, re.MULTILINE)
            packages = set()
            for imp in imports:
                pkg = imp[0] or imp[1]
                if pkg not in ['os', 'sys', 'json', 're', 'time', 'datetime', 'random', 'math', 'collections', 'itertools', 'functools', 'typing', 'pathlib']:
                    packages.add(pkg)
            
            if packages:
                venv_pip = os.path.join(VENV_PATH, 'Scripts', 'pip.exe')
                for pkg in packages:
                    try:
                        subprocess.run(
                            [venv_pip, 'install', pkg, '--quiet'],
                            capture_output=True,
                            timeout=60
                        )
                    except:
                        pass  # Başarısız olursa devam et
        
        # Kodu çalıştır (timeout ile)
        try:
            result = subprocess.run(
                [venv_python, file_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=scripts_dir
            )
            
            output = result.stdout
            error = result.stderr
            
            return jsonify({
                "success": result.returncode == 0,
                "output": output,
                "error": error if error else None,
                "filename": safe_filename,
                "returncode": result.returncode
            })
            
        except subprocess.TimeoutExpired:
            return jsonify({
                "success": False,
                "error": "Kod 30 saniye içinde tamamlanmadı (timeout)",
                "filename": safe_filename
            }), 408
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Calistirma hatasi: {str(e)}"
        }), 500


@app.route('/api/code/execute', methods=['POST'])
@login_required
def code_execute():
    """
    COKLU DIL kod calistirma endpoint'i.
    Desteklenen diller: python, javascript, bash, lua, ruby, go
    """
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        language = data.get('language', 'python').strip().lower()
        
        if not code:
            return jsonify({"success": False, "error": "Kod boş olamaz!"}), 400
        
        # Dil bazlı çalıştırma komutları
        lang_config = {
            'python': {
                'cmd': [os.path.join(VENV_PATH, 'Scripts', 'python.exe'), '-c', code],
                'timeout': 30,
                'ext': '.py'
            },
            'javascript': {
                'cmd': ['node', '-e', code],
                'timeout': 30,
                'ext': '.js'
            },
            'bash': {
                'cmd': ['powershell', '-Command', code] if sys.platform == 'win32' else ['bash', '-c', code],
                'timeout': 30,
                'ext': '.sh'
            },
            'lua': {
                'cmd': ['lua', '-e', code],
                'timeout': 30,
                'ext': '.lua'
            },
            'ruby': {
                'cmd': ['ruby', '-e', code],
                'timeout': 30,
                'ext': '.rb'
            },
            'go': {
                'cmd': None,  # Go için geçici dosya
                'timeout': 60,
                'ext': '.go'
            }
        }
        
        if language not in lang_config:
            return jsonify({
                "success": False,
                "error": f"Desteklenmeyen dil: {language}. Desteklenenler: {', '.join(lang_config.keys())}"
            }), 400
        
        config = lang_config[language]
        
        # Go dili için özel işlem (geçici dosya)
        if language == 'go':
            scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'user_scripts')
            os.makedirs(scripts_dir, exist_ok=True)
            safe_name = f"gocode_{int(time.time())}.go"
            file_path = os.path.join(scripts_dir, safe_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            try:
                result = subprocess.run(
                    ['go', 'run', file_path],
                    capture_output=True, text=True, timeout=config['timeout'],
                    cwd=scripts_dir
                )
                os.remove(file_path)
                return jsonify({
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.stderr else None,
                    "language": language
                })
            except subprocess.TimeoutExpired:
                os.remove(file_path)
                return jsonify({"success": False, "error": f"Go kodu {config['timeout']}s icinde tamamlanmadi"}), 408
            except FileNotFoundError:
                return jsonify({"success": False, "error": "Go derleyicisi bulunamadi. 'go' kurulu degil."}), 400
        
        # Python kodu icin venv kullan
        if language == 'python':
            try:
                result = subprocess.run(
                    config['cmd'],
                    capture_output=True, text=True, timeout=config['timeout'],
                    cwd=os.path.join(os.path.dirname(__file__), '..')
                )
                return jsonify({
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.stderr else None,
                    "language": language
                })
            except subprocess.TimeoutExpired:
                return jsonify({"success": False, "error": f"Python kodu {config['timeout']}s icinde tamamlanmadi"}), 408
        
        # JavaScript / Bash / Lua / Ruby
        try:
            result = subprocess.run(
                config['cmd'],
                capture_output=True, text=True, timeout=config['timeout'],
                shell=(language == 'bash')  # Bash/PowerShell icin shell=True
            )
            return jsonify({
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "language": language
            })
        except subprocess.TimeoutExpired:
            return jsonify({"success": False, "error": f"{language.capitalize()} kodu {config['timeout']}s icinde tamamlanmadi"}), 408
        except FileNotFoundError:
            return jsonify({"success": False, "error": f"{language.capitalize()} calistiricisi bulunamadi. Sistemde kurulu oldugundan emin olun."}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Calistirma hatasi: {str(e)}"}), 500


@app.route('/api/venv/create-game', methods=['POST'])
@login_required
def venv_create_game():
    """
    Kullanıcının tarif ettiği oyunu/uygulamayı oluştur ve çalıştır
    AI tarafından üretilen kodu doğrudan kaydet ve çalıştır
    """
    try:
        data = request.get_json()
        description = data.get('description', '').strip()
        game_type = data.get('type', 'auto')  # 'pygame', 'tkinter', 'console', 'auto'
        
        if not description:
            return jsonify({
                "success": False,
                "error": "Oyun/uygulama tanimi gerekli!"
            }), 400
        
        # AI'dan kod üretmesini iste
        from model_router import get_model_router
        router = get_model_router()
        
        # Prompt oluştur
        prompt = f"""
Kullanici su istegi yapti: "{description}"

Buna gore Python kodu yaz. Sadece calisir Python kodu ver, aciklama ekleme.
Oyun/uygulama turu: {game_type}

Kurallar:
1. Sadece Python kodu, hic aciklama ekleme
2. pygame kullanacaksan init() unutma
3. Dosya islemleri varsa try-except kullan
4. Sonsuz dongu (while True) varsa quit mekanizmasi ekle (ESC veya X tusuna cikis)
5. Kod direkt calissin, hata vermesin
"""
        
        # AI yanıtı al
        ai_result = router.chat(prompt)
        code = ai_result.get('response', '')
        
        # Kod bloklarını temizle
        code = re.sub(r'```python\n?', '', code)
        code = re.sub(r'```\n?', '', code)
        code = code.strip()
        
        # Dosya adı oluştur
        safe_name = re.sub(r'[^\w]', '_', description[:30]).lower()
        filename = f"{safe_name}_{int(time.time())}.py"
        
        # Şimdi bu kodu çalıştır
        scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'user_scripts')
        os.makedirs(scripts_dir, exist_ok=True)
        file_path = os.path.join(scripts_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Yeni pencerede başlat
        if sys.platform == 'win32':
            subprocess.Popen(
                ['cmd', '/c', 'start', 'python', file_path],
                cwd=scripts_dir,
                shell=True
            )
        else:
            venv_python = os.path.join(VENV_PATH, 'Scripts', 'python.exe')
            subprocess.Popen(
                [venv_python, file_path],
                cwd=scripts_dir
            )
        
        return jsonify({
            "success": True,
            "message": f"✅ '{description}' olusturuldu ve baslatildi!",
            "filename": filename,
            "code_preview": code[:200] + "..." if len(code) > 200 else code
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Oyun olusturma hatasi: {str(e)}"
        }), 500


# Import ekle
def check_and_install_package(package_name):
    """Paket kurulu mu kontrol et, yoksa kur"""
    try:
        venv_python = os.path.join(VENV_PATH, 'Scripts', 'python.exe')
        result = subprocess.run(
            [venv_python, '-c', f'import {package_name}'],
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            venv_pip = os.path.join(VENV_PATH, 'Scripts', 'pip.exe')
            subprocess.run([venv_pip, 'install', package_name, '--quiet'], capture_output=True, timeout=60)
        return True
    except:
        return False




# =============================================================================
# 🖥️ VMWARE BAĞLANTI SİSTEMİ
# =============================================================================

class VMwareManager:
    """VMware Workstation/Player bağlantı yöneticisi"""
    
    def __init__(self):
        self.vmrun_path = self._find_vmrun()
        self.vms = {}
    
    def _find_vmrun(self):
        """vmrun executable bul"""
        possible_paths = [
            r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe",
            r"C:\Program Files\VMware\VMware Workstation\vmrun.exe",
            r"C:\Program Files (x86)\VMware\VMware Player\vmrun.exe",
            r"/usr/bin/vmrun",
            r"/Applications/VMware Fusion.app/Contents/Library/vmrun"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def list_vms(self):
        """Mevcut VM'leri listele"""
        if not self.vmrun_path:
            return {"error": "VMware bulunamadı!"}
        
        try:
            result = subprocess.run(
                [self.vmrun_path, "list"],
                capture_output=True,
                text=True
            )
            return {
                "success": True,
                "vms": result.stdout.strip().split('\n')[1:]
            }
        except Exception as e:
            return {"error": str(e)}


vmware_mgr = VMwareManager()


@app.route('/api/vmware/vms', methods=['GET'])
@login_required
def list_vmware_vms():
    """VMware VM'lerini listele"""
    return jsonify(vmware_mgr.list_vms())


# =============================================================================
# ANA SAYFA YÖNLENDİRMESİ
# =============================================================================


# =============================================================================
# 🧩 PLUGIN SYSTEM API
# =============================================================================

@app.route('/api/plugins', methods=['GET'])
@login_required
def api_list_plugins():
    """Tüm pluginleri listele (frontend uyumlu)"""
    if not plugin_manager:
        return jsonify({"success": False, "error": "Plugin sistemi yüklü değil"}), 501
    try:
        names = plugin_manager.get_plugin_names()
        active_names = [p.name for p in plugin_manager.get_active_plugins()]
        # Frontend'in beklediği formatta döndür
        plugins_data = []
        for name in names:
            p = plugin_manager.get_plugin(name)
            if p:
                meta = p.metadata
                is_active = p.is_enabled if hasattr(p, 'is_enabled') else (p.state == 'enabled' or p.name in active_names)
                plugins_data.append({
                    "name": meta.name if hasattr(meta, 'name') else name,
                    "description": meta.description if hasattr(meta, 'description') else "",
                    "version": meta.version if hasattr(meta, 'version') else "1.0",
                    "enabled": is_active,
                    "status": "enabled" if is_active else "disabled",
                    "metadata": {
                        "name": meta.name if hasattr(meta, 'name') else name,
                        "description": meta.description if hasattr(meta, 'description') else "",
                        "version": meta.version if hasattr(meta, 'version') else "1.0",
                        "author": meta.author if hasattr(meta, 'author') else "",
                        "tags": meta.tags if hasattr(meta, 'tags') else [],
                    }
                })
        return jsonify({
            "success": True,
            "plugins": plugins_data,
            "active": active_names,
            "status": f"Sistem: PluginManager v1.0 · {len(plugins_data)} eklenti"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/plugins/<name>/toggle', methods=['POST'])
@login_required
def api_toggle_plugin(name):
    """Plugin'i aç/kapa"""
    if not plugin_manager:
        return jsonify({"success": False, "error": "Plugin sistemi yüklü değil"}), 501
    try:
        plugin = plugin_manager.get_plugin(name)
        if not plugin:
            return jsonify({"success": False, "error": f"Plugin '{name}' bulunamadı"}), 404
        if plugin.is_enabled:
            ok = plugin_manager.disable_plugin(name)
        else:
            ok = plugin_manager.enable_plugin(name)
        return jsonify({"success": ok, "enabled": plugin.is_enabled})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# 🤖 QWEN 14B ASSISTANT API
# =============================================================================

# Qwen plugin'ine erişim için yardımcı
def _get_qwen_plugin():
    """PluginManager'dan Qwen plugin'ini bul."""
    if not plugin_manager:
        return None
    try:
        plugins = plugin_manager.get_plugins()
        for name, instance in plugins.items():
            if instance and hasattr(instance, 'instance') and instance.instance:
                if 'qwen' in name.lower() or 'Qwen' in instance.instance.metadata.name:
                    return instance.instance
        # Alternatif: doğrudan plugin adıyla dene
        for pname in ['Qwen 14B Assistant', 'qwen_assistant', 'QwenAssistantPlugin']:
            p = plugin_manager.get_plugin(pname)
            if p and p.instance:
                return p.instance
    except Exception:
        pass
    return None

# Ollama'ya doğrudan bağlantı (plugin olmasa bile çalışsın)
def _qwen_direct_query(prompt: str, model: str = "qwen2.5-coder:14b") -> dict:
    """Ollama API'sine doğrudan sorgu."""
    import urllib.request, urllib.error, json
    try:
        data = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 4096}
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result.get("response", "").strip()
            return {"success": True, "response": text} if text else {"success": False, "error": "Boş yanıt"}
    except urllib.error.URLError as e:
        return {"success": False, "error": f"Ollama bağlantı hatası: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": f"Sorgu hatası: {str(e)}"}

def _qwen_direct_chat(messages: list, model: str = "qwen2.5-coder:14b") -> dict:
    """Ollama chat API'sine doğrudan sorgu."""
    import urllib.request, urllib.error, json
    try:
        recent = messages[-10:] if len(messages) > 10 else messages
        data = json.dumps({
            "model": model,
            "messages": recent,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 4096}
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result.get("message", {}).get("content", "").strip()
            return {"success": True, "response": text} if text else {"success": False, "error": "Boş yanıt"}
    except urllib.error.URLError as e:
        return {"success": False, "error": f"Ollama bağlantı hatası: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": f"Sorgu hatası: {str(e)}"}

def _qwen_execute_in_venv(code: str) -> dict:
    """Python kodunu .venv içinde çalıştır."""
    import subprocess, tempfile, os
    venv_python = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".venv", "Scripts", "python.exe"
    )
    if not os.path.exists(venv_python):
        venv_python = "python"
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name
        result = subprocess.run(
            [venv_python, temp_path],
            capture_output=True, text=True, timeout=30,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        os.unlink(temp_path)
        if result.returncode == 0:
            return {"success": True, "output": result.stdout.strip() or "✅ Başarılı"}
        return {"success": False, "error": result.stderr.strip() or "Bilinmeyen hata"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "⏱ Zaman aşımı (30sn)"}
    except Exception as e:
        return {"success": False, "error": f"Hata: {str(e)}"}

@app.route('/api/qwen/chat', methods=['POST'])
@login_required
def api_qwen_chat():
    """Qwen 14B ile sohbet et"""
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()
    history = data.get('history', [])
    model = data.get('model', 'qwen2.5-coder:14b')

    if not message:
        return jsonify({"success": False, "error": "Mesaj gerekli"}), 400

    try:
        # Önce plugin'i dene
        qwen_plugin = _get_qwen_plugin()
        if qwen_plugin and hasattr(qwen_plugin, 'chat'):
            result = qwen_plugin.chat(message)
            return jsonify(result)

        # Plugin yoksa doğrudan Ollama'ya git
        if history:
            # Chat API
            messages = history + [{"role": "user", "content": message}]
            result = _qwen_direct_chat(messages, model)
        else:
            result = _qwen_direct_query(message, model)
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": f"Sistem hatası: {str(e)}"}), 500

@app.route('/api/qwen/execute', methods=['POST'])
@login_required
def api_qwen_execute():
    """
    ⚡ Qwen 14B FULL POWER AUTO-FIX ENGINE
    5 strateji, 5 deneme, context-aware, pattern matching
    """
    data = request.get_json(silent=True) or {}
    code = data.get('code', '').strip()
    language = data.get('language', 'python')

    if not code:
        return jsonify({"success": False, "error": "Kod gerekli"}), 400

    import re as _re
    import platform as _platform
    import urllib.request, urllib.error, json as _json

    try:
        # 1. Önce kodu direkt çalıştır
        exec_result = _qwen_execute_in_venv(code)
        if exec_result["success"]:
            return jsonify({
                "success": True, "output": exec_result["output"],
                "fixed_code": None, "message": "✅ Kod başarıyla çalıştı"
            })

        # 2. HATA VAR - Full Power Auto-Fix başlasın!
        error_text = exec_result.get("error", "Bilinmeyen hata")

        # Hata sınıflandırması (detaylı)
        error_lower = error_text.lower()
        error_type = "genel"
        error_desc = error_text[:100]
        error_keywords = []

        if "SyntaxError" in error_text:
            error_type = "syntax_error"; error_desc = "Sentaks hatası"
        elif "IndentationError" in error_text:
            error_type = "indentation_error"; error_desc = "Girinti hatası"
        elif "NameError" in error_text or "is not defined" in error_text:
            error_type = "name_error"; error_desc = "Tanımsız değişken"
            nm = _re.search(r"name\s+'([^']+)'|'([^']+)'\s+is\s+not\s+defined", error_text)
            if nm: error_keywords = [nm.group(1) or nm.group(2)]
        elif "ModuleNotFoundError" in error_text or "ImportError" in error_text:
            error_type = "import_error"; error_desc = "Modül bulunamadı"
            nm = _re.search(r"No module named '([^']+)'", error_text)
            if nm: error_keywords = [nm.group(1)]
        elif "TypeError" in error_text:
            error_type = "type_error"; error_desc = "Tip uyuşmazlığı"
        elif "IndexError" in error_text:
            error_type = "index_error"; error_desc = "İndeks hatası"
        elif "KeyError" in error_text:
            error_type = "key_error"; error_desc = "Anahtar hatası"
        elif "AttributeError" in error_text:
            error_type = "attribute_error"; error_desc = "Nitelik hatası"
        elif "ValueError" in error_text:
            error_type = "value_error"; error_desc = "Değer hatası"
        elif "ZeroDivisionError" in error_text:
            error_type = "zero_division"; error_desc = "Sıfıra bölme"
        elif "FileNotFoundError" in error_text:
            error_type = "file_error"; error_desc = "Dosya bulunamadı"
        elif "PermissionError" in error_text:
            error_type = "permission_error"; error_desc = "Yetki hatası"

        # Ortam bağlamını hazırla
        env_context = (
            f"Python: {sys.version.split()[0]}\n"
            f"OS: {_platform.system()} {_platform.release()}\n"
            f".venv: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\\.venv"
        )

        # 3. ÇOKLU STRATEJİ İLE DÜZELTME
        strategies = [
            "direct", "analyze", "rewrite", "debug", "fallback"
        ]

        strategy_templates = {
            "direct": (
                "Sen bir Python debug uzmanısın. Şu kodu düzelt.\n"
                "{env}\n\n"
                "HATA: {error}\n"
                "HATA TİPİ: {error_type} ({error_desc})\n"
                "{keywords}"
                "KOD:\n{code}\n\n"
                "Sadece DÜZELTİLMİŞ kodu yaz. Açıklama EKLEME."
            ),
            "analyze": (
                "Önce hatayı analiz et, sonra düzeltilmiş kodu yaz.\n\n"
                "ORTAM: {env}\n"
                "HATA: {error}\n"
                "HATA TİPİ: {error_type}\n\n"
                "KOD:\n{code}\n\n"
                "ANALİZ:\n"
                "DÜZELTİLMİŞ KOD:\n```python\n<kod>\n```"
            ),
            "rewrite": (
                "Bu kodun aynı işlevi yapan hatasız versiyonunu yaz.\n"
                "HATA: {error}\nORİJİNAL:\n{code}\nSadece kod:"
            ),
            "debug": (
                "Adım adım debug et ve düzelt.\n"
                "HATA: {error} ({error_desc})\nKOD:\n{code}\n"
                "Adım 1 - Sorun:\nAdım 2 - Düzeltilmiş kod:\n```python\n<kod>\n```"
            ),
            "fallback": (
                "ACİL! En basit çözümü bul. try/except ekle.\n"
                "HATA: {error}\nKOD:\n{code}\nSadece kod:"
            ),
        }

        def _clean_qwen_code(text):
            """Qwen yanıtından temiz kod çıkar."""
            if not text: return ""
            text = text.strip()
            # ```python ... ``` veya ``` ... ```
            m = _re.search(r'```(?:python|py)?\s*\n(.*?)(?:\n\s*)?```', text, _re.DOTALL)
            if m: return m.group(1).strip()
            # Kod görünümlü satırlar
            lines = text.split('\n')
            code_lines = []
            for line in lines:
                s = line.strip()
                if any(s.startswith(kw) for kw in ['import ', 'from ', 'def ', 'class ', 'print', 'if ', 'for ', 'while ', 'try:', 'with ', 'return ', '#']):
                    code_lines.append(s)
                elif code_lines and s and not s.startswith('```'):
                    code_lines.append(s)
            if len(code_lines) >= 2:
                return '\n'.join(code_lines)
            return text

        previous_attempts = []
        all_fixed_codes = []

        for strategy in strategies:
            kw_context = ""
            if error_keywords:
                kw_context = f"EKSİK/HAZALI: {', '.join(error_keywords)}\n"

            prompt = strategy_templates.get(strategy, strategy_templates["direct"]).format(
                env=env_context,
                error=error_text[:300],
                error_type=error_type,
                error_desc=error_desc,
                code=code if not all_fixed_codes else all_fixed_codes[-1],
                keywords=kw_context,
            )

            # Önceki denemeleri ekle
            if previous_attempts:
                prompt += "\n\nÖNCEKİ BAŞARISIZ DENEMELER:\n"
                for i, prev in enumerate(previous_attempts[-3:], 1):
                    prompt += f"  {i}. Strateji={prev['s']}, Hata={prev['e'][:80]}\n"

            fix_result = _qwen_direct_query(prompt)
            if not fix_result.get("success"):
                continue

            fixed_raw = fix_result["response"].strip()
            fixed_code = _clean_qwen_code(fixed_raw)

            if not fixed_code or fixed_code == code or fixed_code in all_fixed_codes:
                continue

            all_fixed_codes.append(fixed_code)

            # Düzeltilmiş kodu çalıştır
            retry = _qwen_execute_in_venv(fixed_code)

            if retry["success"]:
                strat_name = strategy.capitalize()
                return jsonify({
                    "success": True,
                    "output": retry["output"],
                    "fixed_code": fixed_code,
                    "error_type": error_type,
                    "error_desc": error_desc,
                    "strategy": strategy,
                    "attempt": len(all_fixed_codes),
                    "original_error": error_text[:200],
                    "message": f"⚡ Qwen [{strat_name}] hatayı düzeltti! 🎉"
                })

            previous_attempts.append({"s": strategy, "e": retry.get("error", "?")[:150]})

        # 4. SON ÇARE: Plugin'i dene
        qwen_plugin = _get_qwen_plugin()
        if qwen_plugin and hasattr(qwen_plugin, 'execute_code'):
            try:
                plugin_result = qwen_plugin.execute_code(code)
                if plugin_result.get("success"):
                    return jsonify(plugin_result)
            except Exception:
                pass

        # 5. TÜMÜ BAŞARISIZ
        # Son bir postmortem analiz
        postmortem = _qwen_direct_query(
            f"Bu Python kodundaki hatayı 1 cümleyle açıkla:\nHATA: {error_text[:200]}\nKOD:\n{code}"
        )
        advice = postmortem.get("response", "")[:200] if postmortem.get("success") else ""

        return jsonify({
            "success": False,
            "error": error_text[:500],
            "error_type": error_type,
            "error_desc": error_desc,
            "attempts": len(all_fixed_codes),
            "advice": advice.strip(),
            "message": "❌ Qwen 14B tüm stratejileri denedi ama düzeltemedi."
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Sistem hatası: {str(e)}"}), 500

@app.route('/api/qwen/status', methods=['GET'])
@login_required
def api_qwen_status():
    """Qwen 14B plugin durumu"""
    try:
        # Plugin'den durum al
        qwen_plugin = _get_qwen_plugin()
        if qwen_plugin and hasattr(qwen_plugin, 'get_status'):
            return jsonify(qwen_plugin.get_status())

        # Plugin yoksa temel durum
        import urllib.request, json
        ollama_ok = False
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                ollama_ok = any("qwen" in m.get("name", "").lower() for m in data.get("models", []))
        except:
            pass

        return jsonify({
            "name": "Qwen 14B Assistant",
            "version": "1.0.0",
            "enabled": False,
            "ollama_connected": ollama_ok,
            "model": "qwen2.5-coder:14b",
            "message_count": 0,
            "status": "Ollama bağlı değil (plugin yüklü değil)",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/qwen/clear', methods=['POST'])
@login_required
def api_qwen_clear():
    """Qwen konuşma geçmişini temizle"""
    try:
        qwen_plugin = _get_qwen_plugin()
        if qwen_plugin and hasattr(qwen_plugin, 'clear_history'):
            qwen_plugin.clear_history()
            return jsonify({"success": True, "message": "Geçmiş temizlendi"})
        return jsonify({"success": True, "message": "Plugin yüklü değil (geçmiş yok)"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# 🎯 SKILL SYSTEM API
# =============================================================================

@app.route('/api/skills', methods=['GET'])
@login_required
def api_list_skills():
    """Tüm skill'leri listele"""
    if not skill_manager:
        return jsonify({"success": False, "error": "Skill sistemi yüklü değil"}), 501
    try:
        all_skills = skill_manager.get_all_skills()
        enabled = skill_manager.get_enabled_skills()
        skills_list = [s.to_dict() for s in all_skills.values()]
        enabled_names = list(enabled.keys())
        return jsonify({"success": True, "skills": skills_list, "enabled": enabled_names})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/skills/<name>/toggle', methods=['POST'])
@login_required
def api_toggle_skill(name):
    """Skill'i aç/kapa"""
    if not skill_manager:
        return jsonify({"success": False, "error": "Skill sistemi yüklü değil"}), 501
    try:
        skill_manager.toggle_skill(name)
        is_enabled = skill_manager.is_skill_enabled(name)
        return jsonify({"success": True, "enabled": is_enabled})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# 📚 RAG SYSTEM API
# =============================================================================

@app.route('/api/rag/index', methods=['POST'])
@login_required
def api_rag_index():
    """Belge indeksle"""
    if not rag_engine:
        return jsonify({"success": False, "error": "RAG sistemi yüklü değil"}), 501
    try:
        data = request.get_json()
        path = data.get('path', '')
        if not path:
            return jsonify({"success": False, "error": "path gerekli"}), 400
        result = rag_engine.index_document(path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/rag/search', methods=['GET'])
@login_required
def api_rag_search():
    """Belgelerde ara"""
    if not rag_engine:
        return jsonify({"success": False, "error": "RAG sistemi yüklü değil"}), 501
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({"success": False, "error": "q gerekli"}), 400
        results = rag_engine.search(query)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# 🔧 TOOLFORMER API
# =============================================================================

@app.route('/api/tools', methods=['GET'])
@login_required
def api_list_tools():
    """Tüm araçları listele"""
    if not toolformer:
        return jsonify({"success": False, "error": "Toolformer yüklü değil"}), 501
    try:
        tools = toolformer.list_tools()
        return jsonify({"success": True, "tools": tools})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# ⏰ TASK SCHEDULER API
# =============================================================================

@app.route('/api/tasks', methods=['GET'])
@login_required
def api_list_tasks():
    """Tüm görevleri listele"""
    if not task_scheduler:
        return jsonify({"success": False, "error": "Task Scheduler yüklü değil"}), 501
    try:
        tasks = task_scheduler.list_tasks()
        return jsonify({"success": True, "tasks": [t.to_dict() if hasattr(t, 'to_dict') else str(t) for t in tasks]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    """Yeni görev oluştur"""
    if not task_scheduler:
        return jsonify({"success": False, "error": "Task Scheduler yüklü değil"}), 501
    try:
        data = request.get_json()
        name = data.get('name', 'Görev')
        task_type_str = data.get('type', 'notification')
        scheduled_at = data.get('scheduled_at')
        
        # TaskType enum'ına çevir
        from task_scheduler import TaskType
        task_type_map = {
            'notification': TaskType.NOTIFICATION,
            'command': TaskType.COMMAND,
            'api_call': TaskType.API_CALL,
            'webhook': TaskType.WEBHOOK,
            'python_func': TaskType.PYTHON_FUNC,
        }
        task_type = task_type_map.get(task_type_str, TaskType.NOTIFICATION)
        
        task = task_scheduler.create_task(name, task_type, scheduled_at=scheduled_at)
        return jsonify({"success": True, "task": task.to_dict() if hasattr(task, 'to_dict') else str(task)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tasks/<task_id>/delete', methods=['POST'])
@login_required
def api_delete_task(task_id):
    """Görevi sil"""
    if not task_scheduler:
        return jsonify({"success": False, "error": "Task Scheduler yüklü değil"}), 501
    try:
        task_scheduler.delete_task(task_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# 🧠 SUMMARIZER API
# =============================================================================

@app.route('/api/summarize', methods=['POST'])
@login_required
def api_summarize():
    """Metni özetle"""
    if not summarizer:
        return jsonify({"success": False, "error": "Summarizer yüklü değil"}), 501
    try:
        data = request.get_json()
        text = data.get('text', '')
        level = data.get('level', 'normal')
        if not text:
            return jsonify({"success": False, "error": "text gerekli"}), 400
        
        # Session ID kullan veya varsayılan
        session_id = session.get('user_name', 'default')
        messages = [{"role": "user", "content": text}]
        summary = summarizer.summarize(session_id, messages, level=level)
        return jsonify({"success": True, "summary": summary.to_dict() if hasattr(summary, 'to_dict') else str(summary)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# 🎨 THEME API
# =============================================================================

@app.route('/api/theme', methods=['GET'])
@login_required
def api_get_theme():
    """Mevcut temayı getir"""
    return jsonify({
        "success": True,
        "theme": current_theme,
        "themes": THEME_MAP
    })

@app.route('/api/theme', methods=['POST'])
@login_required
def api_set_theme():
    """Temayı değiştir"""
    global current_theme
    data = request.get_json()
    theme = data.get('theme', 'default')
    if theme in THEME_MAP:
        current_theme = theme
        return jsonify({"success": True, "theme": current_theme})
    return jsonify({"success": False, "error": "Geçersiz tema"}), 400


if __name__ == '__main__':
    # OTOMATİK PORT TEMİZLEME SİSTEMİ
    import subprocess
    import os

    try:
        # 5000 portunu dinleyen PID'yi bul (Windows için)
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

    # Flask uygulamasını başlat
    app.run(host='0.0.0.0', port=5000)
