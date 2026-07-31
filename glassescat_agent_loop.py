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
# PLUGIN & SKILL SİSTEMLERİ (opsiyonel)
# ─────────────────────────────────────────────────────────────

try:
    from plugin_system import PluginManager, HookPoint
    PLUGIN_OK = True
except ImportError:
    PLUGIN_OK = False

try:
    from skill_system import SkillManager
    SKILL_OK = True
except ImportError:
    SKILL_OK = False

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
9. DÜŞÜN, KARAR VER, UYGULA, GÖZLEMLE blokları iç düşüncedir, kullanıcıya asla gösterilmez. Sadece ✅ YANITLA bölümünde kullanıcıya cevabını yaz.
"""


def extract_answer(text: str) -> str:
    """ReAct düşünce bloklarını (DÜŞÜN/KARAR/UYGULA/GÖZLEMLE) çıkarır,
    sadece kullanıcıya gösterilecek final yanıtı döndürür."""
    if not text:
        return text
    react_header_re = re.compile(
        r"^\s*#{2,4}\s*[^\n]{0,40}?(?:DÜŞÜN|DUSUN|THINK|KARAR VER|DECIDE|UYGULA|ACT|GÖZLEMLE|OBSERVE|YANITLA|ANSWER)",
        re.IGNORECASE | re.MULTILINE,
    )
    answer_header_re = re.compile(
        r"^\s*#{2,4}\s*[^\n]{0,40}?(?:YANITLA|ANSWER)",
        re.IGNORECASE | re.MULTILINE,
    )
    m = answer_header_re.search(text)
    if m:
        tail = text[m.end():].strip()
        if tail:
            return tail
    lines = text.split("\n")
    out = []
    skip = False
    for ln in lines:
        if react_header_re.match(ln):
            skip = not answer_header_re.match(ln)
            continue
        if not skip:
            out.append(ln)
    joined = "\n".join(out).strip()
    return joined if joined else text


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
        
        # Plugin & Skill sistemleri
        self._plugin_manager = None
        self._skill_manager = None
        if PLUGIN_OK:
            try:
                self._plugin_manager = PluginManager.get_instance()
                self._plugin_manager.load_all_plugins()
                logger.info(f"🔌 Plugin sistemi: {self._plugin_manager.get_plugin_count()} eklenti yüklendi")
            except Exception as e:
                logger.warning(f"Plugin sistemi başlatılamadı: {e}")
        if SKILL_OK:
            try:
                self._skill_manager = SkillManager.get_instance()
                self._skill_manager.discover_skills()
                enabled = self._skill_manager.get_enabled_skills()
                logger.info(f"🧠 Skill sistemi: {len(enabled)} yetenek aktif")
            except Exception as e:
                logger.warning(f"Skill sistemi başlatılamadı: {e}")
    
    def run(self, user_input: str, conversation_history: List = None,
            memory_context: str = "", session_id: str = None,
            custom_prompt: str = "") -> Dict:
        """
        ReAct döngüsünü çalıştır.

        Args:
            user_input: Kullanıcının girdisi
            conversation_history: Konuşma geçmişi
            memory_context: Hafızadan bulunan bağlam
            session_id: Oturum kimliği
            custom_prompt: Stil/tercih/extended thinking prompt'u
        
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
        
        # --- PLUGIN: ON_USER_INPUT ---
        self._run_plugin_hook(HookPoint.ON_USER_INPUT, user_input=user_input, session_id=session_id)
        
        # Sistem prompt'unu oluştur (skill'ler + custom prompt dahil)
        system_prompt = self._build_system_prompt(custom_prompt=custom_prompt)
        
        # Kullanıcı prompt'unu oluştur (hafıza bağlamıyla)
        user_prompt = self._build_user_prompt(user_input, memory_context, conversation_history)
        
        # --- PLUGIN: before_chat ---
        self._run_plugin_hook(HookPoint.BEFORE_CHAT, user_input=user_input, system_prompt=system_prompt)
        
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
                self._run_plugin_hook(HookPoint.ON_ERROR, error="LLM yanıt vermedi", user_input=user_input)
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
            final_response = extract_answer(llm_response)
            self.thoughts.append(Thought(
                step=self.iteration,
                type="answer",
                content=final_response[:200]
            ))
            
            # --- PLUGIN: after_chat ---
            self._run_plugin_hook(HookPoint.AFTER_CHAT, response=final_response, tool_calls=tool_calls)
            
            return {
                "response": final_response,
                "thoughts": [asdict(t) for t in self.thoughts],
                "tool_calls": tool_calls,
                "iterations": self.iteration,
                "success": True
            }
        
        # Maksimum iterasyon aşıldıysa
        final_response = "Bu görevi tamamlamak için daha fazla adıma ihtiyacım var. Kaldığım yerden devam edebilirim."
        
        # --- PLUGIN: after_chat (max iter) ---
        self._run_plugin_hook(HookPoint.AFTER_CHAT, response=final_response, tool_calls=tool_calls, max_iterations_reached=True)
        
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
    
    def _build_system_prompt(self, custom_prompt: str = "") -> str:
        """Sistem prompt'unu oluştur (tool descriptions + custom prompt ile)"""
        tool_descriptions = ""
        if self.core and self.core.toolformer:
            tool_descriptions = self.core.toolformer.build_system_prompt()
            tool_list = []
            for tool in self.core.toolformer.registry.list_all():
                params = ", ".join(f"{p.name}:{p.type}" for p in tool.parameters)
                tool_list.append(f"  • {tool.name}({params}) - {tool.description[:60]}")
            tool_descriptions = "\n".join(tool_list)
        
        base = REACT_SYSTEM_PROMPT.format(
            tool_descriptions=tool_descriptions or "Henüz araç tanımlanmamış.",
            max_iterations=self.max_iterations
        )
        
        if custom_prompt:
            base += f"\n\n## Kullanıcı Tercihleri\n{custom_prompt}"
        
        return base
    
    def _build_user_prompt(self, user_input: str, memory_context: str,
                          conversation_history: List = None) -> str:
        """Kullanıcı prompt'unu oluştur (bağlamla zenginleştirilmiş)"""
        parts = []
        
        # Skill bağlamı
        skill_context = self._get_skill_context()
        if skill_context:
            parts.append(skill_context + "\n")
        
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
    
    def _run_plugin_hook(self, hook_point, **kwargs):
        """Plugin hook'larını güvenli bir şekilde çalıştır."""
        if not self._plugin_manager:
            return []
        try:
            return self._plugin_manager.execute_hooks(hook_point, **kwargs)
        except Exception as e:
            logger.debug(f"Plugin hook {hook_point} hatası: {e}")
            return []

    def _get_skill_context(self) -> str:
        """Skill'lerden birleşik prompt bağlamı oluştur."""
        if not self._skill_manager:
            return ""
        try:
            enabled = self._skill_manager.get_enabled_skills()
            if not enabled:
                return ""
            prompt = self._skill_manager.get_combined_prompt(list(enabled.keys()))
            tools = self._skill_manager.get_combined_tools(list(enabled.keys()))
            examples = self._skill_manager.get_combined_examples(list(enabled.keys()))
            parts = []
            if prompt:
                parts.append(f"## 🎯 Aktif Yeteneklerin\n{prompt}")
            if tools:
                tool_lines = []
                for t in tools:
                    name = t.get("name", "?")
                    desc = t.get("description", "")[:60]
                    tool_lines.append(f"  • {name} - {desc}")
                if tool_lines:
                    parts.append("## 🛠️ Skill Araçları\n" + "\n".join(tool_lines))
            if examples:
                parts.append("## 📚 Örnek Kullanımlar\n" + str(examples)[:300])
            return "\n\n".join(parts)
        except Exception as e:
            logger.debug(f"Skill bağlamı alınamadı: {e}")
            return ""

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
                                    text = response.get('response') or response.get('text') or response.get('answer') or ''
                                    if isinstance(text, dict):
                                        text = text.get('response') or text.get('text') or str(text)
                                    if text:
                                        result_container.append(str(text))
                                    else:
                                        err = response.get('error') or response.get('message') or ''
                                        result_container.append(f"[AI motoru yanıt vermedi] {err}" if err else "[AI motoru yanıt vermedi]")
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
                
                # Ollama - X_OPUS ile dene
                try:
                    resp = session.post(
                        "http://localhost:11434/v1/chat/completions",
                        json={
                            "model": "glassesglitchstudio/x_opus:V1_X_OPUS",
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
        
        # Thread ile calistir (maks 120 saniye - buyuk modeller icin yeterli)
        thread = threading.Thread(target=try_llm, daemon=True)
        thread.start()
        thread.join(timeout=120)
        
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
