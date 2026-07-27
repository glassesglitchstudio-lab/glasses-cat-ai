"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     NEXUS CLI - Hibrit Model Yonetim ve Veri Enjeksiyon         ║
║     Glassesglitch Studio / Glasses Software Altyapisi           ║
║     Antigravity TUI v3.0 - Neon Siber Arayuz                    ║
║                                                                  ║
║     Mimarisi:                                                    ║
║     NexusCLI                                                     ║
║      ├── OllamaDogrulayici      → Servis + model kontrol        ║
║      ├── LocalMotor             → Yerel Qwen 7B cagrisi         ║
║     ├── BulutMotor             → OpenAI / Qwen API             ║
║     ├── FallbackMotor           → Cloud cokerse local'e gec     ║
║      └── VeriEnjektoru          → dataset.json yazici           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

logging.basicConfig(level=logging.INFO, format="[NEXUS] %(message)s")
logger = logging.getLogger("NexusCLI")

RICH_OK = False
QUESTIONARY_OK = False
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.theme import Theme
    from rich.style import Style
    from rich.text import Text
    from rich import box
    RICH_OK = True
except ImportError:
    pass

try:
    import questionary
    QUESTIONARY_OK = True
except ImportError:
    pass

NEXUS_VERSION = "1.0.0"
PROJECT_ROOT = Path(__file__).parent.resolve()
DATASET_PATH = PROJECT_ROOT / "glitch_dataset.json"
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_CHAT = f"{OLLAMA_BASE}/api/chat"
OLLAMA_TAGS = f"{OLLAMA_BASE}/api/tags"
LOCAL_MODEL = "qwen2.5-coder:7b"

NEXUS_THEME = Theme({
    "local": "bold cyan",
    "cloud": "bold yellow",
    "fallback": "bold magenta",
    "success": "bold green",
    "error": "bold red",
    "info": "dim white",
    "title": "bold bright_white",
    "accent": "bold bright_blue",
})

BANNER_ART = r"""
    ╔══╗ ╔══╗ ╔══╗ ╔══╗ ╔══╗ ╔══╗
    ║N ║ ║E ║ ║X ║ ║U ║ ║S ║ ║  ║
    ╚══╝ ╚══╝ ╚══╝ ╚══╝ ╚══╝ ╚══╝
    ╔══╗ ╔══╗ ╔══╗ ╔══╗ ╔══╗ ╔══╗
    ║C ║ ║L ║ ║I ║ ║  ║ ║v ║ ║1 ║
    ╚══╝ ╚══╝ ╚══╝ ╚══╝ ╚══╝ ╚══╝
    ╔══╗ ╔══╗ ╔══╗ ╔══╗ ╔══╗
    ║. ║ ║0 ║ ║. ║ ║0 ║ ║  ║
    ╚══╝ ╚══╝ ╚══╝ ╚══╝ ╚══╝
"""

