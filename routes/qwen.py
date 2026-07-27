"""FastAPI Qwen 14B Assistant API"""

import re
import os
import sys
import platform
import tempfile
import subprocess
import urllib.request
import urllib.error
import json as _json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

router = APIRouter()

# ==================== Helper Functions ====================

def _get_qwen_plugin():
    """PluginManager'dan Qwen plugin'ini bul."""
    try:
        from plugin_system import PluginManager
        pm = PluginManager.get_instance()
        if not pm:
            return None
        plugins = pm.get_plugins()
        for name, instance in plugins.items():
            if instance and hasattr(instance, 'instance') and instance.instance:
                if 'qwen' in name.lower() or 'Qwen' in instance.instance.metadata.name:
                    return instance.instance
        for pname in ['Qwen 14B Assistant', 'qwen_assistant', 'QwenAssistantPlugin']:
            p = pm.get_plugin(pname)
            if p and p.instance:
                return p.instance
    except Exception:
        pass
    return None


def _qwen_direct_query(prompt: str, model: str = "qwen2.5-coder:14b") -> dict:
    """Ollama API'sine doğrudan sorgu."""
    try:
        data = _json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 4096}
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
            text = result.get("response", "").strip()
            return {"success": True, "response": text} if text else {"success": False, "error": "Boş yanıt"}
    except urllib.error.URLError as e:
        return {"success": False, "error": f"Ollama bağlantı hatası: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": f"Sorgu hatası: {str(e)}"}


