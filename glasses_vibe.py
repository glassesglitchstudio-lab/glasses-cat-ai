# -*- coding: utf-8 -*-
"""
GLASSES VIBE - AGI CLI Agent
Niko Software System v1.2.0
Developer: glassesglitchstudio
"""

import os
import sys
import io
import json
import subprocess
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

BANNER_TEXT = ">>> V I B E <<<"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_banner():
    clear_screen()
    logo_text = Text(ASCII_LOGO.strip(), style="bold cyan")
    banner_text = Text(BANNER_TEXT, style="bold magenta")
    version_text = Text("Niko Software System v1.2.0", style="dim #888888")
    separator = Rule("=" * 60, style="cyan")

    console.print()
    console.print(logo_text, justify="center")
    console.print(banner_text, justify="center")
    console.print()
    console.print(separator)
    console.print(version_text, justify="center")
    console.print(separator)
    console.print()


def select_model():
    choice = questionary.select(
        "AI Modelini Seç:",
        choices=[
            questionary.Choice("GulmezCetinerMax (Ollama - Yerel Canavar v1.2.0)", value="local"),
            questionary.Choice("Cloud Model (Niko Cloud Altyapısı)", value="cloud"),
        ],
        style=CUSTOM_STYLE,
        qmark=">>"
    ).ask()

    if choice is None:
        console.print(Panel("[red]Cikis yapiliyor...[/red]", border_style="red"))
        sys.exit(0)

    return choice


def ollama_request(model, prompt, format_schema=None):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if format_schema:
        payload["format"] = format_schema

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.ConnectionError:
        console.print(Panel("[red]Ollama servisi calismiyor! `ollama serve` komutunu calistir.[/red]", border_style="red"))
        return None
    except requests.exceptions.Timeout:
        console.print(Panel("[red]Istek zaman asimina ugradi.[/red]", border_style="red"))
        return None
    except Exception as e:
        console.print(Panel(f"[red]Hata: {e}[/red]", border_style="red"))
        return None


def process_json_response(response_text):
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
        console.print(Panel("[yellow]JSON parse hatasi. Ham yanit isleniyor...[/yellow]", border_style="yellow"))
        return {
            "dusunce": "Yanıt JSON formatında değil.",
            "aksiyon": "mesaj_gonder",
            "dosya_adi": "",
            "kod_icerigi": response_text
        }


