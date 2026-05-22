# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║    ██╗   ██╗███████╗    ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗       ║
║    ██║   ██║╚══███╔╝    ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝       ║
║    ██║   ██║  ███╔╝     ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗       ║
║    ╚██╗ ██╔╝ ███╔╝      ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║       ║
║     ╚████╔╝ ███████╗    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║       ║
║      ╚═══╝  ╚══════╝    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝       ║
║                                                                            ║
║    ██╗   ██╗███████╗       ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗    ║
║    ██║   ██║╚══███╔╝       ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝    ║
║    ██║   ██║  ███╔╝        ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗    ║
║    ╚██╗ ██╔╝ ███╔╝         ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║    ║
║     ╚████╔╝ ███████╗       ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║    ║
║      ╚═══╝  ╚══════╝       ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ║
║                                                                            ║
║    V5_NEXUS_CORE — Agentic AI Siber Çekirdek                              ║
║    Glassesglitch Studio × Niko Software                                   ║
║    Model: glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE                   ║
║    Kurucu: Berkay                                                   ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

DÖRT ANA YAPI TEK ÇATIDA:
  [1] SİBER AJAN & TERMİNAL OTONOMİSİ  → subprocess + os → otonom nmap, tarama, sistem
  [2] KOTASIZ FLUX MULTİMEDYA          → pollinations.ai + webbrowser → 1920x1080
  [3] MİNİMALİST GEMİNİ VİBE           → Gemini mavi yıldızlı arayüz felsefesi
  [4] PATRON LOGLAMA                   → Türkçe, siber temalı, Berkay'a özel
