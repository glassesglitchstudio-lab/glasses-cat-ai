from fastapi import APIRouter, HTTPException
import os

router = APIRouter()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:latest")

def get_router_instance():
    try:
        from model_router import get_model_router
        return get_model_router()
    except:
        return None

@router.get("")
async def list_models():
    """Tüm model bilgilerini getir"""
    r = get_router_instance()
    if not r:
        return {"success": True, "models": {}, "available": [], "default": DEFAULT_MODEL}
    try:
        models_info = r.get_models_info()
        available = r.get_available_models()
        return {"success": True, "models": models_info, "available": available}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/status")
async def model_status():
    """Model durumlarını getir"""
    r = get_router_instance()
    if not r:
        return {"success": True, "status": {}}
    try:
        status = r.get_model_status()
        return {"success": True, "status": status}
    except Exception as e:
        return {"success": False, "error": str(e)}
