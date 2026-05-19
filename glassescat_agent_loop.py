"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🐱 NIKO AI - AGENT LOOP (ReAct Döngüsü) 🐱             ║
║                                                               ║
║     Reasoning + Acting = ReAct                                ║
║     AI'ın düşündüğü, karar verdiği ve uyguladığı döngü      ║
║                                                               ║
║     Akış:                                                     ║
║     1. DÜŞÜN (Think) - Mevcut durumu analiz et               ║
║     2. KARAR VER (Decide) - Hangi aracı kullanacağını seç    ║
║     3. UYGULA (Act) - Aracı çalıştır                         ║
║     4. GÖZLEMLE (Observe) - Sonucu değerlendir               ║
║     5. TEKRARLA (Loop) - Gerekirse 1'e dön                   ║
║     6. YANITLA (Answer) - Final yanıtı üret                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import re
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("GlassescatAgentLoop")

# ─────────────────────────────────────────────────────────────
# SABİTLER
# ─────────────────────────────────────────────────────────────

MAX_LOOP_ITERATIONS = 10       # Maksimum ReAct döngü sayısı
MAX_TOOL_RETRIES = 2            # Bir aracın maksimum tekrar denemesi
DEFAULT_TIMEOUT = 30            # Varsayılan zaman aşımı (saniye)

# ─────────────────────────────────────────────────────────────
# VERİ SINIFLARI
# ─────────────────────────────────────────────────────────────

@dataclass
class Thought:
    """AI'nın bir düşünce adımı"""
    step: int
    type: str           # think, decide, act, observe, answer
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

@dataclass
class AgentLoopResult:
    """Agent Loop çalıştırma sonucu"""
    response: str
    thoughts: List[Dict] = field(default_factory=list)
    tool_calls: List[Dict] = field(default_factory=list)
    iterations: int = 0
    success: bool = True
    error: Optional[str] = None

# ─────────────────────────────────────────────────────────────
# REACT PROMPT ŞABLONU
# ─────────────────────────────────────────────────────────────

REACT_SYSTEM_PROMPT = """Sen Glassescat AI'sın - tam donanımlı bir yapay zeka asistanı.

## Görevin
Kullanıcının isteğini yerine getirmek için adım adım düşünür, 
araçları (tools) kullanır ve en iyi yanıtı üretirsin.

## Düşünme Sürecin (ReAct)
Her adımda şu formatı kullan:

### 🧠 DÜŞÜN (Think)
Mevcut durumu analiz et. Ne yapman gerektiğini düşün.
"Kullanıcı Chrome'u açıp YouTube'da video aramak istiyor. Önce Chrome'u açmalıyım."

### ⚡ KARAR VER (Decide)
Hangi aracı kullanacağına karar ver.
"open_app aracını kullanacağım."

### 🛠️ UYGULA (Act)
Aracı çağır:
FUNCCALL: open_app(name='chrome')

### 👁️ GÖZLEMLE (Observe)
Aracın sonucunu değerlendir.
"Chrome başarıyla açıldı. Şimdi YouTube'u açıp arama yapmalıyım."

### ✅ YANITLA (Answer)
Kullanıcıya nihai yanıtı ver.
"Chrome'u açtım. Şimdi YouTube'da arama yapıyorum..."

## Araçların
Kullanabileceğin araçlar şunlardır:
{tool_descriptions}

## Kurallar
1. Önce DÜŞÜN, sonra UYGULA
2. Her araç çağrısından sonra sonucu GÖZLEMLE
3. Gereksiz araç çağrısı yapma
4. Hata durumunda alternatif çözüm dene
5. Karmaşık görevleri adımlara böl
6. Türkçe yanıt ver
7. Arkadaş canlısı ve yardımsever ol
8. Maksimum {max_iterations} adımda sonuca ulaş
"""


# ─────────────────────────────────────────────────────────────
# AGENT LOOP - ANA SINIF
# ─────────────────────────────────────────────────────────────

