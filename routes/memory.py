from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger("routes.memory")
router = APIRouter()

def get_memory():
    try:
        from nexus_memory import get_nexus_memory
        return get_nexus_memory()
    except Exception as e:
        logger.error(f"Nexus Memory error: {e}")
        return None

@router.get("/stats")
async def memory_stats():
    """Nexus Hafıza istatistikleri"""
    mem = get_memory()
    if not mem:
        return {"error": "Hafıza sistemi mevcut değil", "total_files": 0, "total_size_kb": 0}
    try:
        stats = mem.get_stats()
        return {"total_files": stats["memory_count"], "engine": stats["engine"], "categories": stats["categories"], "status": "active"}
    except Exception as e:
        return {"error": str(e), "total_files": 0}

@router.get("/search")
async def memory_search(q: str = Query(..., description="Arama sorgusu"), limit: int = Query(5, ge=1, le=50)):
    """Nexus Hafızada (SQLite + FTS5) arama yap"""
    mem = get_memory()
    if not mem:
        raise HTTPException(status_code=503, detail="Hafıza sistemi mevcut değil")
    try:
        results = mem.recall(q, limit=limit)
        return {"results": results, "query": q, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
async def memory_recent(limit: int = Query(10, ge=1, le=50)):
    """Son Nexus hafıza kayıtları"""
    mem = get_memory()
    if not mem:
        return {"results": []}
    try:
        results = mem.recall("*", limit=limit)
        return {"results": results}
    except Exception as e:
        return {"results": [], "error": str(e)}