def _qwen_direct_chat(messages: list, model: str = "qwen2.5-coder:14b") -> dict:
    """Ollama chat API'sine doğrudan sorgu."""
    try:
        recent = messages[-10:] if len(messages) > 10 else messages
        data = _json.dumps({
            "model": model,
            "messages": recent,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 4096}
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
            text = result.get("message", {}).get("content", "").strip()
            return {"success": True, "response": text} if text else {"success": False, "error": "Boş yanıt"}
    except urllib.error.URLError as e:
        return {"success": False, "error": f"Ollama bağlantı hatası: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": f"Sorgu hatası: {str(e)}"}


def _qwen_execute_in_venv(code: str) -> dict:
    """Python kodunu .venv içinde çalıştır."""
    venv_python = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".venv", "Scripts", "python.exe"
    )
    if not os.path.exists(venv_python):
        venv_python = "python"
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name
        result = subprocess.run(
            [venv_python, temp_path],
            capture_output=True, text=True, timeout=30,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        os.unlink(temp_path)
        if result.returncode == 0:
            return {"success": True, "output": result.stdout.strip() or "Basarili"}
        return {"success": False, "error": result.stderr.strip() or "Bilinmeyen hata"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Zaman asimi (30sn)"}
    except Exception as e:
        return {"success": False, "error": f"Hata: {str(e)}"}


def _clean_qwen_code(text):
    """Qwen yanitindan temiz kod cikar."""
    if not text:
        return ""
    text = text.strip()
    m = re.search(r'```(?:python|py)?\s*\n(.*?)(?:\n\s*)?```', text, re.DOTALL)
    if m:
        return m.group(1).strip()
    lines = text.split('\n')
    code_lines = []
    for line in lines:
        s = line.strip()
        if any(s.startswith(kw) for kw in ['import ', 'from ', 'def ', 'class ', 'print', 'if ', 'for ', 'while ', 'try:', 'with ', 'return ', '#']):
            code_lines.append(s)
        elif code_lines and s and not s.startswith('```'):
            code_lines.append(s)
    if len(code_lines) >= 2:
        return '\n'.join(code_lines)
    return text


# ==================== Request Models ====================

class QwenChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []
    model: Optional[str] = "qwen2.5-coder:14b"

class QwenExecuteRequest(BaseModel):
    code: str
    language: Optional[str] = "python"


# ==================== Endpoints ====================

@router.post("/chat")
async def qwen_chat(data: QwenChatRequest):
    if not data.message.strip():
        raise HTTPException(status_code=400, detail="Mesaj gerekli")

    try:
        qwen_plugin = _get_qwen_plugin()
        if qwen_plugin and hasattr(qwen_plugin, 'chat'):
            result = qwen_plugin.chat(data.message)
            return result

        if data.history:
            messages = data.history + [{"role": "user", "content": data.message}]
            result = _qwen_direct_chat(messages, data.model)
        else:
            result = _qwen_direct_query(data.message, data.model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sistem hatasi: {str(e)}")


@router.post("/execute")
async def qwen_execute(data: QwenExecuteRequest):
    if not data.code.strip():
        raise HTTPException(status_code=400, detail="Kod gerekli")

    try:
        exec_result = _qwen_execute_in_venv(data.code)
        if exec_result["success"]:
            return {
                "success": True,
                "output": exec_result["output"],
                "fixed_code": None,
                "message": "Kod basariyla calisti"
            }

        error_text = exec_result.get("error", "Bilinmeyen hata")
        error_lower = error_text.lower()
        error_type = "genel"
        error_desc = error_text[:100]
        error_keywords = []

        if "SyntaxError" in error_text:
            error_type = "syntax_error"; error_desc = "Sentaks hatasi"
        elif "IndentationError" in error_text:
            error_type = "indentation_error"; error_desc = "Girinti hatasi"
        elif "NameError" in error_text or "is not defined" in error_text:
            error_type = "name_error"; error_desc = "Tanimsiz degisken"
            nm = re.search(r"name\s+'([^']+)'|'([^']+)'\s+is\s+not\s+defined", error_text)
            if nm:
                error_keywords = [nm.group(1) or nm.group(2)]
        elif "ModuleNotFoundError" in error_text or "ImportError" in error_text:
            error_type = "import_error"; error_desc = "Modul bulunamadi"
            nm = re.search(r"No module named '([^']+)'", error_text)
            if nm:
                error_keywords = [nm.group(1)]
        elif "TypeError" in error_text:
            error_type = "type_error"; error_desc = "Tip uyumsuzlugu"
        elif "IndexError" in error_text:
            error_type = "index_error"; error_desc = "Indeks hatasi"
        elif "KeyError" in error_text:
            error_type = "key_error"; error_desc = "Anahtar hatasi"
        elif "AttributeError" in error_text:
            error_type = "attribute_error"; error_desc = "Nitelik hatasi"
        elif "ValueError" in error_text:
            error_type = "value_error"; error_desc = "Deger hatasi"
        elif "ZeroDivisionError" in error_text:
            error_type = "zero_division"; error_desc = "Sifira bolme"
        elif "FileNotFoundError" in error_text:
            error_type = "file_error"; error_desc = "Dosya bulunamadi"
        elif "PermissionError" in error_text:
            error_type = "permission_error"; error_desc = "Yetki hatasi"

        env_context = (
            f"Python: {sys.version.split()[0]}\n"
            f"OS: {platform.system()} {platform.release()}\n"
            f".venv: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\\.venv"
        )

        strategies = ["direct", "analyze", "rewrite", "debug", "fallback"]

        strategy_templates = {
            "direct": (
                "Sen bir Python debug uzmanisin. Su kodu duzelt.\n"
                "{env}\n\n"
                "HATA: {error}\n"
                "HATA TIPI: {error_type} ({error_desc})\n"
                "{keywords}"
                "KOD:\n{code}\n\n"
                "Sadece DÜZELTMIS kodu yaz. Aciklama EKLEME."
            ),
            "analyze": (
                "Once hatayi analiz et, sonra duzeltilmis kodu yaz.\n\n"
                "ORTAM: {env}\n"
                "HATA: {error}\n"
                "HATA TIPI: {error_type}\n\n"
                "KOD:\n{code}\n\n"
                "ANALIZ:\n"
                "DUZELTMIS KOD:\n```python\n<kod>\n```"
            ),
            "rewrite": (
                "Bu kodun ayni islevi yapan hatasiz versiyonunu yaz.\n"
                "HATA: {error}\nORIJINAL:\n{code}\nSadece kod:"
            ),
            "debug": (
                "Adim adim debug et ve duzelt.\n"
                "HATA: {error} ({error_desc})\nKOD:\n{code}\n"
                "Adim 1 - Sorun:\nAdim 2 - Duzeletilmis kod:\n```python\n<kod>\n```"
            ),
            "fallback": (
                "ACIL! En basit cozumu bul. try/except ekle.\n"
                "HATA: {error}\nKOD:\n{code}\nSadece kod:"
            ),
        }

        previous_attempts = []
        all_fixed_codes = []

        for strategy in strategies:
            kw_context = ""
            if error_keywords:
                kw_context = f"EKSIK/HAZALI: {', '.join(error_keywords)}\n"

            prompt = strategy_templates.get(strategy, strategy_templates["direct"]).format(
                env=env_context,
                error=error_text[:300],
                error_type=error_type,
                error_desc=error_desc,
                code=data.code if not all_fixed_codes else all_fixed_codes[-1],
                keywords=kw_context,
            )

            if previous_attempts:
                prompt += "\n\nONCEKI BASARISIZ DENEMELER:\n"
                for i, prev in enumerate(previous_attempts[-3:], 1):
                    prompt += f"  {i}. Strateji={prev['s']}, Hata={prev['e'][:80]}\n"

            fix_result = _qwen_direct_query(prompt)
            if not fix_result.get("success"):
                continue

            fixed_raw = fix_result["response"].strip()
            fixed_code = _clean_qwen_code(fixed_raw)

            if not fixed_code or fixed_code == data.code or fixed_code in all_fixed_codes:
                continue

            all_fixed_codes.append(fixed_code)

            retry = _qwen_execute_in_venv(fixed_code)

            if retry["success"]:
                return {
                    "success": True,
                    "output": retry["output"],
                    "fixed_code": fixed_code,
                    "error_type": error_type,
                    "error_desc": error_desc,
                    "strategy": strategy,
                    "attempt": len(all_fixed_codes),
                    "original_error": error_text[:200],
                    "message": f"Qwen [{strategy.capitalize()}] hatayi duzeltti!"
                }

            previous_attempts.append({"s": strategy, "e": retry.get("error", "?")[:150]})

        qwen_plugin = _get_qwen_plugin()
        if qwen_plugin and hasattr(qwen_plugin, 'execute_code'):
            try:
                plugin_result = qwen_plugin.execute_code(data.code)
                if plugin_result.get("success"):
                    return plugin_result
            except Exception:
                pass

        postmortem = _qwen_direct_query(
            f"Bu Python kodundaki hatayi 1 cumleyle acikla:\nHATA: {error_text[:200]}\nKOD:\n{data.code}"
        )
        advice = postmortem.get("response", "")[:200] if postmortem.get("success") else ""

        return {
            "success": False,
            "error": error_text[:500],
            "error_type": error_type,
            "error_desc": error_desc,
            "attempts": len(all_fixed_codes),
            "advice": advice.strip(),
            "message": "Qwen 14B tum stratejileri denedi ama duzeltemedi."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sistem hatasi: {str(e)}")


@router.get("/status")
async def qwen_status():
    try:
        qwen_plugin = _get_qwen_plugin()
        if qwen_plugin and hasattr(qwen_plugin, 'get_status'):
            return qwen_plugin.get_status()

        ollama_ok = False
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = _json.loads(resp.read())
                ollama_ok = any("qwen" in m.get("name", "").lower() for m in data.get("models", []))
        except Exception:
            pass

        return {
            "name": "Qwen 14B Assistant",
            "version": "1.0.0",
            "enabled": False,
            "ollama_connected": ollama_ok,
            "model": "qwen2.5-coder:14b",
            "message_count": 0,
            "status": "Ollama bagli degil (plugin yuklu degil)",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def qwen_clear():
    try:
        qwen_plugin = _get_qwen_plugin()
        if qwen_plugin and hasattr(qwen_plugin, 'clear_history'):
            qwen_plugin.clear_history()
            return {"success": True, "message": "Gecmis temizlendi"}
        return {"success": True, "message": "Plugin yuklu degil (gecmis yok)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