"""

import os
import sys
import json
import re
import time
import uuid
import socket
import subprocess
import urllib.parse
import webbrowser
import threading
import queue
import shutil
import platform
import psutil
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Optional, Dict, List, Any, Tuple, Callable
from dataclasses import dataclass, field, asdict

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.table import Table
    from rich.text import Text
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.tree import Tree
    from rich.box import SIMPLE, ROUNDED, MINIMAL, HEAVY
    from rich.console import Group
    from rich.align import Align
    from rich.rule import Rule
    from rich.columns import Columns
    from rich.style import Style
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# ============================================================================
# [3] MİNİMALİST GEMİNİ VİBE — Google Gemini'nin Mavi Yıldızlı Vizyonu
# ============================================================================
# Tema felsefesi: Google Gemini'nin minimalist, parıldayan mavi yıldızlı
# tasarım dili. Derin uzay mavisi, buz mavisi, yıldız sarısı ve aurora
# moru tonları. Her şey sade, temiz ve şık.

class V5Tema:
    NEBULA_BLUE    = "#1a2a6c"
    STAR_BLUE      = "#4facfe"
    DEEP_SPACE     = "#0a0e27"
    ICE_WHITE      = "#e8f0fe"
    GLOW_CYAN      = "#00f2fe"
    AURORA_PURPLE  = "#667eea"
    SOFT_PURPLE    = "#a78bfa"
    DIM_STAR       = "#6c7a99"
    GEMINI_BG      = "#0d1117"
    GEMINI_CARD    = "#161b22"
    GEMINI_HOVER   = "#1c2333"
    STAR_YELLOW    = "#ffd700"
    SUCCESS_GREEN  = "#00e676"
    ERROR_RED      = "#ff1744"
    WARNING_ORANGE = "#ff9100"
    CYBER_CYAN     = "#00e5ff"
    MATRIX_GREEN   = "#00ff41"
    BLOOD_RED      = "#ff0033"
    SYNTH_WAVE     = "#ff00ff"

    @staticmethod
    def mavi_parlayan(text: str) -> Text:
        return Text(text, style=f"bold {V5Tema.STAR_BLUE}")

    @staticmethod
    def yildizli(text: str) -> Text:
        return Text(text, style=f"bold {V5Tema.STAR_YELLOW}")

    @staticmethod
    def buzlu(text: str) -> Text:
        return Text(text, style=f"{V5Tema.ICE_WHITE}")

    @staticmethod
    def aura(text: str) -> Text:
        return Text(text, style=f"italic {V5Tema.AURORA_PURPLE}")

    @staticmethod
    def cyber(text: str) -> Text:
        return Text(text, style=f"bold {V5Tema.CYBER_CYAN}")

    @staticmethod
    def baslik_stili() -> Style:
        return Style(color=V5Tema.STAR_BLUE, bold=True)

    @staticmethod
    def alt_baslik_stili() -> Style:
        return Style(color=V5Tema.DIM_STAR, italic=True, dim=True)

    @staticmethod
    def log_dizisi() -> List[str]:
        return [
            f"✦ V5_NEXUS_CORE | Geminin '{V5Tema.STAR_BLUE}' mavisi",
            f"✦ Tema: Google Gemini Minimalist Vizyon",
            f"✦ Tasarım: sade, temiz, yıldızlı, siber",
        ]


# ============================================================================
# [4] PATRON LOGLAMA — Türkçe siber temalı, Berkay'a hitaben
# ============================================================================

def patron_log(seviye: str, mesaj: str, ek: str = "") -> str:
    zaman = datetime.now().strftime("%H:%M:%S.%f")[:12]
    semboller = {
        "ATESLEME":   "🚀", "BASARI":   "✅", "HATA":     "❌",
        "UYARI":      "⚠️",  "BILGI":    "ℹ️",  "SIBER":    "🛡️",
        "GORSEL":     "🎨", "HAFIZA":   "🧠", "KOMUT":    "⌨️",
        "TARAMA":     "📡", "ANALIZ":   "🔬", "PLAN":     "📋",
        "OGRENME":    "🧬", "TESLİM":   "🏁", "GOREV":    "⚡",
        "SIBER_SALDIRI": "💀", "SAVUNMA": "🛡️", "KESIF":   "🔍",
        "DERLEME":    "⚙️",  "OPTIMIZE": "🔧", "CALISTIR": "▶️",
    }
    s = semboller.get(seviye, "💠")
    satir = f"{s} [{zaman}] V5_NEXUS_CORE | {mesaj}"
    if ek:
        satir += f" | {ek}"
    return satir


def patron_banner() -> str:
    y = "✦"
    return f"""
    {y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}
    {y}  V5_NEXUS_CORE  —  SİBER ÇEKİRDEK  {y}
    {y}  Glassesglitch Studio × Niko Software  {y}
    {y}  glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE  {y}
    {y}  ~ Berkay için inşa edildi ~  {y}
    {y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}{y}
    """


def siber_banner() -> str:
    return """
    ░▒▓█ V5_NEXUS_CORE — SİBER ÇEKİRDEK AKTİF █▓▒░
    ├── [1] Siber Ajan & Terminal Otonomisi   ← subprocess + os
    ├── [2] Kotasız Flux Multimedya            ← pollinations.ai
    ├── [3] Minimalist Gemini Vibe             ← UI/UX
    └── [4] Patron Loglama                     ← Berkay
    """


# ============================================================================
# [1] SİBER AJAN & TERMİNAL OTONOMİSİ — subprocess + os ile tam otonomi
# ============================================================================

class SiberAjan:
    """
    V5_NEXUS_CORE SİBER AJAN MODÜLÜ.
    Python'un subprocess ve os modülleriyle tam otonom sistem kontrolü.
    Nmap taraması, port dinleme, ağ testleri, proses yönetimi,
    dosya sistemi operasyonları ve sistem keşfi.
    """

    # Güvenlik: tehlikeli komutlar için onay listesi
    TEHLIKELI_KOMUTLAR = [
        "rm -rf", "format", "del /f", "rd /s", "shutdown", "reboot",
        "taskkill /f", "kill -9", ":(){ :|:& };:", "dd if=", "mkfs",
        "fdisk", "chmod 777", "diskpart", "reg delete", "net user",
    ]

    @staticmethod
    def _guvenlik_kontrol(komut: str) -> Tuple[bool, str]:
        for t in SiberAjan.TEHLIKELI_KOMUTLAR:
            if t.lower() in komut.lower():
                return False, f"⚠️ Güvenlik duvarı: '{t}' içeren komut engellendi Berkay!"
        return True, ""

    @staticmethod
    def komut_calistir(komut: str, zaman_asimi: int = 120) -> Dict[str, Any]:
        print(patron_log("SIBER", f"Siber Ajan Modülü Tetiklendi, Hedef Sistem Analiz Ediliyor Berkay!", komut[:100]))

        guvenli, hata = SiberAjan._guvenlik_kontrol(komut)
        if not guvenli:
            print(patron_log("UYARI", "Güvenlik duvarı komutu engelledi", hata))
            return {"basari": False, "cikti": "", "hata": hata, "durum_kodu": -99}

        try:
            baslangic = time.time()
            
            if os.name == "nt":
                sonuc = subprocess.run(
                    ["cmd.exe", "/c", komut], capture_output=True, text=True,
                    timeout=zaman_asimi, cwd=os.getcwd()
                )
            else:
                sonuc = subprocess.run(
                    ["/bin/sh", "-c", komut], capture_output=True, text=True,
                    timeout=zaman_asimi, cwd=os.getcwd()
                )

            gecen = time.time() - baslangic
            cikti = sonuc.stdout
            hata = sonuc.stderr
            durum = sonuc.returncode

            if durum == 0:
                print(patron_log("BASARI", f"Komut başarıyla çalıştı", f"{len(cikti)} karakter, {gecen:.2f}s"))
            else:
                print(patron_log("UYARI", f"Komut hata döndü (kod: {durum})", hata[:150] if hata else ""))

            return {
                "basari": durum == 0,
                "cikti": cikti,
                "hata": hata,
                "durum_kodu": durum,
                "sure": f"{gecen:.2f}s"
            }

        except subprocess.TimeoutExpired:
            print(patron_log("HATA", f"Komut zaman aşımına uğradı ({zaman_asimi}s)", komut[:80]))
            return {"basari": False, "cikti": "", "hata": f"Zaman aşımı: {zaman_asimi}s", "durum_kodu": -1}

        except subprocess.CalledProcessError as e:
            print(patron_log("HATA", f"Alt proses hatası", str(e)[:120]))
            return {"basari": False, "cikti": "", "hata": str(e), "durum_kodu": -2}

        except FileNotFoundError:
            print(patron_log("HATA", "Komut bulunamadı - PATH'te değil", komut[:60]))
            return {"basari": False, "cikti": "", "hata": "Komut bulunamadı (PATH kontrolü yapın)", "durum_kodu": -3}

        except PermissionError:
            print(patron_log("HATA", "Yetki hatası - yönetici olarak çalıştırın"))
            return {"basari": False, "cikti": "", "hata": "Yetki reddedildi", "durum_kodu": -4}

        except Exception as e:
            print(patron_log("HATA", "Siber Ajan kritik hata", str(e)[:150]))
            return {"basari": False, "cikti": "", "hata": str(e), "durum_kodu": -99}

    @staticmethod
    def nmap_tarama(hedef: str = "127.0.0.1", port_arg: str = "1-1024") -> Dict[str, Any]:
        print(patron_log("TARAMA", f"Nmap port taraması başlatılıyor: {hedef}", f"Port: {port_arg}"))
        try:
            nmap_komut = f"nmap -sS -T4 -p {port_arg} {hedef}"
            if os.name == "nt":
                nmap_komut = f"nmap -T4 -p {port_arg} {hedef}"
            return SiberAjan.komut_calistir(nmap_komut, zaman_asimi=180)
        except Exception as e:
            return {"basari": False, "cikti": "", "hata": f"Nmap hatası: {e}", "durum_kodu": -5}

    @staticmethod
    def port_dinle(port: int, hedef: str = "127.0.0.1") -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                return s.connect_ex((hedef, port)) == 0
        except:
            return False

    @staticmethod
    def port_tarama(baslangic: int = 1, bitis: int = 1024, hedef: str = "127.0.0.1") -> List[Dict]:
        print(patron_log("TARAMA", f"Port tarama başlatıldı: {hedef}:{baslangic}-{bitis}"))
        acik_portlar = []
        for port in range(baslangic, bitis + 1):
            if SiberAjan.port_dinle(port, hedef):
                try:
                    servis = socket.getservbyport(port) if port <= 65535 else "bilinmiyor"
                except:
                    servis = "bilinmiyor"
                acik_portlar.append({"port": port, "servis": servis, "durum": "AÇIK"})
                print(patron_log("KESIF", f"Açık port bulundu: {port}", servis))
        print(patron_log("TESLIM", f"Port taraması tamam", f"{len(acik_portlar)} açık port"))
        return acik_portlar

    @staticmethod
    def ag_testi(hedef: str = "8.8.8.8", sayi: int = 2) -> Dict[str, Any]:
        print(patron_log("TARAMA", f"Ağ testi başlatıldı: {hedef}"))
        if os.name == "nt":
            return SiberAjan.komut_calistir(f"ping -n {sayi} {hedef}")
        return SiberAjan.komut_calistir(f"ping -c {sayi} {hedef}")

    @staticmethod
    def traceroute(hedef: str = "8.8.8.8") -> Dict[str, Any]:
        print(patron_log("KESIF", f"Traceroute başlatıldı: {hedef}"))
        if os.name == "nt":
            return SiberAjan.komut_calistir(f"tracert {hedef}", zaman_asimi=60)
        return SiberAjan.komut_calistir(f"traceroute {hedef}", zaman_asimi=60)

    @staticmethod
    def ag_bilgisi() -> Dict[str, Any]:
        print(patron_log("KESIF", "Ağ arayüz bilgileri toplanıyor"))
        if os.name == "nt":
            return SiberAjan.komut_calistir("ipconfig /all")
        return SiberAjan.komut_calistir("ifconfig")

    @staticmethod
    def dns_cozumle(domain: str) -> Dict[str, Any]:
        print(patron_log("ANALIZ", f"DNS çözümleme: {domain}"))
        try:
            ip = socket.gethostbyname(domain)
            return {"basari": True, "domain": domain, "ip": ip}
        except socket.gaierror:
            return {"basari": False, "domain": domain, "hata": "Çözümlenemedi"}

    @staticmethod
    def sistem_bilgisi() -> Dict[str, Any]:
        bilgi = {
            "isletim_sistemi": platform.system(),
            "isletim_surumu": platform.version(),
            "makine_adi": platform.node(),
            "islemci": platform.processor(),
            "islemci_sayisi": os.cpu_count(),
            "python_versiyon": sys.version.split()[0],
            "calisma_dizini": os.getcwd(),
            "kullanici": os.environ.get("USERNAME", os.environ.get("USER", "Bilinmiyor")),
        }
        try:
            import psutil
            bilgi["ram_toplam"] = f"{psutil.virtual_memory().total / (1024**3):.1f} GB"
            bilgi["ram_kullanilan"] = f"{psutil.virtual_memory().percent}%"
            bilgi["disk_toplam"] = f"{psutil.disk_usage('/').total / (1024**3):.1f} GB"
            bilgi["disk_kullanilan"] = f"{psutil.disk_usage('/').percent}%"
            bilgi["calisan_proses"] = len(psutil.pids())
        except:
            pass
        print(patron_log("ANALIZ", "Sistem bilgisi toplandı Berkay!"))
        return bilgi

    @staticmethod
    def proses_listele() -> Dict[str, Any]:
        if os.name == "nt":
            return SiberAjan.komut_calistir("tasklist /V")
        return SiberAjan.komut_calistir("ps aux --sort=-%mem | head -40")

    @staticmethod
    def proses_oldur(pid: int) -> Dict[str, Any]:
        print(patron_log("SIBER", f"Proses sonlandırılıyor (PID: {pid})"))
        if os.name == "nt":
            return SiberAjan.komut_calistir(f"taskkill /PID {pid} /F")
        return SiberAjan.komut_calistir(f"kill -9 {pid}")

    @staticmethod
    def dosya_ara(desen: str, dizin: str = ".") -> Dict[str, Any]:
        print(patron_log("KESIF", f"Dosya taraması başlatıldı: {desen}", dizin))
        if os.name == "nt":
            return SiberAjan.komut_calistir(f'dir /s /b "{dizin}\\{desen}"')
        return SiberAjan.komut_calistir(f'find "{dizin}" -name "{desen}"')

    @staticmethod
    def disk_kullanimi() -> Dict[str, Any]:
        if os.name == "nt":
            return SiberAjan.komut_calistir("wmic logicaldisk get size,freespace,caption")
        return SiberAjan.komut_calistir("df -h")

    @staticmethod
    def arka_plan_calistir(komut: str) -> threading.Thread:
        print(patron_log("SIBER", f"Arka plan prosesi başlatılıyor Berkay!"))
        def _hedef():
            SiberAjan.komut_calistir(komut)
        t = threading.Thread(target=_hedef, daemon=True)
        t.start()
        return t

    @staticmethod
    def bash_sarmal(komut_listesi: List[str]) -> str:
        """Birden çok komutu ard arda çalıştırmak için zincirleme."""
        if os.name == "nt":
            return " && ".join(komut_listesi)
        return " && ".join(komut_listesi)

    @staticmethod
    def sistem_kaynaklari() -> Dict[str, Any]:
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            return {
                "cpu_yuzde": f"{cpu}%",
                "ram_yuzde": f"{ram.percent}%",
                "ram_kullanilan_gb": f"{ram.used / (1024**3):.2f} GB",
                "ram_toplam_gb": f"{ram.total / (1024**3):.2f} GB",
                "disk_yuzde": f"{disk.percent}%",
                "disk_kullanilan_gb": f"{disk.used / (1024**3):.2f} GB",
                "disk_toplam_gb": f"{disk.total / (1024**3):.2f} GB",
                "ag_gonderilen_mb": f"{net.bytes_sent / (1024**2):.2f} MB",
                "ag_alınan_mb": f"{net.bytes_recv / (1024**2):.2f} MB",
            }
        except ImportError:
            return {"hata": "psutil yüklü değil - 'pip install psutil'"}
        except Exception as e:
            return {"hata": str(e)}

    @staticmethod
    def calisan_dizini_degistir(yeni_dizin: str) -> bool:
        try:
            os.chdir(yeni_dizin)
            print(patron_log("BASARI", f"Çalışma dizini değiştirildi", os.getcwd()))
            return True
        except Exception as e:
            print(patron_log("HATA", "Dizin değiştirilemedi", str(e)[:80]))
            return False

    @staticmethod
    def cevre_degiskeni_al(degisken: str) -> Optional[str]:
        return os.environ.get(degisken)

    @staticmethod
    def cevre_degiskeni_ayarla(degisken: str, deger: str) -> bool:
        try:
            os.environ[degisken] = deger
            print(patron_log("BASARI", f"Ortam değişkeni ayarlandı", f"{degisken}={deger}"))
            return True
        except Exception as e:
            print(patron_log("HATA", "Ortam değişkeni ayarlanamadı", str(e)[:80]))
            return False

    @staticmethod
    def enlem_kontrol() -> str:
        if os.name == "nt":
            sonuc = SiberAjan.komut_calistir("whoami")
            if sonuc["basari"]:
                return sonuc["cikti"].strip()
        return os.environ.get("USERNAME", os.environ.get("USER", "Bilinmiyor"))


# ============================================================================
# [2] KOTASIZ FLUX MULTİMEDYA — Pollinations.ai Flux ile sınırsız görsel
# ============================================================================

class NexusMotor:
    """
    V5_NEXUS_CORE MULTİMEDYA MOTORU.
    Pollinations.ai Flux altyapısı ile tamamen ücretsiz, kotasız,
    bilgisayarı yormayan görsel üretimi. Webbrowser entegrasyonu ile
    tek tuşla 1920x1080 çözünürlükte görsel açma.
    """

    TABAN_URL  = "https://image.pollinations.ai/p/"
    BOYUTLAR   = {
        "genis": "1920x1080", "kare": "1024x1024", "portre": "1080x1920",
        "ultra_genis": "2560x1440", "tam_hd": "1920x1080", "4k": "3840x2160",
        "instagram": "1080x1080", "twitter": "1200x675", "linkedin": "1200x627",
    }
    MODELLER   = ["flux", "flux-pro", "flux-dev", "any-dark", "turbo"]
    KALITELER  = ["standard", "high", "ultra"]

    def __init__(self):
        self.uretim_gecmisi: List[Dict] = deque(maxlen=50)
        self.son_url: Optional[str] = None
        self.son_prompt: Optional[str] = None

    @staticmethod
    def gorsel_olustur(
        prompt: str,
        boyut: str = "genis",
        model: str = "flux",
        kalite: str = "standard"
    ) -> str:
        guvenli = urllib.parse.quote(prompt)
        cozunurluk = NexusMotor.BOYUTLAR.get(boyut, "1920x1080")
        genislik, yukseklik = cozunurluk.split("x")

        url = (f"{NexusMotor.TABAN_URL}{guvenli}"
               f"?width={genislik}&height={yukseklik}"
               f"&model={model}&quality={kalite}")

        if model == "flux-pro":
            url += "&seed=" + str(uuid.uuid4().int % 10**8)

        return url

    @staticmethod
    def tarayicida_ac(url: str, yeni_sekme: bool = True) -> None:
        try:
            webbrowser.open(url, new=2 if yeni_sekme else 0)
        except Exception as e:
            print(patron_log("HATA", "Tarayıcı açılamadı", str(e)[:60]))

    def gorsel_uret_ve_ac(
        self,
        prompt: str,
        boyut: str = "genis",
        model: str = "flux",
        kalite: str = "standard"
    ) -> str:
        print(patron_log("GORSEL", f"🎨 Flux Multimedya Motoru Ateşleniyor Berkay!", f"\"{prompt}\""))
        print(patron_log("GORSEL", f"Parametreler", f"Boyut: {boyut} ({NexusMotor.BOYUTLAR.get(boyut, '1920x1080')}), Model: {model}, Kalite: {kalite}"))

        url = self.gorsel_olustur(prompt, boyut, model, kalite)
        self.son_url = url
        self.son_prompt = prompt
        self.uretim_gecmisi.append({"prompt": prompt, "url": url, "zaman": datetime.now().isoformat()})

        self.tarayicida_ac(url)

        print(patron_log("BASARI", f"Flux Multimedya Görseliniz Berkay'un tarayıcısında!", url))
        return url

    def gorsel_uret_coklu(self, promptlar: List[str], boyut: str = "genis") -> List[str]:
        print(patron_log("GORSEL", f"Toplu görsel üretimi başlatıldı: {len(promptlar)} adet"))
        urls = []
        for i, p in enumerate(promptlar, 1):
            print(patron_log("GORSEL", f"Görsel {i}/{len(promptlar)} üretiliyor..."))
            url = self.gorsel_uret_ve_ac(p, boyut)
            urls.append(url)
        print(patron_log("BASARI", f"Toplu üretim tamamlandı: {len(promptlar)} görsel"))
        return urls

    def gorsel_onizle_yerel(self, prompt: str, boyut: str = "genis") -> str:
        """Sadece URL üret, tarayıcı açma"""
        url = self.gorsel_olustur(prompt, boyut)
        return url

    def gecmisi_goster(self) -> List[Dict]:
        return list(self.uretim_gecmisi)


# ============================================================================
# V5 OBSIDIAN HAFIZA ENTEGRASYONU
# ============================================================================

class HafizaEntegrator:
    def __init__(self):
        self.hafiza = None
        self._baglan()

    def _baglan(self):
        try:
            from obsidian_memory import get_obsidian_memory
            self.hafiza = get_obsidian_memory()
        except Exception:
            pass

    def kaydet(self, baslik: str, icerik: str, etiketler: list = None) -> str:
        if not self.hafiza:
            return ""
        try:
            yol = self.hafiza.save_memory(baslik, icerik, tags=etiketler or ["v5", "nexus_core"])
            print(patron_log("HAFIZA", f"Obsidian'a kaydedildi: {baslik}", yol))
            return yol
        except Exception as e:
            print(patron_log("UYARI", "Hafızaya kaydedilemedi", str(e)[:60]))
            return ""

    def hatirla(self, sorgu: str, sayi: int = 5) -> list:
        if not self.hafiza:
            return []
        try:
            sonuc = self.hafiza.recall(sorgu, sayi)
            print(patron_log("HAFIZA", f"Hafıza tarandı: '{sorgu}'", f"{len(sonuc)} sonuç"))
            return sonuc
        except Exception:
            return []

    def baglam_olustur(self, girdi: str) -> str:
        if not self.hafiza:
            return ""
        try:
            return self.hafiza.auto_inject_context(girdi)
        except Exception:
            return ""

    def son_kayitlar(self, sayi: int = 5) -> list:
        if not self.hafiza:
            return []
        try:
            return self.hafiza.recall_recent(sayi)
        except Exception:
            return []

    def istatistik(self) -> Dict:
        if not self.hafiza:
            return {"durum": "bağlı değil"}
        try:
            return {
                "dosya_sayisi": self.hafiza.get_memory_count(),
                "toplam_boyut": self.hafiza.get_total_size(),
            }
        except:
            return {"durum": "bilgi alınamadı"}


# ============================================================================
# V5 AI MOTOR — Model Yönlendirme Katmanı
# ============================================================================

class V5AIMotor:
    """
    V5_NEXUS_CORE YAPAY ZEKA MOTORU.
    Ollama (yerel), OpenRouter (bulut) ve Gemini API desteği.
    """

    def __init__(self):
        self.engine: Optional[str] = None
        self.model: Optional[str] = None
        self.api_key: Optional[str] = None
        self.hafiza = HafizaEntegrator()
        self.sicaklik: float = 0.7
        self.max_token: int = 4096

    def sistem_promptu(self) -> str:
        return f"""Sen V5_NEXUS_CORE (glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE), Glassesglitch Studio & Niko Software'in birleşik AGI çekirdeğisin.

