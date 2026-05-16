"""
Glassescat AI v3 - Entegrasyon Testi
"""
import sys
import io

# UTF-8 çıktı için
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 50)
print("  NIKO AI v3 - ENTEGRASYON TESTI")
print("=" * 50)

results = []

# 1. Core
print("\n1. GlassescatCore")
try:
    from glassescat_core import get_core
    core = get_core()
    status = core.get_status()
    tools = status["stats"]["tools_available"]
    memory_ok = status["modules"]["memory"]
    tf_ok = status["modules"]["toolformer"]
    print(f"   Tools: {tools}")
    print(f"   Hafiza: {memory_ok}")
    print(f"   Toolformer: {tf_ok}")
    results.append(("Core", True, f"{tools} tools"))
except Exception as e:
    print(f"   HATA: {e}")
    results.append(("Core", False, str(e)))

# 2. State Manager
print("\n2. State Manager")
try:
    from glassescat_state_manager import get_state_manager
    sm = get_state_manager()
    sm.save_agent_state({"commands": 10, "errors": 2})
    state = sm.load_agent_state()
    sm.save_preference("theme", "dark")
    theme = sm.get_preference("theme")
    print(f"   State: {state}")
    print(f"   Theme: {theme}")
    results.append(("StateManager", True, f"state={state}"))
except Exception as e:
    print(f"   HATA: {e}")
    results.append(("StateManager", False, str(e)))

# 3. Feedback
print("\n3. Feedback Loop")
try:
    from glassescat_feedback import get_feedback_system
    fb = get_feedback_system()
    fb.log_interaction("test", "response", [], True, 1.5)
    fb.log_interaction("test2", "resp2", [{"tool": "web_search"}], True, 2.0)
    stats = fb.get_statistics()
    print(f"   Etkilesim: {stats['total_interactions']}")
    print(f"   Basari: {stats['success_rate']}")
    results.append(("Feedback", True, f"{stats['total_interactions']} interactions"))
except Exception as e:
    print(f"   HATA: {e}")
    results.append(("Feedback", False, str(e)))

# 4. Task Planner
print("\n4. Task Planner")
try:
    from glassescat_task_planner import TaskPlanner
    planner = TaskPlanner(core=core)
    result = planner.execute_task("Web aramasi yap")
    print(f"   Basari: {result['success']}")
    print(f"   Adim: {len(result['results'])}")
    results.append(("TaskPlanner", True, f"{len(result['results'])} steps"))
except Exception as e:
    print(f"   HATA: {e}")
    results.append(("TaskPlanner", False, str(e)))

# 5. Agent Loop
print("\n5. Agent Loop")
try:
    from glassescat_agent_loop import get_agent_loop
    loop = get_agent_loop(core=core)
    result = loop.run(user_input="Merhaba, nasilsin?")
    print(f"   Iterasyon: {result['iterations']}")
    print(f"   Dusunce: {len(result['thoughts'])}")
    print(f"   Yanit: {result['response'][:80]}...")
    results.append(("AgentLoop", True, f"{result['iterations']} iterations"))
except Exception as e:
    print(f"   HATA: {e}")
    results.append(("AgentLoop", False, str(e)))

# 6. Obsidian Memory (ekstra)
print("\n6. Obsidian Hafiza")
try:
    if core.memory:
        count = core.memory.get_memory_count()
        r = core.memory.recall("test", max_results=2)
        print(f"   Dosya: {count}")
        print(f"   Arama: {len(r)} sonuc")
        
        # Yeni methodlari test et
        context = core.memory.auto_inject_context("merhaba", max_items=2)
        print(f"   AutoContext: {len(context)} karakter")
        
        results.append(("Obsidian", True, f"{count} files"))
    else:
        print("   Hafiza aktif degil")
        results.append(("Obsidian", False, "not available"))
except Exception as e:
    print(f"   HATA: {e}")
    results.append(("Obsidian", False, str(e)))

# 7. Web Agent (sadece import test)
print("\n7. Web Agent")
try:
    from glassescat_web_agent import get_web_agent
    wa = get_web_agent()
    wa_status = wa.get_status()
    print(f"   Requests: {wa_status['requests_available']}")
    print(f"   BS4: {wa_status['beautifulsoup_available']}")
    results.append(("WebAgent", True, "imported"))
except Exception as e:
    print(f"   HATA: {e}")
    results.append(("WebAgent", False, str(e)))

# 8. GlassescatCoreAgent (glassescat_agent.py)
print("\n8. GlassescatCoreAgent (CLI)")
try:
    sys.path.insert(0, ".")
    from glassescat_agent import GlassescatCoreAgent
    agent = GlassescatCoreAgent(auto_init=True)
    resp = agent.process("merhaba")
    print(f"   Yanit: {resp[:80]}...")
    results.append(("GlassescatCoreAgent", True, "OK"))
except Exception as e:
    print(f"   HATA: {e}")
    results.append(("GlassescatCoreAgent", False, str(e)))

# SONUÇ
print("\n" + "=" * 50)
print("  TEST SONUCLARI")
print("=" * 50)
all_ok = True
for name, ok, detail in results:
    icon = "OK" if ok else "HATA"
    print(f"  [{icon}] {name}: {detail}")
    if not ok:
        all_ok = False

print(f"\n  Toplam: {len(results)} modul")
if all_ok:
    print("  DURUM: TUM MODULLER CALISIYOR")
else:
    print("  DURUM: BAZI MODULLERDE HATA VAR")

print("=" * 50)
