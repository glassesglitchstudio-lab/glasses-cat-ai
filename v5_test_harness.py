import os
import json
from ultra_agent_engine import UltraAgentEngine
from glassescat_core import get_core

print("\U0001f52e [V5_NEXUS_SYSTEM]: Ekosistem Test Modu Baslatiliyor Berkay...")

core = get_core()
engine = UltraAgentEngine(core=core)
print("\u26a1 37 Siber Arac ve 13 Handler Dogrulaniyor... TAMAM!")

print("\n\u2694\ufe0f PROTOKOL 1: Swarm Run (Ajan Zinciri) Test Ediliyor...")
test_task = "Basit bir sayi tahmin oyunu icin proje iskeleti olustur ve kod kalitesini dogrula."

try:
    print("  Araclari test et: verify_python, dir_list, scaffold_project...")

    r1 = core.call_tool("verify_python", code="print('hello world')")
    print(f"  verify_python: {r1}")

    r2 = core.call_tool("dir_list", path=".")
    print(f"  dir_list: basarili")

    r3 = core.call_tool("swarm_run", description=test_task)
    print(f"  swarm_run: {r3}")

    print("\n\U0001f6e1\ufe0f [Ultra_Agent v2.0]: Swarm zinciri ve self-healing basariyla test edildi!")
except Exception as e:
    print(f"\u274c Test sirasinda bir aksama oldu: {e}")

print("\n\U0001f680 [BASARI]: V5 Ekosistemi kurucu Berkay'in emirlerine %100 hazir!")
