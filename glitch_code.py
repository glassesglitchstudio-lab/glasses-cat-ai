#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     GLITCHCODE CLI — AI Coding Agent (MiMo-style)               ║
║     Python tabanlı, Ollama destekli kod yazma asistanı          ║
║                                                                  ║
║     Kullanım:                                                    ║
║       glitch                      → interaktif CLI               ║
║       glitch "dosya.py yaz"       → tek seferlik komut           ║
║       glitch --model qwen2.5-coder → model seç                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os, sys, json, re, time, uuid, datetime, threading, subprocess, shutil, fnmatch, textwrap, traceback
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field

try:
    import requests
except ImportError:
    print("[!] 'requests' gerekli. pip install requests")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.spinner import Spinner
    from rich import box
    RICH_OK = True
except ImportError:
    RICH_OK = False

# ── Konfigürasyon ─────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".glitchcode"
CONFIG_PATH = CONFIG_DIR / "config.json"
HISTORY_PATH = CONFIG_DIR / "history.json"
SESSIONS_DIR = CONFIG_DIR / "sessions"
OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE"

C = Console() if RICH_OK else None

COLORS = {
    "system": "bold blue",
    "user": "bold green",
    "ai": "bold cyan",
    "error": "bold red",
    "warning": "bold yellow",
    "tool": "bold magenta",
    "success": "bold green",
    "info": "dim white",
}

BANNER = """
[bold cyan]
   ┌─────────────────────────────────────────────┐
   │  ░▒▓█ GLITCHCODE CLI █▓▒░                   │
   │  AI Coding Agent — Ollama Destekli          │
   └─────────────────────────────────────────────┘
[/bold cyan]
"""

# ── Config ────────────────────────────────────────────────────────

def load_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except:
        return {"model": DEFAULT_MODEL, "ollama_url": OLLAMA_URL, "temperature": 0.0, "system_prompt": ""}

def save_config(updates: dict):
    cfg = load_config()
    cfg.update(updates)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")

# ── Ollama ────────────────────────────────────────────────────────

def ollama_list() -> List[dict]:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if r.status_code == 200:
            return r.json().get("models", [])
    except:
        pass
    return []

def ollama_chat(model: str, messages: list, stream: bool = False, temperature: float = 0.0, timeout: int = 120):
    url = f"{OLLAMA_URL}/api/chat"
    payload = {"model": model, "messages": messages, "stream": stream, "options": {"temperature": temperature}}
    try:
        if stream:
            r = requests.post(url, json=payload, stream=True, timeout=timeout)
            r.encoding = "utf-8"
            for line in r.iter_lines(decode_unicode=True):
                if line:
                    try:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]
                        if chunk.get("done"):
                            break
                    except:
                        pass
        else:
            r = requests.post(url, json=payload, timeout=timeout)
            if r.status_code == 200:
                return r.json()["message"]["content"]
            return f"[Hata] HTTP {r.status_code}"
    except Exception as e:
        return f"[Hata] {e}"

# ── Tools ─────────────────────────────────────────────────────────

WORKSPACE_ROOT = Path.cwd().resolve()

def _in_workspace(path: str) -> bool:
    try:
        return WORKSPACE_ROOT in Path(path).resolve().parents or Path(path).resolve() == WORKSPACE_ROOT
    except:
        return False

TOOLS = {}

def tool(name: str, description: str):
    def deco(f):
        TOOLS[name] = {"fn": f, "description": description, "name": name}
        return f
    return deco

@tool("read_file", "Read a file from the workspace")
def tool_read_file(filepath: str) -> str:
    p = Path(filepath)
    if not p.exists():
        return f"[Hata] Dosya bulunamadı: {filepath}"
    if not _in_workspace(str(p)):
        return "[Hata] Çalışma alanı dışındaki dosyalara erişim izni yok"
    try:
        content = p.read_text(encoding="utf-8")
        lines = content.splitlines()
        max_preview = 200
        if len(lines) > max_preview:
            return f"{''.join([f'{i+1:>4}| {l}\n' for i,l in enumerate(lines[:max_preview//2])])}\n... ({len(lines)-max_preview} satır daha) ...\n\n{''.join([f'{i+1:>4}| {l}\n' for i,l in enumerate(lines[-max_preview//2:])])}"
        return "".join([f"{i+1:>4}| {l}\n" for i, l in enumerate(lines)])
    except Exception as e:
        return f"[Hata] Dosya okunamadı: {e}"

