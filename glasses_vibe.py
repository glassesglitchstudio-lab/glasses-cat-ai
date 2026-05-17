# -*- coding: utf-8 -*-
"""
GLASSES VIBE IDE - Terminal Agent v9.0
Full Cloud API Support: OpenRouter + Hugging Face + Ollama
Universal API Bridge with Smart Key Detection
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
from rich.protocol import is_renderable

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

console = Console()

ASCII_LOGO = r"""
   /$$$$$$  /$$   /$$ /$$$$$$  /$$$$$$ /$$      /$$ /$$$$$$$ /$$$$$$ 
  /$$__  $$| $$  | $$/$$__  $$/$$__  $$ $$  /$ | $$| $$__  $$/$$__  $$
 | $$  \__/| $$  | $$ $$  \ $$ $$  \ $$ $$ /$$$| $$| $$  \ $$ $$  \ $$
 |  $$$$$$ | $$$$$$$$ $$$$$$$| $$$$$$$| $$/$$ $$ $$| $$$$$$$/| $$$$$$$
  \____  $$| $$__  $$ $$__  $$| $$_____| $$$$_  $$$$| $$____/| $$__  $$
  /$$  \ $$| $$  | $$ $$  | $$| $$     | $$$/ \  $$$| $$     | $$  \ $$
 |  $$$$$$/| $$  | $$  $$$$$$/| $$     | $$/   \  $$| $$     |  $$$$$$/
  \______/ |__/  |__/\______/ |__/     |__/     \__/|__/      \______/
"""

SYSTEM_PROMPT_JSON = """Sen GLASSES VIBE adli bir AGI asistansin. Niko Software tarafindan gelistirildin.

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
        return SYSTEM_PROMPT_JSON

    def get_messages(self):
        return self.messages

    def clear(self):
        self.messages = []


