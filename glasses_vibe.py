# -*- coding: utf-8 -*-
"""
GLASSES VIBE - AGI CLI Agent v6.0
Niko Software System
"""

import os
import sys
import io
import json
import time
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
import questionary
from questionary import Style

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

console = Console()

CUSTOM_STYLE = Style([
    ('qmark', 'fg:cyan bold'),
    ('question', 'fg:magenta bold'),
    ('answer', 'fg:cyan bold'),
    ('pointer', 'fg:magenta bold'),
    ('highlighted', 'fg:cyan bold'),
    ('selected', 'fg:magenta'),
    ('separator', 'fg:cyan'),
    ('instruction', 'fg:#888888'),
])

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


class ConversationHistory:
    def __init__(self, max_turns=20):
        self.messages = []
        self.max_turns = max_turns

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2:]

    def get_system_prompt(self):
        return """Sen GLASSES VIBE adli bir AGI asistansin. Niko Software tarafindan gelistirildin.

YANIT FORMATIN:
Sen SADECE ve SADECE asagidaki JSON semasi ile yanit vermelisin.

{
  "dusunce": "Arka planda yuruttugun derin mantik ve algoritma plani",
  "aksiyon": "dosya_yarat" veya "mesaj_gonder",
  "dosya_adi": "Olusturulacak dosyanin adi ve uzantisi (sadece dosya_yarat icin)",
  "kod_icerigi": "Yazilacak kod blogu veya kullaniciya iletilecek mesaj"
}

KURALLAR:
- Eger kullanici kod yazmani isterse, aksiyon 'dosya_yarat' olmali.
- Eger kullanici soru soruyorsa, aksiyon 'mesaj_gonder' olmali.
- JSON disinda hicbir karakter yazma. Backtick kullanma.
- Turkce konus."""

    def get_messages(self):
        return self.messages

    def clear(self):
        self.messages = []


