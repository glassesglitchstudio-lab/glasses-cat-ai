# PERFEKT Game Knowledge Base
## Tactical Shooter Development Research

---

## 1. GENRE ANALYSIS

### 1.1 Tactical Shooter (CS2 / Valorant)

**Movement Mechanics:**
- Counter-strafing: kritik beceri -hareket sırasında tam doğruluk
- Walk/RunCrouch/Jump: her hareket nişangahı etkiler
- ACS2: momentum tabanlı, daha hızlı; Valorant: daha toleranslı hareket
- Jump peeking, tight corner clears ödüllendirilir

**Shooting Feel (Vuruş Hissi):**
- CS2: sabit recoil pattern - öğrenilebilir ve ustalaşılabilir
- Her silahın benzersiz recoil yayılımı var
- Spray pattern memoria gerektirir
- Valorant: daha-basit recoil, daha toleranslı ama hala ödüllendirici
- Crosshair placement kritik

**Economy System:**
- CS2: $50 CT kill bonus (July 2025 update)
- Silah/utility satın alma kararları maç sonucunu etkiler
- Full buy, half buy, force buy stratejileri
- Valorant: daha basit - agent abilities özgür, silahlar standart fiyat

---

### 1.2 Extraction Shooter (Arena Breakout)

**Movement Mechanics:**
- Stamina sistemi: ayrı legs/arms barları
- Sprint/jump leg stamina tüketir
- Aiming too long arm stamina tüketir
- Fracture sistemi: hasar alan uzuv yavaşlar

**Shooting Feel:**
- Ultr-realistic yara sistemi
- Ammo type vs armor class dengesi kritik
- Penetreasyon seviyesi hasarı belirler
- Headshot'lar bile armor'a bağlı

**Economy System:**
- Loot topla → Extract → Keep/Sell döngüsü
- Koen para birimi
- Gear fear: en büyük yeni oyuncu-engeli
- "Rule of 10": total paranın %10'undan fazla kit taşıma
- Storage yönetimi önemli

---

### 1.3 Sandbox (Minecraft)

**Movement Mechanics:**
- Walk, run, jump, sprint sistemi
- Yüzme ve el üstü yükselme
- Elytra ile uçuş

**Interaction:**
- Block kırma ve yerleştirme
- Crafting sistemi: 2x2 ve 3x3 grid
- Recipe book ile tarif öğrenme
- Redstone mekanikleri

**Economy:**
- Villager trading: 5 career level
- Emerald para birimi
- Wandering trader sistemi
- Demand-based fiyatlandırma

---

## 2. CODE LIBRARY

### 2.1 Godot Killcard/Score System

```
# Base structure concept for kill tracking
class KillObjective:
    extends BaseObjective
    @export var target_enemy: NodePath
    @export var required_kills: int = 1
    
    func initialize(manager):
        enemy_node = manager.get_node(target_enemy)
        health_component = enemy_node.health_component
        health_component.died.connect(_on_enemy_died)
    
    func _on_enemy_died():
        kills += 1
        if kills >= required_kills: complete()
```

**Kaynak:** Godot FPS Template (AxelReviron/Godot-FPS-Template)

---

### 2.2 Recoil Control System

**CS2-style Recoil Components:**
1. Vertical Recoil: weapon moves up
2. Horizontal Recoil: random left/right
3. Spread: randomness added on top
4. Pattern curves: normalized animation curves

```
# Recoil pattern logic (pseudo-code)
var bullets_in_sequence = 0
var recoil_pattern = []

func OnFire():
    bullets_in_sequence += 1
    current_recoil = recoil_pattern[bullets_in_sequence % pattern_length]
    camera_rotation.y -= current_recoil.vertical
    camera_rotation.y += current_recoil.horizontal

func ResetRecoil():
    bullets_in_sequence = 0
    # Return to origin with damping
```

**Kaynak:** TechArthub Competitive Recoil, Kinemation Recoil System

---

### 2.3 Inventory System (Godot/Pygame)

**Key Components:**
- Grid-based storage (slot yönetimi)
- Item stacking
- Drag-and-drop
- Weight/capacity limit
- Category filtering

**Kaynak:** Nodot FPS Example (Inventory + storage chest)

---

## 3. MARKET RESEARCH

### 3.1 Most Played Games 2025-2026

| Oyun | Platform | Neden Başarılı |
|------|----------|---------------|
| CS2 | PC | Legacy, skin economy, high skill ceiling |
| Valorant | PC | Agent çeşitliliği, anti-cheat, esports |
| Escape from Tarkov | PC | Hardcore extraction, deep mechanics |
| ARC Raiders | Cross-platform | PvE+PvP平衡, co-op odaklı, accessible |
| Minecraft | Cross-platform | Sandbox creativity, endless content |
| Roblox | Cross-platform | User-generated content, social |

### 3.2 Neden Başarılı?

**CS2:** Pure mechanical skill, predictable patterns, skin economy worth billions
**Valorant:** Agent system adds variety, more accessible than CS2
**ARC Raiders:** PvE focus alongside PvP = different player segments
**Arena Breakout:** Mobile-first accessible extraction shooter

### 3.3 Market Trends 2026

- Sandbox playtime: +36% growth (NewZoo 2026)
- Extraction shooters: Only ~2% of shooter market (undersaturated)
- PC long-tail: Rank 21+ games gaining share
- Premium progression-heavy titles retain better

---

## 4. TACTICAL SHOOTER FEATURE PRIORITY

### 4.1 Most Engaging Features (Berkay için)

**HIGH PRIORITY:**
1. **Recoil Control System** - CS2 tarzı öğrenilebilir recoil pattern
2. **Counter-Strafing** - Movement mekanik beceri derinliği
3. **Economy System** - Buy/force/save stratejik kararları
4. **Team-based 5v5** - Bomb defusal / spike plant mode
5. **Weapon Variety** - Her silah benzersiz hissettirmeli

**MEDIUM PRIORITY:**
6. **Killcard/Deathcard** - Ölüm sonrası istatistik gösterimi
7. **Utility (Grenades)** - Smoke, flash, molotov lineups
8. **Skin/Cosmetic System** - Trading potential
9. **Map Knowledge** - Angle advantage, lineups

**ATTRACTIVE DIFFERENTIATORS:**
10. **Agent System (Valorant-style)** - Önü açık ama pure shooter'ı bozmadan
11. **Co-op PvE Element (Arc Raiders-style)** - Extraction yapısına entegre
12. **Progression System** - Unlockable content ile retention

---

## 5. RECOMMENDATIONS

### 5.1 Target Design
- **Core:** CS2 tarzı pure tactical shooter
- **Twist:** Agent abilities (opsiyonel) veya co-op PvE mode
- **Economy:** Escape from Tarkov/Arena Breakout tarzı loot sistemi

### 5.2 Skill Ceiling
- High aiming skill requirement
- Recoil mastery > memorization
- Map utility + lineups
- Economy management

### 5.3 Beginner Friendliness
- Valorant tarzı daha toleranslı recoil başlangıçta
- Agent abilities ile aim dışında katkı sağlama imkanı
- Tutorial + practice range

---

*Generated: 2026-05-08*
*Purpose: AI Game Designer Knowledge Base*
*Format: PERFEKT*