QUESTIONARY_STYLE = questionary.Style([
    ("qmark", "fg:cyan bold"),
    ("question", "fg:white bold"),
    ("answer", "fg:cyan bold"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("selected", "fg:green bold"),
    ("separator", "fg:blue"),
    ("instruction", "fg:gray"),
    ("text", "fg:white"),
    ("disabled", "fg:gray italic"),
]) if QUESTIONARY_OK else None


class NexusUI:
    def __init__(self):
        self.console = Console(theme=NEXUS_THEME) if RICH_OK else None

    def banner(self):
        if self.console:
            panel = Panel(
                Text(BANNER_ART.strip(), style="accent"),
                subtitle=Text("[ Glasses Software - Primary Core v2.5 ]", style="info"),
                box=box.HEAVY,
                border_style="bright_blue",
                padding=(0, 2),
            )
            self.console.print(panel)
            self.console.print()
        else:
            print(BANNER_ART.strip())
            print("  [ Glasses Software - Primary Core v2.5 ]\n")

    def durum_paneli(self, mesaj: str, stil: str = "info"):
        if self.console:
            panel = Panel(Text(mesaj, style=stil), box=box.ROUNDED, border_style=stil, padding=(0, 1))
            self.console.print(panel)
        else:
            print(f"  {mesaj}")

    def hata_paneli(self, baslik: str, mesaj: str):
        if self.console:
            panel = Panel(
                Text(f"{mesaj}", style="error"),
                title=Text(baslik, style="error"),
                box=box.HEAVY,
                border_style="red",
                padding=(0, 1),
            )
            self.console.print(panel)
        else:
            print(f"  {baslik}: {mesaj}")

    def basari_paneli(self, mesaj: str):
        if self.console:
            panel = Panel(Text(mesaj, style="success"), box=box.ROUNDED, border_style="green", padding=(0, 1))
            self.console.print(panel)
        else:
            print(f"  ✅ {mesaj}")

    def yanit_paneli(self, etiket: str, model: str, yanit: str, stil: str = "local"):
        if self.console:
            ust = Text(f"[{etiket}] [{model}]", style=stil)
            icerik = Text(yanit, style="bright_white")
            panel = Panel(icerik, title=ust, box=box.HEAVY, border_style=stil, padding=(1, 2))
            self.console.print(panel)
        else:
            print(f"  [{etiket}][{model}]")
            print(f"  {'─' * 50}")
            print(f"  {yanit}\n")

    def tablo_goster(self, kayitlar: list, toplam: int):
        if self.console and kayitlar:
            table = Table(
                title=Text(f"Glitch Dataset - Toplam {toplam} kayit", style="title"),
                box=box.HEAVY_EDGE,
                border_style="bright_blue",
                header_style="bold cyan",
                title_justify="center",
            )
            table.add_column("#", style="dim", width=4)
            table.add_column("Kategori", style="accent", width=10)
            table.add_column("Soru", style="bright_white", width=50)
            table.add_column("Cevap", style="bright_white", width=50, overflow="fold")

            for i, k in enumerate(kayitlar, 1):
                kat = k.get("category", "general")
                instr = k["instruction"][:80]
                out = k["output"][:80].replace("\n", " ")
                table.add_row(str(i), kat, instr, out)

            self.console.print(table)
        else:
            print(f"[VERI] Toplam {toplam} kayit")
            for k in kayitlar:
                kat = f" [{k.get('category', 'general')}]" if "category" in k else ""
                print(f"  ├─{kat} {k['instruction'][:60]}...")
                print(f"  └─ {k['output'][:60]}...\n")

    def spinner(self, mesaj: str = "Bekleniyor..."):
        if self.console:
            return self.console.status(f"[accent]{mesaj}")
        return _NullSpinner()

    def siber_uyari(self, mesaj: str):
        if self.console:
            self.console.print(f"\n[error]⚡ {mesaj}[/error]\n")
        else:
            print(f"\n  ⚡ {mesaj}\n")


class _NullSpinner:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def update(self, *args, **kwargs):
        pass


class OllamaDogrulayici:
    def __init__(self):
        self.session = requests.Session()

    def servis_kontrol(self) -> bool:
        try:
            r = self.session.get(OLLAMA_BASE, timeout=3)
            return r.status_code < 500
        except requests.exceptions.ConnectionError:
            return False

    def model_kontrol(self, model: str = LOCAL_MODEL) -> bool:
        try:
            r = self.session.get(OLLAMA_TAGS, timeout=5)
            if r.status_code != 200:
                return False
            modeller = r.json().get("models", [])
            return any(m["name"].startswith(model) for m in modeller)
        except Exception:
            return False

    def binary_kontrol(self) -> bool:
        import shutil
        return shutil.which("ollama") is not None

    def binary_yukle(self, ui) -> bool:
        import subprocess
        ui.durum_paneli("Ollama indiriliyor... (winget ile)", "accent")
        try:
            r = subprocess.run(
                ["winget", "install", "Ollama.Ollama", "--accept-package-agreements", "--accept-source-agreements"],
                capture_output=True, text=True, timeout=120
            )
            if r.returncode == 0:
                ui.basari_paneli("[BASARILI] Ollama basariyla yuklendi!")
                return True
            ui.hata_paneli(" KURULUM HATASI ", f"winget basarisiz:\n{r.stderr[:300]}")
            return False
        except FileNotFoundError:
            ui.hata_paneli(" WINGET YOK ", "winget bulunamadi. Ollama'yu https://ollama.com adresinden manuel indir.")
            return False
        except Exception as e:
            ui.hata_paneli(" KURULUM HATASI ", str(e))
            return False

    def servis_baslat(self, ui) -> bool:
        import subprocess, time
        ui.durum_paneli("Ollama servisi baslatiliyor...", "accent")
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for _ in range(15):
                time.sleep(1)
                if self.servis_kontrol():
                    ui.basari_paneli("[BASARILI] Ollama servisi calisiyor!")
                    return True
            ui.hata_paneli(" SERVIS BASLATILAMADI ", "Ollama serve 15sn icinde yanit vermedi.")
            return False
        except Exception as e:
            ui.hata_paneli(" SERVIS HATASI ", str(e))
            return False

    def model_yukle(self, ui, model: str = LOCAL_MODEL) -> bool:
        import subprocess
        ui.durum_paneli(f"Model indiriliyor: {model}", "accent")
        try:
            r = subprocess.run(
                ["ollama", "pull", model],
                capture_output=True, text=True, timeout=600
            )
            if r.returncode == 0:
                ui.basari_paneli(f"[BASARILI] Model {model} basariyla indirildi!")
                return True
            ui.hata_paneli(" MODEL HATASI ", f"ollama pull basarisiz:\n{r.stderr[:300]}")
            return False
        except Exception as e:
            ui.hata_paneli(" MODEL HATASI ", str(e))
            return False

    def rapor(self) -> Dict:
        servis = self.servis_kontrol()
        model_var = self.model_kontrol() if servis else False
        return {
            "servis_aktif": servis,
            "model_mevcut": model_var,
            "model_adi": LOCAL_MODEL,
            "durum": "HAZIR" if (servis and model_var) else ("SERVIS_YOK" if not servis else "MODEL_YOK"),
        }


class LocalMotor:
    def __init__(self):
        self.session = requests.Session()
        self.model = LOCAL_MODEL

    def sor(self, prompt: str, sicaklik: float = 0.3) -> Dict:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Sen NEXUS AI'sin. Glassesglitch Studio icin siber guvenlik ve C#/Unity optimizasyonu uzmanisin. Yanitlarini kisa, net ve uzman seviyesinde ver.",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": sicaklik, "top_p": 0.9},
        }
        try:
            r = self.session.post(OLLAMA_CHAT, json=payload, timeout=120)
            if r.status_code == 200:
                yanit = r.json()["message"]["content"]
                return {"success": True, "response": yanit, "model": self.model, "backend": "ollama"}
            return {"success": False, "error": f"Ollama HTTP {r.status_code}", "model": self.model}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Ollama baglantisi yok! Servisi baslat: ollama serve", "model": self.model}
        except Exception as e:
            return {"success": False, "error": str(e), "model": self.model}


