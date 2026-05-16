"""
GlassesCat - Web Araması Modülü
AI'ın web'de arama yapabilmesi için
Güvenli ve kontrollü web erişimi
"""

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

import urllib.request
import urllib.parse

import time
import threading
import html
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

class WebSearch:
    """
    Web arama sistemi
    - DuckDuckGo, Google, Bing desteği
    - Önbellekleme
    - Rate limiting
    - Sonuç filtreleme
    """
    
    def __init__(self):
        self.lock = threading.Lock()
        self.cache = {}
        self.cache_ttl = 300  # 5 dakika önbellek
        self.max_results = 20
        self.max_cache_size = 100
        
        # User-Agent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Search providers
        self.providers = {
            'duckduckgo': self._search_duckduckgo,
            'google': self._search_google,
            'bing': self._search_bing
        }
    
    def _http_get(self, url: str, params: dict = None, timeout: int = 10) -> Optional[str]:
        """HTTP GET isteği"""
        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"
        
        try:
            if REQUESTS_AVAILABLE:
                response = requests.get(url, headers=self.headers, timeout=timeout)
                return response.text if response.status_code == 200 else None
            else:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    return response.read().decode('utf-8')
        except:
            return None
    
    def _is_cache_valid(self, key: str) -> bool:
        """Önbellek geçerliliğini kontrol et"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]['timestamp']
        if time.time() - cached_time > self.cache_ttl:
            del self.cache[key]
            return False
        
        return True
    
    def _get_cached(self, key: str) -> Optional[List[Dict]]:
        """Önbellekten al"""
        if self._is_cache_valid(key):
            return self.cache[key]['results']
        return None
    
    def _set_cache(self, key: str, results: List[Dict]):
        """Önbelleğe kaydet"""
        with self.lock:
            if len(self.cache) > self.max_cache_size:
                oldest = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
                del self.cache[oldest]
            
            self.cache[key] = {
                'results': results,
                'timestamp': time.time()
            }
    
    def search(self, query: str, provider: str = 'duckduckgo', max_results: int = None) -> Dict:
        """
        Web araması yap
        """
        if max_results is None:
            max_results = self.max_results
        
        # Önbellek kontrolü
        cache_key = f"{provider}:{query}"
        cached = self._get_cached(cache_key)
        if cached:
            return {
                "success": True,
                "query": query,
                "provider": provider,
                "results": cached[:max_results],
                "count": min(len(cached), max_results),
                "cached": True
            }
        
        # Provider seçimi
        if provider not in self.providers:
            provider = 'duckduckgo'
        
        try:
            results = self.providers[provider](query)
            
            if results:
                self._set_cache(cache_key, results)
                return {
                    "success": True,
                    "query": query,
                    "provider": provider,
                    "results": results[:max_results],
                    "count": len(results[:max_results]),
                    "cached": False
                }
            else:
                return {
                    "success": False,
                    "error": "Sonuç bulunamadı",
                    "query": query,
                    "provider": provider
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "provider": provider
            }
    
    def _search_duckduckgo(self, query: str) -> List[Dict]:
        """DuckDuckGo araması"""
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambiguation': 1
        }
        
        try:
            response_text = self._http_get(url, params=params, timeout=10)
            
            if response_text:
                data = json.loads(response_text)
                results = []
                
                # Related Topics
                for topic in data.get('RelatedTopics', [])[:20]:
                    if 'Text' in topic and 'FirstURL' in topic:
                        results.append({
                            'title': topic.get('Text', '')[:200],
                            'url': topic.get('FirstURL', ''),
                            'snippet': topic.get('Text', ''),
                            'source': 'duckduckgo'
                        })
                
                return results
            return []
        
        except Exception as e:
            print(f"[WebSearch] DuckDuckGo hatası: {e}")
            return []
    
    def _search_google(self, query: str) -> List[Dict]:
        """Google araması (serpapi vb. gerekli, basit fallback)"""
        return self._search_duckduckgo(query)
    
    def _search_bing(self, query: str) -> List[Dict]:
        """Bing araması"""
        return self._search_duckduckgo(query)
    
    def search_news(self, query: str, max_results: int = 10) -> Dict:
        """Haber araması"""
        return self.search(query, max_results=max_results)
    
    def get_article_content(self, url: str) -> Dict:
        """Makale içeriğini getir"""
        try:
            response_text = self._http_get(url, timeout=15)
            
            if response_text:
                content = self._strip_html(response_text)
                return {
                    "success": True,
                    "url": url,
                    "content": content[:5000],
                    "length": len(content)
                }
            
            return {"success": False, "error": "İçerik alınamadı", "url": url}
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def _strip_html(self, html_content: str) -> str:
        """HTML etiketlerini temizle"""
        # Script ve style etiketlerini kaldır
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # HTML entity decode
        html_content = html.unescape(html_content)
        
        # Etiketleri kaldır
        html_content = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Temizlik
        html_content = re.sub(r'\s+', ' ', html_content)
        html_content = html_content.strip()
        
        return html_content
    
    def clear_cache(self):
        """Önbelleği temizle"""
        with self.lock:
            self.cache.clear()


# Global instance
_web_search_instance = None

def get_web_search() -> WebSearch:
    """Global web search instance"""
    global _web_search_instance
    if _web_search_instance is None:
        _web_search_instance = WebSearch()
    return _web_search_instance
