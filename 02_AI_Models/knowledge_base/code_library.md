# Code Library - FPS Systems
## Godot & Implementation Examples

---

## 1. WEAPON SYSTEM (Godot 4.x)

### Weapon Resource System
```gdscript
# weapon.gd - Base weapon resource
class_name Weapon
extends Resource

@export var weapon_name: String
@export var mesh: Mesh
@export var damage: float = 10.0
@export var fire_rate: float = 0.1
@export var magazine_size: int = 30
@export var recoil_strength: float = 1.0
@export var spread: float = 0.05

# Add to project as Weapon.tres resource file
```

### Weapon Controller
```gdscript
# weapon_controller.gd
class_name WeaponController
extends Node

@export var current_weapon: Weapon

func _fire():
    if Input.is_action_just_pressed("fire"):
        apply_recoil()
        spawn_projectile()

func apply_recoil():
    var recoil_data = current_weapon.recoil_pattern
    camera.rotation.x -= recoil_data.vertical * current_weapon.recoil_strength
    camera.rotation.y += randf_range(-recoil_data.horizontal, recoil_data.horizontal)
```

---

## 2. RECOIL SYSTEM (Unreal/General)

### Recoil Pattern Data
```csharp
// RecoilPattern.cs - Data asset
[CreateAssetMenu(fileName = "RecoilData", menuName = "FPS/Recoil")]
public class RecoilPattern : ScriptableObject
{
    [Header("Vertical Recoil")]
    public AnimationCurve verticalCurve;
    
    [Header("Horizontal Recoil")]
    public AnimationCurve horizontalCurve;
    
    [Header("Spread")]
    public float baseSpread = 0.05f;
    public float maxSpread = 0.2f;
    
    [Header("Recovery")]
    public float recoverySpeed = 5f;
    public float recoveryDelay = 0.1f;
}
```

### Recoil Application
```csharp
// RecoilSystem.cs
public void ApplyRecoil()
{
    int sequence = bulletsFired % patternLength;
    float vertical = verticalCurve.Evaluate(sequence);
    float horizontal = horizontalCurve.Evaluate(sequence);
    
    // Apply to camera
    cameraRecoil.y -= vertical * strength;
    cameraRecoil.x += Random.Range(-horizontal, horizontal) * strength;
    
    // Recover after fire stops
    if (!isFiring)
        StartCoroutine(RecoverRecoil());
}
```

---

## 3. HUD SYSTEM (Godot)

### Health/Ammo Display
```gdscript
# HUD.gd
extends Control

@onready var health_bar = $VBox/HealthBar
@onready var ammo_label = $VBox/AmmoLabel

func update_health(current, max):
    var tween = create_tween()
    tween.tween_property(health_bar, "value", 
        (float(current) / max) * 100, 0.3)

func update_weapon(weapon_name, magazine, reserve):
    ammo_label.text = "%s: %d/%d" % [weapon_name, magazine, reserve]
    # Add "pop" animation with tween
```

### Crosshair System
```gdscript
# CrosshairData.gd
class_name CrosshairData
extends Resource

@export var size: float = 32.0
@export var color: Color = Color.WHITE
@export var gap: float = 4.0
@export var dynamic: bool = true
@export var spread_multiplier: float = 1.0
```

---

## 4. KILL CARD / SCORE SYSTEM

### Kill Feed Display
```gdscript
# KillFeed.gd
extends VBoxContainer

func add_kill(killer_name, victim_name, weapon_icon):
    var entry = kill_entry_scene.instantiate()
    entry.killer = killer_name
    entry.victim = victim_name
    entry.weapon = weapon_icon
    
    add_child(entry)
    
    # Auto-remove after 3 seconds
    await get_tree().create_timer(3.0).timeout
    entry.queue_free()
```

### Death Stats Card
```gdscript
# DeathCard.gd
class_name DeathCard
extends Control

var stats = {
    "killer": "Player1",
    "damage_dealt": 150,
    "headshots": 2,
    "time_alive": 45.5
}

func show_stats():
    $Panel/KillerLabel.text = stats.killer
    $Panel/DamageLabel.text = "Damage: %d" % stats.damage_dealt
    $Panel/TimeLabel.text = "Time: %.1fs" % stats.time_alive
    anim_player.play("show")
```

---

## 5. INVENTORY SYSTEM

### Grid-Based Inventory
```gdscript
# InventorySlot.gd
class_name InventorySlot
extends Button

var item: ItemData = null
var slot_index: int = 0

func set_item(new_item):
    item = new_item
    if item:
        icon = item.texture
        tooltip_text = item.display_name
    else:
        icon = null
        tooltip_text = ""

func _on_drag_started():
    if item:
        # Create drag preview
        var preview = drag_preview.instantiate()
        preview.init(item)
```

### Item Data
```gdscript
# ItemData.gd
class_name ItemData
extends Resource

@export var item_id: String
@export var display_name: String
@export var icon: Texture2D
@export var max_stack: int = 99
@export var weight: float = 1.0
@export var category: ItemCategory
@export var value: int = 100

enum ItemCategory { WEAPON, ARMOR, MEDICAL, AMMO, KEYCARD }
```

---

## 6. PLAYER MOVEMENT (State Machine)

### Move State Pattern (Godot)
```gdscript
# movement_state.gd
class_name MovementState
extends State

@export var speed: float = 200.0
@export var acceleration: float = 10.0

func handle_input():
    var input_dir = Input.get_vector("move_left", "move_right", "move_forward", "move_back")
    player.velocity.x = move_toward(player.velocity.x, input_dir.x * speed, acceleration)
    player.velocity.z = move_toward(player.velocity.z, input_dir.y * speed, acceleration)

func get_state_transitions():
    return [
        StateTransition.new("Sprint", Input.is_action_pressed("sprint")),
        StateTransition.new("Crouch", Input.is_action_pressed("crouch")),
    ]
```

---

## 7. ECONOMY SYSTEM

### Round Economy Manager
```gdscript
# EconomyManager.gd
class_name EconomyManager
extends Node

var team_money: int = 0
var loss_streak: int = 0
var round_bonus: int = 3500

func calculate_round_bonus(won_round: bool, ct_side: bool):
    if won_round:
        return 3500 + (ct_side * 50)  # CT gets extra $50 per kill from July 2025
    else:
        loss_streak += 1
        return clamp(1400 + (loss_streak * 500), 1400, 3500)

func can_afford(full_buy: bool):
    return team_money >= (full_buy_cost if full_buy else half_buy_cost)
```

---

## 8. ATTACHMENTS / GUNSMITH (Arena Breakout Style)

### Weapon Attachment
```gdscript
# weapon_attachment.gd
class_name WeaponAttachment
extends Resource

@export var attachment_id: String
@export var display_name: String
@export var slot: AttachmentSlot

# Stat modifiers
@export var damage_mod: float = 0.0
@export var recoil_mod: float = 0.0
@export var aim_speed_mod: float = 0.0
@export var range_mod: float = 0.0

enum AttachmentSlot { barrel, magazine, sight, grip, stock }
```

---

*Sources: Godot FPS Template, Nodot FPS, TechArthub, Kinemation*
*Format: Code Snippet Reference*