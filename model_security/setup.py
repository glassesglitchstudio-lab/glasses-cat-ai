"""
╔══════════════════════════════════════════════════════════════════╗
║     GLASSES SECURE SETUP — Tam Sistem Kurulumu                  ║
║     Şifrele → GitHub'a yükle → Ollama'da çalıştır               ║
╚══════════════════════════════════════════════════════════════════╝

Adımlar:
1. Modelleri şifrele
2. GitHub Releases'a yükle
3. Ollama'ya güvenli modelleri kur
4. Her şey hazır!
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from encrypt_model import encrypt_file

# ─── YAPILANDIRMA ───
PROJECT_ROOT = Path(__file__).parent.parent
OLLAMA_BLOBS = Path.home() / ".ollama" / "models" / "blobs"
SECURE_DIR = Path(__file__).parent / "secure_models"
KEY_FILE = Path(__file__).parent / ".key"

MODELS = {
    "x_fable_coder": {
        "blob": "sha256-ac9bc7a69dab38da1c790838955f1293420b55ab555ef6b4615efa1c1507b1ed",
        "desc": "Qwen2.5-Coder 14B Fine-tune",
        "modelfile": "Modelfile_X_Fable_Coder",
        "ollama_name": "glassesglitchstudio/x_fable_coder",
    },
    "glitch_opus": {
        "blob": "sha256-dec52a44569a2a25341c4e4d3fee25846eed4f6f0b936278e3a3c900bb99d37c",
        "desc": "Qwen3.5 9B Fine-tune",
        "modelfile": "Modelfile_GLITCH_OPUS",
        "ollama_name": "glassesglitchstudio/glitch_opus",
    },
}


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🔐 GLASSES SECURE SETUP                                     ║
║     Model Güvenlik Sistemi — Glasses Software                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def get_password():
    """Kullanıcıdan şifre al veya üret."""
    if KEY_FILE.exists():
        with open(KEY_FILE, 'r') as f:
            data = json.load(f)
            saved_key = data.get('key')
            if saved_key:
                print(f"🔑 Kayıtlı anahtar bulundu: {saved_key[:8]}...")
                use_saved = input("   Bu anahtarı kullan? (E/h): ").strip().lower()
                if use_saved != 'h':
                    return saved_key

    print("🔑 Yeni anahtar oluştur:")
    print("   1) Kendim yazayım")
    print("   2) Rastgele üret")
    choice = input("   Seçim (1/2): ").strip()

    if choice == '2':
        import secrets
        key = secrets.token_urlsafe(32)
        print(f"   Üretilen: {key}")
    else:
        key = input("   Anahtar: ").strip()
        if not key:
            print("   ❌ Anahtar boş olamaz!")
            return get_password()

    # Kaydet
    with open(KEY_FILE, 'w') as f:
        json.dump({"key": key, "created": datetime.now().isoformat()}, f, indent=2)
    print(f"   ✅ Anahtar kaydedildi: {KEY_FILE}")

    # .gitignore'a ekle
    gitignore = PROJECT_ROOT / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".key" not in content:
            gitignore.write_text(content + "\n# Model security key\n.key\n")
    else:
        gitignore.write_text(".key\n")

    return key


def step1_encrypt(password):
    """Adım 1: Modelleri şifrele."""
    print("\n" + "="*60)
    print("  ADIM 1: Modelleri Şifrele")
    print("="*60)

    SECURE_DIR.mkdir(parents=True, exist_ok=True)

    for name, info in MODELS.items():
        blob_path = OLLAMA_BLOBS / info["blob"]
        output_path = SECURE_DIR / f"{name}.enc"

        if not blob_path.exists():
            print(f"⚠️  {name} bulunamadı: {blob_path}")
            continue

        print(f"\n📦 {name} — {info['desc']}")
        try:
            encrypt_file(str(blob_path), str(output_path), password)
            print(f"   ✅ {output_path.name}")
        except Exception as e:
            print(f"   ❌ Hata: {e}")
            return False

    print(f"\n📁 Şifreli dosyalar: {SECURE_DIR}")
    return True


def step2_github_push():
    """Adım 2: GitHub Releases'a yükle."""
    print("\n" + "="*60)
    print("  ADIM 2: GitHub Releases'a Yükle")
    print("="*60)

    # GitHub CLI kontrol
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ GitHub CLI (gh) yüklü değil")
            print("   İndir: https://cli.github.com/")
            return False
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) bulunamadı")
        print("   İndir: https://cli.github.com/")
        return False

    # Repo adı
    repo = "glassesglitchstudio-lab/glasses-cat-ai"
    print(f"📦 Repo: {repo}")

    # Tag oluştur
    tag = f"secure-v{datetime.now().strftime('%Y%m%d')}"
    print(f"🏷️  Tag: {tag}")

    # Enc dosyalarını bul
    enc_files = list(SECURE_DIR.glob("*.enc"))
    if not enc_files:
        print("❌ Şifreli dosya bulunamadı. Önce Adım 1'i çalıştır.")
        return False

    print(f"\n📋 Yüklenecek dosyalar:")
    for f in enc_files:
        size_gb = f.stat().st_size / 1e9
        print(f"   • {f.name} ({size_gb:.2f} GB)")

    confirm = input("\n   Devam? (E/h): ").strip().lower()
    if confirm == 'h':
        print("   İptal edildi.")
        return False

    # GitHub'a release oluştur ve yükle
    print("\n📤 GitHub'a yükleniyor...")
    cmd = ['gh', 'release', 'create', tag, '--repo', repo,
           '--title', f'Secure Models {tag}',
           '--notes', 'Şifreli model dosyaları (AES-256-CBC)']

    for f in enc_files:
        cmd.append(str(f))

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Başarıyla yüklendi!")
        print(f"   🔗 {result.stdout.strip()}")
        return True
    else:
        print(f"❌ Yükleme hatası: {result.stderr}")
        return False


