"""FastAPI Code Agent API - Kod analiz ve üretimi"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from code_agent import get_code_agent

router = APIRouter()

class CodeRequest(BaseModel):
    code: str
    language: Optional[str] = "python"

class GenerateRequest(BaseModel):
    description: str
    language: Optional[str] = "python"
    framework: Optional[str] = None

class RefactorRequest(BaseModel):
    code: str
    language: Optional[str] = "python"
    style: Optional[str] = "clean"


@router.get("/capabilities")
async def agent_capabilities():
    code_agent = get_code_agent()
    return code_agent.get_capabilities()


@router.post("/analyze")
async def agent_analyze(data: CodeRequest):
    if not data.code:
        raise HTTPException(status_code=400, detail="code gerekli")
    try:
        code_agent = get_code_agent()
        result = code_agent.analyze_code(data.code, data.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/errors")
async def agent_errors(data: CodeRequest):
    if not data.code:
        raise HTTPException(status_code=400, detail="code gerekli")
    try:
        code_agent = get_code_agent()
        result = code_agent.find_errors(data.code, data.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
async def agent_explain(data: CodeRequest):
    if not data.code:
        raise HTTPException(status_code=400, detail="code gerekli")
    try:
        code_agent = get_code_agent()
        result = code_agent.explain_code(data.code, data.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def agent_generate(data: GenerateRequest):
    if not data.description:
        raise HTTPException(status_code=400, detail="description gerekli")
    try:
        code_agent = get_code_agent()
        result = code_agent.generate_code(data.description, data.language, data.framework)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refactor")
async def agent_refactor(data: RefactorRequest):
    if not data.code:
        raise HTTPException(status_code=400, detail="code gerekli")
    try:
        code_agent = get_code_agent()
        result = code_agent.refactor_code(data.code, data.language, data.style)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def agent_optimize(data: CodeRequest):
    if not data.code:
        raise HTTPException(status_code=400, detail="code gerekli")
    try:
        code_agent = get_code_agent()
        result = code_agent.optimize_code(data.code, data.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/security")
async def agent_security(data: CodeRequest):
    if not data.code:
        raise HTTPException(status_code=400, detail="code gerekli")
    try:
        code_agent = get_code_agent()
        result = code_agent.security_audit(data.code, data.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/document")
async def agent_document(data: CodeRequest):
    if not data.code:
        raise HTTPException(status_code=400, detail="code gerekli")
    try:
        code_agent = get_code_agent()
        result = code_agent.document_code(data.code, data.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
