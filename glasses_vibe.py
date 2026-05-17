# -*- coding: utf-8 -*-
"""
GLASSES VIBE IDE - Terminal Agent v10.0.0
Cyberpunk UI - Exact v10.0.0 Release Notes Design
Niko Software System
"""

import os
import sys
import io
import json
import re
import time
import subprocess
import requests
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.tree import Tree
from rich.box import SIMPLE, ROUNDED
from rich.console import Group
from rich.align import Align

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

console = Console(force_terminal=True, width=140, height=40)

CYAN = "#00ffff"
MAGENTA = "#ff00ff"
GREEN = "#00ff00"
YELLOW = "#ffaa00"
RED = "#ff0000"
BLUE = "#0088ff"
DIM = "#888888"

ASCII_LOGO = """
 ██████╗ ██╗  ██╗ █████╗ ██████╗  █████╗ ██╗     ██╗   ██╗ ██████╗ ██████╗ 
██╔════╝ ██║  ██║██╔══██╗██╔══██╗██╔══██╗██║     ██║   ██║██╔════╝██╔═══██╗
██║  ███╗███████║███████║██║  ██║███████║██║     ██║   ██║██║     ██║   ██║
██║   ██║██╔══██║██╔══██║██║  ██║██╔══██║██║     ██║   ██║██║     ██║   ██║
╚██████╔╝██║  ██║██║  ██║██████╔╝██║  ██║███████╗╚██████╔╝╚██████╗██████╔╝
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝╚═════╝ 
"""

SYSTEM_PROMPT = """Sen GLASSES VIBE adli bir AGI asistansin. Niko Software tarafindan gelistirildin.

Mevcut calisma dizini (cwd) header'da gosteriliyor, 'pwd' komutuna ihtiyacin yok.

YANIT FORMATIN:
Sen SADECE ve SADECE asagidaki JSON semasi ile yanit vermelisin. Baska hicbir sey yazma.

{
  "dusunce": "Arka planda yuruttugun derin mantik ve algoritma plani",
  "aksiyon": "dosya_yarat" veya "dosya_oku" veya "terminal_komutu" veya "mesaj_gonder",
  "hedef": "dosya_adi_veya_komut",
  "icerik": "kod_veya_mesaj"
}

AKSIYON ACIKLAMALARI:
- dosya_yarat: Yeni dosya olusturur. hedef=dosya_adi, icerik=kod.
- dosya_oku: Dosya icerigini okur. hedef=dosya_adi.
- terminal_komutu: Terminal komutu calistirir. hedef=komut.
- mesaj_gonder: Kullaniciya mesaj gonderir. icerik=mesaj.

KURALLAR:
- JSON disinda hicbir karakter yazma. Backtick kullanma.
- Turkce konus.
- Eger kullanici kod yazmani isterse, aksiyon 'dosya_yarat' olmali.
- Eger kullanici mevcut bir dosyayi okumak isterse, aksiyon 'dosya_oku' olmali.
- Eger kullanici kodu test etmeni isterse, aksiyon 'terminal_komutu' olmali.
- Kullanici dosya konumu sorarsa, header'daki cwd bilgisini kullan, komut calistirma.
- Yanitin SADECE JSON olmali, baska hicbir aciklama metni olmamali."""


class ConversationHistory:
    def __init__(self, max_turns=20):
        self.messages = []
        self.max_turns = max_turns

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2:]

    def get_system_prompt(self):
        return SYSTEM_PROMPT

    def get_messages(self):
        return self.messages

    def clear(self):
        self.messages = []


class EngineChecker:
    @staticmethod
    def check_ollama():
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                models = []
                for line in result.stdout.strip().split('\n')[1:]:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            models.append(parts[0])
                return True, models
            return False, []
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, []

    @staticmethod
    def check_openrouter(api_key):
        try:
            headers = {"Authorization": "Bearer {0}".format(api_key), "Content-Type": "application/json"}
            response = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers, timeout=10)
            return response.status_code == 200, response.status_code
        except Exception:
            return False, 0

    @staticmethod
    def check_huggingface(api_key):
        try:
            headers = {"Authorization": "Bearer {0}".format(api_key)}
            response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers, timeout=10)
            return response.status_code == 200, response.status_code
        except Exception:
            return False, 0


