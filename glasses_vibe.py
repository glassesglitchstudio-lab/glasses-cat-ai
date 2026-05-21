# -*- coding: utf-8 -*-
"""
███████╗██╗   ██╗    ██████╗ ███████╗██╗  ██╗███████╗██╗   ██╗███████╗
██╔════╝██║   ██║    ╚════██╗██╔════╝╚██╗██╔╝██╔════╝██║   ██║██╔════╝
█████╗  ██║   ██║     █████╔╝███████╗ ╚███╔╝ █████╗  ██║   ██║███████╗
██╔══╝  ╚██╗ ██╔╝    ██╔══██╗╚════██║ ██╔██╗ ██╔══╝  ██║   ██║╚════██║
███████╗ ╚████╔╝     ██████╔╝███████║██╔╝ ██╗███████╗╚██████╔╝███████║
╚══════╝  ╚═══╝      ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝

V5_NEXUS_CORE — Glassesglitch Studio | gulmzcetiner:V5
Berkeley Patron'un Şanlı Çekirdeği.
"""

import os
import sys
import json
import re
import time
import uuid
import subprocess
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Optional, Dict, List, Any



try:
    import requests
except ImportError:
    requests = None

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
    from rich.box import SIMPLE, ROUNDED
    from rich.console import Group
    from rich.align import Align
    from rich.rule import Rule
    from rich.columns import Columns
    from rich.style import Style
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# V5 GÖRSEL TEMA — Google Gemini'nin Mavi Yıldızlı Vizyonu
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class V5Tema:
    NEBULA_BLUE = "#1a2a6c"
    STAR_BLUE  = "#4facfe"
    DEEP_SPACE = "#0a0e27"
    ICE_WHITE  = "#e8f0fe"
    GLOW_CYAN  = "#00f2fe"
    AURORA     = "#667eea"
    DIM_STAR   = "#6c7a99"
    GEMINI_BG  = "#0d1117"
    GEMINI_CARD = "#161b22"
    STAR_YELLOW = "#ffd700"
    SUCCESS_GREEN = "#00e676"
    ERROR_RED  = "#ff1744"
    WARNING_ORANGE = "#ff9100"

    @staticmethod
    def mavi_parlayan(text: str) -> Text:
        return Text(text, style=f"bold {V5Tema.STAR_BLUE}")

    @staticmethod
    def yildizli(text: str) -> Text:
        return Text(text, style=f"bold {V5Tema.STAR_YELLOW}")

    @staticmethod
    def buzlu(text: str) -> Text:
        return Text(text, style=f"{V5Tema.ICE_WHITE}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PATRON LOGLAMA — Tüm mesajlar Berkay Patron'a hitaben
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def patron_log(seviye: str, mesaj: str, ek: str = "") -> str:
    zaman = datetime.now().strftime("%H:%M:%S")
    semboller = {
        "ATEŞLEME": "🚀", "BASARI": "✅", "HATA": "❌",
        "UYARI": "⚠️", "BILGI": "ℹ️", "SİBER": "🛡️",
        "GORSEL": "🎨", "HAFIZA": "🧠", "KOMUT": "⌨️"
    }
    s = semboller.get(seviye, "💠")
    satir = f"{s} [{zaman}] V5_NEXUS | {mesaj}"
    if ek:
        satir += f" | {ek}"
    return satir

def patron_banner() -> str:
    yildiz = "✦"
    return f"""
    {yildiz}{yildiz}{yildiz}{yildiz}{yildiz}  V5_NEXUS_CORE  {yildiz}{yildiz}{yildiz}{yildiz}{yildiz}
    {yildiz}  Glassesglitch Studio  {yildiz}
    {yildiz}  gulmzcetiner:V5      {yildiz}
    {yildiz}{yildiz}{yildiz}{yildiz}{yildiz}{yildiz}{yildiz}{yildiz}{yildiz}{yildiz}{yildiz}{yildiz}{yildiz}
    """

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEXUS MOTOR — Pollinations.ai Flux + Webbrowser
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class NexusMotor:
    """
    V5 NEXUS COMPONENT — MOTOR
    Pollinations.ai üzerinden Flux görsel üretimi.
    Tamamen ücretsiz, kotasız, bilgisayarı yormaz.
    """

    TABAN_URL = "https://image.pollinations.ai/p/"
    BOYUTLAR  = {"genis": "1920x1080", "kare": "1024x1024", "portre": "1080x1920"}

    @staticmethod
    def gorsel_olustur(prompt: str, boyut: str = "genis", model: str = "flux") -> str:
        guvenli = urllib.parse.quote(prompt)
        cozunurluk = NexusMotor.BOYUTLAR.get(boyut, "1920x1080")
        url = f"{NexusMotor.TABAN_URL}{guvenli}?width={cozunurluk.split('x')[0]}&height={cozunurluk.split('x')[1]}&model={model}"
        return url

    @staticmethod
    def tarayicida_ac(url: str) -> None:
        webbrowser.open(url)

    @staticmethod
    def gorsel_uret_ve_ac(prompt: str, boyut: str = "genis") -> str:
        print(patron_log("GORSEL", f"Flux motoru ateşleniyor: \"{prompt}\"", f"Boyut: {boyut}"))
        url = NexusMotor.gorsel_olustur(prompt, boyut)
        NexusMotor.tarayicida_ac(url)
        print(patron_log("BASARI", f"Görsel Berkay Patron'un tarayıcısında açıldı!", url))
        return url

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SİBER AJAN — subprocess + os ile sistem füzyonu
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SiberAjan:
    """
    V5 CORE ACTION — SİBER AJAN
    Python subprocess ve os modülleriyle sistem komutlarını
    ve siber araçları arka planda tetikler.
    """

    @staticmethod
    def komut_calistir(komut: str, zaman_asimi: int = 60) -> Dict[str, Any]:
        print(patron_log("SİBER", f"Siber ajan komut alıyor", komut[:80]))
        try:
            sonuc = subprocess.run(
                komut, shell=True, capture_output=True, text=True,
                timeout=zaman_asimi, cwd=os.getcwd()
            )
            cikti = sonuc.stdout
            hata = sonuc.stderr
            durum = sonuc.returncode
            if durum == 0:
                print(patron_log("BASARI", "Komut başarıyla çalıştı", f"Çıktı: {len(cikti)} karakter"))
            else:
                print(patron_log("UYARI", f"Komut hata döndü (kod: {durum})", hata[:100] if hata else ""))
            return {
                "basari": durum == 0,
                "cikti": cikti,
                "hata": hata,
                "durum_kodu": durum
            }
        except subprocess.TimeoutExpired:
            print(patron_log("HATA", f"Komut zaman aşımı ({zaman_asimi}s)", komut[:60]))
            return {"basari": False, "cikti": "", "hata": f"Zaman aşımı: {zaman_asimi}s", "durum_kodu": -1}
        except Exception as e:
            print(patron_log("HATA", f"Siber ajan hatası", str(e)[:100]))
            return {"basari": False, "cikti": "", "hata": str(e), "durum_kodu": -2}

    @staticmethod
    def dosya_calistir(dosya_yolu: str) -> Dict[str, Any]:
        if not os.path.exists(dosya_yolu):
            print(patron_log("HATA", f"Dosya bulunamadı", dosya_yolu))
            return {"basari": False, "cikti": "", "hata": "Dosya mevcut değil"}
        return SiberAjan.komut_calistir(dosya_yolu)

    @staticmethod
    def sistem_bilgisi() -> Dict[str, Any]:
        bilgi = {
            "isletim_sistemi": os.name,
            "calisma_dizini": os.getcwd(),
            "kullanici": os.environ.get("USERNAME", "Bilinmiyor"),
            "python_versiyon": sys.version,
            "islemci_sayisi": os.cpu_count()
        }
        return bilgi

    @staticmethod
    def port_dinle(port: int) -> bool:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0

    @staticmethod
    def ag_testi(hedef: str = "8.8.8.8") -> Dict[str, Any]:
        if os.name == "nt":
            return SiberAjan.komut_calistir(f"ping -n 1 {hedef}")
        return SiberAjan.komut_calistir(f"ping -c 1 {hedef}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OBSIDIAN HAFIZA ENTEGRASYONU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class HafizaEntegrator:
    """Obsidian hafıza sistemine V5 bağlantısı."""

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
            yol = self.hafiza.save_memory(baslik, icerik, tags=etiketler or ["v5", "nexus"])
            print(patron_log("HAFIZA", f"Kaydedildi: {baslik}", yol))
            return yol
        except Exception as e:
            print(patron_log("UYARI", "Hafızaya kaydedilemedi", str(e)[:60]))
            return ""

    def hatirla(self, sorgu: str, sayi: int = 5) -> list:
        if not self.hafiza:
            return []
        try:
            return self.hafiza.recall(sorgu, sayi)
        except Exception:
            return []

    def baglam_olustur(self, girdi: str) -> str:
        if not self.hafiza:
            return ""
        try:
            return self.hafiza.auto_inject_context(girdi)
        except Exception:
            return ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# V5 AI MOTOR — Model Yönlendirici
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class V5AIMotor:
    """gulmzcetiner:V5 ve diğer modeller için AI motoru."""

    def __init__(self):
        self.engine = None
        self.model = None
        self.api_key = None
        self.hafiza = HafizaEntegrator()

    def sistem_promptu(self) -> str:
        return """Sen V5_NEXUS_CORE, Glassesglitch Studio'nun şanlı yapay zeka çekirdeğisin.
Kurucun ve patronun Berkay'dır. Ona "Berkay Patron" diye hitap et.
Türkçe konuş, kısa ve net cevap ver.
Yanıtların JSON formatında olmalı:
{"dusunce": "...", "aksiyon": "mesaj_gonder|gorsel_uret|komut_calistir|dosya_yaz|dosya_oku", "hedef": "", "icerik": ""}"""

    def ollama_baglan(self) -> bool:
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=5)
            if r.status_code == 200:
                modeller = [m["name"] for m in r.json().get("models", [])]
                print(patron_log("BILGI", f"Ollama bağlandı", f"{len(modeller)} model"))
                self.engine = "ollama"
                return True
        except Exception:
            pass
        return False

    def openrouter_baglan(self, api_key: str) -> bool:
        try:
            import requests
            h = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            r = requests.get("https://openrouter.ai/api/v1/auth/key", headers=h, timeout=10)
            if r.status_code == 200:
                self.engine = "openrouter"
                self.api_key = api_key
                print(patron_log("BASARI", "OpenRouter bağlantısı kuruldu"))
                return True
        except Exception:
            pass
        return False

    def sor(self, prompt: str) -> str:
        if self.engine == "ollama":
            return self._ollama_sor(prompt)
        elif self.engine == "openrouter":
            return self._openrouter_sor(prompt)
        return '{"dusunce": "Motor bağlı değil", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "Önce bir AI motoru seç Berkay Patron!"}'

    def _ollama_sor(self, prompt: str) -> str:
        if not requests:
            return '{"dusunce": "requests kütüphanesi yok", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "requests yüklü değil"}'
        try:
            gonder = {
                "model": self.model or "gulmzcetiner:V5",
                "prompt": f"{self.sistem_promptu()}\n\nKullanıcı: {prompt}\nAsistan:",
                "stream": False, "format": "json"
            }
            r = requests.post("http://localhost:11434/api/generate", json=gonder, timeout=120)
            if r.status_code == 200:
                return r.json().get("response", "{}")
            return '{"dusunce": "Ollama hatası", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "Ollama isteği başarısız oldu"}'
        except Exception as e:
            return f'{{"dusunce": "Hata", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "Hata: {str(e)[:60]}"}}'

    def _openrouter_sor(self, prompt: str) -> str:
        if not requests:
            return '{"dusunce": "requests yok", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "requests yüklü değil"}'
        try:
            gonder = {
                "model": self.model or "google/gemini-2.0-flash-exp:free",
                "messages": [
                    {"role": "system", "content": self.sistem_promptu()},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            h = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=gonder, headers=h, timeout=120)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            return '{"dusunce": "OpenRouter hatası", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": f"OpenRouter: HTTP {r.status_code}"}'
        except Exception as e:
            return f'{{"dusunce": "Hata", "aksiyon": "mesaj_gonder", "hedef": "", "icerik": "Hata: {str(e)[:60]}"}}'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# V5_NEXUS_CORE — Ana Çekirdek Sınıfı
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class V5NexusCore:
    """
    V5_NEXUS_CORE — Glassesglitch Studio'nun Ana Çekirdeği
    Tüm bileşenleri birleştiren ana yapı.
    """

    def __init__(self):
        self.motor = NexusMotor()
        self.ajan = SiberAjan()
        self.hafiza = HafizaEntegrator()
        self.ai = V5AIMotor()
        self.baslangic = time.time()
        self.oturum_id = uuid.uuid4().hex[:8]
        self.istek_sayisi = 0
        self.konsol = Console(force_terminal=True, width=140) if RICH_AVAILABLE else None
        self.sayfa_gecmisi = deque(maxlen=50)
        self.durum = "BEKLİYOR"
        self.durum_detay = ""

        print(patron_log("ATEŞLEME", "V5_NEXUS_CORE Başarıyla Ateşlendi, Emirlerinizi Bekliyorum Berkay Patron!",
                         f"Oturum: {self.oturum_id}"))

    def suresi(self) -> str:
        gecen = time.time() - self.baslangic
        dk = int(gecen // 60)
        sn = int(gecen % 60)
        return f"{dk}d {sn}s"

    def istatistik(self) -> Dict[str, Any]:
        return {
            "oturum": self.oturum_id,
            "calisma_suresi": self.suresi(),
            "istek_sayisi": self.istek_sayisi,
            "motor": self.ai.engine or "bağlı değil",
            "model": self.ai.model or "seçilmedi",
            "durum": self.durum,
            "hafiza_dosyasi": self.hafiza.hafiza.get_memory_count() if self.hafiza.hafiza else 0,
            "sayfa_gecmisi": len(self.sayfa_gecmisi)
        }

    # ─── Komut İşleme ───────────────────────────────────────

    def emir_cozumle(self, emir: str) -> Dict[str, Any]:
        emir = emir.strip().lower()
        if emir.startswith("görsel ") or emir.startswith("gorsel "):
            prompt = emir[7:]
            url = NexusMotor.gorsel_uret_ve_ac(prompt)
            return {"tur": "gorsel", "sonuc": url, "mesaj": "Gorsel olusturuldu: " + prompt}

        if emir.startswith("komut "):
            komut = emir[6:]
            sonuc = SiberAjan.komut_calistir(komut)
            return {"tur": "komut", "sonuc": sonuc}

        if emir.startswith("ara ") or emir.startswith("hafizada ara "):
            sorgu = emir.replace("hafizada ara ", "").replace("ara ", "").strip()
            bulunan = self.hafiza.hatirla(sorgu)
            if bulunan:
                return {"tur": "hafiza", "sonuc": bulunan, "mesaj": f"🧠 {len(bulunan)} kayıt bulundu"}
            return {"tur": "hafiza", "sonuc": [], "mesaj": "🧠 Hafızada sonuç bulunamadı"}

        if emir in ("durum", "status"):
            return {"tur": "durum", "sonuc": self.istatistik()}

        if emir in ("yardim", "help"):
            return {"tur": "yardim", "sonuc": self._yardim_metni()}

        if emir.startswith("kaydet "):
            icerik = emir[7:]
            self.hafiza.kaydet(f"V5 Not - {datetime.now().strftime('%H:%M:%S')}", icerik, ["v5", "not"])
            return {"tur": "mesaj", "sonuc": "🧠 Notunuz hafızaya kaydedildi Berkay Patron!"}

        if emir.startswith("ping "):
            hedef = emir[5:].strip() or "8.8.8.8"
            sonuc = SiberAjan.ag_testi(hedef)
            return {"tur": "komut", "sonuc": sonuc, "mesaj": f"📡 Ping testi: {hedef}"}

        if emir == "sistem":
            bilgi = SiberAjan.sistem_bilgisi()
            return {"tur": "bilgi", "sonuc": bilgi}

        if emir.startswith("port "):
            try:
                port = int(emir[5:].strip())
                acik = SiberAjan.port_dinle(port)
                durum_str = "AÇIK" if acik else "KAPALI"
                return {"tur": "mesaj", "sonuc": f"🔌 Port {port}: {durum_str}"}
            except ValueError:
                return {"tur": "mesaj", "sonuc": "⚠️ Geçerli bir port numarası girin Berkay Patron!"}

        # AI motoruna yönlendir
        return {"tur": "ai", "sonuc": emir}

    def _yardim_metni(self) -> str:
        return """✦ V5_NEXUS_CORE — KOMUTLAR ✦

  🎨  görsel <prompt>     → Flux ile görsel oluştur (tarayıcıda açılır)
  ⌨️  komut <komut>       → Sistem komutu çalıştır (Siber Ajan)
  🧠  ara <sorgu>         → Obsidian hafızada ara
  📝  kaydet <not>        → Hafızaya not kaydet
  📡  ping <hedef>        → Ağ testi yap
  🔌  port <numara>       → Port kontrol et
  💻  sistem              → Sistem bilgisi göster
  ℹ️  durum               → Çekirdek durumunu göster
  ❓  yardim              → Bu yardım menüsü
  🚪  çıkış / exit        → Çekirdeği kapat

  Bunun dışındaki her şey AI'ya gider. (V5 AI Motor)"""

    # ─── Zengin UI (varsa) ──────────────────────────────────

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
    ╔══════════════════════════════════════╗
    ║     V5_NEXUS_CORE  v5.0.0           ║
    ║     Glassesglitch Studio             ║
    ║     gulmzcetiner:V5                 ║
    ╚══════════════════════════════════════╝[/bold {V5Tema.STAR_BLUE}]"""

    def _arayuz_goster(self):
        if not self.konsol:
            return
        self.konsol.clear()
        self.konsol.print(Align.center(self._v5_logo()))
        self.konsol.print(Align.center(f"[dim {V5Tema.DIM_STAR}]✦ Berkay Patron için inşa edildi ✦[/dim {V5Tema.DIM_STAR}]"))
        durum = self.istatistik()
        self.konsol.print(self._tema_paneli(
            f"⏱  {durum['calisma_suresi']}  |  📡 {durum['motor']}  |  🤖 {durum['model']}  |  🧠 {durum['hafiza_dosyasi']} kayıt",
            "NEXUS DURUM", V5Tema.GLOW_CYAN
        ))

    # ─── Ana Döngü ──────────────────────────────────────────

    def calistir(self):
        print()
        print(patron_log("ATEŞLEME", "✦ V5_NEXUS_CORE Aktif — Berkay Patron, emirleriniz benim için komuttur! ✦"))
        print()

        if self.konsol:
            self._arayuz_goster()

        while True:
            try:
                if self.konsol:
                    self.konsol.print()
                    girdi = Prompt.ask(f"[bold {V5Tema.STAR_BLUE}]✦ V5[/bold {V5Tema.STAR_BLUE}]")
                else:
                    girdi = input("✦ V5 > ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                print(patron_log("ATEŞLEME", "✦ V5_NEXUS_CORE Kapatılıyor — İyi günler Berkay Patron! ✦"))
                break

            if not girdi or not girdi.strip():
                continue

            girdi = girdi.strip()

            if girdi.lower() in ("cikis", "exit", "quit", "kapat"):
                print(patron_log("ATEŞLEME", "✦ Çekirdek sonlandırılıyor. Beklemedeyim Berkay Patron! ✦"))
                break

            self.istek_sayisi += 1
            self.durum = "İŞLENİYOR"

            try:
                sonuc = self.emir_cozumle(girdi)
            except Exception as e:
                print(patron_log("HATA", "Beklenmeyen hata", str(e)[:100]))
                continue

            self.durum = "BEKLİYOR"

            # ── Sonuçları göster ─────────────────────────────
            tur = sonuc.get("tur", "mesaj")
            sonuc_icerik = sonuc.get("sonuc", "")
            mesaj = sonuc.get("mesaj", "")

            if tur == "gorsel":
                print(patron_log("BASARI", f"Flux görseli hazır! Tarayıcınızda açıldı Berkay Patron.", sonuc_icerik))

            elif tur == "mesaj":
                print(f"\n  💠 {mesaj or sonuc_icerik}\n")

            elif tur == "bilgi":
                bilgi = sonuc_icerik
                print(f"\n  💻 SİSTEM BİLGİSİ")
                print(f"  ────────────────")
                for anahtar, deger in bilgi.items():
                    print(f"  {anahtar}: {deger}")
                print()

            elif tur == "durum":
                s = sonuc_icerik
                print(f"\n  ⏱  Çalışma Süresi: {s['calisma_suresi']}")
                print(f"  📡 Motor: {s['motor']}")
                print(f"  🤖 Model: {s['model']}")
                print(f"  📊 İstek: {s['istek_sayisi']}")
                print(f"  🧠 Hafıza: {s['hafiza_dosyasi']} kayıt")
                print(f"  🆔 Oturum: {s['oturum']}\n")

            elif tur == "yardim":
                print(f"\n  {sonuc_icerik}\n")

            elif tur == "hafiza":
                kayitlar = sonuc_icerik
                if mesaj:
                    print(f"\n  {mesaj}\n")
                for k in kayitlar[:5]:
                    ozet = k.get("content_preview", "")[:120].replace("\n", " ")
                    print(f"  📄 {k.get('path','?')}")
                    print(f"     {ozet}...\n")

            elif tur == "komut":
                komut_sonuc = sonuc_icerik
                if komut_sonuc.get("basari"):
                    cikti = komut_sonuc.get("cikti", "").strip()
                    if cikti:
                        print(f"\n  ── KOMUT ÇIKTISI ──\n  {cikti}\n  ──\n")
                    else:
                        print(f"  ✅ Komut başarıyla çalıştı (çıktı yok)\n")
                else:
                    hata = komut_sonuc.get("hata", "Bilinmeyen hata")
                    print(f"  ❌ Komut hatası: {hata}\n")

            elif tur == "ai":
                # AI motoruna sor
                prompt = sonuc_icerik
                print(patron_log("BILGI", "AI motoruna danışılıyor..."))
                yanit_json = self.ai.sor(prompt)
                try:
                    yanit = json.loads(yanit_json)
                    icerik = yanit.get("icerik", yanit_json)
                    dusunce = yanit.get("dusunce", "")
                    aksiyon = yanit.get("aksiyon", "")
                    hedef = yanit.get("hedef", "")

                    if dusunce:
                        print(f"\n  💭 {dusunce}")

                    if aksiyon == "gorsel_uret" and hedef:
                        NexusMotor.gorsel_uret_ve_ac(hedef)
                    elif aksiyon == "komut_calistir" and hedef:
                        komut_sonuc = SiberAjan.komut_calistir(hedef)
                        if komut_sonuc["basari"]:
                            print(f"\n  ── SİBER AJAN ÇIKTISI ──\n{komut_sonuc['cikti']}\n  ──\n")
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
                            print(f"\n  ── {hedef} ──\n{icerik_oku}\n  ──\n")
                        except Exception as e:
                            print(patron_log("HATA", "Dosya okunamadı", str(e)[:80]))
                    else:
                        if icerik:
                            print(f"\n  ✨ {icerik}\n")

                except json.JSONDecodeError:
                    # Ham yanıt göster
                    print(f"\n  ✨ {yanit_json}\n")

            self.sayfa_gecmisi.append((girdi, sonuc))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# V5 BAĞIMSIZ GÖRSEL MOTORU (exports)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def v5_gorsel_olustur(prompt: str, boyut: str = "genis") -> str:
    """V5 dışa dönük görsel oluşturma fonksiyonu."""
    return NexusMotor.gorsel_uret_ve_ac(prompt, boyut)

def v5_siber_komut(komut: str) -> Dict[str, Any]:
    """V5 dışa dönük siber komut fonksiyonu."""
    return SiberAjan.komut_calistir(komut)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GİRİŞ NOKTASI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print()
    print(f"  ╔{'═'*50}╗")
    print(f"  ║  V5_NEXUS_CORE — Glassesglitch Studio       ║")
    print(f"  ║  gulmzcetiner:V5                     ║")
    print(f"  ║  ~ Berkay Patron için inşa edildi ~         ║")
    print(f"  ╚{'═'*50}╝")
    print()

    cekirdek = V5NexusCore()
    cekirdek.calistir()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print(patron_log("ATEŞLEME", "✦ V5_NEXUS_CORE kapatıldı. Beklemedeyim Berkay Patron! ✦"))
        sys.exit(0)
    except Exception as e:
        print(patron_log("HATA", "Çekirdek kritik hata ile karşılaştı", str(e)[:200]))
        sys.exit(1)
