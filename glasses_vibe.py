# -*- coding: utf-8 -*-
"""
GLASSES VIBE - AGI CLI Agent v2.0
Niko Software System
Developer: glassesglitchstudio
"""

import os
import sys
import io
import json
import time
import requests
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich.layout import Layout
from rich.columns import Columns
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
        self.provider = None
        self.model_name = None
        self.api_key = None
        self.history = ConversationHistory()
        self.token_count = 0
        self.request_count = 0
        self.file_count = 0
        self.start_time = time.time()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        self.clear_screen()
        console.print()
        console.print(Panel(
            Text(ASCII_LOGO.strip(), style="bold cyan"),
            subtitle=Text("GlassesVibe", style="dim #888888"),
            border_style="magenta",
            padding=(1, 2)
        ))
        console.print()

    def get_ollama_models(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            models = []
            for m in data.get("models", []):
                name = m.get("name", "")
                size = m.get("size", 0)
                size_gb = round(size / (1024**3), 1) if size else "?"
                models.append({"name": name, "size": f"{size_gb} GB"})
            return models
        except Exception:
            return []

    def select_provider(self):
        choice = questionary.select(
            "Model Saglayici Sec:",
            choices=[
                questionary.Choice("Ollama (Yerel Modeller)", value="ollama"),
                questionary.Choice("OpenRouter (Cloud API)", value="openrouter"),
            ],
            style=CUSTOM_STYLE,
            qmark=">>"
        ).ask()

        if choice is None:
            console.print(Panel("[red]Cikis yapiliyor...[/red]", border_style="red"))
            sys.exit(0)

        return choice

    def select_ollama_model(self):
        with Live(Spinner("dots", text="Ollama modelleri taraniyor...", style="cyan"), refresh_per_second=10, transient=True):
            models = self.get_ollama_models()

        if not models:
            console.print(Panel(
                "[red]Hicbir Ollama modeli bulunamadi!\n"
                "Model indirmek icin: ollama pull <model>[/red]",
                border_style="red"
            ))
            sys.exit(0)

        choices = []
        for m in models:
            tag = f"  [{m['size']}]"
            choices.append(questionary.Choice(f"{m['name']}{tag}", value=m['name']))

        choice = questionary.select(
            "Ollama Modelini Sec:",
            choices=choices,
            style=CUSTOM_STYLE,
            qmark=">>"
        ).ask()

        if choice is None:
            sys.exit(0)

        return choice

    def select_openrouter_model(self):
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            console.print(Panel(
                "[yellow]OpenRouter API Key gerekli![/yellow]\n"
                "[dim]https://openrouter.ai/settings keys adresinden alabilirsin.\n"
                "veya .env dosyasina OPENROUTER_API_KEY=sk-or-xxx ekle.[/dim]",
                border_style="yellow"
            ))
            api_key = questionary.password(
                "OpenRouter API Key gir:",
                style=CUSTOM_STYLE,
                qmark=">>"
            ).ask()
            if not api_key:
                console.print(Panel("[red]API key olmadan OpenRouter kullanilamaz. Ollama'ya yonlendiriliyorsun...[/red]", border_style="red"))
                self.provider = "ollama"
                self.model_name = self.select_ollama_model()
                return

        models = [
            {"id": "google/gemini-2.5-flash", "name": "Google Gemini 2.5 Flash (Ucretsiz)"},
            {"id": "meta-llama/llama-3.1-8b-instruct", "name": "Llama 3.1 8B (Ucretsiz)"},
            {"id": "mistralai/mistral-7b-instruct", "name": "Mistral 7B (Ucretsiz)"},
            {"id": "google/gemini-2.5-pro", "name": "Google Gemini 2.5 Pro"},
            {"id": "anthropic/claude-sonnet-4-20250514", "name": "Claude Sonnet 4"},
            {"id": "openai/gpt-4o", "name": "OpenAI GPT-4o"},
            {"id": "qwen/qwen2.5-coder-32b-instruct", "name": "Qwen 2.5 Coder 32B"},
        ]

        choices = [questionary.Choice(m["name"], value=m["id"]) for m in models]
        choices.append(questionary.Choice("Diger (manuel ID gir)", value="custom"))

        choice = questionary.select(
            "OpenRouter Modelini Sec:",
            choices=choices,
            style=CUSTOM_STYLE,
            qmark=">>"
        ).ask()

        if choice == "custom":
            choice = Prompt.ask("Model ID gir (orn: google/gemini-2.5-pro)")

        if choice is None:
            sys.exit(0)

        return choice, api_key

    def ollama_request_stream(self, model, messages):
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "format": "json",
        }

        full_response = ""
        try:
            with requests.post(url, json=payload, stream=True, timeout=120) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        full_response += content
                        yield content
        except requests.exceptions.ConnectionError:
            console.print(Panel("[red]Ollama servisi calismiyor! `ollama serve`[/red]", border_style="red"))
            yield None
        except Exception as e:
            console.print(Panel(f"[red]Hata: {e}[/red]", border_style="red"))
            yield None

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
            console.print(Panel(f"[red]Hata: {e}[/red]", border_style="red"))
            return None

    def openrouter_request(self, model, api_key, messages):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://glassesglitchstudio.com",
            "X-Title": "GLASSES VIBE",
        }
        payload = {
            "model": model,
            "messages": messages,
            "response_format": {"type": "json_object"},
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            if response.status_code == 401:
                console.print(Panel("[red]API Key gecersiz! OPENROUTER_API_KEY'i kontrol et.[/red]", border_style="red"))
                return None
            if response.status_code == 402:
                console.print(Panel("[red]OpenRouter kredi bitti! Hesabina kredi ekle.[/red]", border_style="red"))
                return None
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            console.print(Panel("[red]Istek zaman asimina ugradi.[/red]", border_style="red"))
            return None
        except Exception as e:
            console.print(Panel(f"[red]OpenRouter Hata: {e}[/red]", border_style="red"))
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

    def show_thought(self, thought):
        console.print(Panel(
            Text(thought, style="italic dim cyan"),
            title="[magenta]thinking[/magenta]",
            border_style="dim cyan",
            padding=(0, 1)
        ))

    def show_file_created(self, file_path, content):
        ext = file_path.split('.')[-1] if '.' in file_path else "text"
        if ext in ("python", "gdscript", "csharp", "javascript", "html", "css", "json", "yaml", "toml", "bash", "powershell"):
            syntax = Syntax(content, ext, theme="monokai", line_numbers=True, word_wrap=True)
        else:
            syntax = Syntax(content, "text", theme="monokai", line_numbers=True, word_wrap=True)

        console.print(Panel(
            syntax,
            title=f"[green]file created: {file_path}[/green]",
            border_style="green",
            padding=(0, 0)
        ))

    def show_message(self, message):
        console.print(Panel(
            Markdown(message),
            border_style="cyan",
            padding=(0, 1)
        ))

    def show_status(self):
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("key", style="dim cyan")
        table.add_column("value", style="bold white")

        table.add_row("provider", self.provider.upper())
        table.add_row("model", self.model_name)
        table.add_row("requests", str(self.request_count))
        table.add_row("files created", str(self.file_count))
        table.add_row("session", f"{minutes}m {seconds}s")

        console.print(Panel(table, title="[magenta]status[/magenta]", border_style="magenta"))

    def show_commands(self):
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("command", style="bold cyan")
        table.add_column("description", style="dim white")

        table.add_row("/status", "Show session status")
        table.add_row("/clear", "Clear conversation history")
        table.add_row("/models", "List available models")
        table.add_row("/help", "Show this help menu")
        table.add_row("/exit", "Exit GLASSES VIBE")

        console.print(Panel(table, title="[magenta]commands[/magenta]", border_style="magenta"))

    def show_input_prompt(self):
        model_short = self.model_name.split(":")[0] if ":" in self.model_name else self.model_name
        provider_tag = "ollama" if self.provider == "ollama" else "cloud"
        return f"[bold cyan]{model_short}[/bold cyan] [dim]({provider_tag})[/dim] > "

    def run(self):
        self.show_banner()

        console.print(Panel(
            "[cyan]GLASSES VIBE AGI CLI Agent v2.0[/cyan]\n"
            "[dim]Kod yaz, dosya olustur, sinirsiz guc seninle.[/dim]\n"
            "[dim]Yardim icin /help yaz.[/dim]",
            border_style="magenta"
        ))
        console.print()

        provider = self.select_provider()

        if provider == "ollama":
            self.provider = "ollama"
            self.model_name = self.select_ollama_model()
        elif provider == "openrouter":
            result = self.select_openrouter_model()
            if result:
                self.provider = "openrouter"
                self.model_name, self.api_key = result
            else:
                return

        console.print()
        console.print(Rule("[dim]session started[/dim]", style="dim cyan"))
        console.print()

        while True:
            try:
                user_input = Prompt.ask(self.show_input_prompt())
            except (EOFError, KeyboardInterrupt):
                console.print()
                console.print(Panel("[magenta]GLASSES VIBE kapatiliyor... Gule gule, Erkay![/magenta]", border_style="magenta"))
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            if user_input.startswith("/"):
                cmd = user_input[1:].lower()
                if cmd == "exit" or cmd == "quit":
                    console.print(Panel("[magenta]GLASSES VIBE kapatiliyor... Gule gule, Erkay![/magenta]", border_style="magenta"))
                    break
                elif cmd == "help":
                    self.show_commands()
                    continue
                elif cmd == "status":
                    self.show_status()
                    continue
                elif cmd == "clear":
                    self.history.clear()
                    console.print(Panel("[cyan]Conversation history cleared.[/cyan]", border_style="cyan"))
                    continue
                elif cmd == "models":
                    if self.provider == "ollama":
                        models = self.get_ollama_models()
                        if models:
                            table = Table(show_header=True, box=None)
                            table.add_column("model", style="cyan")
                            table.add_column("size", style="dim")
                            for m in models:
                                table.add_row(m["name"], m["size"])
                            console.print(Panel(table, title="[magenta]ollama models[/magenta]", border_style="magenta"))
                        else:
                            console.print(Panel("[yellow]No models found.[/yellow]", border_style="yellow"))
                    else:
                        console.print(Panel("[dim]OpenRouter models are selected at startup.[/dim]", border_style="dim"))
                    continue
                else:
                    console.print(Panel(f"[yellow]Unknown command: /{cmd}. Type /help for commands.[/yellow]", border_style="yellow"))
                    continue

            self.history.add("user", user_input)
            self.request_count += 1

            messages = [{"role": "system", "content": self.history.get_system_prompt()}]
            messages.extend(self.history.get_messages())

            console.print()

            if self.provider == "ollama":
                with Live(Spinner("dots", text=f"{self.model_name} thinking...", style="cyan"), refresh_per_second=10, transient=True):
                    response = self.ollama_request(self.model_name, user_input)
            else:
                with Live(Spinner("dots", text=f"{self.model_name} (cloud) thinking...", style="cyan"), refresh_per_second=10, transient=True):
                    response = self.openrouter_request(self.model_name, self.api_key, messages)

            if response is None:
                continue

            parsed = self.process_json_response(response)
            self.history.add("assistant", response)

            dusunce = parsed.get("dusunce", "")
            aksiyon = parsed.get("aksiyon", "mesaj_gonder")
            dosya_adi = parsed.get("dosya_adi", "")
            kod_icerigi = parsed.get("kod_icerigi", "")

            if dusunce:
                self.show_thought(dusunce)

            if aksiyon == "dosya_yarat" and dosya_adi and kod_icerigi:
                success, result = self.create_file(dosya_adi, kod_icerigi)
                if success:
                    self.show_file_created(dosya_adi, kod_icerigi)
                else:
                    console.print(Panel(f"[red]File creation error: {result}[/red]", border_style="red"))
            else:
                if kod_icerigi:
                    self.show_message(kod_icerigi)

            console.print()


def main():
    agent = GlassesVibeAgent()
    agent.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        console.print(Panel("[magenta]GLASSES VIBE kapatiliyor... Gule gule, Erkay![/magenta]", border_style="magenta"))
        sys.exit(0)