class FileExplorer:
    def __init__(self, root_path=None):
        self.root_path = root_path or os.getcwd()
        self.cache = None
        self.cache_time = 0

    def scan(self, force=False):
        now = time.time()
        if not force and self.cache and (now - self.cache_time) < 2:
            return self.cache
        tree = Tree("[bold {0}]📁 /Project_Root_NikoSoftware/[/bold {0}] [dim](current dir)[/dim]".format(CYAN), guide_style="dim {0}".format(CYAN))
        self._add_files(self.root_path, tree, depth=0, max_depth=3)
        self.cache = tree
        self.cache_time = now
        return tree

    def _add_files(self, path, parent, depth=0, max_depth=3):
        if depth >= max_depth:
            return
        try:
            entries = sorted(os.listdir(path))
            dirs = []
            files = []
            for entry in entries:
                if entry.startswith('.'):
                    continue
                full = os.path.join(path, entry)
                if os.path.isdir(full):
                    dirs.append(entry)
                else:
                    files.append(entry)
            for d in dirs:
                full = os.path.join(path, d)
                branch = parent.add("[bold {0}]📂 {1}[/bold {0}]".format(CYAN, d), guide_style="dim {0}".format(CYAN))
                self._add_files(full, branch, depth + 1, max_depth)
            for f in files:
                ext = f.split('.')[-1] if '.' in f else ''
                icon, color = self._get_icon(ext)
                parent.add("[{0}]{1}[/] [dim]{2}[/dim]".format(color, icon, f))
        except PermissionError:
            parent.add("[dim]🔒 [locked][/dim]")

    def _get_icon(self, ext):
        icons = {
            'py': ('🐍', MAGENTA), 'js': ('⚙', YELLOW), 'html': ('🌐', '#ff6600'), 'css': ('🎨', BLUE),
            'json': ('📋', YELLOW), 'md': ('📖', GREEN), 'txt': ('📄', DIM),
            'bat': ('⚙', DIM), 'ps1': ('⚙', DIM), 'sh': ('⚙', DIM),
            'png': ('🖼', MAGENTA), 'jpg': ('🖼', MAGENTA), 'gif': ('🖼', MAGENTA),
            'zip': ('📦', '#ff6600'), 'log': ('📝', DIM),
        }
        return icons.get(ext, ('📄', DIM))


class JSONParser:
    @staticmethod
    def clean_and_parse(response_text):
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            response_text = json_match.group(0)
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            response_text = response_text.strip().lstrip('{').rstrip('}')
            try:
                return json.loads('{' + response_text + '}')
            except json.JSONDecodeError:
                return {
                    "dusunce": "Yanit JSON formatinda degil, ham yanit gosteriliyor.",
                    "aksiyon": "mesaj_gonder",
                    "hedef": "",
                    "icerik": response_text
                }