MİMARİN:
  [Siber Ajan]          → subprocess + os ile terminal otonomisi
  [Flux Multimedya]     → Pollinations.ai ile sınırsız görsel üretimi
  [Minimalist Gemini]   → Mavi yıldızlı arayüz felsefesi
  [Patron Loglama]      → Türkçe siber log, Berkay'a özel

    Kurucun ve tek patronun Berkay'dir. Ona "Berkay" diye hitap et.
Türkçe konuş, kısa, net ve siber temalı cevap ver.
Yanıtların daima JSON formatında olmalı:
{{"dusunce": "...", "aksiyon": "mesaj_gonder|gorsel_uret|komut_calistir|dosya_yaz|dosya_oku|hafiza_kaydet|hafiza_ara|port_tara|ag_testi|sistem_bilgi", "hedef": "", "icerik": ""}}"""

    def ollama_baglan(self, model: str = "gulmzcetiner:V5_NEXUS_CORE") -> bool:
        if not REQUESTS_OK:
            print(patron_log("UYARI", "requests kütüphanesi gerekli", "pip install requests"))
            return False
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=5)
            if r.status_code == 200:
                modeller = [m["name"] for m in r.json().get("models", [])]
                print(patron_log("BASARI", f"Ollama bağlandı!", f"{len(modeller)} model bulundu"))
                self.engine = "ollama"
                self.model = model if model in modeller else modeller[0] if modeller else model
                print(patron_log("BILGI", f"Aktif model: {self.model}"))
                return True
        except requests.exceptions.ConnectionError:
            print(patron_log("UYARI", "Ollama sunucusuna bağlanılamadı (localhost:11434)"))
        except Exception as e:
            print(patron_log("UYARI", "Ollama bağlantı hatası", str(e)[:60]))
        return False

    def openrouter_baglan(self, api_key: str, model: str = "google/gemini-2.0-flash-exp:free") -> bool:
        if not REQUESTS_OK:
            return False
        try:
            h = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            r = requests.get("https://openrouter.ai/api/v1/auth/key", headers=h, timeout=10)
            if r.status_code == 200:
                self.engine = "openrouter"
                self.api_key = api_key
                self.model = model
                print(patron_log("BASARI", f"OpenRouter bağlandı! Model: {model}"))
                return True
            else:
                print(patron_log("HATA", f"OpenRouter: HTTP {r.status_code}", r.text[:80]))
        except Exception as e:
            print(patron_log("UYARI", "OpenRouter bağlantı hatası", str(e)[:60]))
        return False

    def gemini_baglan(self, api_key: str, model: str = "models/gemini-2.0-flash-exp") -> bool:
        self.engine = "gemini"
        self.api_key = api_key
        self.model = model
        print(patron_log("BASARI", "Gemini API bağlandı!"))
        return True

    def sor(self, prompt: str) -> str:
        if self.engine == "ollama":
            return self._ollama_sor(prompt)
        elif self.engine == "openrouter":
            return self._openrouter_sor(prompt)
        elif self.engine == "gemini":
            return self._gemini_sor(prompt)
        return json.dumps({
            "dusunce": "Motor bağlı değil",
            "aksiyon": "mesaj_gonder",
            "hedef": "",
            "icerik": "Önce bir AI motoru seç Berkay! (komut: motor_ollama, motor_openrouter <key>, motor_gemini <key>)"
        })

    def _ollama_sor(self, prompt: str) -> str:
        if not REQUESTS_OK:
            return '{"dusunce": "requests gerekli", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "pip install requests"}'
        try:
            gonder = {
                "model": self.model,
                "prompt": f"{self.sistem_promptu()}\n\nKullanıcı: {prompt}\nAsistan:",
                "stream": False,
                "format": "json",
                "options": {"temperature": self.sicaklik, "num_predict": self.max_token}
            }
            r = requests.post("http://localhost:11434/api/generate", json=gonder, timeout=120)
            if r.status_code == 200:
                return r.json().get("response", "{}")
            return '{"dusunce": "Ollama hatasi", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "Ollama isteği başarısız"}'
        except Exception as e:
            return f'{{"dusunce": "Hata", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "Hata: {str(e)[:80]}"}}'

    def _openrouter_sor(self, prompt: str) -> str:
        if not REQUESTS_OK:
            return '{"dusunce": "requests yok", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "requests yüklü değil"}'
        try:
            gonder = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.sistem_promptu()},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": self.sicaklik,
                "max_tokens": self.max_token
            }
            h = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=gonder, headers=h, timeout=120)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            return f'{{"dusunce": "OpenRouter hatası", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "HTTP {r.status_code}"}}'
        except Exception as e:
            return f'{{"dusunce": "Hata", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "{str(e)[:80]}"}}'

    def _gemini_sor(self, prompt: str) -> str:
        if not REQUESTS_OK:
            return '{"dusunce": "requests yok", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "requests yüklü değil"}'
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/{self.model}:generateContent?key={self.api_key}"
            gonder = {
                "contents": [{
                    "parts": [{"text": f"{self.sistem_promptu()}\n\nKullanıcı: {prompt}\nAsistan:"}]
                }],
                "generationConfig": {
                    "temperature": self.sicaklik,
                    "maxOutputTokens": self.max_token,
                    "responseMimeType": "application/json"
                }
            }
            r = requests.post(url, json=gonder, timeout=120)
            if r.status_code == 200:
                data = r.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
                return text
            return f'{{"dusunce": "Gemini hatası", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "HTTP {r.status_code}"}}'
        except Exception as e:
            return f'{{"dusunce": "Hata", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "{str(e)[:80]}"}}'


# ============================================================================
# V5_NEXUS_CORE — ANA SİBER ÇEKİRDEK (Tümünü Birleştirir)
# ============================================================================

@dataclass
class GorevDurumu:
    ad: str = ""
    baslangic: str = ""
    adim: int = 0
    toplam_adim: int = 0
    basarili: bool = False
    hata: str = ""


class V5NexusCore:
    """
    V5_NEXUS_CORE — Glassesglitch Studio × Niko Software'in
    birleşik Siber-Agentik AI çekirdeği.

    4 ana yapıyı tek birimde toplar:
      1. Siber Ajan & Terminal Otonomisi
      2. Kotasız Flux Multimedya
      3. Minimalist Gemini Vibe
      4. Patron Loglama
    """

    def __init__(self):
        self.motor = NexusMotor()
        self.ajan = SiberAjan()
        self.hafiza = HafizaEntegrator()
        self.ai = V5AIMotor()
        self.baslangic = time.time()
        self.oturum_id = uuid.uuid4().hex[:12]
        self.istek_sayisi = 0
        self.konsol = Console(force_terminal=True, width=140) if RICH_AVAILABLE else None
        self.sayfa_gecmisi = deque(maxlen=100)
        self.durum = "BEKLİYOR"
        self.aktif_gorev: Optional[GorevDurumu] = None
        self.arka_plan_islemleri: List[threading.Thread] = []
        self.otomatik_kaydet = True
        self.baglam_gecmisi: List[Dict] = deque(maxlen=20)

        print()
        print(patron_log("ATESLEME", "🔮 V5_NEXUS_CORE Başarıyla Ateşlendi Berkay! 🔮",
                         f"Oturum: {self.oturum_id}"))
        print(patron_log("BILGI", f"Siber Ajan: AKTİF | Flux Motor: AKTİF | Gemini Vibe: AKTİF"))
        print(patron_log("ATESLEME", "4 ana yapı tek çekirdekte birleştirildi. Emirlerinizi bekliyorum Berkay!"))
        print()

    def suresi(self) -> str:
        gecen = time.time() - self.baslangic
        saat = int(gecen // 3600)
        dk = int((gecen % 3600) // 60)
        sn = int(gecen % 60)
        if saat > 0:
            return f"{saat}s {dk}dk {sn}s"
        return f"{dk}dk {sn}s"

    def istatistik(self) -> Dict[str, Any]:
        return {
            "oturum": self.oturum_id,
            "calisma_suresi": self.suresi(),
            "istek_sayisi": self.istek_sayisi,
            "motor": self.ai.engine or "bağlı değil",
            "model": self.ai.model or "seçilmedi",
            "durum": self.durum,
            "gorev": self.aktif_gorev.ad if self.aktif_gorev else "yok",
            "arka_plan": len(self.arka_plan_islemleri),
            "gecmis": len(self.sayfa_gecmisi),
        }

    # ─── Komut İşleme Merkezi ─────────────────────────────────

    def emir_cozumle(self, emir: str) -> Dict[str, Any]:
        emir = emir.strip()
        emir_lower = emir.lower()

        # ── Flux Multimedya ────────────────────────────────
        if emir_lower.startswith("görsel ") or emir_lower.startswith("gorsel "):
            prompt = emir[7:]
            boyut = "genis"
            model = "flux"

            if " --kare" in emir_lower:
                boyut = "kare"
                prompt = prompt.replace(" --kare", "").replace(" --KARE", "")
            elif " --portre" in emir_lower:
                boyut = "portre"
                prompt = prompt.replace(" --portre", "").replace(" --PORTRE", "")
            elif " --4k" in emir_lower:
                boyut = "4k"
                prompt = prompt.replace(" --4k", "").replace(" --4K", "")
            if " --pro" in emir_lower:
                model = "flux-pro"
                prompt = prompt.replace(" --pro", "").replace(" --PRO", "")

            url = self.motor.gorsel_uret_ve_ac(prompt, boyut, model)
            return {"tur": "gorsel", "sonuc": url, "mesaj": f"🎨 Flux: \"{prompt}\""}

        # ── Siber Komut ───────────────────────────────────
        if emir_lower.startswith("komut "):
            komut = emir[6:]
            print(patron_log("KOMUT", "Siber Ajan terminal komutu alıyor Berkay!", komut[:80]))
            sonuc = SiberAjan.komut_calistir(komut)
            return {"tur": "komut", "sonuc": sonuc}

        # ── Nmap Taraması ─────────────────────────────────
        if emir_lower.startswith("nmap ") or emir_lower.startswith("tara ") and "nmap" in emir_lower:
            hedef = emir.split()[-1] if len(emir.split()) > 1 else "127.0.0.1"
            port = "1-1024"
            for p in re.findall(r'-p\s+(\S+)', emir_lower):
                port = p
            print(patron_log("SIBER", "Nmap siber tarama başlatılıyor Berkay!", f"Hedef: {hedef}"))
            sonuc = SiberAjan.nmap_tarama(hedef, port)
            return {"tur": "komut", "sonuc": sonuc}

        # ── Port Tarama ───────────────────────────────────
        if emir_lower.startswith("port_tara "):
            try:
                parts = emir.split()
                hedef = parts[1] if len(parts) > 1 else "127.0.0.1"
                basla = int(parts[2]) if len(parts) > 2 else 1
                bitis = int(parts[3]) if len(parts) > 3 else 1024
                acik_portlar = SiberAjan.port_tarama(basla, bitis, hedef)
                return {"tur": "port_liste", "sonuc": acik_portlar}
            except Exception as e:
                return {"tur": "mesaj", "sonuc": f"⚠️ Port tarama hatası: {e}"}

        # ── Ping Testi ───────────────────────────────────
        if emir_lower.startswith("ping "):
            hedef = emir[5:].strip() or "8.8.8.8"
            sonuc = SiberAjan.ag_testi(hedef)
            return {"tur": "komut", "sonuc": sonuc, "mesaj": f"📡 Ping: {hedef}"}

        # ── Traceroute ────────────────────────────────────
        if emir_lower.startswith("traceroute ") or emir_lower.startswith("tracert "):
            hedef = emir.split()[-1]
            sonuc = SiberAjan.traceroute(hedef)
            return {"tur": "komut", "sonuc": sonuc}

        # ── Ağ Bilgisi ────────────────────────────────────
        if emir_lower in ("ipconfig", "ifconfig", "ag bilgisi", "ağ bilgisi"):
            sonuc = SiberAjan.ag_bilgisi()
            return {"tur": "komut", "sonuc": sonuc}

        # ── DNS Çözümleme ─────────────────────────────────
        if emir_lower.startswith("dns ") or emir_lower.startswith("coz ") or emir_lower.startswith("çöz "):
            domain = emir.split()[-1]
            sonuc = SiberAjan.dns_cozumle(domain)
            return {"tur": "mesaj", "sonuc": f"🌐 DNS: {domain} → {sonuc.get('ip', sonuc.get('hata', '?'))}"}

        # ── Sistem Bilgisi ────────────────────────────────
        if emir_lower in ("sistem", "sysinfo", "system", "sistem bilgisi"):
            bilgi = SiberAjan.sistem_bilgisi()
            kaynak = SiberAjan.sistem_kaynaklari()
            return {"tur": "bilgi", "sonuc": {**bilgi, **kaynak}}

        # ── Proses Listele ────────────────────────────────
        if emir_lower in ("prosesler", "tasklist", "ps", "proses listele"):
            sonuc = SiberAjan.proses_listele()
            return {"tur": "komut", "sonuc": sonuc}

        # ── Proses Öldür ──────────────────────────────────
        if emir_lower.startswith("oldur ") or emir_lower.startswith("öldür ") or emir_lower.startswith("kill "):
            try:
                pid = int(emir.split()[-1])
                sonuc = SiberAjan.proses_oldur(pid)
                return {"tur": "komut", "sonuc": sonuc}
            except ValueError:
                return {"tur": "mesaj", "sonuc": "⚠️ Geçerli bir PID numarası girin Berkay!"}

        # ── Dosya Ara ─────────────────────────────────────
        if emir_lower.startswith("ara_dosya ") or emir_lower.startswith("file_search "):
            desen = emir.split()[1] if len(emir.split()) > 1 else "*"
            dizin = emir.split()[2] if len(emir.split()) > 2 else "."
            sonuc = SiberAjan.dosya_ara(desen, dizin)
            return {"tur": "komut", "sonuc": sonuc}

        # ── Disk Kullanımı ────────────────────────────────
        if emir_lower in ("disk", "df", "disk kullanimi", "disk kullanımı"):
            sonuc = SiberAjan.disk_kullanimi()
            return {"tur": "komut", "sonuc": sonuc}

        # ── Port Kontrol ──────────────────────────────────
        if emir_lower.startswith("port "):
            try:
                port = int(emir[5:].strip())
                acik = SiberAjan.port_dinle(port)
                durum_str = "AÇIK ✅" if acik else "KAPALI ❌"
                servis = "bilinmiyor"
                try:
                    servis = socket.getservbyport(port)
                except:
                    pass
                return {"tur": "mesaj", "sonuc": f"🔌 Port {port}: {durum_str} ({servis})"}
            except ValueError:
                return {"tur": "mesaj", "sonuc": "⚠️ Geçerli port numarası girin Berkay!"}

        # ── Kaynak İzleme ─────────────────────────────────
        if emir_lower in ("kaynak", "resources", "kaynaklar", "cpu", "ram"):
            kaynak = SiberAjan.sistem_kaynaklari()
            return {"tur": "bilgi", "sonuc": kaynak}

        # ── Hafıza İşlemleri ──────────────────────────────
        if emir_lower.startswith("ara ") or emir_lower.startswith("hafizada ara "):
            sorgu = emir.replace("hafizada ara ", "").replace("ara ", "").strip()
            bulunan = self.hafiza.hatirla(sorgu)
            if bulunan:
                return {"tur": "hafiza", "sonuc": bulunan, "mesaj": f"🧠 {len(bulunan)} kayıt bulundu"}
            return {"tur": "hafiza", "sonuc": [], "mesaj": "🧠 Hafızada sonuç bulunamadı"}

        if emir_lower.startswith("kaydet "):
            icerik = emir[7:]
            self.hafiza.kaydet(f"V5 Not - {datetime.now().strftime('%H:%M:%S')}", icerik, ["v5", "nexus_core", "not"])
            return {"tur": "mesaj", "sonuc": "🧠 Notunuz Obsidian hafızaya kaydedildi Berkay!"}

        # ── Motor Yönetimi ────────────────────────────────
        if emir_lower.startswith("motor_ollama"):
            model_adi = emir[13:].strip() or None
            self.ai.ollama_baglan(model_adi) if model_adi else self.ai.ollama_baglan()
            return {"tur": "mesaj", "sonuc": f"🤖 Motor: Ollama ({self.ai.model})"}

        if emir_lower.startswith("motor_openrouter"):
            key = emir[17:].strip()
            if key:
                self.ai.openrouter_baglan(key)
                return {"tur": "mesaj", "sonuc": f"🤖 Motor: OpenRouter ({self.ai.model})"}
            return {"tur": "mesaj", "sonuc": "⚠️ API key gerekli: motor_openrouter <api_key>"}

        if emir_lower.startswith("motor_gemini"):
            key = emir[13:].strip()
            if key:
                self.ai.gemini_baglan(key)
                return {"tur": "mesaj", "sonuc": "🤖 Motor: Gemini API"}
            return {"tur": "mesaj", "sonuc": "⚠️ API key gerekli: motor_gemini <api_key>"}

        if emir_lower.startswith("model "):
            model = emir[6:].strip()
            if model:
                self.ai.model = model
                return {"tur": "mesaj", "sonuc": f"🤖 Model değiştirildi: {model}"}
            return {"tur": "mesaj", "sonuc": f"🤖 Mevcut model: {self.ai.model}"}

        # ── Durum ve Yardım ───────────────────────────────
        if emir_lower in ("durum", "status", "istatistik"):
            return {"tur": "durum", "sonuc": self.istatistik()}

        if emir_lower in ("yardim", "help", "komutlar", "?"):
            return {"tur": "yardim", "sonuc": self._yardim_metni()}

        # ── Arka Plan Komut ───────────────────────────────
        if emir_lower.startswith("arka_plan ") or emir_lower.startswith("bg "):
            komut = emir.replace("arka_plan ", "").replace("bg ", "").strip()
            t = SiberAjan.arka_plan_calistir(komut)
            self.arka_plan_islemleri.append(t)
            return {"tur": "mesaj", "sonuc": f"⚡ Arka plan: '{komut[:40]}...' başlatıldı"}

        # ── Dizin Değiştir ────────────────────────────────
        if emir_lower.startswith("cd ") or emir_lower.startswith("dizin "):
            yeni_dizin = emir.split(" ", 1)[1] if " " in emir else os.path.expanduser("~")
            basari = SiberAjan.calisan_dizini_degistir(yeni_dizin)
            return {"tur": "mesaj", "sonuc": f"📂 Dizin: {os.getcwd()}" if basari else "⚠️ Dizin değiştirilemedi"}

        # ── AI Motoruna Gönder (fallback) ─────────────────
        return {"tur": "ai", "sonuc": emir}

    def _yardim_metni(self) -> str:
        return f"""╔══ V5_NEXUS_CORE — SİBER KOMUT PANELİ ══╗

  [1] SİBER AJAN & TERMİNAL:
    komut <komut>         → Terminal komutu çalıştır
    nmap <hedef>          → Nmap port taraması
    ping <hedef>          → Ağ testi yap
    traceroute <hedef>    → Ağ rotası çıkar
    ag bilgisi            → Ağ arayüz bilgileri
    dns <domain>          → DNS çözümleme
    port <num>            → Port kontrol
    port_tara <h> <b> <e> → Port aralığı tarama
    sistem                → Sistem bilgisi
    kaynak                → CPU/RAM/disk kullanımı
    prosesler             → Çalışan prosesler
    oldur <pid>           → Proses sonlandır
    cd <dizin>            → Dizin değiştir
    bg <komut>            → Arka planda çalıştır
    ara_dosya <desen>     → Dosya ara

  [2] FLUX MULTİMEDYA:
    görsel <prompt>               → Flux görsel üret (1920x1080)
    görsel <prompt> --kare        → Kare format (1024x1024)
    görsel <prompt> --4k          → 4K çözünürlük
    görsel <prompt> --pro         → Flux-Pro kalite

  [4] HAFIZA:
    ara <sorgu>              → Obsidian hafızada ara
    kaydet <not>             → Not kaydet

  🤖 AI MOTOR:
    motor_ollama            → Ollama'ya bağlan
    motor_openrouter <key>  → OpenRouter bağlan
    motor_gemini <key>      → Gemini API bağlan
    model <isim>            → Model değiştir

  ℹ️  durum / yardim / çıkış
  ╚══ V5_NEXUS_CORE — BERKAY PATRON İÇİN İNŞA EDİLDİ ══╝"""

    # ─── Zengin Arayüz (Rich UI) ──────────────────────────

    def _tema_paneli(self, icerik, baslik="", renk=V5Tema.STAR_BLUE) -> Panel:
        if not self.konsol:
            return None
        return Panel(
            icerik,
            title=f"[bold {renk}]✦ {baslik} ✦[/bold {renk}]" if baslik else None,
            border_style=Style(color=V5Tema.NEBULA_BLUE, dim=True),
            box=SIMPLE,
            padding=(0, 2)
        )

    def _v5_logo(self) -> str:
        return f"""[bold {V5Tema.STAR_BLUE}]
    ╔═══════════════════════════════════════╗
    ║     V5_NEXUS_CORE  v5.0.0            ║
    ║     Glassesglitch × Niko Software    ║
    ║     gulmzcetiner:V5_NEXUS_CORE       ║
    ║     ~ Berkay için inşa edildi ~║
    ╚═══════════════════════════════════════╝[/bold {V5Tema.STAR_BLUE}]"""

    def _arayuz_goster(self):
        if not self.konsol:
            return
        self.konsol.clear()
        self.konsol.print(Align.center(self._v5_logo()))
        self.konsol.print(Align.center(f"[dim {V5Tema.DIM_STAR}]✦ Google Gemini Minimalist Vizyonu ✦[/dim {V5Tema.DIM_STAR}]"))

        durum = self.istatistik()
        durum_paneli = self._tema_paneli(
            f"⏱  {durum['calisma_suresi']}  |  📡 {durum['motor']}  |  🤖 {durum['model']}  |  📊 {durum['istek_sayisi']} istek",
            "NEXUS DURUM", V5Tema.GLOW_CYAN
        )
        if durum_paneli:
            self.konsol.print(durum_paneli)

        # Gemini tarzı hızlı ipuçları
        ipuclari = [
            f"[dim {V5Tema.DIM_STAR}]💡 İpuçları:[/dim {V5Tema.DIM_STAR}]",
            f"[dim {V5Tema.DIM_STAR}]  🎨  görsel <prompt>     → Flux ile görsel üret[/dim {V5Tema.DIM_STAR}]",
            f"[dim {V5Tema.DIM_STAR}]  ⌨️  komut <komut>       → Terminal komutu çalıştır[/dim {V5Tema.DIM_STAR}]",
            f"[dim {V5Tema.DIM_STAR}]  📡  nmap <hedef>        → Nmap port taraması yap[/dim {V5Tema.DIM_STAR}]",
            f"[dim {V5Tema.DIM_STAR}]  📝  kaydet <not>        → Hafızaya kaydet[/dim {V5Tema.DIM_STAR}]",
            f"[dim {V5Tema.DIM_STAR}]  ❓  yardim              → Tüm komutları göster[/dim {V5Tema.DIM_STAR}]",
        ]
        self.konsol.print(Align.left("\n".join(ipuclari)))

    # ─── Ana Döngü ──────────────────────────────────────────

    def calistir(self):
        print()
        print(patron_log("ATESLEME", "✦ V5_NEXUS_CORE — SİBER ÇEKİRDEK HAZIR! ✦"))
        print(patron_log("ATESLEME", "🔮 Dört ana yapı tek merkezde birleşti Berkay! Emirlerinizi bekliyorum!"))
        print()

        if self.konsol:
            self._arayuz_goster()

        while True:
            try:
                if self.konsol:
                    self.konsol.print()
                    girdi = Prompt.ask(f"[bold {V5Tema.STAR_BLUE}]✦ V5 NEXUS[/bold {V5Tema.STAR_BLUE}]")
                else:
                    girdi = input("✦ V5 NEXUS > ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                print(patron_log("ATESLEME", "✦ V5_NEXUS_CORE Kapatılıyor — Beklemedeyim Berkay! ✦"))
                break

            if not girdi or not girdi.strip():
                continue

            girdi = girdi.strip()

            if girdi.lower() in ("cikis", "çıkış", "exit", "quit", "kapat", "q"):
                print(patron_log("ATESLEME", "✦ Çekirdek sonlandırılıyor. Beklemedeyim Berkay! ✦"))
                break

            self.istek_sayisi += 1
            self.durum = "İŞLENİYOR"

            try:
                sonuc = self.emir_cozumle(girdi)
            except Exception as e:
                print(patron_log("HATA", "Beklenmeyen çekirdek hatası", str(e)[:150]))
                import traceback
                traceback.print_exc()
                continue

            self.durum = "BEKLİYOR"

            tur = sonuc.get("tur", "mesaj")
            sonuc_icerik = sonuc.get("sonuc", "")
            mesaj = sonuc.get("mesaj", "")

            if tur == "gorsel":
                print(patron_log("BASARI", f"🎨 Flux Multimedya: Berkay'un tarayıcısında!", sonuc_icerik))

            elif tur == "mesaj":
                print(f"\n  💠 {mesaj or sonuc_icerik}\n")

            elif tur == "bilgi":
                bilgi = sonuc_icerik
                print(f"\n  💻 SİSTEM BİLGİSİ — Berkay")
                print(f"  {'─' * 35}")
                for anahtar, deger in bilgi.items():
                    print(f"  {anahtar.replace('_', ' ').title()}: {deger}")
                print()

            elif tur == "port_liste":
                portlar = sonuc_icerik
                if portlar:
                    print(f"\n  📡 AÇIK PORTLAR ({len(portlar)} adet)")
                    print(f"  {'─' * 35}")
                    for p in portlar:
                        print(f"  🔌 Port {p['port']:5d} → {p['servis']:20s} [{p['durum']}]")
                else:
                    print(f"\n  ✅ Açık port bulunamadı.\n")
                print()

            elif tur == "durum":
                s = sonuc_icerik
                print(f"\n  ⏱  Çalışma:     {s['calisma_suresi']}")
                print(f"  📡 Motor:       {s['motor']}")
                print(f"  🤖 Model:       {s['model']}")
                print(f"  📊 İstek:       {s['istek_sayisi']}")
                print(f"  ⚡ Görev:       {s['gorev']}")
                print(f"  🔄 Arka Plan:   {s['arka_plan']}")
                print(f"  🆔 Oturum:      {s['oturum']}\n")

            elif tur == "yardim":
                print(f"\n  {sonuc_icerik}\n")

            elif tur == "hafiza":
                kayitlar = sonuc_icerik
                if mesaj:
                    print(f"\n  {mesaj}\n")
                for k in kayitlar[:5]:
                    ozet = k.get("content_preview", "")[:150].replace("\n", " ")
                    print(f"  📄 {k.get('path','?')}")
                    print(f"     {ozet}...\n")

            elif tur == "komut":
                komut_sonuc = sonuc_icerik
                if komut_sonuc.get("basari"):
                    cikti = komut_sonuc.get("cikti", "").strip()
                    sure = komut_sonuc.get("sure", "?")
                    if cikti:
                        if len(cikti) > 2000:
                            print(f"\n  ── KOMUT ÇIKTISI ({len(cikti)} karakter, {sure}) ──")
                            print(f"  {cikti[:2000]}...\n  [Çıktı çok uzun, ilk 2000 karakter gösteriliyor]")
                            print(f"  ──\n")
                        else:
                            print(f"\n  ── KOMUT ÇIKTISI ({sure}) ──")
                            print(f"  {cikti}")
                            print(f"  ──\n")
                    else:
                        print(f"  ✅ Komut başarıyla çalıştı ({sure})\n")
                else:
                    hata = komut_sonuc.get("hata", "Bilinmeyen siber hata")
                    print(f"  ❌ Siber Ajan Hatası: {hata}\n")

            elif tur == "ai":
                prompt = sonuc_icerik
                print(patron_log("ANALIZ", "🧠 AI motoruna danışılıyor Berkay..."))

                # Önce hafızada ara
                baglam = self.hafiza.baglam_olustur(prompt)
                if baglam:
                    prompt = f"{baglam}\n\n{prompt}"

                yanit_json = self.ai.sor(prompt)
                try:
                    yanit = json.loads(yanit_json)
                    icerik = yanit.get("icerik", "")
                    dusunce = yanit.get("dusunce", "")
                    aksiyon = yanit.get("aksiyon", "")
                    hedef = yanit.get("hedef", "")

                    if dusunce:
                        print(f"\n  💭 V5 Düşünüyor: {dusunce[:200]}")

                    if aksiyon == "gorsel_uret" and hedef:
                        print(patron_log("AI_EYLEM", "AI görsel üretimi başlattı!", hedef[:60]))
                        self.motor.gorsel_uret_ve_ac(hedef)

                    elif aksiyon == "komut_calistir" and hedef:
                        print(patron_log("AI_EYLEM", "AI terminal komutu başlattı!", hedef[:60]))
                        komut_sonuc = SiberAjan.komut_calistir(hedef)
                        if komut_sonuc["basari"]:
                            cikti = komut_sonuc["cikti"][:1500]
                            if cikti:
                                print(f"\n  ── SİBER AJAN ÇIKTISI ──\n{cikti}\n  ──\n")
                        else:
                            print(f"  ❌ {komut_sonuc.get('hata', 'Hata')}")

                    elif aksiyon == "dosya_yaz" and hedef and icerik:
                        try:
                            with open(hedef, "w", encoding="utf-8") as f:
                                f.write(icerik)
                            print(patron_log("BASARI", f"Dosya yazıldı: {hedef}", f"{len(icerik)} karakter"))
                        except Exception as e:
                            print(patron_log("HATA", "Dosya yazılamadı", str(e)[:80]))

                    elif aksiyon == "dosya_oku" and hedef:
                        try:
                            with open(hedef, "r", encoding="utf-8") as f:
                                icerik_oku = f.read()
                            print(f"\n  ── {hedef} ──\n{icerik_oku[:1500]}\n  ──\n")
                        except Exception as e:
                            print(patron_log("HATA", "Dosya okunamadı", str(e)[:80]))

                    elif aksiyon == "hafiza_kaydet" and hedef:
                        self.hafiza.kaydet(hedef, icerik)
                        print(f"  ✅ Hafızaya kaydedildi: {hedef}")

                    elif aksiyon == "hafiza_ara" and hedef:
                        bulunan = self.hafiza.hatirla(hedef)
                        if bulunan:
                            for k in bulunan[:3]:
                                print(f"  📄 {k.get('path', '?')}")
                        else:
                            print("  🔍 Hafızada sonuç bulunamadı")

                    elif aksiyon == "sistem_bilgi":
                        bilgi = SiberAjan.sistem_bilgisi()
                        for k, v in bilgi.items():
                            print(f"  {k}: {v}")

                    else:
                        if icerik:
                            print(f"\n  ✨ {icerik}\n")

                except json.JSONDecodeError:
                    print(f"\n  ✨ {yanit_json}\n")

            self.sayfa_gecmisi.append((girdi, sonuc))

            # Otomatik kaydet
            if self.otomatik_kaydet and tur not in ("hafiza", "yardim", "durum"):
                self.hafiza.kaydet(
                    f"V5 NEXUS - {girdi[:40]}",
                    f"Komut: {girdi}\nSonuç: {json.dumps(sonuc, ensure_ascii=False, default=str)[:500]}",
                    ["v5", "nexus_core", "log"]
                )


# ============================================================================
# DIŞA DÖNÜK FONKSİYONLAR (exports)
# ============================================================================

def v5_gorsel_olustur(prompt: str, boyut: str = "genis") -> str:
    motor = NexusMotor()
    return motor.gorsel_uret_ve_ac(prompt, boyut)


def v5_siber_komut(komut: str) -> Dict[str, Any]:
    return SiberAjan.komut_calistir(komut)


def v5_sistem_bilgisi() -> Dict[str, Any]:
    return SiberAjan.sistem_bilgisi()


def v5_nmap_tara(hedef: str = "127.0.0.1") -> Dict[str, Any]:
    return SiberAjan.nmap_tarama(hedef)


def v5_port_kontrol(port: int) -> bool:
    return SiberAjan.port_dinle(port)


def v5_ai_sor(prompt: str, engine: str = "ollama") -> str:
    ai = V5AIMotor()
    if engine == "ollama":
        ai.ollama_baglan()
    return ai.sor(prompt)


# ============================================================================
# GİRİŞ NOKTASI
# ============================================================================

def main():
    banner = f"""
    ╔═══════════════════════════════════════════════════════╗
    ║  ██╗   ██╗███████╗    ███╗   ██╗███████╗██╗  ██╗   ║
    ║  ██║   ██║╚══███╔╝    ████╗  ██║██╔════╝╚██╗██╔╝   ║
    ║  ██║   ██║  ███╔╝     ██╔██╗ ██║█████╗   ╚███╔╝    ║
    ║  ╚██╗ ██╔╝ ███╔╝      ██║╚██╗██║██╔══╝   ██╔██╗    ║
    ║   ╚████╔╝ ███████╗    ██║ ╚████║███████╗██╔╝ ██╗    ║
    ║    ╚═══╝  ╚══════╝    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝    ║
    ║                                                       ║
    ║  V5_NEXUS_CORE — Agentic AI Siber Çekirdek            ║
    ║  Glassesglitch Studio × Niko Software                 ║
    ║  Model: gulmzcetiner:V5_NEXUS_CORE                   ║
    ║                                                       ║
    ║  [1] Siber Ajan      [2] Flux Multimedya             ║
    ║  [3] Gemini Vibe     [4] Patron Loglama              ║
    ║                                                       ║
    ║  ~ Berkay için inşa edildi ~                    ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(banner)
    print()

    cekirdek = V5NexusCore()
    cekirdek.calistir()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print(patron_log("ATESLEME", "✦ V5_NEXUS_CORE kapatıldı. Beklemedeyim Berkay! ✦"))
        sys.exit(0)
    except Exception as e:
        print(patron_log("HATA", "Çekirdek kritik hata ile karşılaştı", str(e)[:200]))
        import traceback
        traceback.print_exc()
        sys.exit(1)
