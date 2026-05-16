"""
GlassesCat - Konuşma Hafızası Modülü (Obsidian Infinite Memory)
Oturum bazlı konuşma geçmişi yönetimi + Obsidian .md senkronizasyonu
Hafıza SINIRSIZDIR - her şey .md dosyalarında saklanır.
"""

import os
import json
import time
import threading
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

try:
    from obsidian_memory import get_obsidian_memory, ObsidianMemory
    OBSIDIAN_AVAILABLE = True
except ImportError:
    OBSIDIAN_AVAILABLE = False

class ConversationMemory:
    """
    Gelişmiş konuşma hafızası sistemi (Obsidian entegre)
    - Oturum bazlı geçmiş
    - Obsidian .md dosyalarında sınırsız kalıcı depolama
    - Bağlam yönetimi
    - Arama ve filtreleme
    """
    
    def __init__(self, storage_dir: str = None, use_obsidian: bool = True):
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'storage'
            )
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.conversations_dir = self.storage_dir / 'conversations'
        self.conversations_dir.mkdir(exist_ok=True)
        
        self.lock = threading.Lock()
        
        self.sessions = {}  # Aktif oturumlar
        self.max_context_messages = 10  # AI'a gönderilecek max mesaj
        self.max_session_messages = 999999  # SINIRSIZ - Obsidian .md dosyalarına yazılır
        
        # Obsidian entegrasyonu
        self.use_obsidian = use_obsidian and OBSIDIAN_AVAILABLE
        self._obsidian = None
        if self.use_obsidian:
            try:
                self._obsidian = get_obsidian_memory()
            except Exception as e:
                print(f"[ObsidianMemory] Yüklenemedi: {e}")
                self.use_obsidian = False
        
    def create_session(self, session_id: str = None) -> str:
        """Yeni oturum oluştur"""
        if session_id is None:
            session_id = f"session_{int(time.time())}_{secrets.token_hex(4)}"
        
        with self.lock:
            self.sessions[session_id] = {
                'id': session_id,
                'created_at': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat(),
                'messages': [],
                'metadata': {}
            }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Oturum bilgilerini getir"""
        with self.lock:
            return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None) -> bool:
        """Mesaj ekle - Aynı anda Obsidian .md dosyasına da kaydeder (sınırsız)"""
        with self.lock:
            if session_id not in self.sessions:
                self.create_session(session_id)
            
            message = {
                'id': f"msg_{int(time.time() * 1000)}",
                'role': role,  # 'user' veya 'assistant'
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            self.sessions[session_id]['messages'].append(message)
            self.sessions[session_id]['last_active'] = datetime.now().isoformat()
            
            # Obsidian'a da kaydet (sınırsız .md depolama)
            if self.use_obsidian and self._obsidian:
                try:
                    self._obsidian.save_conversation(
                        session_id=session_id,
                        messages=[message]
                    )
                except:
                    pass  # Obsidian kaydı başarısız olursa session devam eder
            
            return True
    
    def get_context(self, session_id: str, limit: int = None, include_obsidian_context: bool = True) -> List[Dict]:
        """AI için bağlam getir (Obsidian sınırsız hafıza ile)"""
        if limit is None:
            limit = self.max_context_messages
        
        with self.lock:
            if session_id not in self.sessions:
                context = []
            else:
                messages = self.sessions[session_id]['messages']
                recent = messages[-limit:] if len(messages) > limit else messages
                context = [
                    {"role": m['role'], "content": m['content']} 
                    for m in recent
                ]
            
            # Obsidian'dan zenginleştirilmiş bağlam ekle
            if include_obsidian_context and self.use_obsidian and self._obsidian:
                try:
                    last_user_msg = ""
                    for m in reversed(context):
                        if m['role'] == 'user':
                            last_user_msg = m['content']
                            break
                    
                    obsidian_context = self._obsidian.get_context_for_ai(query=last_user_msg)
                    if obsidian_context:
                        context.insert(0, {
                            "role": "system",
                            "content": f"[OBSIDIAN HAFIZA - Sınırsız Geçmiş Bağlamı]\n{obsidian_context}"
                        })
                except:
                    pass
            
            return context
    
    def get_conversation_summary(self, session_id: str) -> str:
        """Konuşma özeti oluştur"""
        with self.lock:
            if session_id not in self.sessions:
                return "Yeni oturum"
            
            messages = self.sessions[session_id]['messages']
            if not messages:
                return "Boş oturum"
            
            # İlk ve son mesajları al
            first = messages[0]['content'][:50]
            last = messages[-1]['content'][:50]
            count = len(messages)
            
            return f"{count} mesaj | İlk: {first}... | Son: {last}..."
    
    def search_messages(self, session_id: str, query: str) -> List[Dict]:
        """Mesajlarda ara"""
        results = []
        query_lower = query.lower()
        
        with self.lock:
            if session_id not in self.sessions:
                return results
            
            for msg in self.sessions[session_id]['messages']:
                if query_lower in msg['content'].lower():
                    results.append(msg)
        
        return results
    
    def delete_session(self, session_id: str) -> bool:
        """Oturumu sil"""
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
            return False
    
    def save_session_to_disk(self, session_id: str) -> str:
        """Oturumu diske kaydet (JSON + Obsidian .md)"""
        with self.lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            filename = f"{session_id}.json"
            filepath = self.conversations_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
            
            # Obsidian'a tüm konuşmayı kaydet (sınırsız)
            if self.use_obsidian and self._obsidian:
                try:
                    self._obsidian.save_conversation(
                        session_id=session_id,
                        messages=session.get('messages', [])
                    )
                except:
                    pass
            
            return str(filepath)
    
    def load_session_from_disk(self, session_id: str) -> bool:
        """Oturumu diskten yükle"""
        filepath = self.conversations_dir / f"{session_id}.json"
        
        if not filepath.exists():
            return False
        
        with self.lock:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                self.sessions[session_id] = session
                return True
            except:
                return False
    
    def list_sessions(self) -> List[Dict]:
        """Tüm oturumları listele"""
        sessions_list = []
        
        with self.lock:
            for sid, session in self.sessions.items():
                sessions_list.append({
                    'id': sid,
                    'created_at': session['created_at'],
                    'last_active': session['last_active'],
                    'message_count': len(session['messages']),
                    'summary': self.get_conversation_summary(sid)
                })
        
        return sorted(sessions_list, key=lambda x: x['last_active'], reverse=True)
    
    def clear_session(self, session_id: str) -> bool:
        """Oturum mesajlarını temizle"""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['messages'] = []
                return True
            return False
    
    def recall_infinite(self, query: str, max_results: int = 10) -> List[Dict]:
        """Tüm Obsidian hafızasında sınırsız arama yap"""
        if self.use_obsidian and self._obsidian:
            return self._obsidian.recall(query, max_results)
        
        # Obsidian yoksa session içinde ara
        results = []
        for sid, session in self.sessions.items():
            for msg in session.get('messages', []):
                if query.lower() in msg.get('content', '').lower():
                    results.append({
                        'session_id': sid,
                        'role': msg.get('role'),
                        'content': msg.get('content')[:300],
                        'timestamp': msg.get('timestamp')
                    })
                    if len(results) >= max_results:
                        return results
        return results
    
    def get_obsidian_context(self, query: str = None) -> str:
        """AI bağlamı için Obsidian hafızasından zenginleştirilmiş içerik al"""
        if self.use_obsidian and self._obsidian:
            return self._obsidian.get_context_for_ai(query=query)
        return ""
    
    def get_obsidian_stats(self) -> Dict:
        """Obsidian hafıza istatistiklerini al"""
        if self.use_obsidian and self._obsidian:
            return {
                'total_files': self._obsidian.get_memory_count(),
                'total_size': self._obsidian.get_total_size()
            }
        return {'total_files': 0, 'total_size': '0 B'}
    
    def save_knowledge_to_obsidian(self, title: str, content: str, category: str = 'general', tags: List[str] = None):
        """Obsidian bilgi tabanına bilgi kaydet"""
        if self.use_obsidian and self._obsidian:
            self._obsidian.save_knowledge(title, content, category, tags)

    def export_conversation(self, session_id: str, format: str = 'json') -> Dict:
        """Konuşmayı dışa aktar"""
        with self.lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            if format == 'json':
                return session
            elif format == 'text':
                lines = []
                for msg in session['messages']:
                    role = "Kullanıcı" if msg['role'] == 'user' else "GlassesCat"
                    lines.append(f"[{msg['timestamp']}] {role}: {msg['content']}")
                return {'text': '\n\n'.join(lines)}
            elif format == 'markdown':
                md = f"# Konuşma - {session['created_at']}\n\n"
                for msg in session['messages']:
                    role = "**Kullanıcı**" if msg['role'] == 'user' else "**GlassesCat**"
                    md += f"{role}: {msg['content']}\n\n"
                return {'markdown': md}
            
            return session


import secrets

# Global instance
_memory_instance = None

def get_memory() -> ConversationMemory:
    """Global memory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ConversationMemory()
    return _memory_instance