class EngineChecker:
    @staticmethod
    def check_ollama():
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True, text=True, timeout=10
            )
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
            headers = {
                "Authorization": "Bearer {0}".format(api_key),
                "Content-Type": "application/json"
            }
            response = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200, response.status_code
        except Exception:
            return False, 0

    @staticmethod
    def check_huggingface(api_key):
        try:
            headers = {"Authorization": "Bearer {0}".format(api_key)}
            response = requests.get(
                "https://huggingface.co/api/whoami-v2",
                headers=headers,
                timeout=10
            )
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
        tree = Tree("[bold cyan]{0}[/bold cyan]".format(os.path.basename(self.root_path)))
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
                branch = parent.add("[bold cyan]:file_opened:[/bold cyan] [cyan]{0}[/cyan]".format(d))
                self._add_files(full, branch, depth + 1, max_depth)
            for f in files:
                ext = f.split('.')[-1] if '.' in f else ''
                icon = self._get_icon(ext)
                parent.add("[dim]{0}[/dim] [white]{1}[/white]".format(icon, f))
        except PermissionError:
            parent.add("[dim][locked][/dim]")

    def _get_icon(self, ext):
        icons = {
            'py': ':snake:', 'js': ':gear:', 'html': ':globe:', 'css': ':art:',
            'json': ':brackets:', 'md': ':book:', 'txt': ':page_facing_up:',
            'bat': ':gear:', 'ps1': ':gear:', 'sh': ':gear:',
            'png': ':image:', 'jpg': ':image:', 'gif': ':image:',
        }
        return icons.get(ext, ':page_facing_up:')


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
        self.last_response = ""

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_header(self):
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        engine_label = self.engine or "not selected"
        cwd = os.getcwd()
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("key", style="dim cyan", ratio=1)
        table.add_column("value", style="bold white", ratio=2)
        table.add_row("engine", engine_label)
        table.add_row("model", self.model_name or "not selected")
        table.add_row("cwd", cwd)
        table.add_row("requests", str(self.request_count))
        table.add_row("files", str(self.file_count))
        table.add_row("session", "{0}m {1}s".format(minutes, seconds))
        return Panel(
            table,
            title="[bold cyan]GLASSES VIBE[/bold cyan]  [dim]v9.0 Cloud IDE[/dim]",
            border_style="cyan",
            padding=(0, 2)
        )

    def get_status_bar(self):
        if self.status == "CONNECTING":
            status_style = "bold blue"
            status_text = "CONNECTING & CHECKING"
            border_style = "blue"
        elif self.status == "THINKING":
            status_style = "bold yellow"
            status_text = "THINKING"
            border_style = "yellow"
        elif self.status == "WRITING":
            status_style = "bold magenta"
            status_text = "WRITING"
            border_style = "magenta"
        elif self.status == "SUCCESS":
            status_style = "bold green"
            status_text = "BASARIYLA DOSYALANDI"
            border_style = "green"
        else:
            status_style = "bold green"
            status_text = "IDLE"
            border_style = "green"

        detail = " - {0}".format(self.status_detail) if self.status_detail else ""
        bar = Text()
        bar.append("STATUS: ", style="dim")
        bar.append(status_text, style=status_style)
        bar.append(detail, style="dim")
        bar.append("  |  ", style="dim")
        bar.append("GLASSES VIBE IDE", style="dim cyan")
        return Panel(
            bar,
            border_style=border_style,
            padding=(0, 2)
        )

    def get_file_explorer_panel(self):
        tree = self.explorer.scan()
        return Panel(
            tree,
            title="[bold cyan]EXPLORER[/bold cyan]",
            border_style="cyan",
            padding=(0, 1)
        )

    def get_workspace_panel(self):
        content = ""

        if self.thought_log:
            content += "[bold magenta]THINKING LOGS[/bold magenta]\n"
            content += "[dim]" + "-" * 40 + "[/dim]\n"
            for t in self.thought_log[-5:]:
                content += "[dim italic]{0}[/dim italic]\n\n".format(t[:150] + "..." if len(t) > 150 else t)

        if self.output_log:
            content += "[bold cyan]OUTPUTS[/bold cyan]\n"
            content += "[dim]" + "-" * 40 + "[/dim]\n"
            for o in self.output_log[-5:]:
                content += o + "\n\n"

        if not content:
            content = "[dim]Waiting for input... Type your message or /help[/dim]"

        return Panel(
            content,
            title="[dim]WORKSPACE[/dim]",
            border_style="dim",
            padding=(1, 2)
        )

    def show_banner(self):
        self.clear_screen()
        console.print()
        console.print(Panel(
            Text(ASCII_LOGO.strip(), style="bold cyan"),
            subtitle=Text("Niko Software System v9.0 - Full Cloud API IDE", style="dim magenta"),
            border_style="magenta",
            padding=(1, 2)
        ))
        console.print()

    def select_model(self):
        console.print(Panel(
            "[bold]Zeka Katmani Secimi[/bold]\n"
            "[dim]Numara ile secim yapin, Enter ile onaylayin[/dim]",
            border_style="cyan",
            padding=(0, 2)
        ))
        console.print()

        console.print("[bold cyan]>>> Sistem Kontrol Ediliyor...[/bold cyan]")
        console.print()

        with Live(Spinner("dots", text="Ollama servisi kontrol ediliyor...", style="cyan"), refresh_per_second=10, transient=True):
            ollama_ok, ollama_models = EngineChecker.check_ollama()

        menu_items = []
        idx = 1

        if ollama_ok:
            console.print(Panel(
                "[bold green]✓ Ollama Servisi: AKTIF[/bold green]\n"
                "[dim]{0} model bulundu[/dim]".format(len(ollama_models)),
                border_style="green",
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

            console.print("[bold cyan]=== YEREL MODELLER (OLLAMA) ===[/bold cyan]")
            console.print("[dim]Otomatik tarandi ve siralandi[/dim]")
            console.print()

            if recommended:
                console.print("  [bold yellow]★ ONERILEN MODELLER[/bold yellow]")
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
                    console.print("  [bold cyan][{0}][/bold cyan] [Yerel] {1}{2}".format(idx, m, size_info))
                    idx += 1
                console.print()

            if other:
                console.print("  [dim]Diger Modeller[/dim]")
                for m in other:
                    menu_items.append({"idx": idx, "engine": "ollama", "model": m, "label": m})
                    console.print("  [cyan][{0}][/cyan] [Yerel] {1}".format(idx, m))
                    idx += 1
                console.print()
        else:
            console.print(Panel(
                "[bold red]✗ Ollama Servisi: PASIF[/bold red]\n"
                "[dim]Ollama yuklu degil veya calismiyor[/dim]",
                border_style="red",
                padding=(0, 2)
            ))
            console.print()
            console.print("  [bold cyan][{0}][/bold cyan] Ollama'yi otomatik baslat".format(idx))
            menu_items.append({"idx": idx, "engine": "ollama_start", "model": "", "label": "Ollama'yi baslat"})
            idx += 1
            console.print("  [bold cyan][{0}][/bold cyan] Ollama yukleme sayfasini ac".format(idx))
            menu_items.append({"idx": idx, "engine": "ollama_install", "model": "", "label": "Ollama yukle"})
            idx += 1
            console.print()

        console.print()
        console.print("[bold magenta]=== BULUT MODELLER (OPENROUTER) ===[/bold magenta]")
        or_key_env = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OR_API_KEY")
        or_status = "[bold green]✓ API Key bulundu[/bold green]" if or_key_env else "[bold yellow]○ API Key yok (secince istenecek)[/bold yellow]"
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
            console.print("  [magenta][{0}][/magenta] [Bulut] OpenRouter - {1}".format(idx, display))
            idx += 1

        console.print()
        console.print("[bold green]=== ACIK KAYNAK MODELLER (HUGGING FACE) ===[/bold green]")
        hf_key_env = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
        hf_status = "[bold green]✓ API Key bulundu[/bold green]" if hf_key_env else "[bold yellow]○ API Key yok (secince istenecek)[/bold yellow]"
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
            console.print("  [green][{0}][/green] [Acik Kaynak] Hugging Face - {1}".format(idx, display))
            idx += 1

        console.print()
        console.print("  [dim]Cikis icin 0 veya Ctrl+C basin[/dim]")
        console.print()

        while True:
            try:
                choice_str = Prompt.ask("[bold cyan]>> Seciminiz[/bold cyan]", default="1")
                choice_num = int(choice_str)
            except (ValueError, TypeError):
                console.print("[red]Gecerli bir numara girin![/red]")
                continue
            except (EOFError, KeyboardInterrupt):
                console.print()
                console.print(Panel("[red]Cikis yapiliyor...[/red]", border_style="red"))
                sys.exit(0)

            if choice_num == 0:
                console.print(Panel("[red]Cikis yapiliyor...[/red]", border_style="red"))
                sys.exit(0)

            if choice_num < 1 or choice_num > len(menu_items):
                console.print("[red]Gecerli bir numara girin (1-{0})![/red]".format(len(menu_items)))
                continue

            selected = menu_items[choice_num - 1]
            engine = selected["engine"]
            model = selected["model"]

            if engine == "ollama_start":
                console.print("[cyan]Ollama baslatiliyor...[/cyan]")
                with Live(Spinner("dots", text="ollama serve calistiriliyor...", style="cyan"), refresh_per_second=10, transient=True):
                    subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                time.sleep(3)
                ok, _ = EngineChecker.check_ollama()
                if ok:
                    console.print(Panel("[bold green]✓ Ollama basarili sekilde baslatildi![/bold green]", border_style="green"))
                    return self.select_model()
                else:
                    console.print(Panel("[red]Ollama baslatilamadi.[/red]", border_style="red"))
                    sys.exit(0)

            if engine == "ollama_install":
                import webbrowser
                webbrowser.open("https://ollama.com/download")
                console.print(Panel("[dim]Tarayicida Ollama indirme sayfasi acildi.[/dim]", border_style="dim"))
                sys.exit(0)

            if engine == "openrouter":
                self.status = "CONNECTING"
                self.status_detail = "Checking OpenRouter API key..."
                api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OR_API_KEY")
                if not api_key:
                    console.print()
                    console.print(Panel(
                        "[bold yellow]OpenRouter API Key gerekiyor[/bold yellow]\n"
                        "[dim]https://openrouter.ai/keys adresinden olusturabilirsiniz.[/dim]",
                        border_style="yellow",
                        padding=(0, 2)
                    ))
                    api_key = Prompt.ask("[bold cyan]>> OpenRouter API Key girin[/bold cyan]")
                    api_key = api_key.strip()
                if api_key:
                    with Live(Spinner("dots", text="OpenRouter API kontrol ediliyor...", style="cyan"), refresh_per_second=10, transient=True):
                        ok, status = EngineChecker.check_openrouter(api_key)
                    if not ok:
                        console.print(Panel("[red]OpenRouter API key gecersiz! (HTTP {0})[/red]".format(status), border_style="red"))
                        console.print("[dim]Tekrar denemek icin Enter basin, cikmak icin Ctrl+C[/dim]")
                        try:
                            input()
                        except KeyboardInterrupt:
                            sys.exit(0)
                        continue
                    self.api_key = api_key
                    console.print(Panel("[bold green]✓ OpenRouter API key dogrulandi![/bold green]", border_style="green"))
                else:
                    console.print(Panel("[red]API key girilmedi.[/red]", border_style="red"))
                    sys.exit(0)

            if engine == "huggingface":
                self.status = "CONNECTING"
                self.status_detail = "Checking Hugging Face API key..."
                api_key = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")
                if not api_key:
                    console.print()
                    console.print(Panel(
                        "[bold yellow]Hugging Face API Key gerekiyor[/bold yellow]\n"
                        "[dim]https://huggingface.co/settings/tokens adresinden olusturabilirsiniz.[/dim]",
                        border_style="yellow",
                        padding=(0, 2)
                    ))
                    api_key = Prompt.ask("[bold cyan]>> Hugging Face API Key girin[/bold cyan]")
                    api_key = api_key.strip()
                if api_key:
                    with Live(Spinner("dots", text="Hugging Face API kontrol ediliyor...", style="cyan"), refresh_per_second=10, transient=True):
                        ok, status = EngineChecker.check_huggingface(api_key)
                    if not ok:
                        console.print(Panel("[red]Hugging Face API key gecersiz! (HTTP {0})[/red]".format(status), border_style="red"))
                        console.print("[dim]Tekrar denemek icin Enter basin, cikmak icin Ctrl+C[/dim]")
                        try:
                            input()
                        except KeyboardInterrupt:
                            sys.exit(0)
                        continue
                    self.api_key = api_key
                    console.print(Panel("[bold green]✓ Hugging Face API key dogrulandi![/bold green]", border_style="green"))
                else:
                    console.print(Panel("[red]API key girilmedi.[/red]", border_style="red"))
                    sys.exit(0)

            if engine == "ollama":
                self.status = "CONNECTING"
                self.status_detail = "Checking Ollama models..."
                with Live(Spinner("dots", text="Ollama kontrol ediliyor...", style="cyan"), refresh_per_second=10, transient=True):
                    ok, models = EngineChecker.check_ollama()
                if not ok:
                    console.print(Panel("[red]Ollama servisi calismiyor![/red]", border_style="red"))
                    sys.exit(0)
                if model not in models:
                    console.print(Panel(
                        "[yellow]Model '{0}' yerel yuklu degil![/yellow]".format(model),
                        border_style="yellow"
                    ))
                    retry = Prompt.ask("[cyan]Simdi indirmek istiyor musunuz? (evet/hayir)[/cyan]", default="hayir")
                    if retry.lower() in ("evet", "e", "yes", "y"):
                        console.print("[yellow]Model indiriliyor: {0}[/yellow]".format(model))
                        with Live(Spinner("dots", text="{0} indiriliyor...".format(model), style="yellow"), refresh_per_second=10, transient=True):
                            try:
                                subprocess.run(["ollama", "pull", model], capture_output=True, text=True, timeout=600)
                                console.print(Panel("[bold green]✓ Model basariyla indirildi![/bold green]", border_style="green"))
                            except Exception:
                                console.print("[red]Indirme basarisiz.[/red]")
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
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
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
            {"role": "system", "content": SYSTEM_PROMPT_JSON},
            {"role": "user", "content": prompt}
        ]
        payload = {
            "model": model,
            "messages": messages,
            "response_format": {"type": "json_object"},
        }
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def call_huggingface(self, model, prompt):
        url = "https://api-inference.huggingface.co/models/{0}".format(model)
        headers = {
            "Authorization": "Bearer {0}".format(self.api_key),
            "Content-Type": "application/json"
        }
        full_prompt = SYSTEM_PROMPT_JSON + "\n\nKullanici: " + prompt + "\nAsistan:"
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "return_full_text": False,
                "max_new_tokens": 2048,
                "temperature": 0.3,
                "do_sample": True,
            }
        }
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
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.getcwd()
            )
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
        console.print("  [bold cyan]/status[/bold cyan]     Show session status")
        console.print("  [bold cyan]/clear[/bold cyan]      Clear conversation history")
        console.print("  [bold cyan]/models[/bold cyan]     List available models")
        console.print("  [bold cyan]/engine[/bold cyan]     Change AI engine")
        console.print("  [bold cyan]/help[/bold cyan]       Show this help menu")
        console.print("  [bold cyan]/exit[/bold cyan]       Exit GLASSES VIBE")
        console.print()
        console.print("  [bold]Yetenekler:[/bold]")
        console.print("  [dim]dosya_yarat     - Yeni dosya olustur[/dim]")
        console.print("  [dim]dosya_oku       - Dosya icerigini oku[/dim]")
        console.print("  [dim]terminal_komutu - Terminal komutu calistir[/dim]")
        console.print("  [dim]mesaj_gonder    - Kullaniciya mesaj gonder[/dim]")
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

    def run(self):
        self.show_banner()

        console.print(Panel(
            "[cyan]GLASSES VIBE IDE Agent v9.0[/cyan]\n"
            "[dim]Multi-Engine: Ollama + OpenRouter + Hugging Face[/dim]\n"
            "[dim]File Explorer + Workspace + Status Bar[/dim]",
            border_style="magenta"
        ))
        console.print()

        self.model_name = self.select_model()

        console.print()
        console.print(Rule("session started", style="dim cyan"))
        console.print()

        while True:
            self.explorer.scan(force=True)

            console.print()
            console.print(self.get_header())
            console.print()

            explorer_panel = self.get_file_explorer_panel()
            workspace_panel = self.get_workspace_panel()

            console.print(explorer_panel)
            console.print()
            console.print(workspace_panel)
            console.print()
            console.print(self.get_status_bar())
            console.print()

            try:
                user_input = Prompt.ask("[bold cyan]>> GLASSES VIBE[/bold cyan]")
            except (EOFError, KeyboardInterrupt):
                console.print()
                console.print(Panel("[magenta]GLASSES VIBE kapatiliyor... Gule gule![/magenta]", border_style="magenta"))
                break

            if user_input is None:
                continue

            user_input = user_input.strip()
            if not user_input:
                continue

            if user_input.startswith("/"):
                cmd = user_input[1:].lower()
                if cmd in ("exit", "quit"):
                    console.print()
                    console.print(Panel("[magenta]GLASSES VIBE kapatiliyor... Gule gule![/magenta]", border_style="magenta"))
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
                    console.print(Rule("engine changed", style="dim cyan"))
                    continue
                else:
                    console.print("  [dim]Unknown command: /{0}. Type /help.[/dim]".format(cmd))
                    continue

            self.status = "CONNECTING"
            self.status_detail = "Connecting to {0}...".format(self.engine)
            self.history.add("user", user_input)
            self.request_count += 1

            prompt = "{0}\n\nKullanici: {1}".format(self.history.get_system_prompt(), user_input)

            console.print()
            console.print(Panel(
                "[bold cyan]User:[/bold cyan] {0}".format(user_input),
                border_style="cyan",
                padding=(0, 1)
            ))
            console.print()

            with Live(Spinner("dots", text="CONNECTING & CHECKING...", style="blue"), refresh_per_second=10, transient=True):
                self.status = "CONNECTING"
                self.status_detail = "Connecting to {0}...".format(self.engine)

            self.status = "THINKING"
            self.status_detail = "Processing with {0} ({1})".format(self.engine, self.model_name)

            with Live(Spinner("dots", text="GLASSES VIBE dusunuyor...", style="yellow"), refresh_per_second=10, transient=True):
                try:
                    response = self.call_engine(prompt)
                except Exception as e:
                    console.print(Panel("[red]Engine error: {0}[/red]".format(e), border_style="red"))
                    self.status = "IDLE"
                    self.status_detail = ""
                    continue

            if response is None:
                self.status = "IDLE"
                self.status_detail = ""
                continue

            parsed = JSONParser.clean_and_parse(response)
            self.history.add("assistant", response)

            dusunce = parsed.get("dusunce", "")
            aksiyon = parsed.get("aksiyon", "mesaj_gonder")
            hedef = parsed.get("hedef", "")
            icerik = parsed.get("icerik", "")

            if dusunce:
                self.thought_log.append(dusunce)
                console.print(Panel(
                    Text(dusunce, style="italic dim magenta"),
                    title="[magenta]thinking[/magenta]",
                    border_style="magenta",
                    padding=(0, 1)
                ))

            if aksiyon == "dosya_yarat" and hedef and icerik:
                self.status = "WRITING"
                self.status_detail = "Creating {0}...".format(hedef)
                with Live(Spinner("dots", text="Dosya yaziliyor: {0}".format(hedef), style="magenta"), refresh_per_second=10, transient=True):
                    success, result = self.create_file(hedef, icerik)
                if success:
                    self.status = "SUCCESS"
                    self.status_detail = "BASARIYLA DOSYALANDI: {0}".format(hedef)
                    self.output_log.append("[green]file created: {0}[/green]\n{1}".format(result, icerik[:200]))
                    ext = hedef.split('.')[-1] if '.' in hedef else "text"
                    lang_map = {"py": "python", "js": "javascript", "html": "html", "css": "css", "json": "json", "yaml": "yaml", "yml": "yaml", "toml": "toml", "sh": "bash", "ps1": "powershell", "cs": "csharp", "gd": "gdscript", "md": "markdown", "xml": "xml", "sql": "sql", "rb": "ruby", "go": "go", "rs": "rust", "ts": "typescript", "java": "java", "cpp": "cpp", "c": "c"}
                    lang = lang_map.get(ext, "text")
                    syntax = Syntax(icerik, lang, theme="monokai", line_numbers=True, word_wrap=True)
                    console.print(Panel(
                        syntax,
                        title="[green]BASARIYLA DOSYALANDI: {0}[/green]".format(hedef),
                        border_style="green",
                        padding=(0, 0)
                    ))
                    console.print(Panel(
                        "[bold green]✓ DOSYA BASARIYLA OLUSTURULDU: {0}[/bold green]".format(result),
                        border_style="green"
                    ))
                    self.explorer.scan(force=True)
                else:
                    console.print(Panel("[red]File creation error: {0}[/red]".format(result), border_style="red"))
                    self.status = "IDLE"
                    self.status_detail = ""

            elif aksiyon == "dosya_oku" and hedef:
                self.status = "THINKING"
                self.status_detail = "Reading {0}...".format(hedef)
                with Live(Spinner("dots", text="Dosya okunuyor: {0}".format(hedef), style="cyan"), refresh_per_second=10, transient=True):
                    success, result = self.read_file(hedef)
                if success:
                    self.status = "SUCCESS"
                    self.status_detail = "DOSYA OKUNDU: {0}".format(hedef)
                    self.output_log.append("[cyan]file read: {0}[/cyan]\n{1}".format(hedef, result[:200]))
                    ext = hedef.split('.')[-1] if '.' in hedef else "text"
                    lang_map = {"py": "python", "js": "javascript", "html": "html", "css": "css", "json": "json", "yaml": "yaml", "yml": "yaml", "toml": "toml", "sh": "bash", "ps1": "powershell", "cs": "csharp", "gd": "gdscript", "md": "markdown", "xml": "xml", "sql": "sql", "rb": "ruby", "go": "go", "rs": "rust", "ts": "typescript", "java": "java", "cpp": "cpp", "c": "c"}
                    lang = lang_map.get(ext, "text")
                    syntax = Syntax(result, lang, theme="monokai", line_numbers=True, word_wrap=True)
                    console.print(Panel(
                        syntax,
                        title="[cyan]DOSYA ICERIGI: {0}[/cyan]".format(hedef),
                        border_style="cyan",
                        padding=(0, 0)
                    ))
                else:
                    console.print(Panel("[red]File read error: {0}[/red]".format(result), border_style="red"))
                    self.status = "IDLE"
                    self.status_detail = ""

            elif aksiyon == "terminal_komutu" and hedef:
                self.status = "WRITING"
                self.status_detail = "Running: {0}".format(hedef)
                with Live(Spinner("dots", text="Komut calistiriliyor: {0}".format(hedef), style="yellow"), refresh_per_second=10, transient=True):
                    success, result = self.run_command(hedef)
                if success:
                    self.status = "SUCCESS"
                    self.status_detail = "KOMUT CALISTIRILDI"
                    self.output_log.append("[green]command: {0}[/green]\n{1}".format(hedef, result.strip()[:500]))
                    console.print(Panel(
                        Text(result.strip(), style="white"),
                        title="[yellow]TERMINAL CIKTISI: {0}[/yellow]".format(hedef),
                        border_style="yellow",
                        padding=(0, 1)
                    ))
                else:
                    console.print(Panel("[red]Command error: {0}[/red]".format(result), border_style="red"))
                    self.status = "IDLE"
                    self.status_detail = ""

            else:
                if icerik:
                    self.output_log.append(icerik[:500])
                    console.print(Panel(
                        Markdown(icerik),
                        border_style="cyan",
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
        console.print(Panel("[magenta]GLASSES VIBE kapatiliyor... Gule gule![/magenta]", border_style="magenta"))
        sys.exit(0)
