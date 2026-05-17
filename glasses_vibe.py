# -*- coding: utf-8 -*-
"""
GLASSES VIBE - AGI CLI Agent
Niko Software System v1.3.0
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
    version_text = Text("Niko Software System v1.3.0", style="dim #888888")
    separator = Rule("=" * 60, style="cyan")

    console.print()
    console.print(logo_text, justify="center")
    console.print(banner_text, justify="center")
    console.print()
    console.print(separator)
    console.print(version_text, justify="center")
    console.print(separator)
    console.print()


def get_ollama_models():
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


def select_model_provider():
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


def select_ollama_model():
    with Live(Spinner("dots", text="Ollama modelleri taraniyor...", style="cyan"), refresh_per_second=10, transient=True):
        models = get_ollama_models()

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
        console.print(Panel("[red]Cikis yapiliyor...[/red]", border_style="red"))
        sys.exit(0)

    return choice


def select_openrouter_model():
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        api_key = questionary.password(
            "OpenRouter API Key gir (veya .env dosyasina OPENROUTER_API_KEY ekle):",
            style=CUSTOM_STYLE,
            qmark=">>"
        ).ask()
        if not api_key:
            console.print(Panel("[red]API key gerekli. Cikis yapiliyor...[/red]", border_style="red"))
            sys.exit(0)

    models = [
        {"id": "google/gemini-2.5-pro", "name": "Google Gemini 2.5 Pro"},
        {"id": "anthropic/claude-sonnet-4-20250514", "name": "Claude Sonnet 4"},
        {"id": "openai/gpt-4o", "name": "OpenAI GPT-4o"},
        {"id": "meta-llama/llama-3.3-70b-instruct", "name": "Llama 3.3 70B"},
        {"id": "qwen/qwen2.5-coder-32b-instruct", "name": "Qwen 2.5 Coder 32B"},
        {"id": "mistralai/mistral-large-2411", "name": "Mistral Large 2"},
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
        choice = questionary.text(
            "Model ID gir (orn: google/gemini-2.5-pro):",
            style=CUSTOM_STYLE,
            qmark=">>"
        ).ask()

    if choice is None:
        console.print(Panel("[red]Cikis yapiliyor...[/red]", border_style="red"))
        sys.exit(0)

    return choice, api_key


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


def openrouter_request(model, api_key, prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://glassesglitchstudio.com",
        "X-Title": "GLASSES VIBE",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Sen GLASSES VIBE adli bir AGI asistansin. SADECE JSON formatinda yanit ver. Backtick kullanma."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        console.print(Panel("[red]Istek zaman asimina ugradi.[/red]", border_style="red"))
        return None
    except Exception as e:
        console.print(Panel(f"[red]OpenRouter Hata: {e}[/red]", border_style="red"))
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
            "dusunce": "Yanit JSON formatinda degil.",
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
    if language in ("python", "gdscript", "csharp", "javascript", "html", "css", "json", "yaml", "toml", "bash", "powershell"):
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
    return """Sen GLASSES VIBE adli bir AGI asistansin. Niko Software tarafindan gelistirildin.

YANIT FORMATIN:
Sen SADECE ve SADECE asagidaki JSON semasi ile yanit vermelisin. Baska hicbir sey yazma.

{
  "dusunce": "Arka planda yuruttugun derin mantik ve algoritma plani",
  "aksiyon": "dosya_yarat" veya "mesaj_gonder",
  "dosya_adi": "Olusturulacak dosyanin adi ve uzantisi (sadece dosya_yarat icin)",
  "kod_icerigi": "Yazilacak kod blogu veya kullaniciya iletilecek mesaj"
}

KURALLAR:
- Eger kullanici kod yazmani isterse, aksiyon 'dosya_yarat' olmali ve uygun dosya uzantisi verilmeli.
- Eger kullanici soru soruyorsa, aksiyon 'mesaj_gonder' olmali.
- JSON disinda hicbir karakter yazma. Backtick kullanma.
- Turkce konus."""


def process_response(parsed):
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
            console.print(Panel(f"[red]Dosya olusturma hatasi: {result}[/red]", border_style="red"))
    else:
        if kod_icerigi:
            display_message_panel(kod_icerigi)


def run_agent(model_name, provider="ollama", api_key=None):
    system_prompt = build_system_prompt()

    if provider == "ollama":
        provider_label = "OLLAMA"
        spinner_text = f"{model_name} dusunuyor..."
    else:
        provider_label = "OPENROUTER"
        spinner_text = f"{model_name} (Cloud) dusunuyor..."

    console.print(Panel(
        f"[cyan]Saglayici:[/cyan] [bold magenta]{provider_label}[/bold magenta]\n"
        f"[cyan]Model:[/cyan] [bold cyan]{model_name}[/bold cyan]\n"
        f"[cyan]Durum:[/cyan] [green]Baglandi[/green]",
        title=f"[cyan]{provider_label} BAGLANTISI[/cyan]",
        border_style="cyan"
    ))

    while True:
        console.print()
        user_input = questionary.text(
            "GLASSES VIBE >",
            style=CUSTOM_STYLE,
            qmark=">>"
        ).ask()

        if user_input is None or user_input.strip().lower() in ['cikis', 'exit', 'quit']:
            console.print(Panel("[magenta]GLASSES VIBE kapatiliyor...[/magenta]", border_style="magenta"))
            break

        if not user_input.strip():
            continue

        console.print()

        prompt = f"{system_prompt}\n\nKullanici: {user_input}"

        with Live(Spinner("dots", text=spinner_text, style="cyan"), refresh_per_second=10, transient=True):
            if provider == "ollama":
                response = ollama_request(model_name, prompt)
            else:
                response = openrouter_request(model_name, api_key, prompt)

        if response is None:
            continue

        parsed = process_json_response(response)
        process_response(parsed)


def main():
    show_banner()

    console.print(Panel(
        "[cyan]GLASSES VIBE AGI CLI Ajana hos geldin, Erkay![/cyan]\n"
        "[dim]Kod yaz, dosya olustur, sinirsiz guc seninle.[/dim]",
        title="[magenta]SISTEM BASLATILDI[/magenta]",
        border_style="magenta"
    ))

    provider = select_model_provider()

    if provider == "ollama":
        model_name = select_ollama_model()
        run_agent(model_name, provider="ollama")
    elif provider == "openrouter":
        model_name, api_key = select_openrouter_model()
        run_agent(model_name, provider="openrouter", api_key=api_key)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        console.print(Panel("[magenta]GLASSES VIBE kapatiliyor... Gule gule, Erkay![/magenta]", border_style="magenta"))
        sys.exit(0)
