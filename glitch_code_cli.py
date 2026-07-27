#!/usr/bin/env python3
"""
GLITCH CODE - Terminal Coding Agent
Powered by Ollama + GlassesCat Models

Architecture inspired by MiMo CLI (https://github.com/KoinaAI/MiMo-CLI)

Usage:
  glitch                    Interactive TUI mode
  glitch run "task"         One-shot task
  glitch models             List available models
  glitch settings           Configure settings
  glitch doctor             System diagnostics
  glitch init               Initialize project
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

import os
import re
import json
import uuid
import difflib
import argparse
import subprocess
import textwrap
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple

import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich import box
from rich.theme import Theme
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.align import Align

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    PROMPT_TOOLKIT_OK = True
except ImportError:
    PROMPT_TOOLKIT_OK = False

# ═══════════════════════════════════════════════════════════════════
# THEME - Purple (#a855f7) replaces MiMo's cyan
# ═══════════════════════════════════════════════════════════════════

PURPLE = "#a855f7"
PURPLE_LIGHT = "#c084fc"
PURPLE_DARK = "#6b21a8"
PURPLE_PINK = "#e879f9"
GRAY_DIM = "#6b7280"
GRAY_MID = "#9ca3af"

GLITCH_THEME = Theme({
    "primary": f"bold {PURPLE}",
    "secondary": f"bold {PURPLE_LIGHT}",
    "accent": f"bold {PURPLE_PINK}",
    "success": "bold #22c55e",
    "warning": "bold #eab308",
    "error": "bold #ef4444",
    "info": f"dim {GRAY_DIM}",
    "title": "bold #ffffff",
    "code": f"bold {PURPLE_LIGHT}",
    "dim": f"dim {GRAY_DIM}",
    "gray": f"{GRAY_DIM}",
    "purple": f"{PURPLE}",
})

console = Console(theme=GLITCH_THEME)

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

APP_NAME = "Glitch Code"
APP_VERSION = "1.0.0"
CONFIG_DIR = Path.home() / ".glitch-code"
CONFIG_PATH = CONFIG_DIR / "config.json"
HISTORY_PATH = CONFIG_DIR / "history.txt"
SESSIONS_DIR = CONFIG_DIR / "sessions"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 4096

SEP = " [dim]\xb7[/] "

# ── Interaction Mode ───────────────────────────────────────────────

MODE_ICONS = {
    "agent": "\u25c6",
    "plan": "\u25c7",
    "yolo": "\u25b2",
}

MODE_LABELS = {
    "agent": f"[bold {PURPLE}]GLITCH[/]",
    "plan": "[bold #3b82f6]PLAN[/]",
    "yolo": "[bold #ef4444]YOLO[/]",
}

MODE_COLORS = {
    "agent": PURPLE,
    "plan": "#3b82f6",
    "yolo": "#ef4444",
}

# ── Sigils (same visual language as MiMo but with purple) ──────────

SIGIL_USER = f"[bold {PURPLE}]\u258e[/]"
SIGIL_ASSISTANT = f"[bold {PURPLE_LIGHT}]\u258e[/]"
SIGIL_THINKING = "[dim]>[/]"
SIGIL_TOOL = "[dim]\xb7[/]"
SIGIL_TOOL_RESULT = "[dim]\u21b3[/]"
SIGIL_SYSTEM = "[dim]\u2022[/]"
SIGIL_ERROR = "[bold #ef4444]\u2716[/]"
SIGIL_DIFF = "[bold #d946ef]\xb1[/]"

ROLE_USER = "you"
ROLE_ASSISTANT = "glitch"
ROLE_THINKING = "thinking"
ROLE_SYSTEM = "system"

# ── Model Registry ─────────────────────────────────────────────────

MODEL_REGISTRY = {
    "glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE": {
        "name": "GulmezCetiner V5",
        "desc": "Flagship \xb7 General AI \xb7 8.0 GB",
    },
    "glassesglitchstudio/gulmzcetiner:V7_HYBRID_TITAN": {
        "name": "GulmezCetiner V7",
        "desc": "Hybrid Titan \xb7 6.6 GB",
    },
    "glassesglitchstudio/gulmzcetiner:V6_OMNI_OVERLORD": {
        "name": "GulmezCetiner V6",
        "desc": "Omni Overlord \xb7 9.0 GB",
    },
    "qwen2.5-coder:14b": {
        "name": "Qwen 2.5 Coder",
        "desc": "Code Specialist \xb7 14B \xb7 9.0 GB",
    },
    "qwen2.5-coder:7b": {
        "name": "Qwen 2.5 Coder 7B",
        "desc": "Code Fast \xb7 7B \xb7 4.7 GB",
    },
    "deepseek-r1:8b": {
        "name": "DeepSeek R1",
        "desc": "Analysis \xb7 8B \xb7 5.2 GB",
    },
    "glitch_opus:latest": {
        "name": "Glitch Opus",
        "desc": "Vision + Code \xb7 6.6 GB",
    },
    "llama3.2:latest": {
        "name": "Llama 3.2",
        "desc": "Lightning Fast \xb7 2.0 GB",
    },
}

MODEL_TIERS = [
    {"tier": "Flagship", "models": [
        "glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE",
        "glassesglitchstudio/gulmzcetiner:V6_OMNI_OVERLORD",
    ]},
    {"tier": "Specialist", "models": [
        "glassesglitchstudio/gulmzcetiner:V7_HYBRID_TITAN",
        "qwen2.5-coder:14b",
        "deepseek-r1:8b",
        "glitch_opus:latest",
    ]},
    {"tier": "Fast", "models": [
        "qwen2.5-coder:7b",
        "llama3.2:latest",
    ]},
]

# ═══════════════════════════════════════════════════════════════════
# ASCII BANNER - "GLITCH CODE" in ANSI Shadow block letters
# Same style as MiMo's banner, but with "GLITCH CODE" and purple
# ═══════════════════════════════════════════════════════════════════

BANNER_LOGO = [
    r"  \u2588\u2588\u2588\u2588\u2588\u2588\u256e \u2588\u2588\u256e     \u2588\u2588\u256e\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u256e \u2588\u2588\u2588\u2588\u2588\u2588\u256e\u2588\u2588\u256e  \u2588\u2588\u256e",
    r" \u2588\u2588\u255a\u2550\u2550\u2550\u2550\u255d \u2588\u2588\u2551     \u2588\u2588\u2551\u255a\u255a\u2550\u2550\u2588\u2588\u255a\u2550\u2550\u255d\u2588\u2588\u255a\u2550\u2550\u2550\u255d\u2588\u2588\u2551  \u2588\u2588\u2551",
    r" \u2588\u2588\u2551  \u2588\u2588\u2588\u256e\u2588\u2588\u2551     \u2588\u2588\u2551   \u2588\u2588\u2551   \u2588\u2588\u2551     \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551",
    r" \u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2551     \u2588\u2588\u2551   \u2588\u2588\u2551   \u2588\u2588\u2551     \u2588\u2588\u255a\u2550\u2550\u2588\u2588\u2551",
    r" \u255a\u2588\u2588\u2588\u2588\u2588\u2588\u255a\u255d\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u256e\u2588\u2588\u2551   \u2588\u2588\u2551   \u255a\u2588\u2588\u2588\u2588\u2588\u2588\u256e\u2588\u2588\u2551  \u2588\u2588\u2551",
    r"  \u255a\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u255d   \u255a\u2550\u255d    \u255a\u2550\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u255d",
    r"",
    r"  \u2588\u2588\u2588\u2588\u2588\u2588\u256e \u2588\u2588\u2588\u2588\u2588\u2588\u256e  \u2588\u2588\u2588\u2588\u2588\u2588\u256e \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u256e",
    r" \u2588\u2588\u255a\u2550\u2550\u2550\u2550\u255d\u2588\u2588\u255a\u2550\u2550\u2550\u2588\u2588\u256e\u2588\u2588\u255a\u2550\u2550\u2588\u2588\u256e\u2588\u2588\u255a\u2550\u2550\u2550\u2550\u255d",
    r" \u2588\u2588\u2551     \u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u256e  ",
    r" \u2588\u2588\u2551     \u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u255a\u2550\u2550\u255d  ",
    r" \u255a\u2588\u2588\u2588\u2588\u2588\u2588\u256e\u255a\u2588\u2588\u2588\u2588\u2588\u2588\u255a\u255d\u2588\u2588\u2588\u2588\u2588\u2588\u255a\u255d\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u256e",
    r"  \u255a\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d",
]

BANNER = "\n".join([
    "",
    *[f"[bold {PURPLE}]{line}[/]" for line in BANNER_LOGO],
    "",
    f"  [bold {PURPLE}]Welcome to Glitch Code[/] [dim]\xb7 Intelligent Coding Agent \xb7 v{APP_VERSION}[/]",
    "",
    f"  [dim]/help for commands \xb7 /settings for config \xb7 /exit to quit[/]",
    f"  [dim]@ files \xb7 Ctrl+R history search \xb7 /keys shortcuts[/]",
    "",
])

# ── System Prompt ─────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Glitch Code, an expert coding assistant powered by GlassesCat models.
You help users write, debug, refactor, and understand code.

Available tools:
- read_file(path)     - Read a file from the workspace
- write_file(path, content) - Write content to a file
- edit_file(path, old, new) - Edit a file using exact string replacement
- glob(pattern)       - Search for files by glob pattern
- grep(pattern, path) - Search for text in files using regex
- run_shell(command)  - Execute a shell command
- list_files(path)    - List directory contents

Rules:
1. Always show the code you generate or modify
2. Explain your changes clearly
3. Use the tools available to you
4. When writing files, show a diff of changes
5. Be concise but thorough"""

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

