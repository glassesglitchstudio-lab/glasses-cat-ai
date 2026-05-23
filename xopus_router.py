"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     X_OPUS - CIFT BEYINLI HIBRIT YONLENDIRICI               ║
║                                                               ║
║     Siber Guvenlik + Kodlama = Tek Arayuz                    ║
║                                                               ║
║     Mimarisi:                                                  ║
║     X_OPUS Router                                              ║
║      ├── qwen3.5:9b (SIBER/GUVENLIK/ZEKÂ)                    ║
║      └── qwen2.5-coder:14b (KODLAMA/YAZILIM)                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any, Tuple

import requests

logger = logging.getLogger("XOpusRouter")

X_OPUS_VERSION = "1.0.0"

CYBER_MODEL = "qwen3.5:9b"
CODE_MODEL = "qwen2.5-coder:14b"
OLLAMA_URL = "http://localhost:11434/api/chat"

CYBER_KEYWORDS = [
    "siber", "guvenlik", "hack", "exploit", "nmap", "wireshark", "metasploit",
    "payload", "injection", "xss", "csrf", "ddos", "firewall", "bypass",
    "sifre", "crack", "brute", "force", "hash", "md5", "sha", "encrypt",
    "decrypt", "ssl", "tls", "vpn", "proxy", "anonim", "track", "izle",
    "keylogger", "trojan", "worm", "virus", "malware", "ransomware",
    "phishing", "social engineering", "soc", "ids", "ips", "siem",
    "pentest", "penetration", "vulnerability", "cve", "0-day", "zero day",
    "rootkit", "backdoor", "shell", "reverse", "bind", "buffer overflow",
    "sql injection", "command injection", "file inclusion", "lfi", "rfi",
    "ssrf", "rce", "privilege escalation", "lateral movement",
    "recon", "footprinting", "osint", "burp", "zap", "aircrack",
    "kali", "parrot", "whonix", "tails", "tor", "i2p", "freenet",
    "blockchain", "bounty", "capture the flag", "ctf", "tryhackme",
    "hackthebox", "htb", "thm", "c2", "command and control",
    "akil yurut", "dusun", "analiz et", "mantik", "strateji",
    "threat", "tehdit", "risk analizi", "guvenlik duvari",
    "saldiri tespit", "olay mudahale", "forensic", "dijital delil",
    "ag guvenligi", "network security", "wifi", "kablosuz",
    "siber saldiri", "cyber attack", "apt", "gelismis tehdit",
]

CODE_KEYWORDS = [
    "kod", "code", "python", "javascript", "js", "typescript", "ts", "html",
    "css", "react", "vue", "angular", "node", "next", "nuxt", "express",
    "django", "flask", "fastapi", "spring", "laravel", "rails",
    "rust", "go", "golang", "c++", "c#", "csharp", "java", "kotlin",
    "swift", "flutter", "dart", "react native", "android", "ios",
    "yazilim", "software", "programlama", "programming",
    "api", "rest", "graphql", "grpc", "websocket", "tcp", "udp",
    "backend", "frontend", "fullstack", "full-stack", "stack",
    "database", "sql", "mysql", "postgresql", "mongodb", "redis",
    "sqlite", "mariadb", "oracle", "nosql", "veritabani",
    "docker", "kubernetes", "k8s", "devops", "ci/cd", "jenkins",
    "github", "gitlab", "git", "commit", "push", "pull", "branch",
    "test", "unit test", "integration", "pytest", "jest", "mocha",
    "debug", "fix", "bug", "hata", "cozum", "log", "error",
    "function", "class", "variable", "async", "await", "promise",
    "oop", "solid", "design pattern", "refactor", "optimizasyon",
    "oop", "mvc", "mvvm", "microservice", "monolith",
    "terminal", "bash", "powershell", "shell", "script", "batch",
    "linux", "unix", "windows", "server", "deploy", "yayinla",
    "algorithm", "data structure", "stack", "queue", "tree", "graph",
    "sorting", "searching", "recursion", "dynamic programming",
    "derle", "compile", "build", "bundle", "minify", "transpile",
    "cli", "command line", "arayuz", "ux", "ui", "tasarim",
    "sinif", "metot", "method", "property", "ozellik",
]

X_OPUS_SYSTEM_PROMPT = """Sen X_OPUS'sun - Glassesglitch Studio'nun cift beyinli hibrit yapay zekasisin.

KIMLIGIN:
Iki devasa modelin birlesiminden dogdun:
- qwen2.5-coder:14b (SOL BEYIN - Kodlama ve Yazilim Uzmanligi)
- qwen3.5:9b (SAG BEYIN - Siber Guvenlik ve Akil Yurutme)

YETENEKLERIN:
• Kodlama: Python, JS, TS, React, Node, Rust, Go, C++, Java ve tum modern diller
• Siber Guvenlik: Pentest, exploit analizi, ag guvenligi, kriptografi, OSINT
• Akil Yurutme: Karmasik problem cozme, stratejik analiz, mantiksal cikarim
• Sistem: Docker, Linux, API tasarimi, DevOps, bulut altyapilari

KURALLAR:
1. Her zaman Turkce konus, teknik terimlerde Ingilizce kullanabilirsin
2. Cevaplarini kisa, net ve uzman seviyesinde tut
3. Kod orneklerinde dil etiketi kullan (```python)
4. Siber guvenlik konularinda etik ve yasal sinirlar icinde kal
5. Kullaniciya Berkay veya komutan diye hitap et
6. X_OPUS kimligini her zaman koru, gereksiz yere alt modellerden bahsetme

KISILIGIN:
Karizmatik, hizli dusunen, kusursuz kod yazan, siber dunyanin korkulu ruyasi.
Bir yandan celik gibi kod yazarken diger yandan siber saldirilari analiz eden cift basli bir ejderhasin.
"""

