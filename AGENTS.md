# GlassesCat AI - Obsidian Sınırsız Hafıza + Otonom Ajan Sistemi

## ZORUNLU: Push & Yayınla Workflow (Unutma!)
Berkay "push la", "yayınla", "github'a at" dediğinde HER ZAMAN:
1. `git add glasses_vibe.py gulmzcetiner/Modelfile && git commit -m "V5_NEXUS_CORE: ..." && git push origin main`
2. `cd gulmzcetiner && ollama create glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE -f Modelfile && ollama push glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE`
3. Link göster: GitHub (glasses-cat-ai) + Ollama (V5_NEXUS_CORE)

## ZORUNLU: Oturum Başlangıcı
Her yeni oturumda BU KOMUTU ÇALIŞTIRARAK başla:
```bash
cd C:\Users\ErCuM\CascadeProjects\niko_ai && python -c "from glassescat_core import get_core; c = get_core(); print(f'Glassescat Core: {c.get_status()[\"stats\"][\"tools_available\"]} tools, {c.memory.get_memory_count() if c.memory else 0} memory files')"
```

## Yeni Mimari (v3.0)

```
Glassescat Core (glassescat_core.py)
  ├── AgentLoop (glassescat_agent_loop.py)    → ReAct: Düşün + Karar Ver + Uygula
  ├── TaskPlanner (glassescat_task_planner.py) → Çok adımlı görev planlama
  ├── StateManager (glassescat_state_manager.py) → Kalıcı durum yönetimi
  ├── WebAgent (glassescat_web_agent.py)       → Otonom web tarayıcı
  ├── FeedbackLoop (glassescat_feedback.py)    → Öğrenme ve hata analizi
  ├── Toolformer (toolformer.py)         → 24 araçlı fonksiyon çağırma
  ├── ObsidianMemory (obsidian_memory.py) → Sınırsız .md hafıza
  └── ModelRouter (model_router.py)      → Akıllı model seçimi
```

## Kullanım

### CLI ile başlatma
```bash
cd C:\Users\ErCuM\CascadeProjects\niko_ai && python glassescat_agent.py
```

### Web sunucusu ile başlatma
```bash
cd C:\Users\ErCuM\CascadeProjects\niko_ai && python main.py
```

### Python'dan kullanma
```python
from glassescat_core import get_core
core = get_core()

# Tek mesaj
result = core.process_message("Merhaba!")
print(result["response"])

# Çok adımlı görev
result = core.execute_task("Chrome'u aç, YouTube'a gir, Mavislime ara")
print(result["summary"])

# Hafızada ara
if core.memory:
    results = core.memory.recall("python", 5)
```

## Önemli Komutlar (CLI'da)
| Komut | Açıklama |
|-------|----------|
| `yardim` | Yardım menüsü |
| `durum` | Sistem durumu |
| `istatistik` | Performans istatistikleri |
| `planla <görev>` | Çok adımlı görev |
| `ara <sorgu>` | Web'de ara |
| `hafizada ara <s>` | Hafızada ara |
| `ogren` | AI öğrenme istatistikleri |

## Hafızaya Kaydetme
```python
from obsidian_memory import get_obsidian_memory
m = get_obsidian_memory()
m.save_memory(title, content, tags=[])
m.save_conversation(session_id, messages)
m.save_knowledge(title, content, category="general")
```

## Hızlı Test
```bash
cd C:\Users\ErCuM\CascadeProjects\niko_ai && python -c "
from glassescat_core import get_core
from glassescat_agent_loop import get_agent_loop
c = get_core()
loop = get_agent_loop(core=c)
r = loop.run(user_input='test')
print('OK' if r['success'] else 'FAIL')
"
```
