"""
Glassescat-AI Engine v1.0
Berkay Software - Lead Engineer AI
Otomatik Hata Tespiti ve Düzeltme Sistemi
Düşünce Akışı Entegrasyonlu
"""

import subprocess
import sys
import os
import json
import traceback
import re
from datetime import datetime
from typing import Dict, List, Optional, Callable

# Glassescat-AI Düşünce Akışı Sistemi
NIKO_THOUGHTS = []

def glassescat_thought(message: str, category: str = "SYSTEM"):
    """Glassescat-AI düşünce logu ekle"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    thought_entry = {
        "timestamp": timestamp,
        "glassescat-ai": True,
        "category": category,
        "message": message
    }
    NIKO_THOUGHTS.append(thought_entry)
    print(f"[{timestamp}] [Glassescat-AI/{category}]: {message}")
    return thought_entry

def get_glassescat_thoughts(limit: int = 10) -> List[Dict]:
    """Son N düşünceyi getir"""
    return NIKO_THOUGHTS[-limit:] if NIKO_THOUGHTS else []

def clear_glassescat_thoughts():
    """Düşünce loglarını temizle"""
    NIKO_THOUGHTS.clear()

# Error-Fix Mekanizması
class ErrorFixEngine:
    """
    Glassescat-AI Otomatik Hata Düzeltme Motoru
    Model Router ile entegre çalışır
    """
    
    def __init__(self, model_router_available: bool = True):
        self.model_router_available = model_router_available
        self.fix_attempts = 0
        self.max_attempts = 3
        glassescat_thought("Error-Fix Engine başlatıldı", "ERROR-FIX")
    
    def analyze_error(self, error_msg: str, error_trace: str, context: str = "") -> Dict:
        """
        Hatayı analiz et ve çözüm öner
        Model Router entegrasyonlu
        """
        glassescat_thought(f"Hata analizi başlatılıyor... Hata: {error_msg[:60]}", "ERROR-FIX")
        
        analysis = {
            "error_type": "UNKNOWN",
            "error_message": error_msg,
            "error_trace": error_trace,
            "root_cause": "",
            "solution": "",
            "auto_fixable": False,
            "fix_code": None,
            "requires_manual": False
        }
        
        # Hata deseni tanıma
        if "ModuleNotFoundError" in error_msg or "No module named" in error_msg:
            analysis["error_type"] = "MISSING_MODULE"
            module_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", error_msg)
            if module_match:
                missing_module = module_match.group(1)
                analysis["root_cause"] = f"Eksik modül: {missing_module}"
                analysis["solution"] = f"pip install {missing_module}"
                analysis["auto_fixable"] = True
                analysis["fix_code"] = f"pip install {missing_module}"
                glassescat_thought(f"Eksik modül tespit edildi: {missing_module}", "ERROR-FIX")
        
        elif "ImportError" in error_msg:
            analysis["error_type"] = "IMPORT_ERROR"
            analysis["root_cause"] = "Modül import hatası - bağımlılık eksik"
            analysis["solution"] = "Gerekli kütüphaneleri yükle"
            analysis["auto_fixable"] = True
            analysis["fix_code"] = "pip install pygame numpy"
            glassescat_thought("Import hatası tespit edildi - bağımlılık sorunu", "ERROR-FIX")
        
        elif "SyntaxError" in error_msg:
            analysis["error_type"] = "SYNTAX_ERROR"
            line_match = re.search(r"line (\d+)", error_msg)
            if line_match:
                line_no = line_match.group(1)
                analysis["root_cause"] = f"Sözdizim hatası - Satır {line_no}"
            else:
                analysis["root_cause"] = "Python sözdizim hatası"
            analysis["solution"] = "Kodu gözden geçir ve düzelt"
            analysis["auto_fixable"] = False
            analysis["requires_manual"] = True
            glassescat_thought("SyntaxError tespit edildi - manuel müdahale gerekli", "ERROR-FIX")
        
        elif "IndentationError" in error_msg:
            analysis["error_type"] = "INDENTATION_ERROR"
            analysis["root_cause"] = "Boşluk/indent hatası"
            analysis["solution"] = "Kod indentasyonunu düzelt"
            analysis["auto_fixable"] = False
            analysis["requires_manual"] = True
            glassescat_thought("IndentationError - manuel düzeltme gerekli", "ERROR-FIX")
        
        elif "AttributeError" in error_msg:
            analysis["error_type"] = "ATTRIBUTE_ERROR"
            attr_match = re.search(r"'([^']+)' object has no attribute '([^']+)'", error_msg)
            if attr_match:
                obj_type, attr_name = attr_match.groups()
                analysis["root_cause"] = f"{obj_type} nesnesinde '{attr_name}' özelliği yok"
                analysis["solution"] = f"Nesne tipini kontrol et veya '{attr_name}' kullanma"
            else:
                analysis["root_cause"] = "Nesne özelliği hatası"
                analysis["solution"] = "Kodu gözden geçir"
            analysis["auto_fixable"] = False
            analysis["requires_manual"] = True
            glassescat_thought("AttributeError - kod mantığı hatası", "ERROR-FIX")
        
        elif "TypeError" in error_msg:
            analysis["error_type"] = "TYPE_ERROR"
            analysis["root_cause"] = "Veri tipi uyuşmazlığı"
            analysis["solution"] = "Değişken tiplerini kontrol et ve dönüştür"
            analysis["auto_fixable"] = False
            analysis["requires_manual"] = True
            glassescat_thought("TypeError - veri tipi sorunu", "ERROR-FIX")
        
        elif "FileNotFoundError" in error_msg:
            analysis["error_type"] = "FILE_NOT_FOUND"
            file_match = re.search(r"No such file or directory: ['\"]([^'\"]+)['\"]", error_msg)
            if file_match:
                missing_file = file_match.group(1)
                analysis["root_cause"] = f"Dosya bulunamadı: {missing_file}"
                analysis["solution"] = f"Dosya yolunu kontrol et veya oluştur: {missing_file}"
            else:
                analysis["root_cause"] = "Dosya bulunamadı"
                analysis["solution"] = "Dosya yolunu kontrol et"
            analysis["auto_fixable"] = False
            analysis["requires_manual"] = True
            glassescat_thought("FileNotFoundError - kaynak dosya eksik", "ERROR-FIX")
        
        elif "pygame" in error_msg.lower():
            analysis["error_type"] = "PYGAME_ERROR"
            analysis["root_cause"] = "Pygame spesifik hata"
            analysis["solution"] = "Pygame kurulumunu ve kullanımını kontrol et"
            analysis["auto_fixable"] = True
            analysis["fix_code"] = "pip install pygame --upgrade"
            glassescat_thought("Pygame hatası - kütüphane sorunu", "ERROR-FIX")
        
        else:
            analysis["root_cause"] = "Bilinmeyen hata tipi"
            analysis["solution"] = "Hata mesajını incele ve manuel düzelt"
            analysis["requires_manual"] = True
            glassescat_thought(f"Tanımlanmamış hata tipi: {error_msg[:50]}", "ERROR-FIX")
        
        return analysis
    
    def attempt_fix(self, analysis: Dict, project_dir: str = ".") -> Dict:
        """
        Otomatik düzeltme dene
        """
        result = {
            "success": False,
            "action_taken": "",
            "output": "",
            "error": ""
        }
        
        if not analysis["auto_fixable"]:
            glassescat_thought("Hata otomatik düzeltilemez - manuel müdahale gerekli", "ERROR-FIX")
            result["action_taken"] = "MANUAL_REQUIRED"
            return result
        
        if analysis["error_type"] == "MISSING_MODULE" or analysis["error_type"] == "IMPORT_ERROR":
            fix_cmd = analysis.get("fix_code", "")
            if fix_cmd:
                glassescat_thought(f"Otomatik düzeltme deneniyor: {fix_cmd}", "ERROR-FIX")
                try:
                    # pip install komutunu çalıştır
                    result_process = subprocess.run(
                        fix_cmd.split(),
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if result_process.returncode == 0:
                        result["success"] = True
                        result["action_taken"] = f"INSTALLED: {fix_cmd}"
                        result["output"] = result_process.stdout
                        glassescat_thought("Bağımlılık başarıyla yüklendi!", "ERROR-FIX")
                    else:
                        result["error"] = result_process.stderr
                        glassescat_thought(f"Yükleme hatası: {result_process.stderr[:100]}", "ERROR-FIX")
                except Exception as e:
                    result["error"] = str(e)
                    glassescat_thought(f"Düzeltme işlemi başarısız: {e}", "ERROR-FIX")
        
        elif analysis["error_type"] == "PYGAME_ERROR":
            glassescat_thought("Pygame kütüphanesi yeniden yükleniyor...", "ERROR-FIX")
            try:
                result_process = subprocess.run(
                    ["pip", "install", "pygame", "--upgrade"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result_process.returncode == 0:
                    result["success"] = True
                    result["action_taken"] = "PYGAME_REINSTALLED"
                    glassescat_thought("Pygame başarıyla güncellendi!", "ERROR-FIX")
                else:
                    result["error"] = result_process.stderr
            except Exception as e:
                result["error"] = str(e)
        
        return result
    
    def run_with_auto_fix(self, cmd: List[str], project_dir: str = ".", 
                          max_retries: int = 3) -> Dict:
        """
        Komutu çalıştır, hata varsa otomatik düzelt ve tekrar dene
        """
        self.fix_attempts = 0
        
        while self.fix_attempts < max_retries:
            glassescat_thought(f"Deneme {self.fix_attempts + 1}/{max_retries}: {' '.join(cmd)}", "RUN")
            
            try:
                # Komutu çalıştır
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=project_dir
                )
                
                if result.returncode == 0:
                    glassescat_thought("Komut başarıyla tamamlandı!", "RUN")
                    return {
                        "success": True,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "attempts": self.fix_attempts + 1,
                        "fixed": False
                    }
                
                # Hata varsa analiz et
                error_msg = result.stderr if result.stderr else "Unknown error"
                error_trace = result.stderr
                
                glassescat_thought(f"Hata tespit edildi: {error_msg[:80]}", "ERROR")
                
                # Hatayı analiz et
                analysis = self.analyze_error(error_msg, error_trace)
                
                if analysis["auto_fixable"] and self.fix_attempts < max_retries - 1:
                    glassescat_thought("Otomatik düzeltme uygulanıyor...", "ERROR-FIX")
                    fix_result = self.attempt_fix(analysis, project_dir)
                    
                    if fix_result["success"]:
                        glassescat_thought("Düzeltme uygulandı, tekrar deneniyor...", "ERROR-FIX")
                        self.fix_attempts += 1
                        continue  # Tekrar dene
                    else:
                        glassescat_thought("Otomatik düzeltme başarısız", "ERROR-FIX")
                        break
                else:
                    glassescat_thought("Hata otomatik düzeltilemez veya deneme limiti doldu", "ERROR-FIX")
                    break
                    
            except subprocess.TimeoutExpired:
                glassescat_thought("Komut zaman aşımına uğradı (300s)", "ERROR")
                return {
                    "success": False,
                    "error": "Timeout",
                    "attempts": self.fix_attempts + 1
                }
            except Exception as e:
                glassescat_thought(f"Çalıştırma hatası: {str(e)}", "ERROR")
                return {
                    "success": False,
                    "error": str(e),
                    "attempts": self.fix_attempts + 1
                }
        
        # Tüm denemeler başarısız
        return {
            "success": False,
            "error": error_msg if 'error_msg' in locals() else "Max retries exceeded",
            "analysis": analysis if 'analysis' in locals() else None,
            "attempts": self.fix_attempts + 1,
            "fixed": False
        }

# Glassescat-AI Sistem Entegrasyonu
class GlassescatAI:
    """
    Glassescat-AI Ana Sistemi
    Berkay Software Lead Engineer AI
    """
    
    def __init__(self):
        glassescat_thought("Glassescat-AI sistemi başlatılıyor...", "SYSTEM")
        self.error_fix_engine = ErrorFixEngine(model_router_available=True)
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        glassescat_thought(f"Proje dizini: {self.project_dir}", "SYSTEM")
        glassescat_thought("Glassescat-AI hazır! Görev bekleniyor...", "SYSTEM")
    
    def develop_game(self, game_name: str, test_in_venv: bool = True) -> Dict:
        """
        2D oyun geliştirme döngüsü
        Hata olursa otomatik düzeltme ile
        """
        glassescat_thought(f"'{game_name}' oyunu geliştirme başlatılıyor...", "GAME-DEV")
        
        # Oyun dosyası yolu
        game_file = os.path.join(self.project_dir, f"{game_name}.py")
        
        # Test komutu
        if test_in_venv:
            venv_python = os.path.join(self.project_dir, ".venv", "Scripts", "python.exe")
            if os.path.exists(venv_python):
                cmd = [venv_python, game_file]
                glassescat_thought(".venv Python kullanılacak", "GAME-DEV")
            else:
                cmd = [sys.executable, game_file]
                glassescat_thought("Sistem Python kullanılacak (.venv bulunamadı)", "GAME-DEV")
        else:
            cmd = [sys.executable, game_file]
        
        # Error-Fix ile çalıştır
        result = self.error_fix_engine.run_with_auto_fix(cmd, self.project_dir)
        
        if result["success"]:
            glassescat_thought("Oyun başarıyla geliştirildi ve test edildi!", "GAME-DEV")
        else:
            glassescat_thought("Oyun testi başarısız - manuel müdahale gerekli", "GAME-DEV")
        
        return {
            "game": game_name,
            "success": result["success"],
            "result": result,
            "niko_thoughts": get_glassescat_thoughts()
        }
    
    def get_status(self) -> Dict:
        """Glassescat-AI durum raporu"""
        return {
            "name": "Glassescat-AI",
            "role": "Berkay Software Lead Engineer",
            "version": "1.0",
            "error_fix": "Active",
            "thoughts_count": len(NIKO_THOUGHTS),
            "project_dir": self.project_dir
        }

# Singleton instance
_glassescat_ai = None

def get_glassescat_ai() -> GlassescatAI:
    """Glassescat-AI singleton instance"""
    global _glassescat_ai
    if _glassescat_ai is None:
        _glassescat_ai = GlassescatAI()
    return _glassescat_ai

if __name__ == "__main__":
    # Test
    ai = get_glassescat_ai()
    print("\n" + "="*60)
    print("Glassescat-AI Engine Test")
    print("="*60)
    print(json.dumps(ai.get_status(), indent=2, ensure_ascii=False))
    print("\n[Glassescat-AI]: Sistem hazır, görev bekleniyor...")
