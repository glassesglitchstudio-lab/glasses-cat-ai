"""FastAPI TTS API - Sesli yanıt"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from tts import get_tts

router = APIRouter()

class TTSSpeakRequest(BaseModel):
    text: str
    provider: Optional[str] = "gtts"

class TTSProviderRequest(BaseModel):
    provider: str


@router.post("/speak")
async def tts_speak(data: TTSSpeakRequest):
    if not data.text:
        raise HTTPException(status_code=400, detail="text gerekli")
    try:
        tts = get_tts()
        result = tts.speak(data.text, provider=data.provider)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def tts_voices(provider: str = "gtts"):
    tts = get_tts()
    result = tts.get_available_voices(provider)
    return result


@router.post("/provider")
async def tts_set_provider(data: TTSProviderRequest):
    try:
        tts = get_tts()
        tts.set_provider(data.provider)
        return {"success": True, "provider": data.provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def tts_clear_cache():
    tts = get_tts()
    tts.clear_cache()
    return {"success": True, "message": "TTS önbelleği temizlendi"}
