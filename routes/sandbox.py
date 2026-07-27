from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger("routes.sandbox")
router = APIRouter()


class SandboxExecuteRequest(BaseModel):
    code: str
    subprocess: Optional[bool] = False


class SandboxValidateRequest(BaseModel):
    code: str


def get_sandbox():
    try:
        from code_sandbox import get_sandbox as _get_sandbox
        return _get_sandbox()
    except Exception as e:
        logger.error(f"CodeSandbox yüklenemedi: {e}")
        return None


@router.post("/execute")
async def sandbox_execute(req: SandboxExecuteRequest):
    sandbox = get_sandbox()
    if not sandbox:
        raise HTTPException(status_code=503, detail="CodeSandbox modülü kullanılamıyor")

    if not req.code.strip():
        raise HTTPException(status_code=400, detail="code gerekli")

    try:
        if req.subprocess:
            result = sandbox.execute_in_subprocess(req.code)
        else:
            result = sandbox.execute(req.code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çalıştırma hatası: {str(e)}")


@router.get("/log")
async def sandbox_log(limit: int = 50):
    sandbox = get_sandbox()
    if not sandbox:
        raise HTTPException(status_code=503, detail="CodeSandbox modülü kullanılamıyor")

    log = sandbox.get_execution_log(limit)
    return {"success": True, "log": log}


@router.post("/validate")
async def sandbox_validate(req: SandboxValidateRequest):
    sandbox = get_sandbox()
    if not sandbox:
        raise HTTPException(status_code=503, detail="CodeSandbox modülü kullanılamıyor")

    if not req.code.strip():
        raise HTTPException(status_code=400, detail="code gerekli")

    try:
        secure, msg = sandbox._check_security(req.code)
        valid, import_msg = sandbox._validate_imports(req.code)
        return {
            "success": True,
            "secure": secure,
            "secure_message": msg,
            "valid": valid,
            "valid_message": import_msg,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Doğrulama hatası: {str(e)}")
