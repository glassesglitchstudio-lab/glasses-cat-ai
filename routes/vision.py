"""FastAPI Vision API - Görsel analiz (LLaVA)"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from vision import get_vision_analyzer, get_vision_status

router = APIRouter()

class VisionAnalyzeRequest(BaseModel):
    image: Optional[str] = None
    path: Optional[str] = None
    question: Optional[str] = "Bu görüntüyü detaylı olarak Türkçe açıkla."

class VisionImageRequest(BaseModel):
    image: Optional[str] = None
    path: Optional[str] = None

class ScreenshotRequest(BaseModel):
    path: Optional[str] = None
    question: Optional[str] = None


@router.post("/analyze")
async def vision_analyze(data: VisionAnalyzeRequest):
    try:
        vision = get_vision_analyzer()
        if data.image:
            result = vision.analyze(data.image, data.question)
        elif data.path:
            result = vision.analyze(data.path, data.question)
        else:
            raise HTTPException(status_code=400, detail="image veya path gerekli")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/screenshot")
async def vision_screenshot(data: ScreenshotRequest):
    try:
        vision = get_vision_analyzer()
        result = vision.analyze_screenshot(data.path, data.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr")
async def vision_ocr(data: VisionImageRequest):
    try:
        vision = get_vision_analyzer()
        if data.image:
            result = vision.ocr_text(data.image)
        elif data.path:
            result = vision.ocr_text(data.path)
        else:
            raise HTTPException(status_code=400, detail="image veya path gerekli")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code")
async def vision_code(data: VisionImageRequest):
    try:
        vision = get_vision_analyzer()
        if data.image:
            result = vision.analyze_code_screenshot(data.image)
        elif data.path:
            result = vision.analyze_code_screenshot(data.path)
        else:
            raise HTTPException(status_code=400, detail="image veya path gerekli")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/error")
async def vision_error(data: VisionImageRequest):
    try:
        vision = get_vision_analyzer()
        if data.image:
            result = vision.analyze_error(data.image)
        elif data.path:
            result = vision.analyze_error(data.path)
        else:
            raise HTTPException(status_code=400, detail="image veya path gerekli")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def vision_status():
    return get_vision_status()
