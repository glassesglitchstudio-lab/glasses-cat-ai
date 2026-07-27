from fastapi import APIRouter

router = APIRouter()

# Route modüllerini kaydet
from routes.chat import router as chat_router
from routes.memory import router as memory_router
from routes.system import router as system_router
from routes.auth import router as auth_router
from routes.scheduler import router as scheduler_router
from routes.rag import router as rag_router
from routes.vision import router as vision_router
from routes.tts import router as tts_router
from routes.code_agent import router as code_agent_router
from routes.qwen import router as qwen_router
from routes.sandbox import router as sandbox_router
from routes.venv import router as venv_router
from routes.code import router as code_router
from routes.admin import router as admin_router
from routes.files import router as files_router
from routes.search import router as search_router
from routes.models import router as models_router
from routes.plugins import router as plugins_router
from routes.skills import router as skills_router
from routes.theme import router as theme_router
from routes.tools import router as tools_router

router.include_router(chat_router, prefix="/api/chat", tags=["chat"])
router.include_router(memory_router, prefix="/api/memory", tags=["memory"])
router.include_router(system_router, prefix="/api/system", tags=["system"])
router.include_router(auth_router, prefix="/api/auth", tags=["auth"])
router.include_router(scheduler_router, prefix="/api/scheduler", tags=["scheduler"])
router.include_router(rag_router, prefix="/api/rag", tags=["rag"])
router.include_router(vision_router, prefix="/api/vision", tags=["vision"])
router.include_router(tts_router, prefix="/api/tts", tags=["tts"])
router.include_router(code_agent_router, prefix="/api/agent", tags=["code_agent"])
router.include_router(qwen_router, prefix="/api/qwen", tags=["qwen"])
router.include_router(sandbox_router, prefix="/api/sandbox", tags=["sandbox"])
router.include_router(venv_router, prefix="/api/venv", tags=["venv"])
router.include_router(code_router, prefix="/api/code", tags=["code"])
router.include_router(admin_router, prefix="/api/admin", tags=["admin"])
router.include_router(files_router, prefix="/api/files", tags=["files"])
router.include_router(search_router, prefix="/api/search", tags=["search"])
router.include_router(models_router, prefix="/api/models", tags=["models"])
router.include_router(plugins_router, prefix="/api/plugins", tags=["plugins"])
router.include_router(skills_router, prefix="/api/skills", tags=["skills"])
router.include_router(theme_router, prefix="/api/theme", tags=["theme"])
router.include_router(tools_router, prefix="/api/tools", tags=["tools"])