def step3_ollama_setup(password):
    """Adım 3: Ollama'da güvenli modelleri kur."""
    print("\n" + "="*60)
    print("  ADIM 3: Ollama Güvenli Modelleri Kur")
    print("="*60)

    import tempfile

    for name, info in MODELS.items():
        enc_file = SECURE_DIR / f"{name}.enc"
        if not enc_file.exists():
            print(f"⚠️  {name}.enc bulunamadı")
            continue

        print(f"\n🔐 {name} çözülüyor...")
        try:
            from model_loader import decrypt_to_memory
            model_data, metadata = decrypt_to_memory(str(enc_file), password)
        except Exception as e:
            print(f"   ❌ Çözme hatası: {e}")
            continue

        # Modelfile bul
        modelfile_path = PROJECT_ROOT / "gulmzcetiner" / info["modelfile"]

        with tempfile.TemporaryDirectory(prefix="glasses_") as tmpdir:
            gguf_path = Path(tmpdir) / metadata['original_name']
            with open(gguf_path, 'wb') as f:
                f.write(model_data)

            # Modelfile oluştur
            if modelfile_path.exists():
                content = modelfile_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                lines[0] = f'FROM {gguf_path}'
                modelfile_content = '\n'.join(lines)
            else:
                modelfile_content = f'FROM {gguf_path}\n'

            mf_path = Path(tmpdir) / 'Modelfile'
            mf_path.write_text(modelfile_content, encoding='utf-8')

            # Güvenli tag ile yükle
            secure_name = f"{name}:secure"
            print(f"   🚀 Ollama'ya yükleniyor: {secure_name}")

            result = subprocess.run(
                ['ollama', 'create', secure_name, '-f', str(mf_path)],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"   ✅ {secure_name} yüklendi!")
            else:
                print(f"   ❌ Hata: {result.stderr}")

    print(f"\n📋 Kullanım:")
    print(f"   ollama run x_fable_coder:secure")
    print(f"   ollama run glitch_opus:secure")


def step4_verify():
    """Adım 4: Doğrulama."""
    print("\n" + "="*60)
    print("  ADIM 4: Doğrulama")
    print("="*60)

    # Enc dosyaları
    enc_files = list(SECURE_DIR.glob("*.enc"))
    print(f"\n📁 Şifreli dosyalar: {len(enc_files)}")
    for f in enc_files:
        size_gb = f.stat().st_size / 1e9
        print(f"   ✅ {f.name} ({size_gb:.2f} GB)")

    # Ollama modelleri
    print(f"\n🤖 Ollama güvenli modeller:")
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            if ':secure' in line:
                print(f"   ✅ {line.strip()}")

    # Anahtar
    if KEY_FILE.exists():
        with open(KEY_FILE, 'r') as f:
            data = json.load(f)
            key = data.get('key', '')
            print(f"\n🔑 Anahtar: {key[:8]}... (tamamı KEY.txt'de)")

    print(f"\n{'='*60}")
    print(f"  ✅ TÜM ADIMLAR TAMAMLANDI!")
    print(f"{'='*60}")
    print(f"""
  📋 Özet:
  • Modeller şifreli → {SECURE_DIR}
  • GitHub'da → glassesglitchstudio-lab/glasses-cat-ai (releases)
  • Ollama'da → x_fable_coder:secure, glitch_opus:secure
  • Anahtar → .key dosyasında

  🎯 Kullanım:
  • Modelle konuş: ollama run x_fable_coder:secure
  • Python'dan: model_loader.py ile yükle
  • Dağıt: GitHub Releases'dan .enc indirilsin
    """)


def main():
    clear_screen()
    print_banner()

    # cryptography kontrol
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher
    except ImportError:
        print("❌ cryptography yüklü değil")
        print("   pip install cryptography")
        return

    # Adımlar
    password = get_password()

    print("\n📋 Yapılacaklar:")
    print("   1) Modelleri şifrele")
    print("   2) GitHub'a yükle")
    print("   3) Ollama'ya kur")
    print("   4) Doğrula")
    print()

    start = input("Başlamak için Enter'a bas... ")

    if not step1_encrypt(password):
        return

    if input("\nGitHub'a yüklemek ister misin? (E/h): ").strip().lower() != 'h':
        step2_github_push()

    if input("\nOllama'ya kurmak ister misin? (E/h): ").strip().lower() != 'h':
        step3_ollama_setup(password)

    step4_verify()


if __name__ == '__main__':
    main()