def create_file(file_name, content):
    try:
        full_path = os.path.join(os.getcwd(), file_name)
        os.makedirs(os.path.dirname(full_path) if os.path.dirname(full_path) else ".", exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, full_path
    except Exception as e:
        return False, str(e)


def display_thought_panel(thought):
    panel = Panel(
        Text(thought, style="italic cyan"),
        title="[magenta]DERIN DUSUNCE[/magenta]",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)


def display_success_panel(file_path):
    panel = Panel(
        Text(f"Dosya basariyla olusturuldu!\nPath: {file_path}", style="bold green"),
        title="[green]DOSYA OLUSTURULDU[/green]",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)


def display_response_panel(content, language="text"):
    if language in ("python", "gdscript", "csharp", "javascript", "html", "css"):
        syntax = Syntax(content, language, theme="monokai", line_numbers=True)
        panel = Panel(syntax, title="[cyan]CIKTI[/cyan]", border_style="cyan", padding=(1, 1))
    else:
        panel = Panel(
            Markdown(content),
            title="[cyan]CIKTI[/cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
    console.print(panel)


def display_message_panel(message):
    panel = Panel(
        Text(message, style="green"),
        title="[green]GLASSES VIBE[/green]",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)


def build_system_prompt():
    return """Sen GLASSES VIBE adlı bir AGI asistansın. Niko Software tarafından geliştirildin.

YANIT FORMATIN:
Sen SADECE ve SADECE aşağıdaki JSON şeması ile yanıt vermelisin. Başka hiçbir şey yazma.

{
  "dusunce": "Arka planda yürüttüğün derin mantık ve algoritma planı",
  "aksiyon": "dosya_yarat" veya "mesaj_gonder",
  "dosya_adi": "Oluşturulacak dosyanın adı ve uzantısı (sadece dosya_yarat için)",
  "kod_icerigi": "Yazılacak kod bloğu veya kullanıcıya iletilecek mesaj"
}

KURALLAR:
- Eğer kullanıcı kod yazmanı isterse, aksiyon 'dosya_yarat' olmalı ve uygun dosya uzantısı verilmeli.
- Eğer kullanıcı soru soruyorsa, aksiyon 'mesaj_gonder' olmalı.
- JSON dışında hiçbir karakter yazma. Backtick kullanma.
- Türkçe konuş."""


def handle_local_mode():
    model_name = "gulmzcetiner"
    system_prompt = build_system_prompt()

    console.print(Panel(
        "[cyan]Model:[/cyan] [bold magenta]{model_name}[/bold magenta]\n"
        "[cyan]Durum:[/cyan] [green]Baglandi[/green]",
        title="[cyan]OLLAMA BAGLANTISI[/cyan]",
        border_style="cyan"
    ))

    conversation_history = []

    while True:
        console.print()
        user_input = questionary.text(
            "GLASSES VIBE >",
            style=CUSTOM_STYLE,
            qmark=">>"
        ).ask()

        if user_input is None or user_input.strip().lower() in ['çıkış', 'exit', 'quit']:
            console.print(Panel("[magenta]GLASSES VIBE kapatiliyor...[/magenta]", border_style="magenta"))
            break

        if not user_input.strip():
            continue

        console.print()

        prompt = f"{system_prompt}\n\nKullanıcı: {user_input}"

        with Live(Spinner("dots", text="GulmezCetinerMax dusunuyor...", style="cyan"), refresh_per_second=10, transient=True):
            response = ollama_request(model_name, prompt)

        if response is None:
            continue

        parsed = process_json_response(response)

        dusunce = parsed.get("dusunce", "")
        aksiyon = parsed.get("aksiyon", "mesaj_gonder")
        dosya_adi = parsed.get("dosya_adi", "")
        kod_icerigi = parsed.get("kod_icerigi", "")

        if dusunce:
            display_thought_panel(dusunce)

        if aksiyon == "dosya_yarat" and dosya_adi and kod_icerigi:
            success, result = create_file(dosya_adi, kod_icerigi)
            if success:
                display_success_panel(result)
                display_response_panel(kod_icerigi, dosya_adi.split('.')[-1] if '.' in dosya_adi else "text")
            else:
                console.print(Panel(f"[red]Dosya oluşturma hatası: {result}[/red]", border_style="red"))
        else:
            if kod_icerigi:
                display_message_panel(kod_icerigi)

        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})


def handle_cloud_mode():
    console.print(Panel(
        "[yellow]Niko Cloud Altyapisi su anda bakimda.[/yellow]\n"
        "[dim]Yakinda aktif olacak. Simdilik Ollama modelini kullan.[/dim]",
        title="[yellow]CLOUD MODEL[/yellow]",
        border_style="yellow"
    ))


def main():
    show_banner()

    console.print(Panel(
        "[cyan]GLASSES VIBE AGI CLI Ajana hos geldin, Erkay![/cyan]\n"
        "[dim]Kod yaz, dosya olustur, sinirsiz guc seninle.[/dim]",
        title="[magenta]SISTEM BASLATILDI[/magenta]",
        border_style="magenta"
    ))

    model_choice = select_model()

    if model_choice == "local":
        handle_local_mode()
    elif model_choice == "cloud":
        handle_cloud_mode()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        console.print(Panel("[magenta]GLASSES VIBE kapatiliyor... Gule gule, Erkay![/magenta]", border_style="magenta"))
        sys.exit(0)
