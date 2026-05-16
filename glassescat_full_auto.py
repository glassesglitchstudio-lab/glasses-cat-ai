"""
GlassesCat - TAM OTOMATIK SISTEM
Web + Godot + Command Parser - Hepsi Otomatik!
Erkay Software - Lead Engineer AI
"""

import os
import sys
import subprocess
import shutil
import threading
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# ==================== GLASSESCAT SISTEM ====================
class GlassesCatSystem:
    """Tam otomatik GlassesCat sistemi"""
    
    def __init__(self):
        self.web_port = 5000
        self.project_path = Path("C:/Users/ErCuM/CascadeProjects/glassescat_ai/glassescat_cs2_auto")
        self.godot_path = None
        self.web_running = False
        
    def find_godot(self) -> str:
        """Godot'u otomatik bul"""
        print("\n[1] Godot araniyor...")
        
        paths = [
            "C:/Program Files/Godot Engine/Godot.exe",
            "C:/Program Files/Godot Engine/Godot 4.2/Godot.exe",
            "C:/Program Files/Godot Engine/Godot 4.1/Godot.exe",
            "D:/Program Files/Godot Engine/Godot.exe",
            "C:/Godot/Godot.exe",
            "godot", "godot4",
        ]
        
        for p in paths:
            if p in ["godot", "godot4"]:
                f = shutil.which(p)
                if f: 
                    print(f"  OK: {f}")
                    self.godot_path = f
                    return f
            elif os.path.exists(p):
                print(f"  OK: {p}")
                self.godot_path = p
                return p
        
        print("  X: Godot bulunamadi")
        return None
    
    def create_cs2_project(self):
        """CS2 Godot projesi olustur"""
        print("\n[2] CS2 proje olusturuluyor...")
        
        if self.project_path.exists():
            shutil.rmtree(self.project_path)
        self.project_path.mkdir(parents=True, exist_ok=True)
        
        # project.godot
        with open(self.project_path / "project.godot", "w") as f:
            f.write("""config_version=5
[application]
config/name="GlassesCat CS2"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.2", "Forward Plus")
[display]
window/size/viewport_width=1280
window/size/viewport_height=720
[input]
move_forward={"deadzone":0.5,"events":[{"physical_keycode":87}]}
move_back={"deadzone":0.5,"events":[{"physical_keycode":83}]}
move_left={"deadzone":0.5,"events":[{"physical_keycode":65}]}
move_right={"deadzone":0.5,"events":[{"physical_keycode":68}]}
jump={"deadzone":0.5,"events":[{"physical_keycode":32}]}
fire={"deadzone":0.5,"events":[{"button_index":1}]}
reload={"deadzone":0.5,"events":[{"physical_keycode":82}]}
[rendering]
renderer/rendering_method="forward_plus"
""")
        
        # player.gd
        with open(self.project_path / "player.gd", "w") as f:
            f.write("""extends CharacterBody3D

# GLASSESCAT CS2 3D - OTOMATIK URETILDI
# [MOTTO]: PERFEKT

@export var speed: float = 8.0
@export var jump_force: float = 5.0
@export var gravity: float = 15.0
@export var mouse_sensitivity: float = 0.002
@export var health: float = 100.0

var weapons = {
	"Pistol": {"damage": 20, "fire_rate": 0.3, "ammo": 12},
	"Rifle": {"damage": 35, "fire_rate": 0.1, "ammo": 30},
	"Sniper": {"damage": 100, "fire_rate": 1.5, "ammo": 5},
}
var current_weapon = "Pistol"
var last_shot = 0.0
var kill_count = 0

@onready var camera = $Camera3D

func _ready():
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	print("[GLASSESCAT] CS2 hazir!")
	print("[MOTTO]: PERFEKT")

func _input(event):
	if event is InputEventMouseMotion:
		rotate_y(-event.relative.x * mouse_sensitivity)
		camera.rotate_x(-event.relative.y * mouse_sensitivity)
		camera.rotation.x = clamp(camera.rotation.x, -PI/2, PI/2)

func _physics_process(delta):
	if not is_on_floor():
		velocity.y -= gravity * delta
	var input = Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	velocity.x = input.x * speed
	velocity.z = input.y * speed
	if Input.is_action_pressed("jump") and is_on_floor():
		velocity.y = jump_force
	if Input.is_action_pressed("fire"):
		shoot()
	move_and_slide()

func shoot():
	var w = weapons[current_weapon]
	var now = Time.get_ticks_msec() / 1000.0
	if now - last_shot < w["fire_rate"]: return
	if w["ammo"] <= 0: return
	last_shot = now
	w["ammo"] -= 1
	var space = get_world_3d().direct_space_state
	var q = PhysicsRayQueryParameters3D.create(camera.global_position, camera.global_position - camera.global_transform.basis.z * 100)
	var r = space.intersect_ray(q)
	if r:
		print(f"[GLASSESCAT] Vurus! {w['damage']}")
		kill_count += 1
""")
        
        # main.tscn
        with open(self.project_path / "main.tscn", "w") as f:
            f.write("""[gd_scene load_steps=2 format=3]
[sub_resource type="Environment" id="1"]
[sub_resource type="CapsuleShape3D" id="2"]
[node name="Main" type="Node3D"]
[node name="WorldEnvironment" type="WorldEnvironment" parent="."]
environment = SubResource("1")
[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
[node name="Floor" type="StaticBody3D" parent="."]
[node name="MeshInstance3D" type="MeshInstance3D" parent="Floor"]
mesh = BoxMesh.new()
[node name="Player" type="CharacterBody3D" parent="."]
script = ExtResource("1")
[node name="CollisionShape3D" type="CollisionShape3D" parent="Player"]
shape = SubResource("2")
[node name="Camera3D" type="Camera3D" parent="Player"]
[node name="CanvasLayer" type="CanvasLayer" parent="."]
[node name="Label" type="Label" parent="CanvasLayer"]
text = "[GLASSESCAT CS2] - PERFEKT"
""")
        
        print(f"  OK: Proje olusturuldu")
        return True
    
    def run_godot(self):
        """Godot'u calistir"""
        if not self.godot_path: 
            print("  X: Godot yok")
            return False
        
        print(f"\n[3] Godot baslatiliyor...")
        try:
            subprocess.Popen([self.godot_path, "--path", str(self.project_path)])
            print(f"  OK: Godot calisiyor")
            return True
        except Exception as e:
            print(f"  X: {e}")
            return False
    
    def start_web(self):
        """Web sunucusunu baslat"""
        print(f"\n[4] Web sunucu baslatiliyor...")
        
        # Flask app import
        try:
            sys.path.append("C:/Users/ErCuM/CascadeProjects/glassescat_ai")
            from web.app import app
            
            # Thread'de calistir
            def run_web():
                app.run(host="0.0.0.0", port=self.web_port, debug=False, use_reloader=False)
            
            t = threading.Thread(target=run_web, daemon=True)
            t.start()
            time.sleep(2)
            
            self.web_running = True
            print(f"  OK: http://localhost:{self.web_port}")
            return True
        except Exception as e:
            print(f"  X: Web hata - {e}")
            return False
    
    def full_auto_start(self):
        """TAM OTOMATIK BASLATICI"""
        
        print("""
================================================================================
   GLASSESCAT - TAM OTOMATIK SISTEM
================================================================================
   [MOTTO]: PERFEKT
   [OWNER]: BERKAY
   [ENGINE]: GULMEZ CETINER
================================================================================
""")
        
        # 1. Godot bul
        self.find_godot()
        
        # 2. CS2 proje olustur
        self.create_cs2_project()
        
        # 3. Godot calistir
        self.run_godot()
        
        # 4. Web baslat
        self.start_web()
        
        print(f"""
================================================================================
   TAMAMLANDI - PERFEKT
================================================================================
   [WEB]   http://localhost:{self.web_port}
   [GODOT] {self.godot_path or "Yok"}
   [PROJE] {self.project_path}
   
   KONTROLLER:
     WASD - Hareket
     MOUSE - Bakma
     SOL TIK - Ates
     R - Reload
     1-4 - Silah
     SPACE - Ziplama
================================================================================
""")
        
        return {
            "web": f"http://localhost:{self.web_port}",
            "godot": self.godot_path,
            "project": str(self.project_path)
        }


# ==================== FLASK WEB APP ====================
# Mevcut web app'i kullan
sys.path.append("C:/Users/ErCuM/CascadeProjects/glassescat_ai")

# GlassesCatSystem instance
gc_system = None

def run_glassescat():
    global gc_system
    gc_system = GlassesCatSystem()
    return gc_system.full_auto_start()


if __name__ == "__main__":
    run_glassescat()