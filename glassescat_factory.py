"""
Niko Universal Game Factory - Full Automation System
Multi-Tenancy | Auto-Injection | Bridge | Build Queue | Mobile Optimization
"""

import os
import json
import uuid
import shutil
import time
import threading
import queue
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent

@dataclass
class User:
    user_id: str
    username: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Project:
    project_id: str
    user_id: str
    name: str
    path: str
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class BuildTask:
    project_id: str
    user_id: str
    project_path: str
    priority: int = 1
    status: str = "queued"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class GlassescatFactory:
    def __init__(self):
        self.storage_root = PROJECT_ROOT / 'storage'
        self.templates_dir = PROJECT_ROOT / 'templates' / 'godot_base'
        self.projects: Dict[str, Project] = {}
        self.users: Dict[str, User] = {}

        self.build_queue = queue.Queue()
        self.active_builds = 0
        self.max_concurrent = 3
        self.build_lock = threading.Lock()

        self.godot_executable = self._find_godot()
        self.gpu_info = self._detect_hardware()

        self._init_template()
        self._start_build_worker()

    def _find_godot(self) -> str:
        paths = [
            'C:\\Program Files\\Godot\\Godot_v4.2.2-stable_win64.exe',
            'C:\\Program Files\\Godot\\Godot_v4.3-stable_win64.exe',
            'godot'
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return 'godot'

    def _detect_hardware(self) -> Dict[str, Any]:
        import subprocess
        import platform
        gpu = 'Unknown'
        ram_gb = 0

        try:
            result = subprocess.run(['powershell', '-Command', 'Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name'],
                capture_output=True, text=True)
            gpu = result.stdout.strip()
        except: pass

        try:
            result = subprocess.run(['powershell', '-Command', '[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 0)'],
                capture_output=True, text=True)
            ram_gb = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 32
        except: ram_gb = 32

        return {'gpu': gpu, 'ram_gb': ram_gb, 'cpu_threads': os.cpu_count() or 8}

    def _init_template(self):
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)

        project_godot = self.templates_dir / 'project.godot'
        if not project_godot.exists():
            project_godot.write_text('''config_version=5

[application]
config/name="Niko Template"
config/version="1.0.0"
run/main_scene="res://scenes/main.tscn"
config/features=PackedStringArray("4.2", "GL Compatibility")

[display]
window/size/viewport_width=1280
window/size/viewport_height=720
window/stretch/mode="canvas_items"

[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
textures/vram_compression/import_etc2_astc=true
anti_aliasing/quality/msaa_2d=0
anti_aliasing/quality/msaa_3d=0
''', encoding='utf-8')

        scenes_dir = self.templates_dir / 'scenes'
        scenes_dir.mkdir(exist_ok=True)
        main_scene = scenes_dir / 'main.tscn'
        if not main_scene.exists():
            main_scene.write_text('''[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/network_listener.gd" id="1"]

[node name="Main" type="Node3D"]
script = ExtResource("1")
''', encoding='utf-8')

        scripts_dir = self.templates_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)

        listener_path = scripts_dir / 'network_listener.gd'
        if not listener_path.exists():
            listener_path.write_text(self._get_network_listener_script(), encoding='utf-8')

    def _get_network_listener_script(self) -> str:
        return '''extends Node

const HOST = "127.0.0.1"
const PORT = 4242
var udp_peer: UDPServer
var connected = false
var current_user = ""
var current_project = ""

func _ready():
	print("[Niko-AI] Factory Listener Ready")
	start_listener()

func start_listener():
	udp_peer = UDPServer.new()
	var err = udp_peer.listen(PORT, HOST)
	if err != OK:
		print("[ERROR] UDP bind failed")
		return
	set_process(true)
	print("[UDP] Listening on ", HOST, ":", PORT)

func _process(delta):
	var peer = udp_peer.poll()
	while peer:
		var packet = udp_peer.get_packet()
		if packet.size() > 0:
			_process_packet(packet)
		peer = udp_peer.poll()

func _process_packet(packet: PoolByteArray):
	var json_str = ""
	if packet.size() >= 4 and packet[0] == 78 and packet[1] == 73 and packet[2] == 75 and packet[3] == 79:
		json_str = packet.slice(4).get_string_from_utf8()
	else:
		json_str = packet.get_string_from_utf8()

	var result = JSON.parse(json_str)
	if result.get_error() != OK:
		return
	var cmd = result.get_result()
	_execute_command(cmd)

func _execute_command(cmd: Dictionary):
	match cmd.get("cmd"):
		"handshake":
			current_user = cmd.get("user_id", "")
			current_project = cmd.get("project_id", "")
			connected = true
			print("=== Niko-AI ve Godot Bağlantısı Başarılı! ===")
		"spawn": _spawn_item(cmd)
		"skin": _apply_skin(cmd)
		"weather": _set_weather(cmd)
		"ai_level": _set_ai(cmd)
		"weapon": _spawn_weapon(cmd)
		"map": _load_map(cmd)

func _spawn_item(cmd): print("[SPAWN] ", cmd.get("item"))
func _apply_skin(cmd): print("[SKIN] ", cmd.get("skin"))
func _set_weather(cmd): print("[WEATHER] ", cmd.get("mode"))
func _set_ai(cmd): print("[AI] Level: ", cmd.get("level"))
func _spawn_weapon(cmd): print("[WEAPON] ", cmd.get("type"))
func _load_map(cmd): print("[MAP] ", cmd.get("name"))
'''

    def create_user(self, username: str) -> User:
        user_id = hashlib.md5(f"{username}{time.time()}".encode()).hexdigest()[:12]
        user = User(user_id=user_id, username=username)

        user_dir = self.storage_root / 'users' / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        (user_dir / 'projects').mkdir(exist_ok=True)
        (user_dir / 'data').mkdir(exist_ok=True)

        self.users[user_id] = user
        return user

    def create_project(self, user_id: str, name: str, ai_code: str = "") -> Project:
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")

        project_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:10]
        project_path = self.storage_root / 'users' / user_id / 'projects' / project_id

        project_path.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.templates_dir, project_path, dirs_exist_ok=True)

        (project_path / 'project.godot').write_text(
            f'''config_version=5

[application]
config/name="{name}"
config/version="1.0.0"
run/main_scene="res://scenes/main.tscn"
config/features=PackedStringArray("4.2", "GL Compatibility")

[display]
window/size/viewport_width=1280
window/size/viewport_height=720
window/stretch/mode="canvas_items"

[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
textures/vram_compression/import_etc2_astc=true
anti_aliasing/quality/msaa_2d=0
anti_aliasing/quality/msaa_3d=0
''', encoding='utf-8')

        if ai_code:
            game_script = project_path / 'scripts' / 'game_logic.gd'
            game_script.write_text(ai_code, encoding='utf-8')

            scene_file = project_path / 'scenes' / 'main.tscn'
            if scene_file.exists():
                content = scene_file.read_text(encoding='utf-8')
                if 'game_logic.gd' not in content:
                    content = content.replace('[gd_scene',
                        '[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://scripts/game_logic.gd" id="2"]\n\n[node name="Main" type="Node3D" groups=["game"]]\nscript = ExtResource("1")\ngame_script = ExtResource("2")')
                    scene_file.write_text(content, encoding='utf-8')

        project = Project(project_id=project_id, user_id=user_id, name=name, path=str(project_path))
        self.projects[project_id] = project

        return project

    def inject_code(self, project_id: str, script_name: str, code: str) -> bool:
        if project_id not in self.projects:
            return False

        project = self.projects[project_id]
        script_path = Path(project.path) / 'scripts' / f'{script_name}.gd'
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(code, encoding='utf-8')
        return True

    def queue_build(self, project_id: str, priority: int = 1) -> str:
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")

        project = self.projects[project_id]
        task = BuildTask(project_id=project_id, user_id=project.user_id,
                        project_path=project.path, priority=priority)

        self.build_queue.put(task)
        project.status = "queued"

        return f"Build queued: {project_id}"

    def _start_build_worker(self):
        worker = threading.Thread(target=self._build_worker, daemon=True)
        worker.start()

    def _build_worker(self):
        while True:
            task = self.build_queue.get()

            with self.build_lock:
                while self.active_builds >= self.max_concurrent:
                    time.sleep(1)

            self.active_builds += 1
            task.status = "building"
            task.started_at = datetime.now().isoformat()

            result = self._build_apk(task)

            self.active_builds -= 1
            task.status = "completed" if result['success'] else "failed"
            task.completed_at = datetime.now().isoformat()

            if self.projects.get(task.project_id):
                self.projects[task.project_id].status = task.status
                if result.get('apk_path'):
                    self.projects[task.project_id].apk_path = result['apk_path']

            self.build_queue.task_done()

    def _build_apk(self, task: BuildTask) -> Dict[str, Any]:
        project_path = Path(task.project_path)
        export_dir = project_path / 'exports'
        export_dir.mkdir(exist_ok=True)
        apk_path = export_dir / f'{project_path.name}.apk'

        print(f"[BUILD] Starting APK build for {task.project_id}")
        print(f"[GPU] {self.gpu_info['gpu']} | RAM: {self.gpu_info['ram_gb']}GB | Threads: {self.gpu_info['cpu_threads']}")

        if os.path.exists(self.godot_executable):
            import subprocess
            cmd = [self.godot_executable, '--headless', '--path', str(project_path),
                   '--export-release', 'Android', str(apk_path)]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                if result.returncode == 0:
                    return {'success': True, 'apk_path': str(apk_path)}
            except Exception as e:
                print(f"[ERROR] Build failed: {e}")

        (export_dir / 'BUILD_REQUIRES_GODOT.txt').write_text(
            'Godot 4.x required for APK build. Download from godotengine.org')
        return {'success': False, 'error': 'Godot not found'}

    def get_status(self) -> Dict[str, Any]:
        return {
            'hardware': self.gpu_info,
            'active_builds': self.active_builds,
            'queued_builds': self.build_queue.qsize(),
            'max_concurrent': self.max_concurrent,
            'total_projects': len(self.projects),
            'users': len(self.users)
        }

    def get_project(self, project_id: str) -> Optional[Project]:
        return self.projects.get(project_id)

    def get_user_projects(self, user_id: str) -> List[Project]:
        return [p for p in self.projects.values() if p.user_id == user_id]