class BulutMotor:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.qwen_key = os.getenv("QWEN_API_KEY", "")
        self.session = requests.Session()

    def sor(self, prompt: str, saglayici: str = "openai") -> Dict:
        if saglayici == "openai":
            return self._openai_sor(prompt)
        elif saglayici == "qwen":
            return self._qwen_sor(prompt)
        return {"success": False, "error": f"Bilinmeyen saglayici: {saglayici}"}

    def _openai_sor(self, prompt: str) -> Dict:
        if not self.openai_key:
            return {"success": False, "error": "OPENAI_API_KEY .env dosyasinda bulunamadi"}
        headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Sen NEXUS AI'sin. Glassesglitch Studio icin uzman siber guvenlik ve C#/Unity mobil optimizasyon danismani."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        try:
            r = self.session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=60)
            if r.status_code == 200:
                yanit = r.json()["choices"][0]["message"]["content"]
                return {"success": True, "response": yanit, "model": "gpt-4o", "backend": "openai"}
            return {"success": False, "error": f"OpenAI HTTP {r.status_code}", "detail": r.text[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _qwen_sor(self, prompt: str) -> Dict:
        if not self.qwen_key:
            return {"success": False, "error": "QWEN_API_KEY .env dosyasinda bulunamadi"}
        headers = {"Authorization": f"Bearer {self.qwen_key}", "Content-Type": "application/json"}
        payload = {
            "model": "qwen3.7-max",
            "messages": [
                {"role": "system", "content": "Sen NEXUS AI'sin."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        try:
            r = self.session.post("https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", json=payload, headers=headers, timeout=60)
            if r.status_code == 200:
                yanit = r.json()["choices"][0]["message"]["content"]
                return {"success": True, "response": yanit, "model": "qwen3.7-max", "backend": "qwen"}
            return {"success": False, "error": f"Qwen HTTP {r.status_code}", "detail": r.text[:200]}
        except Exception as e:
            return {"success": False, "error": str(e)}


class VeriEnjektoru:
    def __init__(self, dosya_yolu: Path = DATASET_PATH):
        self.dosya_yolu = dosya_yolu

    def _yukle(self) -> list:
        if not self.dosya_yolu.exists():
            return []
        try:
            with open(self.dosya_yolu, "r", encoding="utf-8") as f:
                icerik = f.read().strip()
                return json.loads(icerik) if icerik else []
        except (json.JSONDecodeError, Exception):
            return []

    def ekle(self, instruction: str, output: str, category: str = "general") -> Dict:
        veri = self._yukle()
        kayit = {
            "instruction": instruction.strip(),
            "output": output.strip(),
            "category": category.strip(),
            "source": "nexus_cli",
            "timestamp": datetime.now().isoformat(),
        }
        veri.append(kayit)
        with open(self.dosya_yolu, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        return {"success": True, "toplam_kayit": len(veri), "son_eklenen": kayit}

    def listele(self, limit: int = 10) -> Dict:
        veri = self._yukle()
        return {"toplam": len(veri), "kayitlar": veri[-limit:]}


class NexusCLI:
    def __init__(self):
        self.ui = NexusUI()
        self.dogrulayici = OllamaDogrulayici()
        self.enjektor = VeriEnjektoru()

    def tui_menu(self):
        self.ui.banner()
        while True:
            secim = questionary.select(
                "",
                choices=[
                    questionary.Choice(title="  💻 LOCAL MOD", value="local"),
                    questionary.Choice(title="  🌐 CLOUD MOD", value="cloud"),
                    questionary.Choice(title="  📊 DATASET", value="dataset"),
                    questionary.Separator("  ──────────────────────"),
                    questionary.Choice(title="  ❌ CIKIS", value="cikis"),
                ],
                style=QUESTIONARY_STYLE,
                qmark="",
                pointer="▸",
                use_indicator=True,
                instruction=" (↑↓ ok tuslari / mouse ile secin)",
            ).ask()

            if secim is None or secim == "cikis":
                if RICH_OK:
                    self.ui.console.print("\n[info]Gorusuruz.[/info]")
                else:
                    print("\n  Gorusuruz.")
                sys.exit(0)

            if secim == "dataset":
                sonuc = self.enjektor.listele()
                self.ui.tablo_goster(sonuc["kayitlar"], sonuc["toplam"])
                questionary.press_any_key_to_continue(
                    message="\n  Ana menuye donmek icin herhangi bir tusa basin...",
                    style=QUESTIONARY_STYLE,
                ).ask()
                continue

            if secim == "local":
                saglayici = "openai"
                mode_label = "LOCAL MOD"
            else:
                saglayici_secim = questionary.select(
                    "Saglayici secin:",
                    choices=[
                        questionary.Choice(title="  OpenAI GPT-4o", value="openai"),
                        questionary.Choice(title="  Qwen 3.7 Max", value="qwen"),
                    ],
                    style=QUESTIONARY_STYLE,
                    qmark="",
                    pointer="▸",
                ).ask()
                saglayici = saglayici_secim if saglayici_secim else "openai"
                mode_label = "CLOUD MOD"

            prompt = questionary.text(
                "Siber sorunuzu girin:",
                style=QUESTIONARY_STYLE,
                qmark="",
                multiline=False,
            ).ask()

            if not prompt or not prompt.strip():
                continue

            self.ui.banner()
            if secim == "local":
                if not self.dogrulayici.binary_kontrol():
                    self.ui.hata_paneli(" OLLAMA YOK ", "Ollama sistemde bulunamadi.")
                    yukle = questionary.confirm(
                        "Ollama yuklensin mi? (winget ile)",
                        default=True,
                        style=QUESTIONARY_STYLE,
                        qmark="",
                    ).ask()
                    if yukle:
                        if not self.dogrulayici.binary_yukle(self.ui):
                            questionary.press_any_key_to_continue(
                                message="\n  Menuye donmek icin herhangi bir tusa basin...",
                                style=QUESTIONARY_STYLE,
                            ).ask()
                            continue
                    else:
                        self.ui.durum_paneli("Ollama olmadan yerel mod calismaz. Cloud mod deneyin.", "error")
                        questionary.press_any_key_to_continue(
                            message="\n  Menuye donmek icin herhangi bir tusa basin...",
                            style=QUESTIONARY_STYLE,
                        ).ask()
                        continue

                if not self.dogrulayici.servis_kontrol():
                    self.ui.hata_paneli(" KALP ATISI YOK ", "Ollama servisi calismiyor.")
                    baslat = questionary.confirm(
                        "Ollama servisi baslatilsin mi? (ollama serve)",
                        default=True,
                        style=QUESTIONARY_STYLE,
                        qmark="",
                    ).ask()
                    if baslat:
                        if not self.dogrulayici.servis_baslat(self.ui):
                            questionary.press_any_key_to_continue(
                                message="\n  Menuye donmek icin herhangi bir tusa basin...",
                                style=QUESTIONARY_STYLE,
                            ).ask()
                            continue
                    else:
                        continue

                if not self.dogrulayici.model_kontrol():
                    self.ui.durum_paneli(f"Model {LOCAL_MODEL} bulunamadi.", "error")
                    cek = questionary.confirm(
                        f"Model indirilsin mi? (ollama pull {LOCAL_MODEL})",
                        default=True,
                        style=QUESTIONARY_STYLE,
                        qmark="",
                    ).ask()
                    if cek:
                        if not self.dogrulayici.model_yukle(self.ui):
                            questionary.press_any_key_to_continue(
                                message="\n  Menuye donmek icin herhangi bir tusa basin...",
                                style=QUESTIONARY_STYLE,
                            ).ask()
                            continue

                self.ui.durum_paneli(f"Servis: AKTIF | Model: {LOCAL_MODEL} | Durum: HAZIR", "local")
                motor = LocalMotor()
                with self.ui.spinner("Yerel cekirdek isleniyor... [qwen2.5-coder:7b]"):
                    sonuc = motor.sor(prompt)
                kullanilan_backend = "local"

            else:
                motor = BulutMotor()
                with self.ui.spinner("Bulut baglantisi kuruluyor..."):
                    sonuc = motor.sor(prompt, saglayici)
                if not sonuc["success"]:
                    self.ui.durum_paneli(f"Bulut hatasi: {sonuc.get('error', 'Bilinmeyen')}", "error")
                    self.ui.siber_uyari("SIBER AG KOPTU! YEREL CEKIRDEK DEVREYE ALINIYOR...")
                    if not self.dogrulayici.binary_kontrol():
                        yukle = questionary.confirm(
                            "Ollama yuklensin mi? (winget ile)",
                            default=True, style=QUESTIONARY_STYLE, qmark="",
                        ).ask()
                        if yukle:
                            self.dogrulayici.binary_yukle(self.ui)
                        else:
                            continue
                    if not self.dogrulayici.servis_kontrol():
                        self.dogrulayici.servis_baslat(self.ui)
                    if not self.dogrulayici.model_kontrol():
                        cek = questionary.confirm(
                            f"Model indirilsin mi? (ollama pull {LOCAL_MODEL})",
                            default=True, style=QUESTIONARY_STYLE, qmark="",
                        ).ask()
                        if cek:
                            self.dogrulayici.model_yukle(self.ui)
                    if self.dogrulayici.servis_kontrol() and self.dogrulayici.model_kontrol():
                        motor = LocalMotor()
                        with self.ui.spinner("Yerel cekirdege yonleniyor..."):
                            sonuc = motor.sor(prompt)
                        kullanilan_backend = "local_fallback"
                    else:
                        self.ui.hata_paneli(" YEREL CEKIRDEK KULLANILAMIYOR ", "Ollama hazir degil.\n")
                        questionary.press_any_key_to_continue(
                            message="\n  Menuye donmek icin herhangi bir tusa basin...",
                            style=QUESTIONARY_STYLE,
                        ).ask()
                        continue
                else:
                    kullanilan_backend = "cloud"

            if sonuc["success"]:
                yanit = sonuc["response"]
                if kullanilan_backend == "local":
                    etiket, stil = "LOCAL", "local"
                elif kullanilan_backend == "local_fallback":
                    etiket, stil = "FALLBACK", "fallback"
                else:
                    etiket, stil = sonuc.get("backend", "?").upper(), "cloud"
                self.ui.yanit_paneli(etiket, sonuc.get("model", "?"), yanit, stil)

                inject = questionary.confirm(
                    "Bu cevap glitch_dataset.json'a enjekte edilsin mi?",
                    default=False,
                    style=QUESTIONARY_STYLE,
                    qmark="",
                ).ask()

                if inject:
                    category = questionary.select(
                        "Kategori secin:",
                        choices=[
                            questionary.Choice(title="  kali", value="kali"),
                            questionary.Choice(title="  unity", value="unity"),
                            questionary.Choice(title="  csharp", value="csharp"),
                            questionary.Choice(title="  python", value="python"),
                            questionary.Choice(title="  siber", value="siber"),
                            questionary.Choice(title="  general", value="general"),
                        ],
                        style=QUESTIONARY_STYLE,
                        qmark="",
                        pointer="▸",
                    ).ask()
                    if not category:
                        category = "general"
                    enj_sonuc = self.enjektor.ekle(prompt, yanit, category)
                    self.ui.basari_paneli(f"[BASARILI] Siber veri glitch_dataset.json dosyasina muhurlendi! Kategori: [{category}] | Toplam: {enj_sonuc['toplam_kayit']} kayit")
            else:
                self.ui.hata_paneli(" AI YANIT HATASI ", sonuc.get("error", "Bilinmeyen hata"))
                if "detail" in sonuc:
                    print(f"  Detay: {sonuc['detail']}")

            questionary.press_any_key_to_continue(
                message="\n  Ana menuye donmek icin herhangi bir tusa basin...",
                style=QUESTIONARY_STYLE,
            ).ask()

    def calistir(self, mode: str, prompt: str, inject: bool, saglayici: str, sicaklik: float, listele: bool, category: str = "general"):
        if listele:
            sonuc = self.enjektor.listele()
            self.ui.tablo_goster(sonuc["kayitlar"], sonuc["toplam"])
            return

        sonuc = None
        kullanilan_backend = None

        if mode == "local":
            durum = self.dogrulayici.rapor()
            if durum["durum"] == "SERVIS_YOK":
                self.ui.hata_paneli(" KALP ATISI YOK ", "Ollama servisi localhost:11434'te calismiyor.\n\nCozum: Terminalde 'ollama serve' yaz ve tekrar dene.")
                sys.exit(1)
            if durum["durum"] == "MODEL_YOK":
                self.ui.hata_paneli(" MODEL MUHUR BOS ", f"{LOCAL_MODEL} sistemde bulunamadi.\n\nCozum: 'ollama pull {LOCAL_MODEL}' ile modeli cek.")
                sys.exit(1)
            self.ui.durum_paneli(f"Servis: AKTIF | Model: {LOCAL_MODEL} | Durum: HAZIR", "local")
            motor = LocalMotor()
            with self.ui.spinner("Yerel cekirdek isleniyor... [qwen2.5-coder:7b]"):
                sonuc = motor.sor(prompt, sicaklik)
            kullanilan_backend = "local"

        elif mode == "cloud":
            motor = BulutMotor()
            with self.ui.spinner("Bulut baglantisi kuruluyor..."):
                sonuc = motor.sor(prompt, saglayici)
            if not sonuc["success"]:
                self.ui.durum_paneli(f"Bulut hatasi: {sonuc.get('error', 'Bilinmeyen')}", "error")
                self.ui.siber_uyari("SIBER AG KOPTU! YEREL CEKIRDEK DEVREYE ALINIYOR...")
                durum = self.dogrulayici.rapor()
                if durum["durum"] == "HAZIR":
                    motor = LocalMotor()
                    with self.ui.spinner("Yerel cekirdege yonleniyor..."):
                        sonuc = motor.sor(prompt, sicaklik)
                    kullanilan_backend = "local_fallback"
                else:
                    self.ui.hata_paneli(" YEREL CEKIRDEK KULLANILAMIYOR ", "Ollama servisi hazir degil. Lutfen 'ollama serve' ile baslat.\n")
                    sys.exit(1)
            else:
                kullanilan_backend = "cloud"

        else:
            self.ui.hata_paneli(" GECERSIZ MOD ", f"Bilinmeyen mod: {mode}")
            sys.exit(1)

        if sonuc["success"]:
            yanit = sonuc["response"]
            if kullanilan_backend == "local":
                etiket, stil = "LOCAL", "local"
            elif kullanilan_backend == "local_fallback":
                etiket, stil = "FALLBACK", "fallback"
            else:
                etiket, stil = sonuc.get("backend", "?").upper(), "cloud"
            self.ui.yanit_paneli(etiket, sonuc.get("model", "?"), yanit, stil)

            if inject:
                enj_sonuc = self.enjektor.ekle(prompt, yanit, category)
                self.ui.basari_paneli(f"[BASARILI] Siber veri glitch_dataset.json dosyasina muhurlendi! Kategori: [{category}] | Toplam: {enj_sonuc['toplam_kayit']} kayit")
        else:
            self.ui.hata_paneli(" AI YANIT HATASI ", sonuc.get("error", "Bilinmeyen hata"))
            if "detail" in sonuc:
                print(f"  Detay: {sonuc['detail']}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="nexus_cli",
        description="NEXUS CLI - Hibrit Model Yonetim ve Veri Enjeksiyon Sistemi",
        epilog="Ornek: python nexus_cli.py -m local 'Unity C# optimizasyon' -i -c unity | python nexus_cli.py -m cloud --saglayici qwen 'Kali Linux exploit' -i -c kali",
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["local", "cloud"],
        default="local",
        help="local (yerel Qwen 7B) | cloud (OpenAI/Qwen API) [default: local]",
    )
    parser.add_argument(
        "-p", "--prompt",
        type=str,
        default=None,
        help="AI'ya gonderilecek prompt/metin",
    )
    parser.add_argument(
        "-i", "--inject",
        action="store_true",
        help="Yaniti glitch_dataset.json'a instruction-output olarak kaydet",
    )
    parser.add_argument(
        "--saglayici",
        choices=["openai", "qwen"],
        default="openai",
        help="Cloud modunda kullanilacak saglayici [default: openai]",
    )
    parser.add_argument(
        "-t", "--temperature",
        type=float,
        default=0.3,
        help="Model sicakligi 0.0-1.0 [default: 0.3]",
    )
    parser.add_argument(
        "-c", "--category",
        type=str,
        default="general",
        help="Veri kategorisi: unity, kali, csharp, python, siber [default: general]",
    )
    parser.add_argument(
        "-l", "--listele",
        action="store_true",
        help="glitch_dataset.json icindeki son kayitlari goster",
    )

    args = parser.parse_args()

    if not args.listele and not args.prompt:
        if not QUESTIONARY_OK:
            print("❌ questionary kutuphanesi gerekli: pip install questionary")
            sys.exit(1)
        cli = NexusCLI()
        cli.tui_menu()
        return

    cli = NexusCLI()
    cli.ui.banner()
    cli.calistir(
        mode=args.mode,
        prompt=args.prompt,
        inject=args.inject,
        saglayici=args.saglayici,
        sicaklik=args.temperature,
        listele=args.listele,
        category=args.category,
    )


if __name__ == "__main__":
    main()