@tool("write_file", "Write content to a file in the workspace")
def tool_write_file(filepath: str, content: str) -> str:
    p = Path(filepath)
    if not _in_workspace(str(p)):
        return "[Hata] Çalışma alanı dışına yazma izni yok"
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"[OK] {filepath} yazıldı ({len(content)} bytes)"
    except Exception as e:
        return f"[Hata] Dosya yazılamadı: {e}"

@tool("edit_file", "Edit a file by replacing exact text")
def tool_edit_file(filepath: str, old_string: str, new_string: str) -> str:
    p = Path(filepath)
    if not p.exists():
        return f"[Hata] Dosya bulunamadı: {filepath}"
    try:
        content = p.read_text(encoding="utf-8")
        if old_string not in content:
            return f"[Hata] Eşleşen metin bulunamadı"
        new_content = content.replace(old_string, new_string, 1)
        p.write_text(new_content, encoding="utf-8")
        return f"[OK] {filepath} düzenlendi"
    except Exception as e:
        return f"[Hata] Düzenleme başarısız: {e}"

@tool("search_text", "Search for text in workspace files using glob pattern")
def tool_search_text(pattern: str, glob_pattern: str = "**/*") -> str:
    results = []
    try:
        for p in WORKSPACE_ROOT.glob(glob_pattern):
            if p.is_file() and p.stat().st_size < 1024 * 1024:
                try:
                    for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                        if pattern.lower() in line.lower():
                            rel = p.relative_to(WORKSPACE_ROOT)
                            results.append(f"{rel}:{i}: {line.strip()[:120]}")
                except:
                    pass
    except:
        pass
    if not results:
        return "Eşleşme bulunamadı"
    return "\n".join(results[:50])

@tool("list_files", "List files in a directory")
def tool_list_files(path: str = ".") -> str:
    p = (WORKSPACE_ROOT / path).resolve()
    if not _in_workspace(str(p)):
        return "[Hata] Çalışma alanı dışı"
    if not p.exists():
        return "[Hata] Dizin bulunamadı"
    try:
        items = list(p.iterdir())
        dirs = sorted([x.name + "/" for x in items if x.is_dir()])
        files = sorted([x.name for x in items if x.is_file()])
        return "\n".join(dirs + files)
    except Exception as e:
        return f"[Hata] {e}"

@tool("run_command", "Run a shell command in the workspace")
def tool_run_command(command: str) -> str:
    dangerous = ["rmdir /s", "del /f /s", "format", "rd /s", "shutdown"]
    if any(d in command.lower() for d in dangerous):
        return "[Güvenlik] Bu komut tehlikeli olarak işaretlendi ve engellendi"
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=str(WORKSPACE_ROOT))
        out = r.stdout or ""
        err = r.stderr or ""
        if err:
            out += f"\n[STDERR]\n{err}"
        return out[:3000] if out else "(boş çıktı)"
    except subprocess.TimeoutExpired:
        return "[Hata] Komut zaman aşımı"
    except Exception as e:
        return f"[Hata] {e}"

@tool("create_file", "Create a new file with optional content")
def tool_create_file(filepath: str, content: str = "") -> str:
    return tool_write_file(filepath, content)

@tool("delete_file", "Delete a file from the workspace")
def tool_delete_file(filepath: str) -> str:
    p = Path(filepath)
    if not _in_workspace(str(p)):
        return "[Hata] Çalışma alanı dışı"
    if not p.exists():
        return "[Hata] Dosya bulunamadı"
    try:
        p.unlink()
        return f"[OK] {filepath} silindi"
    except Exception as e:
        return f"[Hata] {e}"

# ── System Prompt ─────────────────────────────────────────────────

SYSTEM_PROMPT = """You are GLITCHCODE, an AI coding assistant running in a terminal.
You have access to these tools:
- read_file: Read file contents
- write_file: Write content to a file
- edit_file: Replace exact text in a file
- search_text: Search for text across workspace files
- list_files: List directory contents
- run_command: Execute shell commands
- create_file: Create a new file
- delete_file: Delete a file

Rules:
1. Always work within the current workspace directory.
2. For coding tasks, write clean, working code with proper error handling.
3. When editing files, show the changes you made.
4. If a tool fails, try an alternative approach.
5. You can use multiple tools sequentially to complete a task.

You respond in a concise, helpful manner. Show code with proper syntax."""

TOOL_DESC = """Available tools:
{tools}

When you need to use a tool, respond with:
TOOL_CALL: tool_name
Arguments as JSON on the next lines.
The tool result will be provided after.

Example:
TOOL_CALL: read_file
{{"filepath": "main.py"}}

Then after seeing the result, continue your analysis."""

# ── Session ───────────────────────────────────────────────────────