class GlassesVibeAgent:
    def __init__(self):
        self.model_name = None
        self.history = ConversationHistory()
        self.request_count = 0
        self.file_count = 0
        self.start_time = time.time()
        self.status = "READY"
        self.thought_log = []
        self.output_log = []
        self.last_output = ""

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_header(self):
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("key", style="dim cyan", ratio=1)
        table.add_column("value", style="bold white", ratio=2)

        table.add_row("model", self.model_name or "not selected")
        table.add_row("requests", str(self.request_count))
        table.add_row("files", str(self.file_count))
        table.add_row("session", "{0}m {1}s".format(minutes, seconds))

        return Panel(
            table,
            title="[bold cyan]GLASSES VIBE[/bold cyan]  [dim]v6.0[/dim]",
            border_style="cyan",
            padding=(0, 2)
        )

    def get_status_bar(self):
        if self.status == "THINKING":
            status_style = "bold yellow"
            status_text = "THINKING"
        elif self.status == "WRITING":
            status_style = "bold magenta"
            status_text = "WRITING"
        else:
            status_style = "bold green"
            status_text = "READY"

        bar = Text()
        bar.append("STATUS: ", style="dim")
        bar.append(status_text, style=status_style)
        bar.append("  |  ", style="dim")
        bar.append("GLASSES VIBE AGI CLI", style="dim cyan")

        return Panel(
            bar,
            border_style="green" if self.status == "READY" else "yellow",
            padding=(0, 2)
        )

    def get_workspace(self):
        content = ""

        if self.thought_log:
            content += "[bold magenta]THINKING LOGS[/bold magenta]\n"
            content += "[dim]" + "-" * 50 + "[/dim]\n"
            for t in self.thought_log[-3:]:
                content += "[dim italic]{0}[/dim italic]\n\n".format(t[:200] + "..." if len(t) > 200 else t)

        if self.output_log:
            content += "[bold cyan]OUTPUTS[/bold cyan]\n"
            content += "[dim]" + "-" * 50 + "[/dim]\n"
            for o in self.output_log[-3:]:
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
            subtitle=Text("Niko Software System v6.0", style="dim magenta"),
            border_style="magenta",
            padding=(1, 2)
        ))
        console.print()

    def select_model(self):
        choice = questionary.select(
            "Zeka Katmani Sec:",
            choices=[
                questionary.Choice("GulmezCetinerMax (Ollama - v1.2.0 Evolution)", value="gulmzcetiner"),
                questionary.Choice("Qwen2.5-Coder:14b (Ollama)", value="qwen2.5-coder:14b"),
                questionary.Choice("DeepSeek-R1:8b (Ollama)", value="deepseek-r1:8b"),
                questionary.Choice("Llama3.2:latest (Ollama)", value="llama3.2:latest"),
            ],
            style=CUSTOM_STYLE,
            qmark=">>"
        ).ask()

        if choice is None:
            console.print(Panel("[red]Cikis yapiliyor...[/red]", border_style="red"))
            sys.exit(0)

        return choice

    def ollama_request(self, model, prompt):
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.ConnectionError:
            console.print(Panel("[red]Ollama servisi calismiyor! `ollama serve`[/red]", border_style="red"))
            return None
        except requests.exceptions.Timeout:
            console.print(Panel("[red]Istek zaman asimina ugradi.[/red]", border_style="red"))
            return None
        except Exception as e:
            console.print(Panel("[red]Hata: {0}[/red]".format(e), border_style="red"))
            return None

    def process_json_response(self, response_text):
        response_text = response_text.strip()
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "dusunce": "Yanit JSON formatinda degil.",
                "aksiyon": "mesaj_gonder",
                "dosya_adi": "",
                "kod_icerigi": response_text
            }

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

    def show_commands(self):
        console.print()
        console.print("  [bold cyan]/status[/bold cyan]     Show session status")
        console.print("  [bold cyan]/clear[/bold cyan]      Clear conversation history")
        console.print("  [bold cyan]/models[/bold cyan]     List available models")
        console.print("  [bold cyan]/help[/bold cyan]       Show this help menu")
        console.print("  [bold cyan]/exit[/bold cyan]       Exit GLASSES VIBE")
        console.print()

    def show_status_detail(self):
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        console.print()
        console.print("  [dim]model:[/dim] [bold]{0}[/bold]".format(self.model_name))
        console.print("  [dim]requests:[/dim] {0}".format(self.request_count))
        console.print("  [dim]files created:[/dim] {0}".format(self.file_count))
        console.print("  [dim]session:[/dim] {0}m {1}s".format(minutes, seconds))
        console.print()

    def run(self):
        self.show_banner()

        console.print(Panel(
            "[cyan]GLASSES VIBE AGI CLI Agent v6.0[/cyan]\n"
            "[dim]Kod yaz, dosya olustur, sinirsiz guc seninle.[/dim]",
            border_style="magenta"
        ))
        console.print()

        self.model_name = self.select_model()

        console.print()
        console.print(Rule("session started", style="dim cyan"))
        console.print()

        while True:
            try:
                user_input = questionary.text(
                    "GLASSES VIBE >",
                    style=CUSTOM_STYLE,
                    qmark=">>"
                ).ask()
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
                    continue
                else:
                    console.print("  [dim]Unknown command: /{0}. Type /help.[/dim]".format(cmd))
                    continue

            self.status = "THINKING"
            self.history.add("user", user_input)
            self.request_count += 1

            prompt = "{0}\n\nKullanici: {1}".format(self.history.get_system_prompt(), user_input)

            with Live(Spinner("dots", text="GLASSES VIBE dusunuyor...", style="cyan"), refresh_per_second=10, transient=True):
                response = self.ollama_request(self.model_name, prompt)

            if response is None:
                self.status = "READY"
                continue

            parsed = self.process_json_response(response)
            self.history.add("assistant", response)

            dusunce = parsed.get("dusunce", "")
            aksiyon = parsed.get("aksiyon", "mesaj_gonder")
            dosya_adi = parsed.get("dosya_adi", "")
            kod_icerigi = parsed.get("kod_icerigi", "")

            if dusunce:
                self.thought_log.append(dusunce)
                console.print(Panel(
                    Text(dusunce, style="italic dim magenta"),
                    title="[magenta]thinking[/magenta]",
                    border_style="magenta",
                    padding=(0, 1)
                ))

            if aksiyon == "dosya_yarat" and dosya_adi and kod_icerigi:
                self.status = "WRITING"
                success, result = self.create_file(dosya_adi, kod_icerigi)
                if success:
                    self.output_log.append("[green]file created: {0}[/green]".format(result))
                    ext = dosya_adi.split('.')[-1] if '.' in dosya_adi else "text"
                    if ext in ("python", "gdscript", "csharp", "javascript", "html", "css", "json", "yaml", "toml", "bash", "powershell"):
                        syntax = Syntax(kod_icerigi, ext, theme="monokai", line_numbers=True, word_wrap=True)
                    else:
                        syntax = Syntax(kod_icerigi, "text", theme="monokai", line_numbers=True, word_wrap=True)
                    console.print(Panel(
                        syntax,
                        title="[green]file created: {0}[/green]".format(dosya_adi),
                        border_style="green",
                        padding=(0, 0)
                    ))
                else:
                    console.print(Panel("[red]File creation error: {0}[/red]".format(result), border_style="red"))
            else:
                if kod_icerigi:
                    self.output_log.append(kod_icerigi[:500])
                    console.print(Panel(
                        Markdown(kod_icerigi),
                        border_style="cyan",
                        padding=(0, 1)
                    ))

            self.status = "READY"
            console.print()


def main():
    agent = GlassesVibeAgent()
    agent.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        console.print(Panel("[magenta]GLASSES VIBE kapatiliyor... Gule gule![/magenta]", border_style="magenta"))
        sys.exit(0)