class GlitchConfig:
    def __init__(self):
        self.data = self._load()

    def _load(self) -> dict:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        defaults = {
            "ollama_url": DEFAULT_OLLAMA_URL,
            "model": DEFAULT_MODEL,
            "temperature": DEFAULT_TEMPERATURE,
            "max_tokens": DEFAULT_MAX_TOKENS,
        }
        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                defaults.update(data)
            except Exception:
                pass
        return defaults

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value
        self.save()

    def interactive_setup(self):
        console.print()
        console.print(Panel(
            f"[bold {PURPLE}]  Glitch Code Configuration[/]",
            box=box.ROUNDED,
            border_style=PURPLE,
        ))
        url = Prompt.ask(
            "Ollama URL",
            default=self.get("ollama_url", DEFAULT_OLLAMA_URL),
        )
        self.set("ollama_url", url)

        models = self._fetch_models(url)
        if models:
            console.print(f"\n[secondary]Available models:[/]")
            for m in models:
                info = MODEL_REGISTRY.get(m, {})
                desc = info.get("desc", "")
                if desc:
                    console.print(f"   [code]{m}[/] [dim]({desc})[/]")
                else:
                    console.print(f"   [code]{m}[/]")
            model = Prompt.ask("Select model", default=self.get("model", DEFAULT_MODEL))
        else:
            model = Prompt.ask("Model name", default=self.get("model", DEFAULT_MODEL))

        self.set("model", model)

        temp = Prompt.ask(
            "Temperature",
            default=str(self.get("temperature", DEFAULT_TEMPERATURE)),
        )
        self.set("temperature", float(temp))

        console.print(f"[success] Configuration saved![/]")

    def _fetch_models(self, url: str) -> List[str]:
        try:
            resp = requests.get(f"{url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

# ═══════════════════════════════════════════════════════════════════
# OLLAMA CLIENT
# ═══════════════════════════════════════════════════════════════════

class OllamaClient:
    def __init__(self, config: GlitchConfig):
        self.config = config

    @property
    def base_url(self) -> str:
        return self.config.get("ollama_url", DEFAULT_OLLAMA_URL)

    @property
    def model(self) -> str:
        return self.config.get("model", DEFAULT_MODEL)

    def chat(self, messages: List[dict], stream: bool = True):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": self.config.get("temperature", DEFAULT_TEMPERATURE),
                "num_predict": self.config.get("max_tokens", DEFAULT_MAX_TOKENS),
            },
        }
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=stream,
            timeout=120,
        )
        resp.raise_for_status()
        if stream:
            return self._stream_response(resp)
        data = resp.json()
        return data.get("message", {}).get("content", "")

    def _stream_response(self, resp):
        full = ""
        for line in resp.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    full += content
                    yield content
                except json.JSONDecodeError:
                    pass
        yield full

    def check_available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[dict]:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                return resp.json().get("models", [])
        except Exception:
            pass
        return []

