from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os

from middleware.auth import require_auth

router = APIRouter()

# Lazy singleton for file_ops
_file_ops = None

def _get_file_ops():
    global _file_ops
    if _file_ops is None:
        from file_ops import get_file_ops
        _file_ops = get_file_ops()
    return _file_ops


# ==================== Pydantic models ====================

class ReadFileRequest(BaseModel):
    path: str

class WriteFileRequest(BaseModel):
    path: str
    content: str
    append: bool = False

class CopyFileRequest(BaseModel):
    source: str
    destination: str

class DeleteFileRequest(BaseModel):
    path: str

class MkdirRequest(BaseModel):
    path: str


# ==================== Endpoints ====================

@router.post("/read")
async def api_read_file(body: ReadFileRequest, user=Depends(require_auth)):
    if not body.path:
        raise HTTPException(status_code=400, detail="path gerekli")
    try:
        result = _get_file_ops().read_file(body.path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/write")
async def api_write_file(body: WriteFileRequest, user=Depends(require_auth)):
    if not body.path:
        raise HTTPException(status_code=400, detail="path gerekli")
    try:
        result = _get_file_ops().write_file(body.path, body.content, append=body.append)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copy")
async def api_copy_file(body: CopyFileRequest, user=Depends(require_auth)):
    if not body.source or not body.destination:
        raise HTTPException(status_code=400, detail="source ve destination gerekli")
    try:
        result = _get_file_ops().copy_file(body.source, body.destination)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete")
async def api_delete_file(body: DeleteFileRequest, user=Depends(require_auth)):
    if not body.path:
        raise HTTPException(status_code=400, detail="path gerekli")
    try:
        result = _get_file_ops().delete_file(body.path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def api_list_directory(
    path: str = Query(default=os.path.expanduser("~")),
    user=Depends(require_auth),
):
    try:
        result = _get_file_ops().list_directory(path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def api_search_files(
    root: str = Query(default=os.path.expanduser("~")),
    pattern: str = Query(...),
    recursive: str = Query(default="true"),
    user=Depends(require_auth),
):
    if not pattern:
        raise HTTPException(status_code=400, detail="pattern gerekli")
    try:
        result = _get_file_ops().search_files(root, pattern, recursive.lower() == "true")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def api_file_info(
    path: str = Query(...),
    user=Depends(require_auth),
):
    if not path:
        raise HTTPException(status_code=400, detail="path gerekli")
    try:
        result = _get_file_ops().get_file_info(path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mkdir")
async def api_create_directory(body: MkdirRequest, user=Depends(require_auth)):
    if not body.path:
        raise HTTPException(status_code=400, detail="path gerekli")
    try:
        result = _get_file_ops().create_directory(body.path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/log")
async def api_file_log(
    limit: int = Query(default=50),
    user=Depends(require_auth),
):
    log = _get_file_ops().get_operation_log(limit)
    return {"success": True, "log": log}
