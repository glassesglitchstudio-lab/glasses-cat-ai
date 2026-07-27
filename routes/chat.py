from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
import json
import httpx
import logging
import os

logger = logging.getLogger("routes.chat")
router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    model: Optional[str] = None

def get_core():
    try:
        from glassescat_core import get_core as _get_core
        return _get_core()
    except:
        return None

async def ollama_stream(message: str, model: str = None):
    """Ollama'ya streaming istek gönder"""
    core = get_core()
    if core and core.model_router:
        if not model:
            model = core.model_router.select_model(message)
        ollama_url = core.model_router.ollama_url
    else:
        model = model or os.getenv("DEFAULT_MODEL", "gulmzcetiner:latest")
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{ollama_url}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message}],
                    "stream": True
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        logger.error(f"Ollama streaming hatası: {e}")
        yield f"Hata: {e}"

@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """WebSocket ile streaming sohbet"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            message = msg.get("message", "")
            model = msg.get("model")

            if not message:
                await websocket.send_json({"type": "error", "content": "Mesaj boş olamaz"})
                continue

            await websocket.send_json({"type": "start", "content": ""})

            full_response = ""
            async for token in ollama_stream(message, model):
                full_response += token
                await websocket.send_json({"type": "token", "content": token})

            await websocket.send_json({"type": "done", "content": full_response})

    except WebSocketDisconnect:
        logger.info("WebSocket bağlantısı kesildi")
    except Exception as e:
        logger.error(f"WebSocket hatası: {e}")
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except:
            pass

@router.post("/")
async def http_chat(msg: ChatMessage):
    """HTTP ile sohbet (streaming yok, geriye uyumluluk)"""
    core = get_core()
    if core:
        result = core.process_message(msg.message, session_id=msg.session_id)
        return {
            "response": result.get("response", ""),
            "tool_calls": result.get("tool_calls", []),
            "thoughts": result.get("thoughts", [])
        }

    # Fallback: doğrudan Ollama'ya bağlan
    full_response = ""
    async for token in ollama_stream(msg.message, msg.model):
        full_response += token

    return {"response": full_response, "tool_calls": [], "thoughts": []}

@router.get("/models")
async def list_models():
    """Kullanılabilir modelleri listele"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("http://localhost:11434/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                return {"models": models}
    except:
        pass
    return {"models": []}

class SummarizeRequest(BaseModel):
    text: str
    level: str = "normal"

@router.post("/summarize")
async def summarize(msg: SummarizeRequest):
    """Metni özetle"""
    try:
        from conversation_summarizer import ConversationSummarizer
        summarizer = ConversationSummarizer()
    except:
        return {"success": False, "error": "Summarizer yüklü değil"}

    if not msg.text:
        return {"success": False, "error": "text gerekli"}

    try:
        messages = [{"role": "user", "content": msg.text}]
        summary = summarizer.summarize("default", messages, level=msg.level)
        return {
            "success": True,
            "summary": summary.to_dict() if hasattr(summary, 'to_dict') else str(summary)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
