from obsidian_memory import get_obsidian_memory

m = get_obsidian_memory()
print("--- Hafizada Ara: ErCuM ---")
results = m.recall("ErCuM", 5)
for r in results:
    print(f'Dosya: {r["path"]}')
    print(r['content_preview'][:300])
    print()

print("--- Hafizada Ara: kullanici ---")
results = m.recall("kullanici", 5)
for r in results:
    print(f'Dosya: {r["path"]}')
    print(r['content_preview'][:300])
    print()

print("--- Hafizada Ara: merhaba ---")
results = m.recall("merhaba", 5)
for r in results:
    print(f'Dosya: {r["path"]}')
    print(r['content_preview'][:300])
    print()

print("--- Hafizada Ara: user ---")
results = m.recall("user", 5)
for r in results:
    print(f'Dosya: {r["path"]}')
    print(r['content_preview'][:300])
    print()

# Tum memory dosyalarini listele
import os
mem_dir = os.path.join(m.memory_path, "memories")
if os.path.exists(mem_dir):
    files = os.listdir(mem_dir)
    print(f"--- Tum memory dosyalari ({len(files)}) ---")
    for f in files:
        print(f)

conv_dir = os.path.join(m.memory_path, "conversations")
if os.path.exists(conv_dir):
    files = os.listdir(conv_dir)
    print(f"--- Tum conversation dosyalari ({len(files)}) ---")
    for f in files:
        print(f)