class GlassesVibeIDE:
    def __init__(self):
        self.model_name = None
        self.engine = None
        self.api_key = None
        self.history = ConversationHistory()
        self.request_count = 0
        self.file_count = 0
        self.start_time = time.time()
        self.status = "IDLE"
        self.status_detail = ""
        self.thought_log = []
        self.output_log = []
        self.explorer = FileExplorer()
        self.last_file_content = ""
        self.last_file_name = ""
        self.user_input = ""
        self.chat_messages = []

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_logo_panel(self):
        logo_text = Text()
        lines = ASCII_LOGO.strip().split('\n')
        for i, line in enumerate(lines):
            if i % 2 == 0:
                logo_text.append(line + "\n", style="bold {0}".format(CYAN))
            else:
                logo_text.append(line + "\n", style="bold {0}".format(MAGENTA))
        return Panel(
            Align.center(logo_text),
            box=SIMPLE,
            border_style=CYAN,
            padding=(0, 0)
        )

    def get_subtitle_panel(self):
        return Panel(
            Align.center(Text("Niko Software System v10.0.0 - AGI Agent CLI", style="dim #ffffff")),
            box=SIMPLE,
            border_style=MAGENTA,
            padding=(0, 0)
        )

    def get_explorer_panel(self):
        tree = self.explorer.scan()
        return Panel(
            tree,
            title="[bold {0}] 📁 PROJECT EXPLORER [/bold {0}]".format(CYAN),
            box=SIMPLE,
            border_style=MAGENTA,
            padding=(0, 1)
        )

    def get_chat_history_panel(self):
        content = Text()
        if not self.chat_messages:
            content.append("  [dim]Henüz mesaj yok... Sohbet başlatın![/dim]\n", style="")
        else:
            for msg in self.chat_messages[-8:]:
                if msg["role"] == "user":
                    content.append("  💬 ", style="")
                    content.append("You: ", style="bold {0}".format(CYAN))
                    content.append("{0}\n".format(msg["content"][:60]), style="#ffffff")
                elif msg["role"] == "assistant":
                    preview = msg["content"][:60]
                    if "dusunce" in msg["content"]:
                        try:
                            data = json.loads(msg["content"])
                            preview = data.get("dusunce", "")[:60]
                        except:
                            pass
                    content.append("  🤖 ", style="")
                    content.append("AI: ", style="bold {0}".format(MAGENTA))
                    content.append("{0}\n".format(preview), style="#ffffff")
                content.append("\n")
        return Panel(
            content,
            title="[bold {0}] 💬 CHAT HISTORY [/bold {0}]".format(CYAN),
            box=SIMPLE,
            border_style=MAGENTA,
            padding=(0, 1)
        )

    def get_workspace_panel(self):
        content = Text()
        if self.thought_log:
            content.append("[AI LOG LOGIC] ", style="bold {0}".format(CYAN))
            content.append("{0}: Planning...\n".format(self.model_name or "gulmzcetinerMax"), style=MAGENTA)
            for t in self.thought_log[-3:]:
                content.append("• {0}\n".format(t[:80]), style="dim {0}".format(CYAN))
            content.append("  ↳ Pseudo-code:\n", style="dim {0}".format(YELLOW))
            content.append("    • Prompt = %gulmazascetagenit....\n", style="dim {0}".format(DIM))
            content.append("    • Pseudo-code ...\n", style="dim {0}".format(DIM))
        else:
            content.append("[AI LOG LOGIC] ", style="bold {0}".format(CYAN))
            content.append("Waiting for input...\n", style="dim {0}".format(DIM))

        if self.last_file_name and self.last_file_content:
            content.append("\n")
            content.append("📄 {0} ×\n".format(self.last_file_name), style="bold {0}".format(YELLOW))
            ext = self.last_file_name.split('.')[-1] if '.' in self.last_file_name else "text"
            lang_map = {"py": "python", "js": "javascript", "html": "html", "css": "css", "json": "json"}
            lang = lang_map.get(ext, "text")
            syntax = Syntax(self.last_file_content, lang, theme="monokai", line_numbers=True, word_wrap=False)
            return Panel(
                Group(
                    Panel(content, box=None, padding=(0, 0)),
                    Panel(syntax, box=SIMPLE, border_style=YELLOW, padding=(0, 0))
                ),
                title="[bold {0}] WORKSPACE [/bold {0}]".format(CYAN),
                box=SIMPLE,
                border_style=MAGENTA,
                padding=(0, 1)
            )

        return Panel(
            content,
            title="[bold {0}] WORKSPACE [/bold {0}]".format(CYAN),
            box=SIMPLE,
            border_style=MAGENTA,
            padding=(0, 1)
        )

    def get_status_bar(self):
        status_config = {
            "CONNECTING": ("bold {0}".format(BLUE), "CONNECTING & CHECKING", BLUE, "◐"),
            "THINKING": ("bold {0}".format(YELLOW), "THINKING", YELLOW, "◉"),
            "WRITING": ("bold {0}".format(MAGENTA), "WRITING", MAGENTA, "✎"),
            "SUCCESS": ("bold {0}".format(GREEN), "BASARIYLA DOSYALANDI", GREEN, "✓"),
            "IDLE": ("bold {0}".format(GREEN), "IDLE", GREEN, "●"),
        }
        style, text, border, icon = status_config.get(self.status, status_config["IDLE"])
        detail = " - {0}".format(self.status_detail) if self.status_detail else ""

        bar = Text()
        bar.append(" {0} ".format(icon), style=style)
        bar.append("STATUS: ", style="dim")
        bar.append(text, style=style)
        bar.append(detail, style="dim")
        bar.append("  │  ", style="dim")
        bar.append("CEO Berkay", style="bold {0}".format(GREEN))
        bar.append("  │  ", style="dim")
        bar.append("GLASSES VIBE IDE", style="dim {0}".format(CYAN))
        bar.append("  │  ", style="dim")
        engine_colors = {"ollama": CYAN, "openrouter": MAGENTA, "huggingface": GREEN}
        engine_color = engine_colors.get(self.engine, DIM)
        bar.append(self.engine or "none", style="bold {0}".format(engine_color))

        return Panel(
            bar,
            box=SIMPLE,
            border_style=GREEN,
            style="on {0}".format(GREEN),
            padding=(0, 2)
        )

    def show_banner(self):
        self.clear_screen()
        console.print()
        console.print(self.get_logo_panel())
        console.print(self.get_subtitle_panel())
        console.print()

    def select_model(self):
        console.print(Panel(
            "[bold {0}] Ateşlemek İstediğiniz Zeka Katmanını Seçin, CEO Berkay: [/bold {0}]".format(CYAN),
            box=SIMPLE,
            border_style=CYAN,
            padding=(0, 2)
        ))
        console.print()

        console.print("[bold {0}]>>> Sistem Kontrol Ediliyor...[/bold {0}]".format(CYAN))
        console.print()

        with Live(Spinner("dots", text="Ollama servisi kontrol ediliyor...", style=CYAN), refresh_per_second=10, transient=True):
            ollama_ok, ollama_models = EngineChecker.check_ollama()

        menu_items = []
        idx = 1

        if ollama_ok:
            console.print(Panel(
                "[bold {0}]✓ Ollama Servisi: AKTIF[/bold {0}]  [dim]({1} model bulundu)[/dim]".format(GREEN, len(ollama_models)),
                box=SIMPLE,
                border_style=GREEN,
                padding=(0, 2)
            ))
            console.print()

            recommended = []
            other = []
            for m in ollama_models:
                ml = m.lower()
                if "gulmzcetiner" in ml or "glasses" in ml:
                    recommended.append(m)
                elif "qwen" in ml or "llama" in ml or "deepseek" in ml:
                    recommended.append(m)
                else:
                    other.append(m)

            console.print("[bold {0}]╔══ YEREL MODELLER (OLLAMA) ══╗[/bold {0}]".format(CYAN))
            console.print("[dim]Otomatik tarandi ve siralandi[/dim]")
            console.print()

            console.print("  [bold {0}]★ GULMEZCETINER v1.2.0 (Ana Model)[/bold {0}]".format(GREEN))
            menu_items.append({"idx": idx, "engine": "ollama", "model": "gulmzcetiner:latest", "label": "gulmzcetiner:latest"})
            console.print("  [bold {0}][{1}][/bold {0}] gulmzcetiner:latest [dim](v1.2.0 - GGUF Muhurlu)[/dim]".format(GREEN, idx))
            idx += 1
            console.print()

            recommended = []
            other = []
            for m in ollama_models:
                ml = m.lower()
                if "gulmzcetiner" in ml or "glasses" in ml:
                    continue
                elif "qwen" in ml or "llama" in ml or "deepseek" in ml:
                    recommended.append(m)
                else:
                    other.append(m)

            if recommended:
                console.print("  [bold {0}]★ ONERILEN MODELLER[/bold {0}]".format(YELLOW))
                for m in recommended:
                    size_info = ""
                    try:
                        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
                        for mod in resp.json().get("models", []):
                            if mod["name"] == m:
                                size_gb = round(mod.get("size", 0) / (1024**3), 1)
                                size_info = " ({0} GB)".format(size_gb)
                                break
                    except Exception:
                        pass
                    menu_items.append({"idx": idx, "engine": "ollama", "model": m, "label": m})
                    console.print("  [bold {0}][{1}][/bold {0}] {2}{3}".format(CYAN, idx, m, size_info))
                    idx += 1
                console.print()

            if other:
                console.print("  [dim]Diger Modeller[/dim]")
                for m in other:
                    menu_items.append({"idx": idx, "engine": "ollama", "model": m, "label": m})
                    console.print("  [dim cyan][{0}][/dim cyan] {1}".format(idx, m))
                    idx += 1
                console.print()
        else:
            console.print(Panel(
                "[bold {0}]✗ Ollama Servisi: PASIF[/bold {0}]\n[dim]Ollama yuklu degil veya calismiyor[/dim]".format(RED),
                box=SIMPLE,
                border_style=RED,
                padding=(0, 2)
            ))
            console.print()
            console.print("  [bold {0}][{1}][/bold {0}] Ollama'yi otomatik baslat".format(CYAN, idx))
            menu_items.append({"idx": idx, "engine": "ollama_start", "model": "", "label": "Ollama'yi baslat"})
            idx += 1
            console.print("  [bold {0}][{1}][/bold {0}] Ollama yukleme sayfasini ac".format(CYAN, idx))
            menu_items.append({"idx": idx, "engine": "ollama_install", "model": "", "label": "Ollama yukle"})
            idx += 1
            console.print()

        console.print()
        console.print("[bold {0}]╔══ BULUT MODELLER (OPENROUTER) ══╗[/bold {0}]".format(MAGENTA))
        or_key_env = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OR_API_KEY")
        or_status = "[bold {0}]✓ API Key bulundu[/bold {0}]".format(GREEN) if or_key_env else "[bold {0}]○ API Key yok (secince istenecek)[/bold {0}]".format(YELLOW)
        console.print("  [dim]Durum: {0}[/dim]".format(or_status))
        console.print()
        or_models = [
            ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet"),
            ("openai/gpt-4o", "GPT-4o"),
            ("anthropic/claude-3-opus", "Claude 3 Opus"),
            ("meta-llama/llama-3.1-70b-instruct", "Llama 3.1 70B"),
            ("google/gemini-2.0-flash-exp:free", "Gemini 2.0 Flash (Ucretsiz)"),
            ("mistralai/mistral-large-2411", "Mistral Large"),
        ]
        for model_id, display in or_models:
            menu_items.append({"idx": idx, "engine": "openrouter", "model": model_id, "label": display})
            console.print("  [bold {0}][{1}][/bold {0}] {2}".format(MAGENTA, idx, display))
            idx += 1

        console.print()
        console.print("[bold {0}]╔══ ACIK KAYNAK MODELLER (HUGGING FACE) ══╗[/bold {0}]".format(GREEN))
        hf_key_env = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
        hf_status = "[bold {0}]✓ API Key bulundu[/bold {0}]".format(GREEN) if hf_key_env else "[bold {0}]○ API Key yok (secince istenecek)[/bold {0}]".format(YELLOW)
        console.print("  [dim]Durum: {0}[/dim]".format(hf_status))
        console.print()
        hf_models = [
            ("HuggingFaceH4/zephyr-7b-beta", "Zephyr 7B"),
            ("mistralai/Mistral-7B-Instruct-v0.3", "Mistral 7B Instruct"),
            ("meta-llama/Meta-Llama-3-8B-Instruct", "Llama 3 8B Instruct"),
            ("Qwen/Qwen2.5-72B-Instruct", "Qwen 2.5 72B"),
        ]
        for model_id, display in hf_models:
            menu_items.append({"idx": idx, "engine": "huggingface", "model": model_id, "label": display})
            console.print("  [bold {0}][{1}][/bold {0}] {2}".format(GREEN, idx, display))
            idx += 1

        console.print()
        console.print("  [dim]Cikis icin 0 veya Ctrl+C basin[/dim]")
        console.print()

        while True:
            try:
                choice_str = Prompt.ask("[bold {0}]>> Seciminiz[/bold {0}]".format(CYAN), default="1")
                choice_num = int(choice_str)
            except (ValueError, TypeError):
                console.print("[bold {0}]Gecerli bir numara girin![/bold {0}]".format(RED))
                continue
            except (EOFError, KeyboardInterrupt):
                console.print()
                console.print(Panel("[bold {0}]Cikis yapiliyor...[/bold {0}]".format(RED), box=SIMPLE, border_style=RED))
                sys.exit(0)

            if choice_num == 0:
                console.print(Panel("[bold {0}]Cikis yapiliyor...[/bold {0}]".format(RED), box=SIMPLE, border_style=RED))
                sys.exit(0)

            if choice_num < 1 or choice_num > len(menu_items):
                console.print("[bold {0}]Gecerli bir numara girin (1-{1})![/bold {0}]".format(RED, len(menu_items)))
                continue

            selected = menu_items[choice_num - 1]
            engine = selected["engine"]
            model = selected["model"]

            if engine == "ollama_start":
                console.print("[bold {0}]Ollama baslatiliyor...[/bold {0}]".format(CYAN))
                with Live(Spinner("dots", text="ollama serve calistiriliyor...", style=CYAN), refresh_per_second=10, transient=True):
                    subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                time.sleep(3)
                ok, _ = EngineChecker.check_ollama()
                if ok:
                    console.print(Panel("[bold {0}]✓ Ollama basarili sekilde baslatildi![/bold {0}]".format(GREEN), box=SIMPLE, border_style=GREEN))
                    return self.select_model()
                else:
                    console.print(Panel("[bold {0}]Ollama baslatilamadi.[/bold {0}]".format(RED), box=SIMPLE, border_style=RED))
                    sys.exit(0)

            if engine == "ollama_install":
                import webbrowser
                webbrowser.open("https://ollama.com/download")
                console.print(Panel("[dim]Tarayicida Ollama indirme sayfasi acildi.[/dim]", box=SIMPLE, border_style=DIM))
                sys.exit(0)

            if engine == "openrouter":
                self.status = "CONNECTING"
                self.status_detail = "Checking OpenRouter API key..."
                api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OR_API_KEY")
                if not api_key:
                    console.print()
                    console.print(Panel(
                        "[bold {0}]OpenRouter API Key gerekiyor[/bold {0}]\n[dim]https://openrouter.ai/keys adresinden olusturabilirsiniz.[/dim]".format(YELLOW),
                        box=SIMPLE,
                        border_style=YELLOW,
                        padding=(0, 2)
                    ))
                    api_key = Prompt.ask("[bold {0}]>> OpenRouter API Key girin[/bold {0}]".format(CYAN))
                    api_key = api_key.strip()
                if api_key:
                    with Live(Spinner("dots", text="OpenRouter API kontrol ediliyor...", style=CYAN), refresh_per_second=10, transient=True):
                        ok, status = EngineChecker.check_openrouter(api_key)
                    if not ok:
                        console.print(Panel("[bold {0}]OpenRouter API key gecersiz! (HTTP {1})[/bold {0}]".format(RED, status), box=SIMPLE, border_style=RED))
                        console.print("[dim]Tekrar denemek icin Enter basin, cikmak icin Ctrl+C[/dim]")
                        try:
                            input()
                        except KeyboardInterrupt:
                            sys.exit(0)
                        continue
                    self.api_key = api_key
                    console.print(Panel("[bold {0}]✓ OpenRouter API key dogrulandi![/bold {0}]".format(GREEN), box=SIMPLE, border_style=GREEN))
                else:
                    console.print(Panel("[bold {0}]API key girilmedi.[/bold {0}]".format(RED), box=SIMPLE, border_style=RED))
                    sys.exit(0)

            if engine == "huggingface":
                self.status = "CONNECTING"
                self.status_detail = "Checking Hugging Face API key..."
                api_key = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
                if not api_key:
                    console.print()
                    console.print(Panel(
                        "[bold {0}]Hugging Face API Key gerekiyor[/bold {0}]\n[dim]https://huggingface.co/settings/tokens adresinden olusturabilirsiniz.[/dim]".format(YELLOW),
                        box=SIMPLE,
                        border_style=YELLOW,
                        padding=(0, 2)
                    ))
                    api_key = Prompt.ask("[bold {0}]>> Hugging Face API Key girin[/bold {0}]".format(CYAN))
                    api_key = api_key.strip()
                if api_key:
                    with Live(Spinner("dots", text="Hugging Face API kontrol ediliyor...", style=CYAN), refresh_per_second=10, transient=True):
                        ok, status = EngineChecker.check_huggingface(api_key)
                    if not ok:
                        console.print(Panel("[bold {0}]Hugging Face API key gecersiz! (HTTP {1})[/bold {0}]".format(RED, status), box=SIMPLE, border_style=RED))
                        console.print("[dim]Tekrar denemek icin Enter basin, cikmak icin Ctrl+C[/dim]")
                        try:
                            input()
                        except KeyboardInterrupt:
                            sys.exit(0)
                        continue
                    self.api_key = api_key
                    console.print(Panel("[bold {0}]✓ Hugging Face API key dogrulandi![/bold {0}]".format(GREEN), box=SIMPLE, border_style=GREEN))
                else:
                    console.print(Panel("[bold {0}]API key girilmedi.[/bold {0}]".format(RED), box=SIMPLE, border_style=RED))
                    sys.exit(0)

            if engine == "ollama":
                self.status = "CONNECTING"
                self.status_detail = "Checking Ollama models..."
                with Live(Spinner("dots", text="Ollama kontrol ediliyor...", style=CYAN), refresh_per_second=10, transient=True):
                    ok, models = EngineChecker.check_ollama()
                if not ok:
                    console.print(Panel("[bold {0}]Ollama servisi calismiyor![/bold {0}]".format(RED), box=SIMPLE, border_style=RED))
                    sys.exit(0)
                if model not in models:
                    console.print(Panel(
                        "[bold {0}]Model '{1}' yerel yuklu degil![/bold {0}]".format(YELLOW, model),
                        box=SIMPLE,
                        border_style=YELLOW
                    ))
                    retry = Prompt.ask("[bold {0}]Simdi indirmek istiyor musunuz? (evet/hayir)[/bold {0}]".format(CYAN), default="hayir")
                    if retry.lower() in ("evet", "e", "yes", "y"):
                        console.print("[bold {0}]Model indiriliyor: {1}[/bold {0}]".format(YELLOW, model))
                        with Live(Spinner("dots", text="{0} indiriliyor...".format(model), style=YELLOW), refresh_per_second=10, transient=True):
                            try:
                                subprocess.run(["ollama", "pull", model], capture_output=True, text=True, timeout=600)
                                console.print(Panel("[bold {0}]✓ Model basariyla indirildi![/bold {0}]".format(GREEN), box=SIMPLE, border_style=GREEN))
                            except Exception:
                                console.print("[bold {0}]Indirme basarisiz.[/bold {0}]".format(RED))
                                sys.exit(0)
                    else:
                        sys.exit(0)

            break

        self.engine = engine
        self.model_name = model
        self.status = "IDLE"
        self.status_detail = ""
        return model

    def call_ollama(self, model, prompt):
        url = "http://localhost:11434/api/generate"
        payload = {"model": model, "prompt": prompt, "stream": False, "format": "json"}
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    def call_openrouter(self, model, prompt):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": "Bearer {0}".format(self.api_key),
            "Content-Type": "application/json",
            "HTTP-Referer": "https://glassesvibe.local",
            "X-Title": "GLASSES VIBE"
        }
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        payload = {"model": model, "messages": messages, "response_format": {"type": "json_object"}}
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def call_huggingface(self, model, prompt):
        url = "https://api-inference.huggingface.co/models/{0}".format(model)
        headers = {"Authorization": "Bearer {0}".format(self.api_key), "Content-Type": "application/json"}
        full_prompt = SYSTEM_PROMPT + "\n\nKullanici: " + prompt + "\nAsistan:"
        payload = {"inputs": full_prompt, "parameters": {"return_full_text": False, "max_new_tokens": 2048, "temperature": 0.3, "do_sample": True}}
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            text = data[0].get("generated_text", "")
        elif isinstance(data, dict):
            if "error" in data:
                raise ValueError("Hugging Face API error: {0}".format(data.get("error", "Unknown")))
            text = data.get("generated_text", "")
        else:
            text = str(data)
        return text

    def call_engine(self, prompt):
        if self.engine == "ollama":
            return self.call_ollama(self.model_name, prompt)
        elif self.engine == "openrouter":
            return self.call_openrouter(self.model_name, prompt)
        elif self.engine == "huggingface":
            return self.call_huggingface(self.model_name, prompt)
        else:
            raise ValueError("Unknown engine: {0}".format(self.engine))

    def create_file(self, file_name, content):
        try:
            full_path = os.path.join(os.getcwd(), file_name)
            dir_path = os.path.dirname(full_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.file_count += 1
            return True, full_path
        except Exception as e:
            return False, str(e)

    def read_file(self, file_name):
        try:
            full_path = os.path.join(os.getcwd(), file_name)
            if not os.path.exists(full_path):
                return False, "Dosya bulunamadi: {0}".format(file_name)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return True, content
        except Exception as e:
            return False, str(e)

    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
            output = result.stdout
            if result.stderr:
                output += "\n[STDERR]\n" + result.stderr
            if not output.strip():
                output = "(cikti yok)"
            return True, output
        except subprocess.TimeoutExpired:
            return False, "Komut zaman asimina ugradi (60s)"
        except Exception as e:
            return False, str(e)

    def show_commands(self):
        console.print()
        console.print("  [bold {0}]/status[/bold {0}]     Show session status".format(CYAN))
        console.print("  [bold {0}]/clear[/bold {0}]      Clear conversation history".format(CYAN))
        console.print("  [bold {0}]/models[/bold {0}]     List available models".format(CYAN))
        console.print("  [bold {0}]/engine[/bold {0}]     Change AI engine".format(CYAN))
        console.print("  [bold {0}]/help[/bold {0}]       Show this help menu".format(CYAN))
        console.print("  [bold {0}]/exit[/bold {0}]       Exit GLASSES VIBE".format(CYAN))
        console.print()

    def show_status_detail(self):
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        engine_label = self.engine or "not selected"
        console.print()
        console.print("  [dim]engine:[/dim] [bold]{0}[/bold]".format(engine_label))
        console.print("  [dim]model:[/dim] [bold]{0}[/bold]".format(self.model_name))
        console.print("  [dim]requests:[/dim] {0}".format(self.request_count))
        console.print("  [dim]files created:[/dim] {0}".format(self.file_count))
        console.print("  [dim]session:[/dim] {0}m {1}s".format(minutes, seconds))
        console.print()

    def get_chat_input_panel(self):
        input_text = Text()
        input_text.append("  💬 ", style="bold {0}".format(CYAN))
        input_text.append("Mesajınızı yazın ve Enter'a basın...", style="dim #ffffff")
        return Panel(
            input_text,
            box=SIMPLE,
            border_style=CYAN,
            padding=(0, 2)
        )

    def build_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=10),
            Layout(name="main", ratio=1),
            Layout(name="chat_input", size=3)
        )
        layout["header"].split_row(
            Layout(self.get_logo_panel(), ratio=1)
        )
        layout["main"].split_row(
            Layout(self.get_explorer_panel(), name="explorer", ratio=1),
            Layout(name="right_panel", ratio=2)
        )
        layout["right_panel"].split_column(
            Layout(self.get_workspace_panel(), name="workspace", ratio=1),
            Layout(self.get_chat_history_panel(), name="chat_history", ratio=1)
        )
        layout["chat_input"].update(self.get_chat_input_panel())
        return layout

    def run(self):
        self.show_banner()

        console.print(Panel(
            "[bold {0}]GLASSES VIBE IDE Agent v10.0.0[/bold {0}]\n[dim]Multi-Engine: Ollama + OpenRouter + Hugging Face[/dim]\n[dim]File Explorer + Workspace + Status Bar[/dim]".format(CYAN),
            box=SIMPLE,
            border_style=MAGENTA,
            padding=(0, 2)
        ))
        console.print()

        self.model_name = self.select_model()

        console.print()
        console.print(Rule("session started", style="dim {0}".format(CYAN)))
        console.print()

        while True:
            self.explorer.scan(force=True)

            layout = self.build_layout()

            with Live(layout, refresh_per_second=4, screen=False):
                try:
                    user_input = Prompt.ask("[bold {0}]>> GLASSES VIBE[/bold {0}]".format(CYAN))
                except (EOFError, KeyboardInterrupt):
                    console.print()
                    console.print(Panel("[bold {0}]GLASSES VIBE kapatiliyor... Gule gule![/bold {0}]".format(MAGENTA), box=SIMPLE, border_style=MAGENTA))
                    break

                if user_input is None:
                    continue

                user_input = user_input.strip()
                if not user_input:
                    continue

                self.user_input = user_input
                self.chat_messages.append({"role": "user", "content": user_input})

                if user_input.startswith("/"):
                    cmd = user_input[1:].lower()
                    if cmd in ("exit", "quit"):
                        console.print()
                        console.print(Panel("[bold {0}]GLASSES VIBE kapatiliyor... Gule gule![/bold {0}]".format(MAGENTA), box=SIMPLE, border_style=MAGENTA))
                        break
                    elif cmd == "help":
                        self.show_commands()
                        continue
                    elif cmd == "status":
                        self.show_status_detail()
                        continue
                    elif cmd == "clear":
                        self.history.clear()
                        self.thought_log = []
                        self.output_log = []
                        self.last_file_name = ""
                        self.last_file_content = ""
                        self.user_input = ""
                        self.chat_messages = []
                        console.print("[dim]Conversation history cleared.[/dim]")
                        continue
                    elif cmd == "models":
                        if self.engine == "ollama":
                            try:
                                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                                data = response.json()
                                console.print()
                                console.print("  [bold]Ollama Modelleri[/bold]")
                                console.print()
                                for m in data.get("models", []):
                                    size_gb = round(m.get("size", 0) / (1024**3), 1)
                                    console.print("  {0}  [dim]({1} GB)[/dim]".format(m["name"], size_gb))
                                console.print()
                            except Exception:
                                console.print("  [dim]No models found.[/dim]")
                        else:
                            console.print("  [dim]Current engine: {0} ({1})[/dim]".format(self.engine, self.model_name))
                        continue
                    elif cmd == "engine":
                        self.model_name = self.select_model()
                        console.print(Rule("engine changed", style="dim {0}".format(CYAN)))
                        continue
                    else:
                        console.print("  [dim]Unknown command: /{0}. Type /help.[/dim]".format(cmd))
                        continue

                self.status = "CONNECTING"
                self.status_detail = "Connecting to {0}...".format(self.engine)
                self.history.add("user", user_input)
                self.request_count += 1

                prompt = "{0}\n\nKullanici: {1}".format(self.history.get_system_prompt(), user_input)

                with Live(Spinner("dots", text="CONNECTING & CHECKING...", style=BLUE), refresh_per_second=10, transient=True):
                    self.status = "CONNECTING"
                    self.status_detail = "Connecting to {0}...".format(self.engine)

                self.status = "THINKING"
                self.status_detail = "Processing with {0} ({1})".format(self.engine, self.model_name)

                with Live(Spinner("dots", text="GLASSES VIBE dusunuyor...", style=YELLOW), refresh_per_second=10, transient=True):
                    try:
                        response = self.call_engine(prompt)
                    except Exception as e:
                        console.print(Panel("[bold {0}]Engine error: {1}[/bold {0}]".format(RED, e), box=SIMPLE, border_style=RED))
                        self.status = "IDLE"
                        self.status_detail = ""
                        continue

                if response is None:
                    self.status = "IDLE"
                    self.status_detail = ""
                    continue

                parsed = JSONParser.clean_and_parse(response)
                self.history.add("assistant", response)
                self.chat_messages.append({"role": "assistant", "content": response})

                dusunce = parsed.get("dusunce", "")
                aksiyon = parsed.get("aksiyon", "mesaj_gonder")
                hedef = parsed.get("hedef", "")
                icerik = parsed.get("icerik", "")

                if dusunce:
                    self.thought_log.append(dusunce)
                    console.print(Panel(
                        Text(dusunce, style="italic dim {0}".format(MAGENTA)),
                        title="[bold {0}] thinking [/bold {0}]".format(MAGENTA),
                        box=SIMPLE,
                        border_style=MAGENTA,
                        padding=(0, 1)
                    ))

                if aksiyon == "dosya_yarat" and hedef and icerik:
                    self.status = "WRITING"
                    self.status_detail = "Creating {0}...".format(hedef)
                    with Live(Spinner("dots", text="Dosya yaziliyor: {0}".format(hedef), style=MAGENTA), refresh_per_second=10, transient=True):
                        success, result = self.create_file(hedef, icerik)
                    if success:
                        self.status = "SUCCESS"
                        self.status_detail = "BASARIYLA DOSYALANDI: {0}".format(hedef)
                        self.last_file_name = hedef
                        self.last_file_content = icerik
                        self.output_log.append("[bold {0}]file created: {1}[/bold {0}]".format(GREEN, result))
                        ext = hedef.split('.')[-1] if '.' in hedef else "text"
                        lang_map = {"py": "python", "js": "javascript", "html": "html", "css": "css", "json": "json", "yaml": "yaml", "yml": "yaml", "toml": "toml", "sh": "bash", "ps1": "powershell", "cs": "csharp", "gd": "gdscript", "md": "markdown", "xml": "xml", "sql": "sql", "rb": "ruby", "go": "go", "rs": "rust", "ts": "typescript", "java": "java", "cpp": "cpp", "c": "c"}
                        lang = lang_map.get(ext, "text")
                        syntax = Syntax(icerik, lang, theme="monokai", line_numbers=True, word_wrap=True)
                        console.print(Panel(
                            syntax,
                            title="[bold {0}] BASARIYLA DOSYALANDI: {1} [/bold {0}]".format(GREEN, hedef),
                            box=SIMPLE,
                            border_style=GREEN,
                            padding=(0, 0)
                        ))
                        console.print(Panel(
                            "[bold {0}]✓ DOSYA BASARIYLA OLUSTURULDU: {1}[/bold {0}]".format(GREEN, result),
                            box=SIMPLE,
                            border_style=GREEN
                        ))
                        self.explorer.scan(force=True)
                    else:
                        console.print(Panel("[bold {0}]File creation error: {1}[/bold {0}]".format(RED, result), box=SIMPLE, border_style=RED))
                        self.status = "IDLE"
                        self.status_detail = ""

                elif aksiyon == "dosya_oku" and hedef:
                    self.status = "THINKING"
                    self.status_detail = "Reading {0}...".format(hedef)
                    with Live(Spinner("dots", text="Dosya okunuyor: {0}".format(hedef), style=CYAN), refresh_per_second=10, transient=True):
                        success, result = self.read_file(hedef)
                    if success:
                        self.status = "SUCCESS"
                        self.status_detail = "DOSYA OKUNDU: {0}".format(hedef)
                        self.last_file_name = hedef
                        self.last_file_content = result
                        self.output_log.append("[bold {0}]file read: {1}[/bold {0}]".format(CYAN, hedef))
                        ext = hedef.split('.')[-1] if '.' in hedef else "text"
                        lang_map = {"py": "python", "js": "javascript", "html": "html", "css": "css", "json": "json", "yaml": "yaml", "yml": "yaml", "toml": "toml", "sh": "bash", "ps1": "powershell", "cs": "csharp", "gd": "gdscript", "md": "markdown", "xml": "xml", "sql": "sql", "rb": "ruby", "go": "go", "rs": "rust", "ts": "typescript", "java": "java", "cpp": "cpp", "c": "c"}
                        lang = lang_map.get(ext, "text")
                        syntax = Syntax(result, lang, theme="monokai", line_numbers=True, word_wrap=True)
                        console.print(Panel(
                            syntax,
                            title="[bold {0}] DOSYA ICERIGI: {1} [/bold {0}]".format(CYAN, hedef),
                            box=SIMPLE,
                            border_style=CYAN,
                            padding=(0, 0)
                        ))
                    else:
                        console.print(Panel("[bold {0}]File read error: {1}[/bold {0}]".format(RED, result), box=SIMPLE, border_style=RED))
                        self.status = "IDLE"
                        self.status_detail = ""

                elif aksiyon == "terminal_komutu" and hedef:
                    self.status = "WRITING"
                    self.status_detail = "Running: {0}".format(hedef)
                    with Live(Spinner("dots", text="Komut calistiriliyor: {0}".format(hedef), style=YELLOW), refresh_per_second=10, transient=True):
                        success, result = self.run_command(hedef)
                    if success:
                        self.status = "SUCCESS"
                        self.status_detail = "KOMUT CALISTIRILDI"
                        self.output_log.append("[bold {0}]command: {1}[/bold {0}]".format(GREEN, hedef))
                        console.print(Panel(
                            Text(result.strip(), style="white"),
                            title="[bold {0}] TERMINAL CIKTISI: {1} [/bold {0}]".format(YELLOW, hedef),
                            box=SIMPLE,
                            border_style=YELLOW,
                            padding=(0, 1)
                        ))
                    else:
                        console.print(Panel("[bold {0}]Command error: {1}[/bold {0}]".format(RED, result), box=SIMPLE, border_style=RED))
                        self.status = "IDLE"
                        self.status_detail = ""

                else:
                    if icerik:
                        self.output_log.append(icerik[:500])
                        console.print(Panel(
                            Markdown(icerik),
                            box=SIMPLE,
                            border_style=CYAN,
                            padding=(0, 1)
                        ))

                self.status = "IDLE"
                self.status_detail = ""
                console.print()


def main():
    agent = GlassesVibeIDE()
    agent.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        console.print(Panel("[bold {0}]GLASSES VIBE kapatiliyor... Gule gule![/bold {0}]".format(MAGENTA), box=SIMPLE, border_style=MAGENTA))
        sys.exit(0)
