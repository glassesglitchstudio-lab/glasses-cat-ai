"""
Hızlı Şifreleme — Mevcut Ollama modellerini şifrele
Sadece çalıştır: python quick_encrypt.py
"""

import os
import sys
import secrets
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from encrypt_model import encrypt_file

OLLAMA_BLOBS = Path.home() / ".ollama" / "models" / "blobs"
OUTPUT_DIR = Path(__file__).parent / "encrypted_models"

MODELS = {
    "x_fable_coder": {
        "blob": "sha256-ac9bc7a69dab38da1c790838955f1293420b55ab555ef6b4615efa1c1507b1ed",
        "desc": "Qwen2.5-Coder 14B Fine-tune (8.37 GB)"
    },
    "glitch_opus": {
        "blob": "sha256-dec52a44569a2a25341c4e4d3fee25846eed4f6f0b936278e3a3c900bb99d37c",
        "desc": "Qwen3.5 9B Fine-tune (6.14 GB)"
    },
}

def main():
    print("=" * 60)
    print("  Glasses Software — Model Şifreleme")
    print("=" * 60)
    print()

    # Kullanıcıdan anahtar iste
    key = input("🔑 Şifreleme anahtarı girin (boş bırakırsanız rastgele üretilir): ").strip()
    if not key:
        key = secrets.token_urlsafe(32)
        print(f"   Üretilen anahtar: {key}")

    print()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, info in MODELS.items():
        blob_path = OLLAMA_BLOBS / info["blob"]
        output_path = OUTPUT_DIR / f"{name}.enc"

        if not blob_path.exists():
            print(f"⚠️  {name} blob bulunamadı: {blob_path}")
            continue

        print(f"📦 {name} — {info['desc']}")
        try:
            encrypt_file(str(blob_path), str(output_path), key)
        except Exception as e:
            print(f"❌ Hata: {e}")
            continue

    print()
    print("=" * 60)
    print("  TAMAMLANDI!")
    print(f"  Çıktı: {OUTPUT_DIR}")
    print(f"  Anahtar: {key}")
    print()
    print("  ⚠️  Anahtarı GÜVENLİ bir yere kaydedin!")
    print("  ⚠️  Bu anahtarı kimseyle paylaşmayın!")
    print("=" * 60)

    # Anahtar dosyası kaydet
    key_file = OUTPUT_DIR / "KEY.txt"
    with open(key_file, 'w') as f:
        f.write(f"Glasses Software — Model Encryption Key\n")
        f.write(f"========================================\n\n")
        f.write(f"Anahtar: {key}\n\n")
        f.write(f"Bu dosyayı GÜVENLİ bir yere taşıyın!\n")
        f.write(f"Bu dosyayı ASLA GitHub'a yüklemeyin!\n")
    print(f"\n  🔑 Anahtar dosyası: {key_file}")

if __name__ == '__main__':
    main()
