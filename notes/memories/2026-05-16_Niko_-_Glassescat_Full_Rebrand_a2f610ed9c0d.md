---
title: "Niko -> Glassescat Full Rebrand"
memory_id: "a2f610ed9c0d"
created: 2026-05-16T17:29:46.648538
modified: 2026-05-16T17:29:46.648538
type: memory
date: 2026-05-16
tags:
  - glassescat
  - rebrand
  - refactoring
  - milestone
aliases: ["glassescat", "rebrand", "refactoring"]
cssclass: memory-note
---

# 💭 Niko -> Glassescat Full Rebrand

**Oluşturulma:** 2026-05-16 17:29:46
**ID:** `a2f610ed9c0d`

---

Tum proje Niko isimlendirmesinden Glassescat isimlendirmesine donusturuldu.

DOSYA DEGISTIRME (10 dosya):
- niko_core.py -> glassescat_core.py
- niko_agent.py -> glassescat_agent.py
- niko_agent_loop.py -> glassescat_agent_loop.py
- niko_ai_engine.py -> glassescat_ai_engine.py
- niko_feedback.py -> glassescat_feedback.py
- niko_factory.py -> glassescat_factory.py
- niko_gui.py -> glassescat_gui.py
- niko_state_manager.py -> glassescat_state_manager.py
- niko_task_planner.py -> glassescat_task_planner.py
- niko_web_agent.py -> glassescat_web_agent.py

ICERIK DEGISTIRME (30+ dosya):
- Niko Software -> Glassescat Software
- NikoAICore -> GlassescatCore
- Niko AI -> Glassescat AI
- Tum class isimleri (NikoCore -> GlassescatCore, vb.)
- Tum import'lar (from niko_ -> from glassescat_)
- Tum degisken isimleri
- AGENTS.md, opencode.json, package.json, baslat.bat, server.py guncellendi

MODEL ROUTER GUNCELLEME:
- AGI modu eklendi (USE_AGI_MODE = True)
- Birincil model: gulmzcetinermax:latest
- Tum gorevler (chat, coding, analysis) artik GulmezCetinerMax ile calisiyor

---
## 🔗 İlgili Bağlantılar
- [[daily/2026-05-16|📅 Günlük Not - 2026-05-16]]