factory = GlassescatFactory()

def main():
    print("=" * 60)
    print("  NIKO UNIVERSAL GAME FACTORY")
    print("  Multi-Tenancy | Auto-Injection | Bridge | Build Queue")
    print("=" * 60)
    print(f"\nHardware: {factory.gpu_info['gpu']}")
    print(f"RAM: {factory.gpu_info['ram_gb']}GB | Threads: {factory.gpu_info['cpu_threads']}")
    print(f"Max Concurrent Builds: {factory.max_concurrent}")
    print(f"Template: {factory.templates_dir}")

    user = factory.create_user("test_user")
    print(f"\n[+] User created: {user.user_id}")

    ai_code = """extends Node3D
var score = 0
func _ready():
    print("Glassescat AI loaded - Expert Mode")
    spawn_enemies(5)

func spawn_enemies(count):
    for i in range(count):
        print("Enemy ", i, " spawned with expert AI")
"""

    project = factory.create_project(user.user_id, "Bicak_Yarisi", ai_code)
    print(f"[+] Project created: {project.project_id}")

    factory.inject_code(project.project_id, "weapon_system", """extends Node3D
var weapons = ["Karambit", "Butterfly", "Flip"]
func _ready(): print("Weapons: ", weapons)
""")

    factory.queue_build(project.project_id)

    print(f"\n[+] Build queued for {project.project_id}")
    print(f"    Status: {project.status}")

    print("\n=== Factory Ready ===")
    print("Use: factory.create_user(), factory.create_project(), factory.queue_build()")

if __name__ == '__main__':
    main()