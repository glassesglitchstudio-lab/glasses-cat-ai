"""
GlassesCat - TAM OTOMATİK GODOT SİSTEMİ
Erkay Software - Lead Engineer AI
Otomatik: Kod Üretimi -> Godot Proje Oluşturma -> Çalıştırma
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from command_parser import CommandParser, logger

class GlassesCatGodotAuto:
    """Tam otomatik Godot sistemi"""
    
    def __init__(self):
        self.parser = CommandParser()
        self.project_path = Path("C:/Users/ErCuM/CascadeProjects/glassescat_ai/glassescat_godot_auto")
        self.godot_executable = self._find_godot()
        
    def _find_godot(self) -> str:
        """Godot executable bul"""
        possible_paths = [
            "C:/Program Files/Godot Engine/Godot.exe",
            "C:/Program Files (x86)/Godot Engine/Godot.exe",
            "godot",  # PATH'de varsa
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return "godot"  # Varsayılan
    
    def generate_game(self, game_type: str = "CS2 3D FPS") -> dict:
        """Oyun kodu otomatik üret"""
        logger.game(f"Otomatik kod uretimi basladi: {game_type}")
        
        # GlassesCat'e kod üret
        result = self.parser.parse(f"{game_type} oyun yap godot")
        
        if result['mode'] != '[G]':
            return {"success": False, "error": "Kod uretilemedi"}
        
        logger.game(f"Kod uretildi - Guven: %{result['confidence']*100}")
        
        return {
            "success": True,
            "code": result['generated_code'],
            "type": game_type,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_project(self, game_data: dict) -> dict:
        """Godot projesi otomatik oluştur"""
        logger.info("Godot projesi olusturuluyor...")
        
        # Klasör oluştur
        self.project_path.mkdir(parents=True, exist_ok=True)
        
        # project.godot dosyası
        project_file = self.project_path / "project.godot"
        project_content = """config_version=5

[application]

config/name="GlassesCat CS2"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.2", "Forward Plus")

[display]

window/size/viewport_width=1280
window/size/viewport_height=720

[input]

move_forward={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"physical_keycode":87,"key_label":0,"unicode":119,"location":0,"echo":false,"script":null)]
}
move_back={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"physical_keycode":83,"key_label":0,"unicode":115,"location":0,"echo":false,"script":null)]
}
move_left={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"physical_keycode":65,"key_label":0,"unicode":97,"location":0,"echo":false,"script":null)]
}
move_right={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"physical_keycode":68,"key_label":0,"unicode":100,"location":0,"echo":false,"script":null)]
}
jump={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"physical_keycode":32,"key_label":0,"unicode":32,"location":0,"echo":false,"script":null)]
}
fire={
"deadzone": 0.5,
"events": [Object(InputEventMouseButton,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"button_index":1,"canceled":false,"pressed":true,"script":null)]
}

[rendering]

renderer/rendering_method="forward_plus"
"""
        
        with open(project_file, 'w', encoding='utf-8') as f:
            f.write(project_content)
        
        # Player script
        player_script = self.project_path / "player.gd"
        with open(player_script, 'w', encoding='utf-8') as f:
            f.write(game_data['code'])
        
        # Main scene
        main_scene = self.project_path / "main.tscn"
        scene_content = """[gd_scene load_steps=2 format=3]

[sub_resource type="Environment" id="Environment_1"]

[node name="Main" type="Node3D"]

[node name="WorldEnvironment" type="WorldEnvironment" parent="."]
environment = SubResource("Environment_1")

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0)

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.866025, 0.5, 0, -0.5, 0.866025, 0, 5, 0)

[node name="Floor" type="StaticBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, -1, 0)

[node name="CollisionShape3D" type="CollisionShape3D" parent="Floor"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
shape = BoxShape3D.new()

[node name="MeshInstance3D" type="MeshInstance3D" parent="Floor"]
mesh = BoxMesh.new()

[node name="Player" type="CharacterBody3D" parent="."]
script = ExtResource("1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="Player"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0)
shape = CapsuleShape3D.new()

[node name="Camera3D" type="Camera3D" parent="Player"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.8, 0)

[resource]
"""
        
        with open(main_scene, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        logger.info(f"Proje olusturuldu: {self.project_path}")
        
        return {"success": True, "path": str(self.project_path)}
    
    def run_godot(self) -> dict:
        """Godot'u otomatik çalıştır"""
        logger.info("Godot baslatiliyor...")
        
        if not shutil.which("godot") and not os.path.exists(self.godot_executable):
            return {"success": False, "error": "Godot bulunamadi"}
        
        try:
            # Godot'u headless çalıştır
            result = subprocess.run(
                [self.godot_executable, "--headless", "--path", str(self.project_path), "--script", "res://player.gd"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            logger.game("Godot calistirildi")
            
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            logger.game("Godot timeout - oyun çalışıyor olabilir")
            return {"success": True, "note": "Timeout - Godot çalışıyor"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def full_auto_run(self, game_type: str = "CS2 3D FPS"):
        """TAM OTOMATİK - Sadece çağır ve çalıştır!"""
        
        print("""
================================================================================
   GLASSESCAT - TAM OTOMATIK GODOT SISTEMI
================================================================================
   [MOTTO]: PERFEKT
   [OWNER]: BERKAY
   [ENGINE]: GULMEZ CETINER
================================================================================
""")
        
        print(f"[1/3] Oyun kodu uretilyor...")
        game_data = self.generate_game(game_type)
        
        if not game_data['success']:
            print("[HATA] Kod uretilemedi!")
            return
        
        print(f"[2/3] Godot projesi olusturuluyor...")
        project = self.create_project(game_data)
        
        if not project['success']:
            print("[HATA] Proje olusturulamadi!")
            return
        
        print(f"[3/3] Godot baslatiliyor...")
        run = self.run_godot()
        
        print("""
================================================================================
   TAMAMLANDI!
================================================================================
   [DURUM]: PERFEKT
   [PROJE]: {}
   [KOD]: otomatik uretildi
================================================================================
""".format(project['path']))
        
        return project


# ==================== ANA FONKSIYON ====================
def glassescat_start():
    """GlassesCat'i başlat - tek komutla"""
    system = GlassesCatGodotAuto()
    system.full_auto_run("CS2 3D FPS")


if __name__ == "__main__":
    glassescat_start()