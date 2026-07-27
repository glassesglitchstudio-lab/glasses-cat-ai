"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     MODEL YUKLEYICI — Glasses Software                         ║
║     Sifreli model dosyalarini bellekte cozup Ollama'ya yukler  ║
║     Streaming destegi: buyuk dosyalar icin RAM dostu            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Kullanim:
    # Tek model
    python model_loader.py --enc model.enc --password "ANAHTAR" --name x_fable_coder

    # Modelfile ile
    python model_loader.py --enc model.enc --password "ANAHTAR" --modelfile Modelfile_X_Fable_Coder

    # Batch
    python model_loader.py --dir ./encrypted --password "ANAHTAR"

    # Streaming cozme (buyuk dosyalar icin)
    python model_loader.py --enc model.enc --password "ANAHTAR" --name x_fable_coder --streaming
"""

import argparse
import gc
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding as sym_padding
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

CHUNK_SIZE = 1024 * 1024  # 1MB


def derive_key(password: str, salt: bytes) -> bytes:
    """PBKDF2 ile anahtar turet (encrypt_model.py ile ayni)."""
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations=100_000,
        dklen=32
    )


def read_metadata(encrypted_path: str) -> dict:
    """Sifreli dosyanin metadata'sini oku (sifrecozmeden)."""
    with open(encrypted_path, 'rb') as f:
        metadata_len = int.from_bytes(f.read(4), 'big')
        metadata_bytes = f.read(metadata_len)
        return json.loads(metadata_bytes.decode('utf-8'))


def decrypt_to_memory(encrypted_path: str, password: str) -> tuple[bytes, dict]:
    """Sifreli dosyayi bellege coz. (model, metadata) dondurur."""
    encrypted_path = Path(encrypted_path)

    with open(encrypted_path, 'rb') as f:
        metadata_len = int.from_bytes(f.read(4), 'big')
        metadata_bytes = f.read(metadata_len)
        metadata = json.loads(metadata_bytes.decode('utf-8'))
        ciphertext = f.read()

    salt = bytes.fromhex(metadata['salt'])
    key = derive_key(password, salt)
    algorithm = metadata.get('algorithm', 'AES-256-CBC')

    if algorithm == 'AES-256-CTR':
        # CTR modu
        nonce = bytes.fromhex(metadata['nonce'])
        initial_counter = bytes.fromhex(metadata['initial_counter'])
        counter_block = bytearray(nonce + initial_counter)

        cipher = Cipher(algorithms.AES(key), modes.CTR(bytes(counter_block)), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    else:
        # CBC modu (geriye donuk uyumluluk)
        iv = bytes.fromhex(metadata['iv'])

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = sym_padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded) + unpadder.finalize()

    assert len(plaintext) == metadata['original_size'], "Boyut uyumsuzlugu!"
    return plaintext, metadata


def decrypt_to_file_streaming(encrypted_path: str, password: str, output_path: str) -> bool:
    """Sifreli dosyayi streaming ile disk'e coz (RAM dostu)."""
    metadata = read_metadata(encrypted_path)
    salt = bytes.fromhex(metadata['salt'])
    key = derive_key(password, salt)
    algorithm = metadata.get('algorithm', 'AES-256-CBC')
    original_size = metadata['original_size']

    if algorithm == 'AES-256-CTR':
        nonce = bytes.fromhex(metadata['nonce'])
        initial_counter = bytes.fromhex(metadata['initial_counter'])
        counter_block = bytearray(nonce + initial_counter)

        metadata_len = 4 + len(json.dumps(metadata).encode('utf-8'))
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(encrypted_path, 'rb') as fin, open(output_path, 'wb') as fout:
            fin.read(metadata_len)

            cipher = Cipher(algorithms.AES(key), modes.CTR(bytes(counter_block)), backend=default_backend())
            decryptor = cipher.decryptor()

            enc_size = metadata.get('encrypted_size', original_size)
            bytes_read = 0

            while True:
                chunk = fin.read(CHUNK_SIZE)
                if not chunk:
                    break
                decrypted = decryptor.update(chunk)
                fout.write(decrypted)
                bytes_read += len(chunk)
                progress = (bytes_read / enc_size) * 100 if enc_size > 0 else 100
                print(f"\r  Cozuluyor: {progress:.1f}%", end="", flush=True)

            fout.write(decryptor.finalize())

        print()
        actual = output_path.stat().st_size
        assert actual == original_size, f"Boyut uyumsuzlugu: {actual} != {original_size}"
        return True

    else:
        # CBC - eski yontem (dosyayi disk'e yaz, RAM'den sil)
        model_data, _ = decrypt_to_memory(encrypted_path, password)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(model_data)
        del model_data  # RAM'i serbest birak
        gc.collect()
        return True


