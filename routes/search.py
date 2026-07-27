from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from middleware.auth import require_auth

router = APIRouter()

# Lazy singleton for web_search
_web_search = None

def _get_web_search():
    global _web_search
    if _web_search is None:
        from web_search import get_web_search
        _web_search = get_web_search()
    return _web_search


@router.get("")
async def api_web_search(
    q: str = Query(...),
    provider: str = Query(default="duckduckgo"),
    limit: int = Query(default=10),
    user=Depends(require_auth),
):
    if not q:
        raise HTTPException(status_code=400, detail="q (query) gerekli")
    try:
        result = _get_web_search().search(q, provider=provider, max_results=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news")
async def api_news_search(
    q: str = Query(...),
    limit: int = Query(default=10),
    user=Depends(require_auth),
):
    if not q:
        raise HTTPException(status_code=400, detail="q gerekli")
    try:
        result = _get_web_search().search_news(q, max_results=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/article")
async def api_get_article(
    url: str = Query(...),
    user=Depends(require_auth),
):
    if not url:
        raise HTTPException(status_code=400, detail="url gerekli")
    try:
        result = _get_web_search().get_article_content(url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def api_clear_search_cache(user=Depends(require_auth)):
    _get_web_search().clear_cache()
    return {"success": True, "message": "Onbellek temizlendi"}
