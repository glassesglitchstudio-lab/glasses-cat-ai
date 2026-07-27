import os
import hashlib
import secrets
from functools import wraps
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# Session depolama (production'da Redis/DB kullanın)
sessions: dict = {}
users: dict = {}

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{h}"

def verify_password(password: str, stored: str) -> bool:
    salt, h = stored.split(":", 1)
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == h

def create_session(user_email: str) -> str:
    token = secrets.token_hex(32)
    sessions[token] = {
        "email": user_email,
        "created": __import__("datetime").datetime.now().isoformat()
    }
    return token

def get_session_user(token: str) -> dict | None:
    return sessions.get(token)

async def require_auth(request: Request):
    token = request.cookies.get("session_token") or request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Oturum açmanız gerekiyor")
    return sessions[token]

async def require_admin(request: Request):
    user = await require_auth(request)
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    if not admin_password:
        raise HTTPException(status_code=500, detail="Admin şifresi tanımlı değil")
    return user