def load_model_to_ollama(
    encrypted_path: str,
    password: str,
    model_name: str,
    modelfile_path: Optional[str] = None,
    tag: str = "latest",
    streaming: bool = None
) -> bool:
    """Sifreli modeli coz, gecici GGUF olustur, Ollama'ya yukle."""
    print(f"Sifreli dosya okunuyor: {encrypted_path}")

    metadata = read_metadata(encrypted_path)
    algorithm = metadata.get('algorithm', 'AES-256-CBC')

    # Streaming modunu belirle
    if streaming is None:
        file_size = Path(encrypted_path).stat().st_size
        streaming = algorithm == 'AES-256-CTR' or file_size > 100 * 1024 * 1024

    if streaming:
        # Streaming cozme - dosyayi disk'e yaz
        with tempfile.TemporaryDirectory(prefix="glasses_model_") as tmpdir:
            gguf_path = os.path.join(tmpdir, metadata['original_name'])
            print(f"Streaming cozuluyor...")
            decrypt_to_file_streaming(encrypted_path, password, gguf_path)

            print(f"Ollama'ya yukleniyor: {model_name}:{tag}")
            # Modelfile olustur veya kullan
            if modelfile_path:
                modelfile = Path(modelfile_path)
                content = modelfile.read_text(encoding='utf-8')
                lines = content.split('\n')
                lines[0] = f'FROM {gguf_path}'
                modelfile_content = '\n'.join(lines)
            else:
                modelfile_content = f'FROM {gguf_path}\n'

            mf_path = os.path.join(tmpdir, 'Modelfile')
            with open(mf_path, 'w', encoding='utf-8') as f:
                f.write(modelfile_content)

            result = subprocess.run(
                ['ollama', 'create', f'{model_name}:{tag}', '-f', mf_path],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"Basariyla yuklendi: {model_name}:{tag}")
                return True
            else:
                print(f"Yukleme hatasi: {result.stderr}")
                return False
    else:
        # CBC - bellege coz, disk'e yaz, RAM'den sil
        print(f"  CBC cozuluyor ({metadata.get('original_size', 0) / 1e9:.2f} GB)...")
        model_data, meta = decrypt_to_memory(encrypted_path, password)
        print(f"  Cozuldu: {meta['original_name']} ({len(model_data) / 1e9:.2f} GB)")

        with tempfile.TemporaryDirectory(prefix="glasses_model_") as tmpdir:
            gguf_path = os.path.join(tmpdir, meta['original_name'])
            with open(gguf_path, 'wb') as f:
                f.write(model_data)
            del model_data  # RAM'i hemen serbest birak
            gc.collect()

            mf_path = os.path.join(tmpdir, 'Modelfile')
            with open(mf_path, 'w', encoding='utf-8') as f:
                f.write(f'FROM {gguf_path}\n')

            full_name = f"{model_name}:{tag}"
            print(f"  Ollama'ya yukleniyor: {full_name}")
            result = subprocess.run(
                ['ollama', 'create', full_name, '-f', mf_path],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"  {full_name} yuklendi!")
                return True
            else:
                print(f"  Yukleme hatasi: {result.stderr}")
                return False


def batch_load(directory: str, password: str):
    """Dizindeki tum .enc dosyalarini Ollama'ya yukle."""
    directory = Path(directory)
    enc_files = list(directory.glob("*.enc"))

    if not enc_files:
        print(f"{directory} icinde .enc dosyasi bulunamadi")
        return

    print(f"{len(enc_files)} sifreli dosya bulundu")
    for enc_file in enc_files:
        model_name = enc_file.stem
        print(f"\n{'='*50}")
        print(f"Yukleniyor: {model_name}")
        load_model_to_ollama(str(enc_file), password, model_name)


def verify_password(encrypted_path: str, password: str) -> bool:
    """Sifre dogru mu kontrol et (dosyayi tamamen cozmeden)."""
    try:
        decrypt_to_memory(encrypted_path, password)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description='Model Yukleyici (Sifreli -> Ollama)')
    parser.add_argument('--enc', '-e', help='Sifreli model dosyasi (.enc)')
    parser.add_argument('--password', '-p', required=True, help='Sifre cozme anahtari')
    parser.add_argument('--name', '-n', help='Ollama model adi (varsayilan: dosya adi)')
    parser.add_argument('--tag', '-t', default='latest', help='Ollama tag (varsayilan: latest)')
    parser.add_argument('--modelfile', '-f', help='Modelfile yolu (opsiyonel)')
    parser.add_argument('--dir', '-d', help='Toplu yukleme dizini')
    parser.add_argument('--verify', action='store_true', help='Sadece sifreyi dogrula')
    parser.add_argument('--streaming', action='store_true', help='Zorla streaming cozme')
    parser.add_argument('--info', action='store_true', help='Sadece metadata goster')

    args = parser.parse_args()

    if not HAS_CRYPTO:
        print("cryptography yuklu degil: pip install cryptography")
        sys.exit(1)

    if args.info and args.enc:
        meta = read_metadata(args.enc)
        print(json.dumps(meta, indent=2))
        sys.exit(0)

    if args.verify:
        if verify_password(args.enc, args.password):
            print("Sifre dogru")
        else:
            print("Sifre yanlis")
        sys.exit(0)

    if args.dir:
        batch_load(args.dir, args.password)
    elif args.enc:
        name = args.name or Path(args.enc).stem
        load_model_to_ollama(args.enc, args.password, name, args.modelfile, args.tag, args.streaming)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
