from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

THEME_MAP = {
    "default": {"name": "Mavi", "css_class": ""},
    "code": {"name": "Turuncu Kod", "css_class": "theme-code"},
    "sohbet": {"name": "Mor Sohbet", "css_class": "theme-chat"},
    "analiz": {"name": "Yeşil Analiz", "css_class": "theme-analysis"},
}

current_theme = "default"

class ThemeRequest(BaseModel):
    theme: str = "default"

@router.get("")
async def get_theme():
    """Mevcut temayı getir"""
    return {"success": True, "theme": current_theme, "themes": THEME_MAP}

@router.post("")
async def set_theme(req: ThemeRequest):
    """Temayı değiştir"""
    global current_theme
    if req.theme not in THEME_MAP:
        raise HTTPException(status_code=400, detail="Geçersiz tema")
    current_theme = req.theme
    return {"success": True, "theme": current_theme}
