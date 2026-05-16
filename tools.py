
"""
Niko Evrensel Sistem Ajanı - Universal Toolbox
Dosya sistemi, sistem komutları, ortam kurulumu ve daha fazlası
"""

import os
import shutil
import glob
import pathlib
import subprocess
import webbrowser
import json
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax


console = Console()


class UniversalToolbox:
    """Evrensel Araç Kutusu - Tüm sistem işlemleri burada"""
    
    def __init__(self):
        self.console = Console()
        self.dangerous_commands = [
            'rm -rf /', 'format', 'del /s /q', 'rd /s /q',
            'mkfs', 'dd if=', 'chmod 777', 'chown -R'
        ]
    
    def confirm_action(self, message):
        """Kullanıcıdan onay al"""
        self.console.print(f"\n[yellow]⚠️  {message}[/yellow]")
        response = input("[Onay] (y/n): ").strip().lower()
        return response == 'y'
    
    def is_dangerous_command(self, command):
        """Tehlikeli komut kontrolü"""
        command_lower = command.lower()
        return any(danger in command_lower for danger in self.dangerous_commands)
    
    def file_system_panel(self, title, content):
        """Dosya sistemi işlemleri için panel göster"""
        self.console.print(Panel(content, title=f"📁 {title}", border_style="blue"))
    
    def command_panel(self, title, command, output=None):
        """Komut işlemleri için panel göster"""
        content = f"[cyan]Komut:[/cyan] {command}\n"
        if output:
            content += f"\n[green]Çıktı:[/green]\n{output}"
        self.console.print(Panel(content, title=f"⚙️  {title}", border_style="yellow"))
    
    def report_panel(self, title, data):
        """Final rapor paneli"""
        table = Table(title=title)
        table.add_column("Özellik", style="cyan")
        table.add_column("Değer", style="green")
        
        for key, value in data.items():
            table.add_row(str(key), str(value))
        
        self.console.print(Panel(table, title="📊 Final Raporu", border_style="green"))
    
    def find_files(self, pattern, directory="."):
        """Dosya bulma (glob ile)"""
        search_path = os.path.join(directory, pattern)
        files = glob.glob(search_path, recursive=True)
        return files
    
    def copy_file(self, src, dst):
        """Dosya kopyalama"""
        try:
            shutil.copy2(src, dst)
            return {"success": True, "source": src, "destination": dst}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def move_file(self, src, dst):
        """Dosya taşıma"""
        try:
            shutil.move(src, dst)
            return {"success": True, "source": src, "destination": dst}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_file(self, path, confirm=True):
        """Dosya silme"""
        try:
            if confirm:
                if not self.confirm_action(f"{path} dosyasını silmek istediğinize emin misiniz?"):
                    return {"success": False, "error": "İşlem iptal edildi"}
            
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_directory(self, path):
        """Dizin oluşturma"""
        try:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_directory(self, path="."):
        """Dizin içeriğini listeleme"""
        try:
            items = os.listdir(path)
            files = []
            directories = []
            
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    files.append(item)
                else:
                    directories.append(item)
            
            return {
                "success": True,
                "path": path,
                "files": files,
                "directories": directories
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, path):
        """Dosya okuma"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "path": path, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_file(self, path, content):
        """Dosya yazma"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_command(self, command, shell=True, confirm_dangerous=True):
        """Sistem komutu çalıştırma"""
        try:
            if self.is_dangerous_command(command) and confirm_dangerous:
                if not self.confirm_action(f"Bu komut tehlikeli olabilir: {command}\nDevam etmek istediğinize emin misiniz?"):
                    return {"success": False, "error": "İşlem iptal edildi"}
            
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_browser(self, url):
        """Tarayıcıda URL açma"""
        try:
            webbrowser.open(url)
            return {"success": True, "url": url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def detect_project_type(self, directory="."):
        """Proje türünü algıla"""
        if os.path.exists(os.path.join(directory, "package.json")):
            return "node"
        elif os.path.exists(os.path.join(directory, "requirements.txt")) or os.path.exists(os.path.join(directory, "setup.py")):
            return "python"
        elif os.path.exists(os.path.join(directory, "CMakeLists.txt")):
            return "cpp"
        elif os.path.exists(os.path.join(directory, "go.mod")):
            return "go"
        elif any(f.endswith(".csproj") for f in os.listdir(directory)):
            return "dotnet"
        return None
    
    def setup_environment(self, directory="."):
        """Otomatik ortam kurulumu"""
        project_type = self.detect_project_type(directory)
        results = {"project_type": project_type, "steps": []}
        
        try:
            if project_type == "node":
                self.console.print("[cyan]Node.js projesi algılandı, npm install çalıştırılıyor...[/cyan]")
                result = self.run_command("npm install")
                results["steps"].append({"action": "npm install", "result": result})
            
            elif project_type == "python":
                self.console.print("[cyan]Python projesi algılandı, venv oluşturuluyor...[/cyan]")
                if not os.path.exists("venv"):
                    venv_result = self.run_command("python -m venv venv")
                    results["steps"].append({"action": "create venv", "result": venv_result})
                
                if os.path.exists("requirements.txt"):
                    pip_cmd = "venv\\Scripts\\pip install -r requirements.txt" if os.name == 'nt' else "venv/bin/pip install -r requirements.txt"
                    pip_result = self.run_command(pip_cmd)
                    results["steps"].append({"action": "pip install", "result": pip_result})
            
            elif project_type == "dotnet":
                self.console.print("[cyan].NET projesi algılandı, dotnet restore çalıştırılıyor...[/cyan]")
                result = self.run_command("dotnet restore")
                results["steps"].append({"action": "dotnet restore", "result": result})
            
            results["success"] = True
            return results
        
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            return results
    
    def find_and_open_file(self, filename, directory="."):
        """Dosya bul ve aç (Windows'ta varsayılan program ile)"""
        try:
            found_files = []
            for root, dirs, files in os.walk(directory):
                for f in files:
                    if filename.lower() in f.lower():
                        found_files.append(os.path.join(root, f))
            
            if not found_files:
                return {"success": False, "error": f"Dosya bulunamadı: {filename}"}
            
            if len(found_files) == 1:
                file_to_open = found_files[0]
            else:
                file_to_open = found_files[0]
            
            os.startfile(file_to_open)
            return {"success": True, "path": file_to_open, "all_found": found_files}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_notepad(self, path=None):
        """Not defterini aç (ister dosya ile, ister boş)"""
        try:
            if path:
                if not os.path.exists(path):
                    with open(path, 'w', encoding='utf-8') as f:
                        pass
                os.startfile(path)
                return {"success": True, "path": path}
            else:
                subprocess.Popen("notepad.exe")
                return {"success": True, "message": "Boş not defteri açıldı"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_to_notepad(self, path, text):
        """Not defterine yaz ve aç"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
            os.startfile(path)
            return {"success": True, "path": path, "text": text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def append_to_notepad(self, path, text):
        """Not defterine ekleme yap"""
        try:
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    pass
            with open(path, 'a', encoding='utf-8') as f:
                f.write(text + "\n")
            os.startfile(path)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_running_processes(self):
        """Sistemdeki çalışan tüm uygulamaları listele (Windows)"""
        try:
            import csv
            from io import StringIO
            
            # tasklist komutunu CSV formatında çalıştır
            result = subprocess.run(
                ['tasklist', '/FO', 'CSV', '/NH'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode != 0:
                return {"success": False, "error": "tasklist komutu çalıştırılamadı"}
            
            processes = []
            csv_reader = csv.DictReader(StringIO(result.stdout), fieldnames=['Image Name', 'PID', 'Session Name', 'Session#', 'Mem Usage'])
            
            for row in csv_reader:
                processes.append({
                    'name': row['Image Name'].strip('"'),
                    'pid': int(row['PID'].strip('"')) if row['PID'].strip('"').isdigit() else row['PID'].strip('"'),
                    'memory': row['Mem Usage'].strip('"')
                })
            
            return {"success": True, "processes": processes, "count": len(processes)}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_active_window(self):
        """Aktif pencereyi al (Windows)"""
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            
            # Aktif pencere handle'ını al
            hwnd = user32.GetForegroundWindow()
            
            # Pencere başlığını al
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            window_title = buff.value
            
            return {"success": True, "hwnd": hwnd, "title": window_title}
        
        except Exception as e:
            return {"success": False, "error": str(e)}


toolbox = UniversalToolbox()