@dataclass
class Session:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    messages: List[dict] = field(default_factory=list)
    model: str = DEFAULT_MODEL

    def save(self):
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        (SESSIONS_DIR / f"{self.id}.json").write_text(
            json.dumps({"id": self.id, "created": self.created, "model": self.model, "messages": self.messages},
                       indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def load(sid: str) -> Optional["Session"]:
        p = SESSIONS_DIR / f"{sid}.json"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            return Session(id=data["id"], created=data["created"], messages=data["messages"], model=data.get("model", DEFAULT_MODEL))
        return None

    @staticmethod
    def list_sessions() -> List[dict]:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        sessions = []
        for p in sorted(SESSIONS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            data = json.loads(p.read_text(encoding="utf-8"))
            sessions.append({"id": data["id"], "created": data["created"], "model": data.get("model", "?"), "msg_count": len(data.get("messages", []))})
        return sessions

# ── Tool Call Parser ──────────────────────────────────────────────

TOOL_CALL_RE = re.compile(r"TOOL_CALL:\s*(\w+)", re.IGNORECASE)
JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*\n(.*?)\n```", re.DOTALL)

def extract_tool_call(text: str) -> Optional[tuple]:
    m = TOOL_CALL_RE.search(text)
    if m:
        tool_name = m.group(1).lower()
        rest = text[m.end():]
        jm = JSON_BLOCK_RE.search(rest)
        if jm:
            try:
                args = json.loads(jm.group(1))
                return tool_name, args
            except:
                pass
        try:
            args = json.loads(rest.strip())
            return tool_name, args
        except:
            pass
    return None

def execute_tool_call(tool_name: str, args: dict) -> str:
    if tool_name not in TOOLS:
        return f"[Hata] Bilinmeyen araç: {tool_name}. Kullanılabilir: {', '.join(TOOLS.keys())}"
    try:
        return TOOLS[tool_name]["fn"](**args)
    except TypeError as e:
        return f"[Hata] Argüman hatası: {e}"
    except Exception as e:
        return f"[Hata] {e}"

# ── CLI Engine ────────────────────────────────────────────────────

TOOL_LIST_STR = "\n".join(f"  {n} - {t['description']}" for n, t in TOOLS.items())

def build_system_prompt(custom_prompt: str = "") -> str:
    base = custom_prompt or SYSTEM_PROMPT
    return base + "\n\n" + TOOL_DESC.format(tools=TOOL_LIST_STR)

def chat_completion(messages: list, model: str, temperature: float, custom_prompt: str = "") -> str:
    full_messages = [{"role": "system", "content": build_system_prompt(custom_prompt)}]
    full_messages.extend(messages)
    return ollama_chat(model, full_messages, stream=False, temperature=temperature)

def chat_completion_stream(messages: list, model: str, temperature: float, custom_prompt: str = "") -> str:
    full_messages = [{"role": "system", "content": build_system_prompt(custom_prompt)}]
    full_messages.extend(messages)
    result = ""
    for chunk in ollama_chat(model, full_messages, stream=True, temperature=temperature):
        if chunk:
            result += chunk
            if RICH_OK:
                C.out(chunk, end="")
            else:
                sys.stdout.write(chunk)
                sys.stdout.flush()
    return result

# ── Interactive Mode ──────────────────────────────────────────────

def interactive_mode(model: str, temperature: float, custom_prompt: str = "", session_id: Optional[str] = None):
    session = Session.load(session_id) if session_id else Session(model=model)
    if session_id:
        session.model = model
        print(f"\n  ↻ Session devam: {session_id}")
    else:
        print(f"\n  ✦ Yeni session: {session.id}")

    messages = session.messages[:]
    message_count = len(messages) // 2

    if message_count > 0:
        print(f"  ↻ {message_count} mesaj devam ediyor\n")

    print(f"  Model: {model}")
    print(f"  Çalışma dizini: {WORKSPACE_ROOT}")
    print(f"  {'='*50}")
    print("  /help → komutlar | /exit → çık | /model <ad> | /save | /sessions")
    print(f"  {'='*50}\n")

    while True:
        try:
            if RICH_OK:
                user_input = Prompt.ask("[bold green]┌─ You[/bold green]")
            else:
                user_input = input("\n┌─ You: ")
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break

        if not user_input.strip():
            continue

        if user_input.startswith("/"):
            cmd = user_input[1:].strip()
            parts = cmd.split(maxsplit=1)
            command = parts[0].lower() if parts else ""

            if command == "exit" or command == "quit":
                if messages:
                    session.messages = messages
                    session.save()
                    print(f"  Session kaydedildi: {session.id}")
                break

            elif command == "help":
                print(f"""
  [Komutlar]
    /exit, /quit        → Çıkış
    /model <ad>         → Model değiştir (örn: /model qwen2.5-coder:14b)
    /temp <0.0-1.0>     → Sıcaklık ayarla
    /save               → Session'ı kaydet
    /sessions           → Session listesi
    /load <id>          → Session yükle
    /clear              → Mesajları temizle
    /workspace <dizin>  → Çalışma dizinini değiştir
    /tools              → Araçları göster
    /models             → Kullanılabilir modeller
    /prompt <metin>     → Sistem prompt'u değiştir
""")
                continue

            elif command == "model":
                if len(parts) > 1:
                    model = parts[1]
                    print(f"  Model → {model}")
                else:
                    print(f"  Mevcut model: {model}")
                continue

            elif command == "temp":
                if len(parts) > 1:
                    try:
                        temperature = float(parts[1])
                        print(f"  Temperature → {temperature}")
                    except:
                        print("  Geçersiz değer")
                continue

            elif command == "save":
                session.messages = messages
                session.model = model
                session.save()
                print(f"  ✓ Kaydedildi: {session.id}")
                continue

            elif command == "sessions":
                sessions = Session.list_sessions()
                if not sessions:
                    print("  Hiç session yok")
                else:
                    for s in sessions[:10]:
                        print(f"  {s['id']} | {s['created'][:19]} | {s['model']} | {s['msg_count']} mesaj")
                continue

            elif command == "load":
                if len(parts) > 1:
                    loaded = Session.load(parts[1])
                    if loaded:
                        session = loaded
                        messages = loaded.messages[:]
                        model = loaded.model
                        print(f"  ✓ Yüklendi: {loaded.id} ({len(loaded.messages)} mesaj)")
                    else:
                        print(f"  Session bulunamadı: {parts[1]}")
                continue

            elif command == "clear":
                messages = []
                print("  ✦ Mesajlar temizlendi")
                continue

            elif command == "workspace":
                if len(parts) > 1:
                    global WORKSPACE_ROOT
                    new_root = Path(parts[1]).resolve()
                    if new_root.exists():
                        WORKSPACE_ROOT = new_root
                        os.chdir(str(new_root))
                        print(f"  Çalışma dizini → {WORKSPACE_ROOT}")
                    else:
                        print(f"  Dizin bulunamadı: {parts[1]}")
                else:
                    print(f"  Çalışma dizini: {WORKSPACE_ROOT}")
                continue

            elif command == "tools":
                for n, t in TOOLS.items():
                    print(f"  • {n}: {t['description']}")
                continue

            elif command == "models":
                models = ollama_list()
                if models:
                    for m in models:
                        print(f"  • {m['name']}")
                else:
                    print("  Model listesi alınamadı")
                continue

            elif command == "prompt":
                if len(parts) > 1:
                    custom_prompt = parts[1]
                    print("  Sistem prompt'u güncellendi")
                continue

            else:
                print(f"  Bilinmeyen komut: /{command}")
                continue

        messages.append({"role": "user", "content": user_input})

        if RICH_OK:
            C.print("\n[bold cyan]└─ AI[/bold cyan] ", end="")
        else:
            print("\n└─ AI: ", end="")

        response = chat_completion_stream(messages, model, temperature, custom_prompt)
        print("\n")

        messages.append({"role": "assistant", "content": response})

        # Tool call loop
        MAX_TOOL_ITERS = 10
        for _ in range(MAX_TOOL_ITERS):
            tc = extract_tool_call(response)
            if not tc:
                break
            tool_name, args = tc
            if RICH_OK:
                C.print(f"\n[bold magenta]  ◈ ARAÇ: {tool_name}[/bold magenta]")
                C.print(f"    Args: {json.dumps(args, ensure_ascii=False)}")
            else:
                print(f"\n  ◈ ARAÇ: {tool_name}")
                print(f"    Args: {json.dumps(args, ensure_ascii=False)}")

            result = execute_tool_call(tool_name, args)
            if RICH_OK:
                C.print(f"[dim]    Sonuç: {result[:200]}[/dim]")
            else:
                print(f"    Sonuç: {result[:200]}")

            messages.append({"role": "assistant", "content": f"[Tool {tool_name} result]\n{result}"})

            if RICH_OK:
                C.print("\n[bold cyan]└─ AI (devam)[/bold cyan] ", end="")
            else:
                print("\n└─ AI (devam): ", end="")

            response = chat_completion_stream(messages, model, temperature, custom_prompt)
            print("\n")
            messages.append({"role": "assistant", "content": response})

    if messages:
        session.messages = messages
        session.model = model
        session.save()

# ── One-shot Mode ─────────────────────────────────────────────────

def one_shot_mode(prompt: str, model: str, temperature: float, custom_prompt: str = ""):
    messages = [{"role": "user", "content": prompt}]

    if RICH_OK:
        C.print("\n[bold cyan]AI Yanıtı:[/bold cyan]\n")
    else:
        print("\nAI Yanıtı:\n")

    response = chat_completion_stream(messages, model, temperature, custom_prompt)
    print("\n")

    for _ in range(10):
        tc = extract_tool_call(response)
        if not tc:
            break
        tool_name, args = tc
        if RICH_OK:
            C.print(f"\n[bold magenta]  ◈ ARAÇ: {tool_name}[/bold magenta]")
        else:
            print(f"\n  ◈ ARAÇ: {tool_name}")
        result = execute_tool_call(tool_name, args)
        if RICH_OK:
            C.print(f"[dim]    {result[:200]}[/dim]")
        else:
            print(f"    {result[:200]}")
        messages.append({"role": "assistant", "content": f"[Tool {tool_name} result]\n{result}"})
        if RICH_OK:
            C.print("\n[bold cyan]Devam:[/bold cyan] ", end="")
        else:
            print("\nDevam: ", end="")
        response = chat_completion_stream(messages, model, temperature, custom_prompt)
        print("\n")

# ── Settings ──────────────────────────────────────────────────────

def settings_wizard():
    print("\n  ⚙ GLITCHCODE SETTINGS\n")
    cfg = load_config()

    current = cfg.get("model", DEFAULT_MODEL)
    print(f"  Mevcut model: {current}")
    models = ollama_list()
    if models:
        print("\n  Kullanılabilir modeller:")
        for m in models:
            print(f"    {m['name']}")
    model = input(f"\n  Model [{current}]: ").strip() or current

    temp = cfg.get("temperature", 0.0)
    try:
        inp = input(f"  Temperature [{temp}]: ").strip()
        if inp:
            temp = float(inp)
    except:
        pass

    sp = cfg.get("system_prompt", "")
    print(f"\n  Sistem prompt'u ({len(sp)} karakter)")
    inp = input("  Değiştir? (Enter = aynı, y = yeni): ").strip().lower()
    if inp == "y":
        sp = input("  Yeni prompt: ").strip()

    save_config({"model": model, "temperature": temp, "system_prompt": sp})
    print(f"\n  ✓ Kaydedildi: {CONFIG_PATH}")

# ── Main ──────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="GLITCHCODE CLI — AI Coding Agent")
    parser.add_argument("prompt", nargs="?", help="Tek seferlik komut (boş = interaktif mod)")
    parser.add_argument("--model", "-m", help="Model adı (örn: qwen2.5-coder:14b)")
    parser.add_argument("--temperature", "-t", type=float, default=None, help="Sıcaklık (0.0-1.0)")
    parser.add_argument("--session", "-s", help="Session ID yükle")
    parser.add_argument("--settings", action="store_true", help="Ayarlar sihirbazı")
    parser.add_argument("--system-prompt", help="Özel sistem prompt'u")
    parser.add_argument("--list-models", action="store_true", help="Modelleri listele")
    parser.add_argument("--list-sessions", action="store_true", help="Session'ları listele")
    parser.add_argument("--version", "-v", action="store_true", help="Versiyon bilgisi")
    args = parser.parse_args()

    cfg = load_config()
    model = args.model or cfg.get("model", DEFAULT_MODEL)
    temperature = args.temperature if args.temperature is not None else cfg.get("temperature", 0.0)
    custom_prompt = args.system_prompt or cfg.get("system_prompt", "")

    if args.version:
        print("GLITCHCODE CLI v1.0")
        print("Glassesglitch Studio — AI Coding Agent")
        return

    if args.list_models:
        models = ollama_list()
        if not models:
            print("[!] Model listesi alınamadı. Ollama çalışıyor mu?")
            return
        for m in models:
            print(f"  {m['name']}  ({m['details']['parameter_size']})")
        return

    if args.list_sessions:
        sessions = Session.list_sessions()
        if not sessions:
            print("  Hiç session yok")
        else:
            for s in sessions:
                print(f"  {s['id']} | {s['created'][:19]} | {s['model']} | {s['msg_count']} mesaj")
        return

    if args.settings:
        settings_wizard()
        return

    if RICH_OK:
        C.print(BANNER)
    else:
        print("\n=== GLITCHCODE CLI ===\n")

    if args.prompt:
        one_shot_mode(args.prompt, model, temperature, custom_prompt)
    else:
        interactive_mode(model, temperature, custom_prompt, session_id=args.session)

if __name__ == "__main__":
    main()
