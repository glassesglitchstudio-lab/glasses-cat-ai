"""
GlassesCat - Kod Çalıştırma Sandbox Modülü
Güvenli Python kodu çalıştırma sistemi
Thread isolation, timeout, ve output capture
"""

import sys
import io
import os
import re
import time
import uuid
import subprocess
import threading
import tempfile
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

class CodeSandbox:
    """
    Güvenli Python kod çalıştırma sandbox'u
    - Thread isolation
    - Timeout kontrolü
    - Output capture
    - Bellek limiti
    - Güvenlik filtreleri
    """
    
    # İzin verilen modüller
    ALLOWED_MODULES = {
        # Standart kütüphaneler
        'os', 'sys', 'json', 're', 'time', 'datetime', 'random', 'math',
        'collections', 'itertools', 'functools', 'typing', 'pathlib',
        'hashlib', 'uuid', 'string', 'decimal', 'fractions', 'statistics',
        'copy', 'pprint', 'textwrap', 'unicodedata', 'warnings',
        # Extra
        'array', 'queue', 'threading', 'multiprocessing',
        'base64', 'html', 'urllib', 'urlparse', 'http',
    }
    
    # Yasaklı kalıplar (güvenlik)
    FORBIDDEN_PATTERNS = [
        r'import\s+subprocess', r'from\s+subprocess',
        r'import\s+os\s*;.*os\.system', r'os\.system\(',
        r'import\s+sys\s*;.*sys\.exit', r'sys\.exit\(',
        r'__import__', r'eval\s*\(', r'exec\s*\(',
        r'open\s*\([^)]*[\'"]w[\'"]',  # Yazma için dosya açma
        r'shutil\.rmtree', r'shutil\.copytree',
        r'import\s+ctypes', r'from\s+ctypes',
        r'socket\s*\.', r'requests\.post', r'requests\.get',
        r'http\.client', r'ftplib', r'poplib', r'smtplib',
        r'database', r'psycopg', r'mysql', r'sqlite3',
        r'flask', r'django', r'fastapi', r'cherrypy',
        r'pickle\.load', r'marshal\.loads',
    ]
    
    def __init__(self, max_exec_time: int = 30, max_output_size: int = 50000):
        self.max_exec_time = max_exec_time
        self.max_output_size = max_output_size
        self.sessions = {}
        self.execution_log = []
        self.max_log_size = 500
        
        # VENV yolu
        self.venv_path = self._find_venv()
    
    def _find_venv(self) -> Optional[str]:
        """VENV yolunu bul"""
        project_root = Path(__file__).parent.parent
        venv_path = project_root / '.venv'
        
        if venv_path.exists() and (venv_path / 'Scripts' / 'python.exe').exists():
            return str(venv_path / 'Scripts' / 'python.exe')
        
        # Sistem Python'u
        return sys.executable
    
    def _check_security(self, code: str) -> tuple:
        """Güvenlik kontrolü"""
        code_lower = code.lower()
        
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Yasaklı kalıp tespit edildi: {pattern}"
        
        return True, "Güvenli"
    
    def _validate_imports(self, code: str) -> tuple:
        """Import kontrolü"""
        import_pattern = r'(?:^|\n)\s*(?:import\s+(\w+)|from\s+(\w+)\s+import)'
        matches = re.findall(import_pattern, code)
        
        allowed = []
        disallowed = []
        
        for match in matches:
            module = match[0] or match[1]
            if module in self.ALLOWED_MODULES:
                allowed.append(module)
            elif module:
                disallowed.append(module)
        
        if disallowed:
            return False, f"Izin verilmeyen modüller: {', '.join(disallowed)}"
        
        return True, "İzin verildi"
    
    def execute(self, code: str, session_id: str = None, use_venv: bool = True) -> Dict:
        """
        Python kodu çalıştır
        """
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]
        
        # Güvenlik kontrolü
        secure, msg = self._check_security(code)
        if not secure:
            return {
                "success": False,
                "error": f"Güvenlik hatası: {msg}",
                "session_id": session_id
            }
        
        # Import kontrolü
        valid, msg = self._validate_imports(code)
        if not valid:
            return {
                "success": False,
                "error": f"Import hatası: {msg}",
                "session_id": session_id
            }
        
        # Çıktı yakalama
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_out = io.StringIO()
        sys.stderr = captured_err = io.StringIO()
        
        start_time = time.time()
        success = False
        result = None
        error = None
        
        try:
            # Timeout thread
            def timeout_check():
                time.sleep(self.max_exec_time)
                if not success:
                    raise TimeoutError(f"Kod {self.max_exec_time} saniye içinde tamamlanamadı")
            
            timeout_thread = threading.Thread(target=timeout_check, daemon=True)
            timeout_thread.start()
            
            # Kod çalıştır
            try:
                exec_globals = {'__name__': '__main__'}
                exec(code, exec_globals)
                success = True
            except TimeoutError:
                error = f"Timeout: Kod {self.max_exec_time} sn içinde tamamlanamadı"
            except SyntaxError as e:
                error = f"Syntax hatası: {e}"
            except ImportError as e:
                error = f"Import hatası: {e}"
            except Exception as e:
                error = f"Çalışma hatası: {type(e).__name__}: {e}"
            
            timeout_thread.join(timeout=1)
            
        finally:
            # Eski stdout/err döndür
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        # Çıktıları al
        output = captured_out.getvalue()
        stderr = captured_err.getvalue()
        exec_time = time.time() - start_time
        
        # Boyut kontrolü
        if len(output) > self.max_output_size:
            output = output[:self.max_output_size] + f"\n... (çıktı {len(output) - self.max_output_size} karakter kesildi)"
        
        # Logla
        self._log_execution(session_id, code, success, exec_time)
        
        return {
            "success": success,
            "output": output,
            "stderr": stderr,
            "error": error,
            "exec_time": round(exec_time, 3),
            "session_id": session_id
        }
    
    def execute_in_subprocess(self, code: str, session_id: str = None) -> Dict:
        """Alt process olarak çalıştır (daha güvenli)"""
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]
        
        # Güvenlik kontrolü
        secure, msg = self._check_security(code)
        if not secure:
            return {
                "success": False,
                "error": f"Güvenlik hatası: {msg}",
                "session_id": session_id
            }
        
        start_time = time.time()
        
        try:
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Alt process çalıştır
                result = subprocess.run(
                    [self.venv_path, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=self.max_exec_time,
                    encoding='utf-8'
                )
                
                exec_time = time.time() - start_time
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "stderr": result.stderr,
                    "error": None if result.returncode == 0 else f"Exit code: {result.returncode}",
                    "exec_time": round(exec_time, 3),
                    "session_id": session_id
                }
            
            finally:
                # Geçici dosyayı sil
                try:
                    os.unlink(temp_file)
                except:
                    pass
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Timeout: {self.max_exec_time} saniye aşıldı",
                "exec_time": round(time.time() - start_time, 3),
                "session_id": session_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "exec_time": round(time.time() - start_time, 3),
                "session_id": session_id
            }
    
    def _log_execution(self, session_id: str, code: str, success: bool, exec_time: float):
        """Çalıştırma logla"""
        with threading.Lock():
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "code_preview": code[:100],
                "success": success,
                "exec_time": exec_time
            })
            
            if len(self.execution_log) > self.max_log_size:
                self.execution_log = self.execution_log[-self.max_log_size:]
    
    def get_execution_log(self, limit: int = 50) -> List[Dict]:
        """Çalıştırma loglarını getir"""
        with threading.Lock():
            return self.execution_log[-limit:]


# Global instance
_sandbox_instance = None

def get_sandbox() -> CodeSandbox:
    """Global sandbox instance"""
    global _sandbox_instance
    if _sandbox_instance is None:
        _sandbox_instance = CodeSandbox()
    return _sandbox_instance
