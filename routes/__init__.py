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
try:
    from routes.code_agent import router as code_agent_router
    CODE_AGENT_OK = True
except Exception:
    CODE_AGENT_OK = False
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
from routes.mcp import router as mcp_router
try:
    from routes.multi_agent import router as multi_agent_router
    MULTI_AGENT_OK = True
except Exception:
    MULTI_AGENT_OK = False

router.include_router(chat_router, prefix="/api/chat", tags=["chat"])
router.include_router(mcp_router, prefix="/api/mcp", tags=["mcp"])
router.include_router(memory_router, prefix="/api/memory", tags=["memory"])
router.include_router(system_router, prefix="/api/system", tags=["system"])
router.include_router(auth_router, prefix="/api/auth", tags=["auth"])
router.include_router(scheduler_router, prefix="/api/scheduler", tags=["scheduler"])
router.include_router(rag_router, prefix="/api/rag", tags=["rag"])
router.include_router(vision_router, prefix="/api/vision", tags=["vision"])
router.include_router(tts_router, prefix="/api/tts", tags=["tts"])
if CODE_AGENT_OK:
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
if MULTI_AGENT_OK:
    router.include_router(multi_agent_router, prefix="/api/multi-agent", tags=["multi_agent"])
