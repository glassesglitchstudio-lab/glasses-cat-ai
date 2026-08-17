"""
Multi-Agent API Endpoint — SSE Streaming
POST /api/multi-agent/run  → SSE event stream
POST /api/multi-agent/abort → Çalışan işlemi iptal et
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger("routes.multi_agent")
router = APIRouter()


class MultiAgentRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    model: Optional[str] = None


class MultiAgentAbortRequest(BaseModel):
    session_id: Optional[str] = "default"


@router.post("/run")
async def multi_agent_run(request: MultiAgentRequest):
    """
    Multi-Agent orkestrasyon — SSE streaming.
    
    SSE Events:
      {"type":"plan","agents":[{"id":"...","label":"...","icon":"..."}]}
      {"type":"agent_start","agent":"...","label":"..."}
      {"type":"agent_done","agent":"...","result":"...","elapsed":1.2}
      {"type":"token","content":"..."}
      {"type":"done","full_response":"..."}
      {"type":"error","message":"..."}
    """
    try:
        from multi_agent import get_multi_agent_engine
        engine = get_multi_agent_engine()

        async def event_generator():
            try:
                async for event in engine.run(
                    message=request.message,
                    session_id=request.session_id or "default",
                    model=request.model,
                ):
                    yield event
            except Exception as e:
                import json
                logger.error(f"Multi-agent stream hatası: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    except ImportError:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "multi_agent modülü yüklenemedi"},
        )
    except Exception as e:
        logger.error(f"Multi-agent endpoint hatası: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )


@router.post("/abort")
async def multi_agent_abort(request: MultiAgentAbortRequest):
    """Çalışan multi-agent oturumunu iptal et"""
    try:
        from multi_agent import get_multi_agent_engine
        engine = get_multi_agent_engine()
        success = engine.abort(session_id=request.session_id or "default")
        return {"success": success, "message": "İptal edildi" if success else "Aktif oturum bulunamadı"}
    except Exception as e:
        logger.error(f"Multi-agent abort hatası: {e}")
        return {"success": False, "error": str(e)}