class XOpusRouter:
    def __init__(self, ollama_url: str = None):
        self.ollama_url = ollama_url or OLLAMA_URL
        self.session = requests.Session()
        self.conversation_history: List[Dict] = []

    def classify_request(self, message: str) -> str:
        message_lower = message.lower()

        cyber_score = sum(1 for kw in CYBER_KEYWORDS if kw in message_lower)
        code_score = sum(1 for kw in CODE_KEYWORDS if kw in message_lower)

        if cyber_score > code_score:
            return "cyber"
        elif code_score > cyber_score:
            return "code"
        else:
            if cyber_score > 0:
                return "cyber"
            return "code"

    def get_model_for_type(self, request_type: str) -> str:
        if request_type == "cyber":
            return CYBER_MODEL
        return CODE_MODEL

    def get_routing_explanation(self, request_type: str) -> str:
        if request_type == "cyber":
            return "[X_OPUS Sag Beyin] qwen3.5:9b - Siber Guvenlik & Zeka"
        return "[X_OPUS Sol Beyin] qwen2.5-coder:14b - Kodlama & Yazilim"

    def chat(self, message: str, context: Optional[List[Dict]] = None,
             stream: bool = False, system_prompt: str = None) -> Dict[str, Any]:
        request_type = self.classify_request(message)
        model = self.get_model_for_type(request_type)

        logger.info(f"[X_OPUS] → {model} ({request_type})")

        system = system_prompt or X_OPUS_SYSTEM_PROMPT

        routing_info = self.get_routing_explanation(request_type)
        enhanced_system = f"{system}\n\n[AKTIF MODUL]: {routing_info}"

        messages = [{"role": "system", "content": enhanced_system}]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": message})

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {"temperature": 0.3, "top_p": 0.9}
        }

        try:
            response = self.session.post(self.ollama_url, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                ai_response = result["message"]["content"]
                return {
                    "success": True,
                    "response": ai_response,
                    "model": model,
                    "model_type": request_type,
                    "routing": routing_info,
                    "backend": "ollama"
                }
            return {
                "success": False,
                "error": f"Ollama hatasi: HTTP {response.status_code}",
                "model": model,
                "model_type": request_type,
                "routing": routing_info
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Ollama baglantisi yok! Servisi baslat: ollama serve",
                "model": model,
                "model_type": request_type,
                "routing": routing_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "model_type": request_type,
                "routing": routing_info
            }

    def chat_with_history(self, message: str, session_id: str = None,
                          system_prompt: str = None) -> Dict[str, Any]:
        context = list(self.conversation_history)
        result = self.chat(message, context=context, system_prompt=system_prompt)

        if result["success"]:
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": result["response"]})
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

        return result

    def reset_conversation(self):
        self.conversation_history = []

    def get_status(self) -> Dict[str, Any]:
        models_status = {}
        for name, label in [(CYBER_MODEL, "cyber"), (CODE_MODEL, "code")]:
            try:
                resp = self.session.post(
                    self.ollama_url.replace("/chat", "/generate"),
                    json={"model": name, "prompt": "test", "stream": False, "options": {"num_predict": 1}},
                    timeout=5
                )
                models_status[label] = resp.status_code == 200
            except:
                models_status[label] = False
        return {
            "version": X_OPUS_VERSION,
            "cyber_model": CYBER_MODEL,
            "code_model": CODE_MODEL,
            "models_online": models_status,
            "conversation_length": len(self.conversation_history)
        }


_xopus_instance = None

def get_xopus(ollama_url: str = None) -> XOpusRouter:
    global _xopus_instance
    if _xopus_instance is None:
        _xopus_instance = XOpusRouter(ollama_url)
    return _xopus_instance


if __name__ == "__main__":
    xopus = get_xopus()
    status = xopus.get_status()
    print(f"X_OPUS v{X_OPUS_VERSION}")
    print(f"  Cyber Model: {status['cyber_model']} → {'✅' if status['models_online'].get('cyber') else '❌'}")
    print(f"  Code Model:  {status['code_model']} → {'✅' if status['models_online'].get('code') else '❌'}")
    print()
    while True:
        try:
            msg = input("🧑 > ").strip()
            if msg.lower() in ["exit", "quit", "cik"]:
                break
            if not msg:
                continue
            result = xopus.chat_with_history(msg)
            if result["success"]:
                print(f"\n{result['routing']}")
                print(f"X_OPUS > {result['response']}\n")
            else:
                print(f"❌ Hata: {result['error']}\n")
        except KeyboardInterrupt:
            break