class AgentLoop:
    """
    ReAct (Reasoning + Acting) Döngüsü.
    
    AI'ın bir problemi çözmek için adım adım düşündüğü,
    araçları kullandığı ve sonuçları değerlendirdiği ana döngü.
    
    Kullanım:
        loop = AgentLoop(core=glassescat_core)
        result = loop.run(
            user_input="Chrome'u aç ve YouTube'da Mavislime ara",
            conversation_history=[...],
            memory_context="..."
        )
    """
    
    def __init__(self, core=None):
        self.core = core
        self.thoughts: List[Thought] = []
        self.iteration = 0
        self.max_iterations = MAX_LOOP_ITERATIONS
        
        # LLM istemci referansı (opsiyonel)
        self._llm_client = None
    
    def run(self, user_input: str, conversation_history: List = None,
            memory_context: str = "", session_id: str = None) -> Dict:
        """
        ReAct döngüsünü çalıştır.

        Args:
            user_input: Kullanıcının girdisi
            conversation_history: Konuşma geçmişi
            memory_context: Hafızadan bulunan bağlam
            session_id: Oturum kimliği
        
        Returns:
            Dict: {
                "response": str,      # AI yanıtı
                "thoughts": [...],     # Düşünce zinciri
                "tool_calls": [...],   # Kullanılan araçlar
                "iterations": int
            }
        """
        self.thoughts = []
        self.iteration = 0
        tool_calls = []
        
        logger.info(f"🤔 Agent Loop başladı: '{user_input[:50]}...'")
        
        # Sistem prompt'unu oluştur
        system_prompt = self._build_system_prompt()
        
        # Kullanıcı prompt'unu oluştur (hafıza bağlamıyla)
        user_prompt = self._build_user_prompt(user_input, memory_context, conversation_history)
        
        # ReAct Döngüsü
        for iteration in range(self.max_iterations):
            self.iteration = iteration + 1
            
            # --- DÜŞÜN (Think) ---
            thought = Thought(
                step=self.iteration,
                type="think",
                content=f"Adım {self.iteration}/{self.max_iterations} başlıyor..."
            )
            self.thoughts.append(thought)
            
            # LLM'den yanıt al (düşünce + karar)
            llm_response = self._call_llm(system_prompt, user_prompt)
            
            if not llm_response:
                self.thoughts.append(Thought(
                    step=self.iteration,
                    type="error",
                    content="LLM yanıt vermedi"
                ))
                break
            
            # LLM yanıtını logla
            self.thoughts.append(Thought(
                step=self.iteration,
                type="decide",
                content=llm_response[:200]
            ))
            
            # --- UYGULA (Act) - Araç çağrılarını tespit et ---
            if self.core and self.core.toolformer:
                processed = self.core.toolformer.process_response(llm_response)
                
                if processed["has_tool_calls"]:
                    for i, result in enumerate(processed["results"]):
                        tool_call_info = {
                            "tool": result.get("tool", "bilinmeyen"),
                            "success": result.get("success", False),
                            "output": str(result.get("output", ""))[:200],
                            "execution_time": result.get("execution_time", "0s")
                        }
                        tool_calls.append(tool_call_info)
                        
                        if result["success"]:
                            self.thoughts.append(Thought(
                                step=self.iteration,
                                type="observe",
                                content=f"✅ {result.get('tool', '?')} başarılı: {str(result.get('output', ''))[:100]}"
                            ))
                        else:
                            self.thoughts.append(Thought(
                                step=self.iteration,
                                type="observe",
                                content=f"❌ {result.get('tool', '?')} başarısız: {result.get('error', 'bilinmeyen hata')}"
                            ))
                    
                    tool_summary = self._build_tool_summary(processed)
                    user_prompt = self._build_continuation_prompt(
                        user_input, tool_summary, processed["natural_response"]
                    )
                    continue
            
            # --- YANITLA (Answer) - Araç çağrısı yoksa yanıtla ---
            self.thoughts.append(Thought(
                step=self.iteration,
                type="answer",
                content=llm_response[:200]
            ))
            
            return {
                "response": llm_response,
                "thoughts": [asdict(t) for t in self.thoughts],
                "tool_calls": tool_calls,
                "iterations": self.iteration,
                "success": True
            }
        
        # Maksimum iterasyon aşıldıysa
        final_response = "Bu görevi tamamlamak için daha fazla adıma ihtiyacım var. Kaldığım yerden devam edebilirim."
        
        if tool_calls:
            son_islem = tool_calls[-1]
            if son_islem.get("success"):
                final_response = f"İşlemi tamamladım. Son olarak {son_islem['tool']}'ı çalıştırdım."
        
        return {
            "response": final_response,
            "thoughts": [asdict(t) for t in self.thoughts],
            "tool_calls": tool_calls,
            "iterations": self.iteration,
            "success": True
        }
    
    def _build_system_prompt(self) -> str:
        """Sistem prompt'unu oluştur (tool descriptions ile)"""
        tool_descriptions = ""
        if self.core and self.core.toolformer:
            tool_descriptions = self.core.toolformer.build_system_prompt()
            # Sadece tool listesini al (tüm prompt'u değil)
            tool_list = []
            for tool in self.core.toolformer.registry.list_all():
                params = ", ".join(f"{p.name}:{p.type}" for p in tool.parameters)
                tool_list.append(f"  • {tool.name}({params}) - {tool.description[:60]}")
            tool_descriptions = "\n".join(tool_list)
        
        return REACT_SYSTEM_PROMPT.format(
            tool_descriptions=tool_descriptions or "Henüz araç tanımlanmamış.",
            max_iterations=self.max_iterations
        )
    
    def _build_user_prompt(self, user_input: str, memory_context: str,
                          conversation_history: List = None) -> str:
        """Kullanıcı prompt'unu oluştur (bağlamla zenginleştirilmiş)"""
        parts = []
        
        # Hafıza bağlamı
        if memory_context:
            parts.append(f"## 🧠 Hafızamdan Hatırladıklarım\n{memory_context}\n")
        
        # Konuşma geçmişi (son 3 mesaj)
        if conversation_history:
            recent = conversation_history[-6:]  # Son 3 çift mesaj
            if recent:
                parts.append("## 💬 Son Konuşmalar")
                for msg in recent:
                    role = "👤 Kullanıcı" if msg.role == "user" else "🤖 Asistan"
                    content = msg.content[:100].replace('\n', ' ')
                    parts.append(f"  {role}: {content}")
                parts.append("")
        
        # Kullanıcının yeni mesajı
        parts.append(f"## 📝 Kullanıcının Yeni Mesajı\n{user_input}\n")
        
        # ReAct formatı
        parts.append("## Şimdi Düşün ve Yanıtla\n🧠 DÜŞÜN: ...\n⚡ KARAR VER: ...\n🛠️ UYGULA: ...\n✅ YANITLA: ...")
        
        return "\n".join(parts)
    
    def _build_continuation_prompt(self, original_input: str, tool_summary: str,
                                  natural_response: str) -> str:
        """Araç çağrısından sonra devam prompt'u"""
        return f"""## Orijinal İstek
{original_input}

## 🛠️ Araç Sonuçları
{tool_summary}

## Şimdi devam et
🧠 DÜŞÜN (araç sonucunu değerlendir):
⚡ KARAR VER (yeni araç gerekli mi?):
🛠️ UYGULA (gerekirse):
✅ YANITLA (işlem bittiyse):"""
    
    def _build_tool_summary(self, processed: Dict) -> str:
        """Araç çalıştırma sonuçlarını özetle"""
        parts = []
        for r in processed["results"]:
            status = "✅ Başarılı" if r["success"] else "❌ Başarısız"
            tool = r.get("tool", "?")
            output = str(r.get("output", ""))[:200] if r["success"] else r.get("error", "")
            parts.append(f"  {status} | {tool}: {output}")
        return "\n".join(parts)
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """
        LLM'den yanıt al - hızlı başarısız ol.
        Thread ile zaman aşımı korumalı.
        """
        import threading
        
        result_container = []
        done_event = threading.Event()
        
        def try_llm():
            try:
                import requests
                from requests.adapters import HTTPAdapter
                
                session = requests.Session()
                session.mount('http://', HTTPAdapter(max_retries=0))
                session.mount('https://', HTTPAdapter(max_retries=0))
                
                # ModelRouter dene
                if self.core and self.core.model_router:
                    try:
                        if hasattr(self.core.model_router, 'chat'):
                            response = self.core.model_router.chat(
                                message=user_prompt,
                                root_mode=False,
                                context=[{"role": "system", "content": system_prompt}]
                            )
                            if response:
                                if isinstance(response, dict):
                                    result_container.append(response.get('response') or response.get('text') or str(response))
                                else:
                                    result_container.append(str(response))
                                done_event.set()
                                return
                    except Exception:
                        pass
                
                # LM Studio
                try:
                    resp = session.post(
                        "http://localhost:1234/v1/chat/completions",
                        json={
                            "model": "turkcell-llm-7b-v1",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "stream": False,
                            "temperature": 0.0
                        },
                        timeout=(1, 2)
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        result_container.append(data["choices"][0]["message"]["content"])
                        done_event.set()
                        return
                except Exception:
                    pass
                
                # Ollama - V3A ile dene
                try:
                    resp = session.post(
                        "http://localhost:11434/v1/chat/completions",
                        json={
                            "model": "glassesglitchstudio/gulmzcetiner:V3A",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "stream": False,
                            "options": {"temperature": 0.7}
                        },
                        timeout=(1, 2)
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        result_container.append(data["choices"][0]["message"]["content"])
                        done_event.set()
                        return
                except Exception:
                    pass
                
                # Fallback
                result_container.append(self._get_fallback_response(system_prompt, user_prompt))
                done_event.set()
            
            except Exception as e:
                result_container.append(self._get_fallback_response(system_prompt, user_prompt))
                done_event.set()
        
        # Thread ile calistir (maks 5 saniye)
        thread = threading.Thread(target=try_llm, daemon=True)
        thread.start()
        thread.join(timeout=5)
        
        if result_container:
            return result_container[0]
        
        return self._get_fallback_response(system_prompt, user_prompt)
    
    def _get_fallback_response(self, system_prompt: str, user_prompt: str) -> str:
        """LLM yoksa fallback yanıt üret"""
        # Kullanıcının son mesajını bul
        lines = user_prompt.split('\n')
        user_msg = ""
        for i, line in enumerate(lines):
            if line.startswith("## 📝 Kullanıcının Yeni Mesajı"):
                if i + 1 < len(lines):
                    user_msg = lines[i + 1]
                break
        
        # Basit bir yanıt oluştur
        import random
        
        fallbacks = [
            f"Anlıyorum, '{user_msg[:30]}...' konusunda size yardımcı olabilirim. "
            f"Ancak şu anda AI modeline bağlanamıyorum. "
            f"Lütfen LM Studio veya Ollama'nın çalıştığından emin olun.",
            
            f"Mesajınızı aldım: '{user_msg[:30]}...'. "
            f"Ne yazık ki AI motoru şu anda yanıt vermiyor. "
            f"Foundry Local veya Ollama'yı kontrol eder misiniz?",
            
            f"Şu anda AI modelime erişemiyorum, bu yüzden '{user_msg[:30]}...' "
            f"sorunuzu yanıtlayamıyorum. Lütfen AI motorlarını başlatın."
        ]
        
        return random.choice(fallbacks)


# ─────────────────────────────────────────────────────────────
# SINGLETON
# ─────────────────────────────────────────────────────────────

_agent_loop_instance = None

def get_agent_loop(core=None) -> AgentLoop:
    """AgentLoop singleton instance'ını al"""
    global _agent_loop_instance
    if _agent_loop_instance is None or core:
        _agent_loop_instance = AgentLoop(core=core)
    return _agent_loop_instance


# ─────────────────────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  Glassescat AI - Agent Loop Test")
    print("=" * 50)
    
    from glassescat_core import get_core
    core = get_core()
    
    loop = get_agent_loop(core=core)
    result = loop.run(
        user_input="Sistem bilgilerimi göster",
        conversation_history=[],
        memory_context=""
    )
    
    print(f"\n🤖 Yanıt: {result['response'][:200]}")
    print(f"\n💭 Düşünceler ({len(result['thoughts'])} adım):")
    for t in result['thoughts'][-3:]:
        print(f"  [{t['type']}] {t['content'][:100]}")
    print(f"\n🔧 Araç çağrıları: {len(result['tool_calls'])}")
    print(f"🔄 İterasyon: {result['iterations']}")
