# -*- coding: utf-8 -*-
"""
GlassesVibe - AGI CLI Agent v5.0
Niko Software
"""

import os
import sys
import io
import json
import time
import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from rich.prompt import Prompt
from rich.rule import Rule

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
        return """Sen GlassesVibe adli bir AGI asistansin.

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

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        self.clear_screen()
        console.print()
        console.print("  [bold white]GlassesVibe[/bold white]")
        console.print()

    def show_welcome(self):
        console.print("  [dim]Kod yaz, dosya olustur, sinirsiz guc seninle.[/dim]")
        console.print("  [dim]/help ile komutlari gor.[/dim]")
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

    def select_model(self):
        with Live(Spinner("dots", text="Modeller taraniyor...", style="cyan"), refresh_per_second=10, transient=True):
            models = self.get_ollama_models()
        if not models:
            console.print()
            console.print("  [red]Hicbir Ollama modeli bulunamadi![/red]")
            console.print()
            console.print("  [dim]Ollama yuklu degil veya hic model indirilmemis.[/dim]")
            console.print("  [dim]Ollama indir: https://ollama.com[/dim]")
            console.print("  [dim]Model indir: ollama pull qwen2.5-coder:14b[/dim]")
            console.print()
            sys.exit(0)
        console.print()
        console.print("  [bold]Kullanilabilir Modeller[/bold]")
        console.print()
        for i, m in enumerate(models, 1):
            console.print("  [cyan]{0}[/cyan]  {1}  [dim]({2})[/dim]".format(i, m['name'], m['size']))
        console.print()
        choice = Prompt.ask("  Model sec", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                return models[idx]["name"]
        except ValueError:
            pass
        return models[0]["name"]

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
            console.print()
            console.print("  [red]Ollama servisi calismiyor![/red]")
            console.print("  [dim]Terminalde `ollama serve` komutunu calistir.[/dim]")
            console.print()
            return None
        except requests.exceptions.Timeout:
            console.print("  [red]Istek zaman asimina ugradi.[/red]")
            return None
        except Exception as e:
            console.print("  [red]Hata: {0}[/red]".format(e))
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
        console.print("  [dim]thinking...[/dim]")
        console.print("  [dim]{0}[/dim]".format(thought))

    def show_file_created(self, file_path, content):
        ext = file_path.split('.')[-1] if '.' in file_path else "text"
        if ext in ("python", "gdscript", "csharp", "javascript", "html", "css", "json", "yaml", "toml", "bash", "powershell"):
            syntax = Syntax(content, ext, theme="monokai", line_numbers=True, word_wrap=True)
        else:
            syntax = Syntax(content, "text", theme="monokai", line_numbers=True, word_wrap=True)
        console.print()
        console.print("  [green]file created: {0}[/green]".format(file_path))
        console.print(syntax)

    def show_message(self, message):
        console.print()
        console.print(Markdown(message))

    def show_status(self):
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        console.print()
        console.print("  [dim]model:[/dim] {0}".format(self.model_name))
        console.print("  [dim]requests:[/dim] {0}".format(self.request_count))
        console.print("  [dim]files created:[/dim] {0}".format(self.file_count))
        console.print("  [dim]session:[/dim] {0}m {1}s".format(minutes, seconds))
        console.print()

    def show_commands(self):
        console.print()
        console.print("  [bold cyan]/status[/bold cyan]     Show session status")
        console.print("  [bold cyan]/clear[/bold cyan]      Clear conversation history")
        console.print("  [bold cyan]/models[/bold cyan]     List available models")
        console.print("  [bold cyan]/help[/bold cyan]       Show this help menu")
        console.print("  [bold cyan]/exit[/bold cyan]       Exit GlassesVibe")
        console.print()

    def get_input_prompt(self):
        return "[bold]>[/bold] "

    def run(self):
        self.show_banner()
        self.show_welcome()
        self.model_name = self.select_model()
        console.print()
        console.print("  [dim]session started[/dim]")
        console.print()
        while True:
            try:
                user_input = Prompt.ask(self.get_input_prompt())
            except (EOFError, KeyboardInterrupt):
                console.print()
                console.print("  [dim]Gule gule![/dim]")
                break
            user_input = user_input.strip()
            if not user_input:
                continue
            if user_input.startswith("/"):
                cmd = user_input[1:].lower()
                if cmd in ("exit", "quit"):
                    console.print()
                    console.print("  [dim]Gule gule![/dim]")
                    break
                elif cmd == "help":
                    self.show_commands()
                    continue
                elif cmd == "status":
                    self.show_status()
                    continue
                elif cmd == "clear":
                    self.history.clear()
                    console.print("  [dim]Conversation history cleared.[/dim]")
                    continue
                elif cmd == "models":
                    models = self.get_ollama_models()
                    if models:
                        console.print()
                        console.print("  [bold]Ollama Modelleri[/bold]")
                        console.print()
                        for m in models:
                            console.print("  {0}  [dim]({1})[/dim]".format(m["name"], m["size"]))
                        console.print()
                    else:
                        console.print("  [dim]No models found.[/dim]")
                    continue
                else:
                    console.print("  [dim]Unknown command: /{0}. Type /help.[/dim]".format(cmd))
                    continue
            self.history.add("user", user_input)
            self.request_count += 1
            messages = [{"role": "system", "content": self.history.get_system_prompt()}]
            messages.extend(self.history.get_messages())
            console.print()
            with Live(Spinner("dots", text="thinking...", style="cyan"), refresh_per_second=10, transient=True):
                response = self.ollama_request(self.model_name, user_input)
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
                    console.print("  [red]File creation error: {0}[/red]".format(result))
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
        console.print("  [dim]Gule gule![/dim]")
        sys.exit(0)