# ═══════════════════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════════════════

class ToolResult:
    def __init__(self, success: bool, output: str, error: str = ""):
        self.success = success
        self.output = output
        self.error = error

class Tools:
    def __init__(self, workspace: str):
        self.workspace = Path(workspace).resolve()

    def _validate_path(self, path: str) -> Optional[Path]:
        full = (self.workspace / path).resolve()
        try:
            full.relative_to(self.workspace)
            return full
        except ValueError:
            return None

    def read_file(self, path: str) -> ToolResult:
        full = self._validate_path(path)
        if not full:
            return ToolResult(False, "", f"Access denied: {path} is outside workspace")
        if not full.exists():
            return ToolResult(False, "", f"File not found: {path}")
        try:
            content = full.read_text(encoding="utf-8")
            return ToolResult(True, content)
        except Exception as e:
            return ToolResult(False, "", str(e))

    def write_file(self, path: str, content: str) -> ToolResult:
        full = self._validate_path(path)
        if not full:
            return ToolResult(False, "", f"Access denied: {path} is outside workspace")
        try:
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            return ToolResult(True, f"Written {len(content)} bytes to {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))

    def edit_file(self, path: str, old_str: str, new_str: str) -> ToolResult:
        full = self._validate_path(path)
        if not full:
            return ToolResult(False, "", f"Access denied: {path} is outside workspace")
        if not full.exists():
            return ToolResult(False, "", f"File not found: {path}")
        try:
            content = full.read_text(encoding="utf-8")
            if old_str not in content:
                return ToolResult(False, "", f"String not found in {path}")
            count = content.count(old_str)
            new_content = content.replace(old_str, new_str)
            full.write_text(new_content, encoding="utf-8")
            diff = list(difflib.unified_diff(
                content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=path,
                tofile=path,
            ))
            diff_text = "".join(diff)
            return ToolResult(True, f"Replaced {count} occurrence(s) in {path}\n\n{diff_text}")
        except Exception as e:
            return ToolResult(False, "", str(e))

    def glob_files(self, pattern: str) -> ToolResult:
        try:
            results = [
                str(p.relative_to(self.workspace))
                for p in self.workspace.rglob(pattern)
                if p.is_file()
            ]
            return ToolResult(True, "\n".join(results) if results else "No files found")
        except Exception as e:
            return ToolResult(False, "", str(e))

    def grep(self, pattern: str, path: str = ".") -> ToolResult:
        full = self._validate_path(path)
        if not full:
            return ToolResult(False, "", f"Access denied: {path} is outside workspace")
        if not full.exists():
            return ToolResult(False, "", f"Path not found: {path}")
        try:
            results = []
            regex = re.compile(pattern)
            target_suffixes = {
                ".py", ".js", ".ts", ".html", ".css", ".json",
                ".md", ".txt", ".jsx", ".tsx", ".yml", ".yaml",
                ".toml", ".ini", ".cfg", ".conf", ".env", ".sh",
                ".bat", ".ps1", ".rs", ".go", ".java", ".c",
                ".cpp", ".h", ".hpp", ".sql", ".rb", ".php",
            }
            for p in full.rglob("*"):
                if p.is_file() and p.suffix in target_suffixes:
                    try:
                        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                            if regex.search(line):
                                rel = p.relative_to(self.workspace)
                                results.append(f"{rel}:{i}: {line.strip()}")
                    except Exception:
                        pass
            return ToolResult(True, "\n".join(results[:200]) if results else "No matches found")
        except Exception as e:
            return ToolResult(False, "", str(e))

    def list_files(self, path: str = ".") -> ToolResult:
        full = self._validate_path(path)
        if not full:
            return ToolResult(False, "", f"Access denied: {path} is outside workspace")
        if not full.exists():
            return ToolResult(False, "", f"Path not found: {path}")
        try:
            items = []
            for p in sorted(full.iterdir()):
                name = p.name + "/" if p.is_dir() else p.name
                items.append(name)
            return ToolResult(True, "\n".join(items) if items else "Empty directory")
        except Exception as e:
            return ToolResult(False, "", str(e))

    def run_shell(self, command: str) -> ToolResult:
        dangerous = [
            "rm -rf /", "format ", "del /s", "rd /s",
            "mkfs", "dd if=", "chmod 777 /", ":(){ :|:& };:",
        ]
        cmd_lower = command.lower()
        for d in dangerous:
            if d in cmd_lower:
                return ToolResult(False, "", f"Dangerous command blocked: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.workspace),
            )
            output = result.stdout or ""
            if result.stderr:
                output += "\n[stderr]\n" + result.stderr
            return ToolResult(
                result.returncode == 0,
                output[:2000],
                result.stderr[:1000] if result.returncode != 0 else "",
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, "", "Command timed out after 30s")
        except Exception as e:
            return ToolResult(False, "", str(e))

TOOL_DEFINITIONS = [
    {"name": "read_file", "fn": "read_file(path)"},
    {"name": "write_file", "fn": "write_file(path, content)"},
    {"name": "edit_file", "fn": "edit_file(path, old, new)"},
    {"name": "glob", "fn": "glob(pattern)"},
    {"name": "grep", "fn": "grep(pattern, path)"},
    {"name": "run_shell", "fn": "run_shell(command)"},
    {"name": "list_files", "fn": "list_files(path)"},
]

# ═══════════════════════════════════════════════════════════════════
# AGENT
# ═══════════════════════════════════════════════════════════════════

class CodeAgent:
    def __init__(self, config: GlitchConfig, workspace: str, mode: str = "agent"):
        self.config = config
        self.llm = OllamaClient(config)
        self.tools = Tools(workspace)
        self.workspace = workspace
        self.mode = mode
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.tool_call_count = 0

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def run(self, user_input: str, stream_callback: Callable = None) -> str:
        self.add_message("user", user_input)
        full_response = ""
        for chunk in self.llm.chat(self.messages):
            if isinstance(chunk, str):
                full_response += chunk
                if stream_callback:
                    stream_callback(chunk)
        self.add_message("assistant", full_response)
        return full_response

    def process_tool_call(self, text: str) -> Optional[str]:
        tool_patterns = [
            (r"read_file\(['\"](.+?)['\"]\)", self.tools.read_file),
            (r"write_file\(['\"](.+?)['\"],\s*['\"](.+?)['\"]\)", self.tools.write_file),
            (r"edit_file\(['\"](.+?)['\"],\s*['\"](.+?)['\"],\s*['\"](.+?)['\"]\)", self.tools.edit_file),
            (r"glob\(['\"](.+?)['\"]\)", self.tools.glob_files),
            (r"grep\(['\"](.+?)['\"],\s*['\"](.+?)['\"]\)", self.tools.grep),
            (r"run_shell\(['\"](.+?)['\"]\)", self.tools.run_shell),
            (r"list_files\(['\"](.+?)['\"]\)", self.tools.list_files),
        ]

        for pattern, func in tool_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                self.tool_call_count += 1
                args = match.groups()
                result = func(*args)
                if result.success:
                    return f"Tool result:\n{result.output}"
                return f"Tool error: {result.error}"
        return None

# ═══════════════════════════════════════════════════════════════════
# INTERACTIVE TUI
# ═══════════════════════════════════════════════════════════════════

def format_status_line(
    config: GlitchConfig,
    agent: CodeAgent,
    session_id: str,
    cwd: str,
    mode: str = "agent",
) -> str:
    model_short = config.get("model", DEFAULT_MODEL)
    if "/" in model_short:
        model_short = model_short.split("/")[-1]
    parts = [
        f'{MODE_ICONS.get(mode, "\u25c6")} {MODE_LABELS.get(mode, "GLITCH")}',
        f"[yellow]{model_short}[/]",
        f"[dim]ollama[/]",
        f"[{PURPLE}]{len(TOOL_DEFINITIONS)} tools[/]",
        f"[dim]session {session_id[:8]}[/]",
        f"[dim]{_shorten_path(cwd)}[/]",
    ]
    return SEP.join(parts)

def _shorten_path(cwd: str) -> str:
    home = str(Path.home())
    if cwd.startswith(home):
        return "~" + cwd[len(home):]
    return cwd

def print_splash():
    console.print(BANNER)

def print_help():
    console.print(Panel(
        f"[bold {PURPLE_LIGHT}]Commands:[/]\n"
        f"  [bold {PURPLE}]/help[/]      [dim]- Show this help[/]\n"
        f"  [bold {PURPLE}]/models[/]    [dim]- List available models[/]\n"
        f"  [bold {PURPLE}]/model <n>[/] [dim]- Switch model[/]\n"
        f"  [bold {PURPLE}]/mode[/]      [dim]- Toggle interaction mode[/]\n"
        f"  [bold {PURPLE}]/clear[/]     [dim]- Clear conversation[/]\n"
        f"  [bold {PURPLE}]/workspace[/] [dim]- Show workspace[/]\n"
        f"  [bold {PURPLE}]/settings[/]  [dim]- Open settings[/]\n"
        f"  [bold {PURPLE}]/save <n>[/]  [dim]- Save session[/]\n"
        f"  [bold {PURPLE}]/status[/]    [dim]- Show status[/]\n"
        f"  [bold {PURPLE}]/exit[/]      [dim]- Exit[/]\n"
        f"\n[bold {PURPLE_LIGHT}]Built-in Tools:[/]\n"
        f"  [bold {PURPLE}]read_file('path')[/]        [dim]- Read a file[/]\n"
        f"  [bold {PURPLE}]write_file('p','c')[/]      [dim]- Write a file[/]\n"
        f"  [bold {PURPLE}]edit_file('p','o','n')[/]   [dim]- Edit a file[/]\n"
        f"  [bold {PURPLE}]glob('*.py')[/]              [dim]- Search files[/]\n"
        f"  [bold {PURPLE}]grep('p','path')[/]          [dim]- Search in files[/]\n"
        f"  [bold {PURPLE}]run_shell('cmd')[/]          [dim]- Run a command[/]\n"
        f"  [bold {PURPLE}]list_files('dir')[/]         [dim]- List directory[/]",
        border_style=PURPLE,
        box=box.ROUNDED,
        title=f"[bold {PURPLE_LIGHT}]Help[/]",
    ))

def print_model_table(models: List[dict]):
    table = Table(
        title=f"[bold {PURPLE}]Available Models[/]",
        box=box.ROUNDED,
        header_style=f"bold {PURPLE_LIGHT}",
        border_style=GRAY_DIM,
    )
    table.add_column("Model", style="bold")
    table.add_column("Size", style="dim")
    table.add_column("Family")
    table.add_column("Quantization")

    for m in models:
        details = m.get("details", {})
        name = m["name"]
        size = m.get("size", 0)
        size_str = f"{size / 1e9:.1f} GB" if size else "?"
        family = details.get("family", "-")
        quant = details.get("quantization_level", "-")
        table.add_row(name, size_str, family, quant)

    console.print(table)

def print_mode_info(current_mode: str):
    console.print(f"[dim]Current mode:[/] {MODE_ICONS.get(current_mode, '?')} {MODE_LABELS.get(current_mode, 'UNKNOWN')}")

def interactive_mode(config: GlitchConfig, workspace: str):
    if not PROMPT_TOOLKIT_OK:
        console.print("[error]prompt_toolkit is required for interactive mode[/]")
        console.print("[dim]pip install prompt_toolkit[/]")
        return

    session_id = str(uuid.uuid4())
    current_mode = "agent"
    agent = CodeAgent(config, workspace, mode=current_mode)

    history_path = HISTORY_PATH
    history_path.parent.mkdir(parents=True, exist_ok=True)
    if not history_path.exists():
        history_path.write_text("", encoding="utf-8")

    prompt_session = PromptSession(
        history=FileHistory(str(history_path)),
        auto_suggest=AutoSuggestFromHistory(),
    )

    os.system("cls" if os.name == "nt" else "clear")
    print_splash()

    status = format_status_line(config, agent, session_id, workspace, current_mode)
    console.print(Panel(
        status,
        border_style=PURPLE_DARK,
        box=box.ROUNDED,
    ))
    console.print()

    console.print(f"[dim]Enter send \xb7 Ctrl+J newline \xb7 Tab switches mode \xb7 /help \xb7 /keys[/]")
    console.print()

    while True:
        mode_icon = MODE_ICONS.get(current_mode, "\u25c6")
        prompt_text = f"\n[bold {PURPLE}]{mode_icon} glitch[/][[bold {PURPLE_LIGHT}]~[/]]$ "

        try:
            user_input = prompt_session.prompt(ANSI(str(
                Text.from_markup(prompt_text)
            )) if False else prompt_text)
        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[bold {PURPLE}]Session saved. Goodbye![/]")
            break

        if not user_input.strip():
            continue

        if user_input.startswith("/"):
            cmd = user_input[1:].strip().lower()
            args = cmd.split()
            cmd_base = args[0] if args else ""
            cmd_rest = " ".join(args[1:]) if len(args) > 1 else ""

            if cmd_base in ("exit", "quit", "q"):
                console.print(f"[bold {PURPLE}]Session saved. Goodbye![/]")
                session_path = SESSIONS_DIR / f"{session_id[:8]}.json"
                SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
                session_path.write_text(
                    json.dumps({
                        "id": session_id,
                        "mode": current_mode,
                        "messages": agent.messages,
                        "updated_at": datetime.now().isoformat(),
                    }, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                break

            elif cmd_base == "help":
                print_help()

            elif cmd_base == "models":
                client = OllamaClient(config)
                if not client.check_available():
                    console.print(f"[error] Ollama not available at {client.base_url}[/]")
                else:
                    models = client.list_models()
                    print_model_table(models)
                    console.print(f"\n[info]Total: {len(models)} models[/]")

            elif cmd_base == "model" and cmd_rest:
                config.set("model", cmd_rest)
                agent = CodeAgent(config, workspace, mode=current_mode)
                console.print(f"[bold {PURPLE}]Switched to model:[/] [bold {PURPLE_LIGHT}]{cmd_rest}[/]")

            elif cmd_base == "mode":
                modes = ["agent", "plan", "yolo"]
                idx = (modes.index(current_mode) + 1) % len(modes) if current_mode in modes else 0
                current_mode = modes[idx]
                agent.mode = current_mode
                console.print(f"[bold {PURPLE}]Switched to mode:[/] {MODE_ICONS[current_mode]} {MODE_LABELS[current_mode]}")

            elif cmd_base == "clear":
                agent.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                agent.tool_call_count = 0
                console.print(f"[bold {PURPLE}]Conversation cleared[/]")

            elif cmd_base == "workspace":
                console.print(f"[code]{workspace}[/]")

            elif cmd_base == "settings":
                config.interactive_setup()

            elif cmd_base == "save" and cmd_rest:
                path = SESSIONS_DIR / f"{cmd_rest}.json"
                SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps(agent.messages, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                console.print(f"[bold {PURPLE}]Session saved:[/] [bold {PURPLE_LIGHT}]{path.name}[/]")

            elif cmd_base == "status":
                status = format_status_line(config, agent, session_id, workspace, current_mode)
                console.print(status)

            else:
                console.print(f"[error]Unknown command: /{cmd_base}[/]")
            continue

        # --- Process user message ---
        console.print(f"\n{SIGIL_USER} [bold]{ROLE_USER}[/]")
        console.print(f"  {user_input}")

        console.print(f"\n{SIGIL_ASSISTANT} [bold]{ROLE_ASSISTANT}[/]")

        response_text = ""
        with console.status(f"[bold {PURPLE_LIGHT}]Thinking...[/]", spinner="dots"):
            try:
                for chunk in agent.llm.chat([
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input},
                ]):
                    if isinstance(chunk, str):
                        response_text += chunk
            except requests.exceptions.ConnectionError:
                console.print(f"\n{SIGIL_ERROR} [error]Cannot connect to Ollama at {agent.llm.base_url}[/]")
                console.print(f"  [dim]Make sure Ollama is running: [code]ollama serve[/][/]")
                continue
            except Exception as e:
                console.print(f"\n{SIGIL_ERROR} [error]{str(e)}[/]")
                continue

        # Check for tool calls in the response
        tool_result = agent.process_tool_call(response_text)
        if tool_result:
            console.print(f"\n{SIGIL_TOOL_RESULT} [dim]tool result[/]")
            console.print(Panel(
                tool_result[:2000],
                border_style=PURPLE,
                box=box.ROUNDED,
                title=f"[bold {PURPLE_LIGHT}]Tool Result[/]",
            ))
        else:
            try:
                md = Markdown(response_text)
                console.print(f"  ", end="")
                console.print(md)
            except Exception:
                console.print(f"  {response_text}")

        # Update agent history
        agent.add_message("user", user_input)
        agent.add_message("assistant", response_text)

# ═══════════════════════════════════════════════════════════════════
# ONE-SHOT RUN
# ═══════════════════════════════════════════════════════════════════

def run_task(config: GlitchConfig, task: str, workspace: str):
    agent = CodeAgent(config, workspace)
    console.print(f"[dim]Task:[/] [code]{task}[/]")
    console.print()

    response_text = ""
    with console.status(f"[bold {PURPLE_LIGHT}]Thinking...[/]", spinner="dots"):
        try:
            for chunk in agent.llm.chat(agent.messages + [{"role": "user", "content": task}]):
                if isinstance(chunk, str):
                    response_text += chunk
        except requests.exceptions.ConnectionError:
            console.print(f"[error]Cannot connect to Ollama at {agent.llm.base_url}[/]")
            console.print(f"[dim]Make sure Ollama is running: [code]ollama serve[/code][/]")
            return
        except Exception as e:
            console.print(f"[error]{str(e)}[/]")
            return

    tool_result = agent.process_tool_call(response_text)
    if tool_result:
        console.print(Panel(
            tool_result[:5000],
            border_style="#22c55e",
            box=box.ROUNDED,
            title="[success]Result[/]",
        ))
    else:
        try:
            md = Markdown(response_text)
            console.print(md)
        except Exception:
            console.print(response_text)

# ═══════════════════════════════════════════════════════════════════
# SETTINGS MODE
# ═══════════════════════════════════════════════════════════════════

def settings_mode(config: GlitchConfig):
    console.print()
    console.print(f"[bold {PURPLE}]  Glitch Code Configuration[/]")
    console.print()
    config.interactive_setup()

# ═══════════════════════════════════════════════════════════════════
# MODELS MODE
# ═══════════════════════════════════════════════════════════════════

def models_mode(config: GlitchConfig):
    client = OllamaClient(config)
    if not client.check_available():
        console.print(f"[error] Ollama not available at {client.base_url}[/]")
        console.print(f"[dim]Make sure Ollama is running: [code]ollama serve[/code][/]")
        return
    models = client.list_models()
    print_model_table(models)
    console.print(f"\n[info]Total: {len(models)} models[/]")

    console.print(f"\n[dim]Tip: use [bold {PURPLE}]/model <name>[/] to switch[/]")

# ═══════════════════════════════════════════════════════════════════
# DOCTOR MODE
# ═══════════════════════════════════════════════════════════════════

def doctor_mode(config: GlitchConfig):
    console.print()
    console.print(f"[bold {PURPLE}]  System Diagnostics[/]")
    console.print()

    issues = []

    # Ollama check
    ollama = OllamaClient(config)
    if ollama.check_available():
        console.print(f"  [success] [/] [code]{config.get('ollama_url')}[/]  Ollama is running")
    else:
        console.print(f"  [error] [/] [code]{config.get('ollama_url')}[/]  Ollama not reachable")
        issues.append("Ollama is not running")

    # Model check
    models = ollama.list_models()
    model_name = config.get("model")
    if any(m["name"] == model_name for m in models):
        console.print(f"  [success] [/] Model [code]{model_name}[/]  available locally")
    else:
        console.print(f"  [warning] [/] Model [code]{model_name}[/]  not found locally (will pull on demand)")
        issues.append(f"Model {model_name} not downloaded")

    # Config check
    if CONFIG_PATH.exists():
        console.print(f"  [success] [/] Config: [code]{CONFIG_PATH}[/]")
    else:
        console.print(f"  [info] [/] Config not found, will use defaults")

    # Python version
    py_ver = sys.version
    console.print(f"  [success] [/] Python [code]{py_ver.split()[0]}[/]")

    # Package checks
    pkgs = {"rich": True, "requests": True, "prompt_toolkit": PROMPT_TOOLKIT_OK}
    for pkg, ok in pkgs.items():
        icon = "[success] [/]" if ok else "[error] [/]"
        console.print(f"  {icon}[code]{pkg}[/]")

    console.print()
    if issues:
        console.print(f"[warning] Issues found:[/]")
        for i in issues:
            console.print(f"   {i}")
    else:
        console.print(f"[success] All systems ready![/]")

# ═══════════════════════════════════════════════════════════════════
# INIT MODE
# ═══════════════════════════════════════════════════════════════════

def init_project(workspace: str):
    ws = Path(workspace).resolve()
    glitch_dir = ws / ".glitch-code"
    glitch_dir.mkdir(parents=True, exist_ok=True)

    agents_md = ws / "AGENTS.md"
    if not agents_md.exists():
        agents_md.write_text(
            f"# Glitch Code - Project Context\n\n"
            f"Project initialized on {datetime.now().strftime('%Y-%m-%d')}\n",
            encoding="utf-8",
        )

    console.print(f"[success] Initialized Glitch Code in {ws}[/]")
    console.print(f"  [dim]Created:[/] [code]{glitch_dir}/[/]")
    console.print(f"  [dim]Created:[/] [code]{agents_md}[/]")

# ═══════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

def main():
    config = GlitchConfig()

    parser = argparse.ArgumentParser(
        description="Glitch Code - Terminal Coding Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              glitch                      Start interactive session
              glitch run "Refactor main.py"  One-shot task
              glitch models               List Ollama models
              glitch settings             Configure
              glitch doctor               System check
              glitch init                 Initialize project
        """),
    )

    parser.add_argument("-C", "--cwd", default=os.getcwd(), help="Working directory")
    parser.add_argument("--model", help="Model to use")

    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Run a task non-interactively")
    run_p.add_argument("task", nargs="+", help="Task description")

    sub.add_parser("settings", help="Configure settings")
    sub.add_parser("models", help="List available models")
    sub.add_parser("doctor", help="System diagnostics")
    sub.add_parser("init", help="Initialize project")

    args = parser.parse_args()

    workspace = str(Path(args.cwd).resolve())

    if args.model:
        config.set("model", args.model)

    if args.command == "settings":
        settings_mode(config)
    elif args.command == "models":
        models_mode(config)
    elif args.command == "doctor":
        doctor_mode(config)
    elif args.command == "init":
        init_project(workspace)
    elif args.command == "run":
        task = " ".join(args.task)
        interactive_mode(config, workspace)
    else:
        interactive_mode(config, workspace)

if __name__ == "__main__":
    main()
