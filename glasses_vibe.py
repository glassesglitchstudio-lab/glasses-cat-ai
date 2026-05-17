# -*- coding: utf-8 -*-
"""
GlassesVibe - AGI CLI Agent v3.0
Niko Software
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
from rich import print as rprint

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

console = Console()


class ConversationHistory:
    def __init__(self, max_turns=20):
        self.messages = []
        self.max_turns = max_turns

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2:]

    def get_system_prompt(self):
        return """Sen GlassesVibe adli bir AGI asistansin. Niko Software tarafindan gelistirildin.

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
        self.request_count = 0
        self.file_count = 0
        self.start_time = time.time()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        self.clear_screen()
        console.print()
        console.print("[bold cyan]GlassesVibe[/bold cyan] [dim]v3.0[/dim]")
        console.print(Rule(style="dim"))
        console.print()

    def show_welcome(self):
        console.print("[bold]GlassesVibe AGI CLI Agent[/bold]")
        console.print("[dim]Kod yaz, dosya olustur, sinirsiz guc seninle.[/dim]")
        console.print("[dim]Yardim icin /help yaz.[/dim]")
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
        console.print("[bold]Model Saglayici Sec:[/bold]")
        console.print("  [cyan]1[/cyan]) Ollama (Yerel Modeller)")
        console.print("  [cyan]2[/cyan]) OpenRouter (Cloud API)")
        console.print()

        choice = Prompt.ask("Secim", choices=["1", "2"], default="1")

        if choice == "2":
            return "openrouter"
        return "ollama"

    def select_ollama_model(self):
        with Live(Spinner("dots", text="Modeller taraniyor...", style="cyan"), refresh_per_second=10, transient=True):
            models = self.get_ollama_models()

        if not models:
            console.print()
            console.print("[red]Hicbir Ollama modeli bulunamadi![/red]")
            console.print("[dim]Model indirmek icin: ollama pull <model>[/dim]")
            sys.exit(0)

        console.print()
        console.print("[bold]Ollama Modelleri:[/bold]")
        for i, m in enumerate(models, 1):
            console.print(f"  [cyan]{i}[/cyan]) {m['name']}  [dim]({m['size']})[/dim]")
        console.print()

        choice = Prompt.ask("Model sec", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                return models[idx]["name"]
        except ValueError:
            pass

        return models[0]["name"]

    def select_openrouter_model(self):
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            console.print()
            console.print("[yellow]OpenRouter API Key gerekli![/yellow]")
            console.print("[dim]https://openrouter.ai/settings/keys adresinden al.[/dim]")
            console.print()
            api_key = Prompt.ask("API Key gir", password=True)
            if not api_key:
                console.print("[red]API key olmadan OpenRouter kullanilamaz.[/red]")
                return None, None

        models = [
            {"id": "google/gemini-2.5-flash", "name": "Google Gemini 2.5 Flash (Ucretsiz)"},
            {"id": "meta-llama/llama-3.1-8b-instruct", "name": "Llama 3.1 8B (Ucretsiz)"},
            {"id": "mistralai/mistral-7b-instruct", "name": "Mistral 7B (Ucretsiz)"},
            {"id": "google/gemini-2.5-pro", "name": "Google Gemini 2.5 Pro"},
            {"id": "anthropic/claude-sonnet-4-20250514", "name": "Claude Sonnet 4"},
            {"id": "openai/gpt-4o", "name": "OpenAI GPT-4o"},
            {"id": "qwen/qwen2.5-coder-32b-instruct", "name": "Qwen 2.5 Coder 32B"},
        ]

        console.print()
        console.print("[bold]OpenRouter Modelleri:[/bold]")
        for i, m in enumerate(models, 1):
            console.print(f"  [cyan]{i}[/cyan]) {m['name']}")
        console.print("  [cyan]8[/cyan]) Diger (manuel ID gir)")
        console.print()

        choice = Prompt.ask("Model sec", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                return models[idx]["id"], api_key
            elif idx == 7:
                model_id = Prompt.ask("Model ID gir (orn: google/gemini-2.5-pro)")
                return model_id, api_key
        except ValueError:
            pass

        return models[0]["id"], api_key

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
            console.print("[red]Ollama servisi calismiyor! `ollama serve`[/red]")
            return None
        except requests.exceptions.Timeout:
            console.print("[red]Istek zaman asimina ugradi.[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Hata: {e}[/red]")
            return None

    def openrouter_request(self, model, api_key, messages):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://glassesglitchstudio.com",
            "X-Title": "GlassesVibe",
        }
        payload = {
            "model": model,
            "messages": messages,
            "response_format": {"type": "json_object"},
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            if response.status_code == 401:
                console.print("[red]API Key gecersiz! OPENROUTER_API_KEY'i kontrol et.[/red]")
                return None
            if response.status_code == 402:
                console.print("[red]OpenRouter kredi bitti![/red]")
                return None
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            console.print("[red]Istek zaman asimina ugradi.[/red]")
            return None
        except Exception as e:
            console.print(f"[red]OpenRouter Hata: {e}[/red]")
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
        console.print()
        console.print(Panel(
            Text(thought, style="italic dim"),
            title="thinking",
            border_style="dim",
            padding=(0, 1)
        ))

    def show_file_created(self, file_path, content):
        ext = file_path.split('.')[-1] if '.' in file_path else "text"
        if ext in ("python", "gdscript", "csharp", "javascript", "html", "css", "json", "yaml", "toml", "bash", "powershell"):
            syntax = Syntax(content, ext, theme="monokai", line_numbers=True, word_wrap=True)
        else:
            syntax = Syntax(content, "text", theme="monokai", line_numbers=True, word_wrap=True)

        console.print()
        console.print(Panel(
            syntax,
            title=f"file created: {file_path}",
            border_style="green",
            padding=(0, 0)
        ))

    def show_message(self, message):
        console.print()
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
        table.add_column("key", style="dim")
        table.add_column("value", style="bold")

        table.add_row("provider", self.provider.upper())
        table.add_row("model", self.model_name)
        table.add_row("requests", str(self.request_count))
        table.add_row("files created", str(self.file_count))
        table.add_row("session", f"{minutes}m {seconds}s")

        console.print()
        console.print(Panel(table, title="status", border_style="dim"))

    def show_commands(self):
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("command", style="bold cyan")
        table.add_column("description", style="dim")

        table.add_row("/status", "Show session status")
        table.add_row("/clear", "Clear conversation history")
        table.add_row("/models", "List available models")
        table.add_row("/help", "Show this help menu")
        table.add_row("/exit", "Exit GlassesVibe")

        console.print()
        console.print(Panel(table, title="commands", border_style="dim"))

    def get_input_prompt(self):
        model_short = self.model_name.split(":")[0] if ":" in self.model_name else self.model_name
        provider_tag = "ollama" if self.provider == "ollama" else "cloud"
        return f"[bold cyan]{model_short}[/bold cyan] [dim]({provider_tag})[/dim] > "

    def run(self):
        self.show_banner()
        self.show_welcome()

        provider = self.select_provider()

        if provider == "ollama":
            self.provider = "ollama"
            self.model_name = self.select_ollama_model()
        elif provider == "openrouter":
            result = self.select_openrouter_model()
            if result[0] is None:
                console.print("[red]OpenRouter kurulumu basarisiz. Cikis yapiliyor...[/red]")
                return
            self.provider = "openrouter"
            self.model_name, self.api_key = result

        console.print()
        console.print(Rule("session started", style="dim"))
        console.print()

        while True:
            try:
                user_input = Prompt.ask(self.get_input_prompt())
            except (EOFError, KeyboardInterrupt):
                console.print()
                console.print("[dim]Gule gule, Erkay![/dim]")
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            if user_input.startswith("/"):
                cmd = user_input[1:].lower()
                if cmd in ("exit", "quit"):
                    console.print()
                    console.print("[dim]Gule gule, Erkay![/dim]")
                    break
                elif cmd == "help":
                    self.show_commands()
                    continue
                elif cmd == "status":
                    self.show_status()
                    continue
                elif cmd == "clear":
                    self.history.clear()
                    console.print("[dim]Conversation history cleared.[/dim]")
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
                            console.print()
                            console.print(Panel(table, title="ollama models", border_style="dim"))
                        else:
                            console.print("[dim]No models found.[/dim]")
                    else:
                        console.print("[dim]OpenRouter models are selected at startup.[/dim]")
                    continue
                else:
                    console.print(f"[dim]Unknown command: /{cmd}. Type /help.[/dim]")
                    continue

            self.history.add("user", user_input)
            self.request_count += 1

            messages = [{"role": "system", "content": self.history.get_system_prompt()}]
            messages.extend(self.history.get_messages())

            console.print()

            if self.provider == "ollama":
                with Live(Spinner("dots", text="thinking...", style="cyan"), refresh_per_second=10, transient=True):
                    response = self.ollama_request(self.model_name, user_input)
            else:
                with Live(Spinner("dots", text="thinking...", style="cyan"), refresh_per_second=10, transient=True):
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
                    console.print(f"[red]File creation error: {result}[/red]")
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
        console.print("[dim]Gule gule, Erkay![/dim]")
        sys.exit(0)
