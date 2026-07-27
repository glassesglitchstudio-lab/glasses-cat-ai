from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger("routes.memory")
router = APIRouter()

def get_memory():
    try:
        from obsidian_memory import get_obsidian_memory
        return get_obsidian_memory()
    except:
        return None

@router.get("/stats")
async def memory_stats():
    """Hafıza istatistikleri"""
    mem = get_memory()
    if not mem:
        return {"error": "Hafıza sistemi mevcut değil", "total_files": 0, "total_size_kb": 0}
    try:
        count = mem.get_memory_count()
        return {"total_files": count, "status": "active"}
    except Exception as e:
        return {"error": str(e), "total_files": 0}

@router.get("/search")
async def memory_search(q: str = Query(..., description="Arama sorgusu"), limit: int = Query(5, ge=1, le=50)):
    """Hafızada ara"""
    mem = get_memory()
    if not mem:
        raise HTTPException(status_code=503, detail="Hafıza sistemi mevcut değil")
    try:
        results = mem.recall(q, limit)
        return {"results": results, "query": q, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
async def memory_recent(limit: int = Query(10, ge=1, le=50)):
    """Son hafıza kayıtları"""
    mem = get_memory()
    if not mem:
        return {"results": []}
    try:
        results = mem.get_recent(limit)
        return {"results": results}
    except Exception as e:
        return {"results": [], "error": str(e)}
