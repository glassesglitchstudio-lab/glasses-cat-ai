from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import json
import time
import threading
from collections import Counter
from datetime import datetime

from middleware.auth import require_admin, sessions

router = APIRouter()

# ==================== Storage ====================

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "glasses_admin_2024")
MAX_LOGS = 100
MAX_USER_MESSAGES = 500

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS_DB = os.path.join(BASE_DIR, "api_keys.json")

# API request logs
request_logs: list = []

# Beta access keys — kalici (api_keys.json)
def _load_keys() -> dict:
    if os.path.exists(KEYS_DB):
        try:
            with open(KEYS_DB, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}

def _save_keys():
    try:
        with open(KEYS_DB, "w", encoding="utf-8") as f:
            json.dump(valid_keys, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

valid_keys: dict = _load_keys()  # {key_code: {created_at, created_by, is_active, description, used_by}}

# User messages
user_messages: list = []

# Simple request queue status (lightweight replica)
class _QueueStatus:
    def __init__(self):
        self.lock = threading.Lock()
        self.queue_size = 0
        self.processing = False
        self.active_requests = 0
        self.rate_limit = 2

request_queue = _QueueStatus()


# ==================== Pydantic models ====================

class CreateKeyRequest(BaseModel):
    description: str = ""

class DeleteKeyRequest(BaseModel):
    key: str

class ToggleKeyRequest(BaseModel):
    key: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# ==================== Helpers ====================

def generate_access_key(length: int = 16) -> str:
    import secrets as _secrets
    import string as _string
    return ''.join(_secrets.choice(_string.ascii_uppercase + _string.digits) for _ in range(length))


# ==================== Key management ====================

@router.get("/keys")
async def list_keys(user=Depends(require_admin)):
    return {
        "success": True,
        "keys": [{"key": k, **v} for k, v in valid_keys.items()],
    }


@router.post("/keys/create")
async def create_key(body: CreateKeyRequest, user=Depends(require_admin)):
    new_key = generate_access_key()
    while new_key in valid_keys:
        new_key = generate_access_key()

    valid_keys[new_key] = {
        "created_at": datetime.now().isoformat(),
        "created_by": "admin",
        "used_by": None,
        "is_active": True,
        "description": body.description.strip() or "Genel Kullanici",
    }
    _save_keys()

    return {
        "success": True,
        "key": new_key,
        "message": f"Yeni Beta Key olusturuldu: {new_key}",
    }


@router.post("/keys/delete")
async def delete_key(body: DeleteKeyRequest, user=Depends(require_admin)):
    key = body.key.strip().upper()
    if key not in valid_keys:
        raise HTTPException(status_code=404, detail="Kod bulunamadi")
    del valid_keys[key]
    _save_keys()
    return {
        "success": True,
        "message": f"Beta Key silindi: {key}",
    }


@router.post("/keys/toggle")
async def toggle_key(body: ToggleKeyRequest, user=Depends(require_admin)):
    key = body.key.strip().upper()
    if key not in valid_keys:
        raise HTTPException(status_code=404, detail="Kod bulunamadi")

    valid_keys[key]["is_active"] = not valid_keys[key]["is_active"]
    _save_keys()
    status = "aktif" if valid_keys[key]["is_active"] else "pasif"

    return {
        "success": True,
        "message": f"Beta Key {status} yapildi: {key}",
        "is_active": valid_keys[key]["is_active"],
    }


# ==================== Logs ====================

@router.get("/logs/api")
async def get_api_logs(user=Depends(require_admin)):
    return {
        "logs": request_logs,
        "total": len(request_logs),
        "max_logs": MAX_LOGS,
    }


@router.post("/logs/clear")
async def clear_logs(user=Depends(require_admin)):
    request_logs.clear()
    return {"message": "Loglar temizlendi"}


# ==================== Stats ====================

@router.get("/stats")
async def get_stats(user=Depends(require_admin)):
    if not request_logs:
        return {"message": "Henuz log yok"}

    endpoints = Counter(log["endpoint"] for log in request_logs)
    statuses = Counter(log["status"] for log in request_logs)

    now = datetime.now()
    last_24h = [
        log for log in request_logs
        if (now - datetime.fromisoformat(log["timestamp"])).days < 1
    ]

    return {
        "total_requests": len(request_logs),
        "requests_24h": len(last_24h),
        "endpoints": dict(endpoints),
        "statuses": dict(statuses),
        "unique_ips": len(set(log["ip"] for log in request_logs)),
    }


# ==================== Queue ====================

@router.get("/queue")
async def get_queue_status(user=Depends(require_admin)):
    return {
        "queue_size": request_queue.queue_size,
        "processing": request_queue.processing,
        "active_requests": request_queue.active_requests,
        "rate_limit": request_queue.rate_limit,
    }


# ==================== Messages ====================

@router.get("/messages")
async def get_user_messages(
    sort: str = Query("newest"),
    user_filter: str = Query("", alias="user"),
    type_filter: str = Query("", alias="type"),
    limit: int = Query(100),
    _user=Depends(require_admin),
):
    filtered = list(user_messages)

    if user_filter:
        filtered = [m for m in filtered if user_filter.lower() in m["username"].lower()]
    if type_filter:
        filtered = [m for m in filtered if m["type"] == type_filter]

    if sort == "newest":
        filtered.sort(key=lambda x: x["timestamp"], reverse=True)
    elif sort == "oldest":
        filtered.sort(key=lambda x: x["timestamp"])
    elif sort == "username":
        filtered.sort(key=lambda x: x["username"].lower())
    elif sort == "type":
        filtered.sort(key=lambda x: x["type"])

    filtered = filtered[:limit]

    return {
        "messages": filtered,
        "total": len(user_messages),
        "filtered": len(filtered),
        "sort_by": sort,
    }


@router.post("/messages/clear")
async def clear_user_messages(user=Depends(require_admin)):
    count = len(user_messages)
    user_messages.clear()
    return {
        "message": f"{count} mesaj silindi",
        "cleared": count,
    }


@router.get("/messages/stats")
async def get_message_stats(user=Depends(require_admin)):
    if not user_messages:
        return {"message": "Henuz mesaj yok"}

    users = Counter(m["username"] for m in user_messages)
    types = Counter(m["type"] for m in user_messages)

    most_active = users.most_common(1)[0] if users else None

    now = datetime.now()
    last_24h = [
        m for m in user_messages
        if (now - datetime.fromisoformat(m["timestamp"])).days < 1
    ]

    return {
        "total_messages": len(user_messages),
        "messages_24h": len(last_24h),
        "unique_users": len(users),
        "types": dict(types),
        "most_active_user": most_active[0] if most_active else None,
        "most_active_count": most_active[1] if most_active else 0,
    }


# ==================== Admin password ====================

@router.post("/password")
async def change_admin_password(body: ChangePasswordRequest, user=Depends(require_admin)):
    global ADMIN_PASSWORD

    if body.current_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Mevcut sifre yanlis")

    if not body.new_password:
        raise HTTPException(status_code=400, detail="Yeni sifre bos olamaz")

    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Sifre en az 6 karakter olmali")

    ADMIN_PASSWORD = body.new_password

    return {
        "success": True,
        "message": "Admin sifresi basariyla degistirildi!",
    }


# ==================== Helper: log functions (called by other modules) ====================

def log_request(endpoint: str, data: dict, ip_address: str, status: str = "success", error: str = None):
    """Log an API request — call from other route modules."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "data": data.get("message", "")[:100] if isinstance(data, dict) else str(data)[:100],
        "ip": ip_address,
        "status": status,
        "error": error,
    }
    request_logs.append(entry)
    if len(request_logs) > MAX_LOGS:
        request_logs.pop(0)


def log_user_message(username: str, message: str, msg_type: str = "text", response: str = None):
    """Log a user message for admin review."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "username": username or "Misafir",
        "message": message[:500],
        "type": msg_type,
        "response": (response[:200] + "...") if response and len(response) > 200 else response,
    }
    user_messages.append(entry)
    if len(user_messages) > MAX_USER_MESSAGES:
        user_messages.pop(0)
