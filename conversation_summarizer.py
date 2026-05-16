"""
GlassesCat - Konuşma Özetleme Modülü
Uzun konuşmaları otomatik özetleyerek bağlam yönetimini iyileştirir
"""

import os
import json
import time
import uuid
import logging
import threading
import requests
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class SummaryLevel(Enum):
    """Özetleme seviyeleri"""
    BRIEF = "brief"
    NORMAL = "normal"
    DETAILED = "detailed"


@dataclass
class Summary:
    """Bir konuşma özeti kaydı"""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    session_id: str = ""
    level: SummaryLevel = SummaryLevel.NORMAL
    summary_text: str = ""
    key_points: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    message_count: int = 0
    token_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    source_message_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'session_id': self.session_id,
            'level': self.level.value,
            'summary_text': self.summary_text,
            'key_points': self.key_points,
            'action_items': self.action_items,
            'topics': self.topics,
            'message_count': self.message_count,
            'token_count': self.token_count,
            'created_at': self.created_at,
            'source_message_ids': self.source_message_ids
        }
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Summary':
        data = data.copy()
        data['level'] = SummaryLevel(data.get('level', 'normal'))
        return cls(**data)


class SummaryStore:
    """Özetlerin kalıcı depolanması ve yönetimi"""

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.summaries_file = storage_dir / 'summaries.json'
        self._lock = threading.Lock()
        self._summaries: Dict[str, List[Summary]] = {}
        self._load()

    def _load(self):
        if self.summaries_file.exists():
            try:
                with open(self.summaries_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_id, summary_list in data.items():
                        self._summaries[session_id] = [
                            Summary.from_dict(s) for s in summary_list
                        ]
            except Exception as e:
                logger.error(f"Özetler yüklenemedi: {e}")

    def _save(self):
        with self._lock:
            data = {}
            for session_id, summaries in self._summaries.items():
                data[session_id] = [s.to_dict() for s in summaries]
            with open(self.summaries_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, session_id: str, summary: Summary):
        with self._lock:
            if session_id not in self._summaries:
                self._summaries[session_id] = []
            self._summaries[session_id].append(summary)
        self._save()

    def get_session_summaries(self, session_id: str) -> List[Summary]:
        with self._lock:
            return list(self._summaries.get(session_id, []))

    def get_latest(self, session_id: str) -> Optional[Summary]:
        with self._lock:
            summaries = self._summaries.get(session_id, [])
            return summaries[-1] if summaries else None

    def get_all(self) -> Dict[str, List[Summary]]:
        with self._lock:
            return {k: list(v) for k, v in self._summaries.items()}

    def delete_session_summaries(self, session_id: str) -> bool:
        with self._lock:
            if session_id in self._summaries:
                del self._summaries[session_id]
                self._save()
                return True
            return False

    def clear(self):
        with self._lock:
            self._summaries.clear()
        self._save()


# Varsayılan prompt şablonları - Türkçe
SUMMARIZE_PROMPTS = {
    SummaryLevel.BRIEF: (
        "Aşağıdaki konuşmayı 2-3 cümle ile özetle. "
        "Sadece en önemli konuyu belirt.\n\n"
        "Konuşma:\n{conversation_text}"
    ),
    SummaryLevel.NORMAL: (
        "Aşağıdaki konuşmayı özetle:\n"
        "1. Kısa bir genel özet (3-5 cümle)\n"
        "2. Önemli noktalar (madde halinde)\n"
        "3. Çıkarılması gereken aksiyonlar (varsa)\n"
        "4. Konu başlıkları\n\n"
        "Format:\n"
        "ÖZET: <genel özet>\n"
        "ÖNEMLİ NOKTALAR:\n"
        "- <madde 1>\n"
        "- <madde 2>\n"
        "AKSİYONLAR:\n"
        "- <aksiyon 1>\n"
        "KONULAR:\n"
        "- <konu 1>\n\n"
        "Konuşma:\n{conversation_text}"
    ),
    SummaryLevel.DETAILED: (
        "Aşağıdaki konuşmayı detaylı şekilde özetle:\n"
        "1. Kapsamlı bir genel özet (paragraf)\n"
        "2. Konuşmanın akışı ve önemli dönüm noktaları\n"
        "3. Alınan kararlar ve nedenleri\n"
        "4. Tüm önemli noktalar (detaylı madde)\n"
        "5. Aksiyon maddeleri (sorumlu kişiyle birlikte)\n"
        "6. İlgili konu başlıkları ve alt konular\n"
        "7. Sonraki adımlar veya öneriler\n\n"
        "Format:\n"
        "ÖZET: <kapsamlı özet>\n"
        "KONUŞMA AKIŞI:\n"
        "- <aşama 1>\n"
        "KARARLAR:\n"
        "- <karar 1>: <nedeni>\n"
        "ÖNEMLİ NOKTALAR:\n"
        "- <madde 1>\n"
        "AKSİYONLAR:\n"
        "- [Kişi] <aksiyon>\n"
        "KONULAR:\n"
        "- <konu 1>\n"
        "SONRAKİ ADIMLAR:\n"
        "- <öneri 1>\n\n"
        "Konuşma:\n{conversation_text}"
    )
}


class ConversationSummarizer:
    """
    Konuşma özetleme sistemi
    - Otomatik tetikleme (mesaj sayısı / token limiti)
    - Çoklu özetleme seviyesi
    - Ollama ile yerel model kullanımı
    - Özet geri çağırma ile eski mesajları özetle değiştirme
    """

    def __init__(
        self,
        memory=None,
        ollama_url: str = "http://localhost:11434/api/chat",
        model: str = "llama3.1:latest",
        storage_dir: str = None,
        auto_summarize: bool = True,
        trigger_message_count: int = 20,
        trigger_token_count: int = 2048,
        summary_level: SummaryLevel = SummaryLevel.NORMAL,
    ):
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'storage'
            )
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.memory = memory
        self.ollama_url = ollama_url
        self.model = model
        self.auto_summarize = auto_summarize
        self.trigger_message_count = trigger_message_count
        self.trigger_token_count = trigger_token_count
        self.default_level = summary_level

        self.summary_store = SummaryStore(self.storage_dir)
        self._lock = threading.Lock()
        self._callbacks: List[Callable] = []

        self._ollama_available: Optional[bool] = None

    def on_summary_created(self, callback: Callable):
        """Özet oluşturulduğunda tetiklenecek callback ekle"""
        self._callbacks.append(callback)

    def _call_ollama(self, prompt: str, system: Optional[str] = None) -> Optional[str]:
        """Ollama modeline sorgu gönder"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {"num_predict": 2048}
                },
                timeout=120
            )
            if response.status_code == 200:
                result = response.json()
                content = result.get('message', {}).get('content', '')
                if content:
                    self._ollama_available = True
                    return content.strip()

            self._ollama_available = False
            logger.error(f"Ollama hatası: {response.status_code}")
            return None

        except requests.exceptions.ConnectionError:
            self._ollama_available = False
            logger.warning("Ollama bağlantısı kurulamadı")
            return None
        except Exception as e:
            self._ollama_available = False
            logger.error(f"Ollama çağrı hatası: {e}")
            return None

    def check_ollama(self) -> bool:
        """Ollama bağlantısını kontrol et"""
        try:
            response = requests.get(
                self.ollama_url.replace('/api/chat', '/api/tags'),
                timeout=5
            )
            self._ollama_available = response.status_code == 200
            return self._ollama_available
        except:
            self._ollama_available = False
            return False

    @property
    def is_ollama_available(self) -> bool:
        if self._ollama_available is None:
            self.check_ollama()
        return self._ollama_available

    def _prepare_conversation_text(self, messages: List[Dict]) -> str:
        """Mesaj listesini özetleme için metne dönüştür"""
        lines = []
        for m in messages:
            role = "Kullanıcı" if m.get('role') == 'user' else 'Asistan'
            content = m.get('content', '')
            lines.append(f"[{role}]: {content}")
        return '\n'.join(lines)

    def _parse_summary_response(self, text: str) -> Dict[str, Any]:
        """Ollama yanıtını yapılandırılmış özete çözümle"""
        result = {
            'summary_text': '',
            'key_points': [],
            'action_items': [],
            'topics': []
        }

        if not text:
            return result

        lines = text.strip().split('\n')
        current_section = None
        summary_parts = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            upper = line.upper()

            if upper.startswith('ÖZET:') or upper.startswith('ÖZET') or line.startswith('**ÖZET**'):
                current_section = 'summary'
                summary_parts.append(line.split(':', 1)[-1].strip())
            elif upper.startswith('ÖNEMLİ NOKTALAR') or 'ÖNEMLİ' in line:
                current_section = 'key_points'
            elif upper.startswith('AKSİYON') or line.startswith('**AKSİYON'):
                current_section = 'action_items'
            elif upper.startswith('KONULAR') or line.startswith('**KONULAR'):
                current_section = 'topics'
            elif line.startswith('-') or line.startswith('*'):
                item = line.lstrip('-* ').strip()
                if current_section == 'key_points':
                    result['key_points'].append(item)
                elif current_section == 'action_items':
                    result['action_items'].append(item)
                elif current_section == 'topics':
                    result['topics'].append(item)
            elif current_section == 'summary':
                summary_parts.append(line)

        result['summary_text'] = ' '.join(summary_parts).strip()

        if not result['summary_text'] and text:
            result['summary_text'] = text[:500]

        return result

    def summarize(
        self,
        messages: List[Dict],
        level: Optional[SummaryLevel] = None,
        session_id: str = ""
    ) -> Summary:
        """Konuşma mesajlarını özetle"""
        if level is None:
            level = self.default_level

        conversation_text = self._prepare_conversation_text(messages)
        prompt_template = SUMMARIZE_PROMPTS.get(level, SUMMARIZE_PROMPTS[SummaryLevel.NORMAL])
        prompt = prompt_template.format(conversation_text=conversation_text)

        raw_response = self._call_ollama(prompt)
        parsed = self._parse_summary_response(raw_response) if raw_response else {
            'summary_text': 'Özetleme başarısız oldu (Ollama bağlantısı yok)',
            'key_points': [],
            'action_items': [],
            'topics': []
        }

        summary = Summary(
            session_id=session_id,
            level=level,
            summary_text=parsed['summary_text'],
            key_points=parsed['key_points'],
            action_items=parsed['action_items'],
            topics=parsed['topics'],
            message_count=len(messages),
            source_message_ids=[m.get('id', '') for m in messages if m.get('id')]
        )

        self.summary_store.add(session_id, summary)

        for cb in self._callbacks:
            try:
                cb(summary)
            except Exception as e:
                logger.error(f"Özet callback hatası: {e}")

        logger.info(f"Özet oluşturuldu: {summary.id} ({level.value}, {len(messages)} mesaj)")
        return summary

    def should_summarize(self, session_id: str) -> Tuple[bool, str]:
        """Özetleme gerekip gerekmediğini kontrol et"""
        if not self.auto_summarize:
            return False, "Otomatik özetleme kapalı"

        messages = self._get_session_messages(session_id)
        if not messages:
            return False, "Mesaj yok"

        if len(messages) >= self.trigger_message_count:
            return True, f"Mesaj sayısı limiti aşıldı ({len(messages)} >= {self.trigger_message_count})"

        token_estimate = sum(len(m.get('content', '')) // 2 for m in messages)
        if token_estimate >= self.trigger_token_count:
            return True, f"Token sayısı limiti aşıldı (~{token_estimate} >= {self.trigger_token_count})"

        return False, "Limit aşılmadı"

    def _get_session_messages(self, session_id: str) -> List[Dict]:
        """Oturum mesajlarını memory'den al"""
        if self.memory is None:
            return []
        session = self.memory.get_session(session_id)
        if session is None:
            return []
        return session.get('messages', [])

    def auto_summarize_if_needed(self, session_id: str) -> Optional[Summary]:
        """Gerekirse otomatik özetleme yap"""
        should, reason = self.should_summarize(session_id)
        if not should:
            return None

        logger.info(f"Otomatik özetleme tetiklendi: {reason}")
        messages = self._get_session_messages(session_id)
        if not messages:
            return None

        return self.summarize(messages, session_id=session_id)

    def replace_old_with_summary(self, session_id: str, keep_recent: int = 5):
        """
        Eski mesajları özetleriyle değiştir (bağlam yönetimi)
        - keep_recent: korunacak son mesaj sayısı
        """
        if self.memory is None:
            return False

        session = self.memory.get_session(session_id)
        if not session:
            return False

        messages = session.get('messages', [])
        if len(messages) <= keep_recent + 3:
            return False

        old_messages = messages[:-keep_recent]
        recent_messages = messages[-keep_recent:]

        summary = self.summarize(old_messages, session_id=session_id)

        summarizer_msg = {
            'id': f"summary_{summary.id}",
            'role': 'system',
            'content': (
                "【ÖZET】Aşağıdaki eski konuşmanın yerini almıştır:\n"
                f"{summary.summary_text}\n\n"
                f"Önemli Noktalar:\n" +
                '\n'.join(f"- {kp}" for kp in summary.key_points[:5]) +
                (f"\n\nAksiyonlar:\n" + '\n'.join(f"- {ai}" for ai in summary.action_items[:3]) if summary.action_items else "")
            ),
            'timestamp': datetime.now().isoformat(),
            'metadata': {'is_summary': True, 'summary_id': summary.id}
        }

        updated_messages = [summarizer_msg] + recent_messages
        session['messages'] = updated_messages

        logger.info(f"Eski mesajlar özetle değiştirildi: {len(old_messages)} mesaj -> 1 özet")
        return True

    def get_session_summaries(self, session_id: str) -> List[Summary]:
        """Oturumun tüm özetlerini getir"""
        return self.summary_store.get_session_summaries(session_id)

    def get_latest_summary(self, session_id: str) -> Optional[Summary]:
        """Son özeti getir"""
        return self.summary_store.get_latest(session_id)

    def get_summary_context(self, session_id: str, max_summaries: int = 3) -> str:
        """AI bağlamı için özet metnini hazırla"""
        summaries = self.get_session_summaries(session_id)
        if not summaries:
            return ""

        summaries = summaries[-max_summaries:]
        parts = []
        for s in summaries:
            created = s.created_at[:19]
            parts.append(f"[{created}] {s.summary_text}")

        return '\n\n'.join(parts)

    def delete_session_data(self, session_id: str) -> bool:
        """Oturum özetlerini temizle"""
        return self.summary_store.delete_session_summaries(session_id)


# Global örnek
_summarizer_instance: Optional[ConversationSummarizer] = None

def get_summarizer(memory=None) -> ConversationSummarizer:
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = ConversationSummarizer(memory=memory)
    return _summarizer_instance
