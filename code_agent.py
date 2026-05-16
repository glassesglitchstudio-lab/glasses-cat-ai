"""
GlassesCat - Code Agent Module
Akıllı kod analiz ve üretim asistanı
ModelRouter ile entegre çalışır
"""

import os
import re
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

import requests


OLLAMA_URL = "http://localhost:11434/api/chat"


class CodeAgent:
    """
    Kod analiz ve üretim asistanı.
    LLM destekli akıllı kod işlemleri.
    """
    
    def __init__(self, ollama_url: str = None):
        self.ollama_url = ollama_url or OLLAMA_URL
        self.models = {
            "chat": "llama3.1:latest",
            "coding": "qwen2.5-coder:14b",
            "analysis": "deepseek-r1:8b"
        }
        self.history = []
        self.max_history = 100
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _chat_with_model(
        self,
        model: str,
        system_prompt: str,
        user_message: str,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """Belirtilen model ile sohbet."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.0}
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=timeout)
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result["message"]["content"],
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ═══════════════════════════════════════════════════════════════
    # 🔍 KOD ANALİZ FONKSİYONLARI
    # ═══════════════════════════════════════════════════════════════
    
    def analyze_code(self, code: str, language: str = "auto") -> Dict[str, Any]:
        """
        Kod analiz et.
        Hataları, performansı ve güvenliği kontrol eder.
        """
        system_prompt = (
            "Sen bir kod analiz asistanısın. Türkçe konuş. "
            "Verilen kodu analiz et ve şunları belirt:\n"
            "1. Programlama dili\n"
            "2. Kodun amacı\n"
            "3. Potansiyel hatalar veya buglar\n"
            "4. Performans iyileştirmeleri\n"
            "5. Güvenlik açıkları\n"
            "6. Genel kod kalitesi puanı (1-10)\n"
            "Detaylı ve açık bir analiz yap."
        )
        
        prompt = f"Dil: {language}\n\nKod:\n```{language}\n{code}\n```"
        
        result = self._chat_with_model(
            self.models["analysis"],
            system_prompt,
            prompt,
            timeout=90
        )
        
        if result["success"]:
            self.history.append({
                "type": "analyze",
                "timestamp": self._get_timestamp(),
                "language": language,
                "success": True
            })
        
        return result
    
    def find_errors(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Koddaki hataları bul ve düzelt."""
        system_prompt = (
            "Sen bir kod hata ayıklama asistanısın. Türkçe konuş. "
            "Verilen kodda hata var. Şunları yap:\n"
            "1. Hataları tespit et\n"
            "2. Her hata için satır numarası belirt\n"
            "3. Hata nedenini açıkla\n"
            "4. Düzeltilmiş kodu ver\n"
            "5. Düzeltme açıklaması yap\n"
            "Kodu ``` ile sarılmış olarak ver."
        )
        
        prompt = f"Kod:\n```{language}\n{code}\n```"
        
        return self._chat_with_model(
            self.models["coding"],
            system_prompt,
            prompt
        )
    
    def explain_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Kodu açıkla."""
        system_prompt = (
            "Sen bir kod açıklama asistanısın. Türkçe konuş. "
            "Verilen kodu satır satır veya blok blok açıkla. "
            "Ne yaptığını, neden yapıldığını anlat. "
            "Kodun yapısını ve bileşenlerini göster. "
            "Anlaşılır ve detaylı ol."
        )
        
        prompt = f"Kod:\n```{language}\n{code}\n```"
        
        return self._chat_with_model(
            self.models["chat"],
            system_prompt,
            prompt
        )
    
    # ═══════════════════════════════════════════════════════════════
    # ✍️ KOD ÜRETİM FONKSİYONLARI
    # ═══════════════════════════════════════════════════════════════
    
    def generate_code(
        self,
        description: str,
        language: str = "python",
        framework: str = None
    ) -> Dict[str, Any]:
        """
        Açıklamadan kod üret.
        """
        system_prompt = (
            "Sen bir kod üretim asistanısın. Türkçe konuş. "
            "Verilen açıklamaya göre temiz, çalışır kod yaz. "
            "Kodun açıklamasını da ekle. "
            "Güvenli ve optimize kod yaz. "
            "Kodu ``` ile sarılmış olarak ver."
        )
        
        prompt = f"Açıklama: {description}\n"
        if framework:
            prompt += f"Framework/Kütüphane: {framework}\n"
        prompt += f"Programlama dili: {language}\n\n"
        prompt += "Lütfen çalışır bir kod yaz:"
        
        return self._chat_with_model(
            self.models["coding"],
            system_prompt,
            prompt,
            timeout=120
        )
    
    def refactor_code(
        self,
        code: str,
        language: str = "python",
        style: str = "clean"
    ) -> Dict[str, Any]:
        """
        Kodu yeniden düzenle (refactor).
        Daha temiz ve okunabilir hale getir.
        """
        system_prompt = (
            f"Sen bir kod refactor asistanısın. Türkçe konuş. "
            f"Verilen kodu {style} stiline göre yeniden düzenle. "
            "1. Daha temiz ve okunabilir yap\n"
            "2. Gereksiz tekrarları kaldır\n"
            "3. Fonksiyonları modülerleştir\n"
            "4. Değişken isimlerini iyileştir\n"
            "5. Yorumlar ekle\n"
            "6. Aynı işlevselliği koru\n"
            "Kodu ``` ile sarılmış olarak ver."
        )
        
        prompt = f"Kod:\n```{language}\n{code}\n```"
        
        return self._chat_with_model(
            self.models["coding"],
            system_prompt,
            prompt
        )
    
    def optimize_code(
        self,
        code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Kodu optimize et.
        Performans ve bellek açısından iyileştir.
        """
        system_prompt = (
            "Sen bir kod optimizasyon asistanısın. Türkçe konuş. "
            "Verilen kodu performans açısından optimize et. "
            "1. Yavaş döngüleri iyileştir\n"
            "2. Gereksiz işlemleri kaldır\n"
            "3. Bellek kullanımını optimize et\n"
            "4. Algoritma karmaşıklığını iyileştir\n"
            "5. İssiz işlemleri paralelleştir (mümkünse)\n"
            "Her iyileştirme için açıklama ekle.\n"
            "Optimize edilmiş kodu ``` ile sarılmış olarak ver."
        )
        
        prompt = f"Kod:\n```{language}\n{code}\n```"
        
        return self._chat_with_model(
            self.models["coding"],
            system_prompt,
            prompt
        )
    
    # ═══════════════════════════════════════════════════════════════
    # 🛡️ GÜVENLİK FONKSİYONLARI
    # ═══════════════════════════════════════════════════════════════
    
    def security_audit(
        self,
        code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Kod için güvenlik denetimi yap.
        """
        system_prompt = (
            "Sen bir siber güvenlik uzmanısın. Türkçe konuş. "
            "Verilen kodda güvenlik açıkları ara. Şunları kontrol et:\n"
            "1. SQL Injection\n"
            "2. XSS (Cross-Site Scripting)\n"
            "3. Command Injection\n"
            "4. Authentication/Authorization sorunları\n"
            "5. Sensitive Data Exposure\n"
            "6. CSRF\n"
            "7. Unvalidated Redirects\n"
            "8. File Inclusion\n"
            "9. Hardcoded credentials\n"
            "10. Logging sensitive data\n"
            "Her açık için risk seviyesi (HIGH/MEDIUM/LOW) ve çözüm önerisi ver."
        )
        
        prompt = f"Kod:\n```{language}\n{code}\n```"
        
        return self._chat_with_model(
            self.models["analysis"],
            system_prompt,
            prompt
        )
    
    # ═══════════════════════════════════════════════════════════════
    # 📝 DÖKÜMANASYON FONKSİYONLARI
    # ═══════════════════════════════════════════════════════════════
    
    def document_code(
        self,
        code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Koda dökümanasyon ekle.
        """
        system_prompt = (
            "Sen bir teknik dökümanasyon uzmanısın. Türkçe konuş. "
            "Verilen koda profesyonel dökümanasyon ekle. Şunları ekle:\n"
            "1. Modül/Fonksiyon docstring\n"
            "2. Argüman açıklamaları (Args:)\n"
            "3. Dönüş değeri açıklaması (Returns:)\n"
            "4. Özel durumlar (Raises:)\n"
            "5. Kullanım örneği (Examples:)\n"
            "6. Satır içi yorumlar\n"
            "7. Type hints kontrolü\n"
            "Docstring'leri Google veya Sphinx stiline göre yaz."
        )
        
        prompt = f"Kod:\n```{language}\n{code}\n```"
        
        return self._chat_with_model(
            self.models["coding"],
            system_prompt,
            prompt
        )
    
    def generate_doc(self, project_description: str) -> Dict[str, Any]:
        """
        Proje için README veya döküman üret.
        """
        system_prompt = (
            "Sen bir teknik yazar asistanısın. Türkçe konuş. "
            "Verilen proje açıklamasına göre döküman üret. Şunları ekle:\n"
            "1. Proje başlığı ve açıklaması\n"
            "2. Özellikler listesi\n"
            "3. Kurulum adımları\n"
            "4. Kullanım örnekleri\n"
            "5. API endpointleri (varsa)\n"
            "6. Lisans bilgisi\n"
            "Markdown formatında yaz."
        )
        
        prompt = f"Proje: {project_description}"
        
        return self._chat_with_model(
            self.models["chat"],
            system_prompt,
            prompt
        )
    
    # ═══════════════════════════════════════════════════════════════
    # 🌐 WEB GELİŞTİRME FONKSİYONLARI
    # ═══════════════════════════════════════════════════════════════
    
    def generate_html(
        self,
        description: str,
        css_framework: str = None
    ) -> Dict[str, Any]:
        """HTML/CSS kodu üret."""
        system_prompt = (
            "Sen bir web geliştirme asistanısın. Türkçe konuş. "
            "Verilen açıklamaya göre modern ve responsive HTML/CSS kodu yaz. "
        )
        
        if css_framework:
            system_prompt += f"CSS Framework: {css_framework} kullan.\n"
        
        system_prompt += (
            "1. Semantic HTML kullan\n"
            "2. CSS'i inline veya <style> tag içinde ver\n"
            "3. Responsive tasarım yap\n"
            "4. Modern görünüm sağla\n"
            "Kodu tek bir HTML dosyası olarak ver."
        )
        
        prompt = f"Açıklama: {description}"
        
        return self._chat_with_model(
            self.models["coding"],
            system_prompt,
            prompt
        )
    
    def generate_api(
        self,
        description: str,
        framework: str = "flask"
    ) -> Dict[str, Any]:
        """API endpoint kodu üret."""
        system_prompt = (
            f"Sen bir backend geliştirme asistanısın. Türkçe konuş. "
            f"Verilen açıklamaya göre {framework} API kodu yaz. Şunları ekle:\n"
            "1. Endpoint tanımları (@app.route)\n"
            "2. Request/Response handling\n"
            "3. Error handling\n"
            "4. Input validation\n"
            "5. API dökümanasyonu (docstring)\n"
            "Temiz ve production-ready kod yaz."
        )
        
        prompt = f"Açıklama: {description}"
        
        return self._chat_with_model(
            self.models["coding"],
            system_prompt,
            prompt
        )
    
    # ═══════════════════════════════════════════════════════════════
    # YARDIMCI FONKSİYONLAR
    # ═══════════════════════════════════════════════════════════════
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """İşlem geçmişini getir."""
        return self.history[-limit:]
    
    def clear_history(self):
        """İşlem geçmişini temizle."""
        self.history = []
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Agent'ın yeteneklerini listele."""
        return {
            "name": "GlassesCat Code Agent",
            "version": "1.0",
            "capabilities": [
                "Kod Analizi",
                "Hata Ayıklama",
                "Kod Açıklama",
                "Kod Üretimi",
                "Refactoring",
                "Optimizasyon",
                "Güvenlik Denetimi",
                "Dökümanasyon",
                "HTML/CSS Üretimi",
                "API Geliştirme"
            ],
            "supported_languages": [
                "python", "javascript", "typescript", "html", "css",
                "java", "c++", "c#", "rust", "go", "ruby", "php"
            ],
            "models": self.models
        }


# Global instance
_code_agent = None

def get_code_agent() -> CodeAgent:
    """Global code agent instance."""
    global _code_agent
    if _code_agent is None:
        _code_agent = CodeAgent()
    return _code_agent
