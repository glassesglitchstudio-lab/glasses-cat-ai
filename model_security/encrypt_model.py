"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     MODEL ŞİFRELEME ARACI — Glasses Software                   ║
║     Fine-tuned model ağırlıklarını AES-256 ile şifreler        ║
║     Büyük dosyalar için STREAMING desteği (1MB chunk)           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Kullanım:
    python encrypt_model.py --input model.gguf --output model.enc
    python encrypt_model.py --input model.gguf --output model.enc --key "ANAHTAR"
    python encrypt_model.py --batch --input-dir ./models --output-dir ./encrypted
    python encrypt_model.py --input big_model.gguf --output big.enc --streaming
"""

import argparse
import hashlib
import json
import os
import sys
import secrets
import struct
from pathlib import Path
from typing import Optional

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding as sym_padding
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    print("cryptography yuklu degil: pip install cryptography")

CHUNK_SIZE = 1024 * 1024  # 1MB streaming chunk
MEMORY_THRESHOLD = 100 * 1024 * 1024  # 100MB altinda CBC (eski format), ustunde CTR (streaming)


def derive_key(password: str, salt: bytes) -> bytes:
    """PBKDF2 ile anahtar turet."""
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations=100_000,
        dklen=32
    )


def _get_cipher(key: str, mode_name: str, iv_or_nonce: bytes):
    """AES cipher olustur."""
    if mode_name == "AES-256-CTR":
        return Cipher(algorithms.AES(key), modes.CTR(iv_or_nonce), backend=default_backend())
    else:
        return Cipher(algorithms.AES(key), modes.CBC(iv_or_nonce), backend=default_backend())


def encrypt_file(input_path: str, output_path: str, password: str, streaming: bool = None) -> dict:
    """
    Dosyayi AES-256 ile sifrele.
    streaming=None ise otomatik: 100MB+ ise CTR streaming, degilse CBC.
    streaming=True ise zorla CTR streaming kullanir.
    """
    if not HAS_CRYPTO:
        raise RuntimeError("cryptography paketi yuklu degil")

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Dosya bulunamadi: {input_path}")

    file_size = input_path.stat().st_size

    # Streaming modunu belirle
    if streaming is None:
        streaming = file_size > MEMORY_THRESHOLD

    salt = secrets.token_bytes(16)

    if streaming:
        return _encrypt_streaming(input_path, output_path, password, salt, file_size)
    else:
        return _encrypt_cbc(input_path, output_path, password, salt, file_size)


def _encrypt_cbc(input_path: Path, output_path: Path, password: str, salt: bytes, file_size: int) -> dict:
    """Klasik CBC sifreleme (kucuk dosyalar icin)."""
    iv = secrets.token_bytes(16)
    key = derive_key(password, salt)

    print(f"Okunuyor: {input_path} ({file_size / 1e9:.2f} GB)")
    with open(input_path, 'rb') as f:
        plaintext = f.read()

    padder = sym_padding.PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()

    print("Sifreleniyor (CBC)...")
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    metadata = {
        "version": 1,
        "algorithm": "AES-256-CBC",
        "key_derivation": "PBKDF2-SHA256",
        "iterations": 100_000,
        "salt": salt.hex(),
        "iv": iv.hex(),
        "original_size": file_size,
        "encrypted_size": len(ciphertext),
        "original_name": input_path.name,
    }

    metadata_bytes = json.dumps(metadata).encode('utf-8')
    metadata_len = len(metadata_bytes).to_bytes(4, 'big')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(metadata_len)
        f.write(metadata_bytes)
        f.write(ciphertext)

    print(f"Sifrelendi: {output_path} ({output_path.stat().st_size / 1e9:.2f} GB)")
    return metadata


def _encrypt_streaming(input_path: Path, output_path: Path, password: str, salt: bytes, file_size: int) -> dict:
    """CTR streaming sifreleme - 1MB chunk, RAM'i zorlamaz."""
    nonce = secrets.token_bytes(16)  # CTR icin nonce
    key = derive_key(password, salt)

    # CTR initial counter = 0
    initial_counter = b'\x00' * 16

    # Metadata onceden yazilir, sonra ciphertext akar
    metadata = {
        "version": 2,
        "algorithm": "AES-256-CTR",
        "key_derivation": "PBKDF2-SHA256",
        "iterations": 100_000,
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "initial_counter": initial_counter.hex(),
        "original_size": file_size,
        "encrypted_size": file_size,  # CTR'da boyut degismez
        "original_name": input_path.name,
        "chunk_size": CHUNK_SIZE,
    }

    metadata_bytes = json.dumps(metadata).encode('utf-8')
    metadata_len = len(metadata_bytes).to_bytes(4, 'big')

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Streaming sifreleme: {input_path} ({file_size / 1e9:.2f} GB)")
    print(f"  Chunk boyutu: {CHUNK_SIZE // 1024} KB")
    print(f"  Mod: AES-256-CTR (RAM dostu)")

    with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
        # Metadata yaz
        fout.write(metadata_len)
        fout.write(metadata_bytes)

        # CTR cipher baslat
        # Counter'i nonce ile birlestir: nonce (8 byte) + counter (8 byte)
        # Her chunk icin counter: chunk_index * (chunk_size / 16)
        counter_block = bytearray(nonce + initial_counter)

        cipher = Cipher(algorithms.AES(key), modes.CTR(bytes(counter_block)), backend=default_backend())
        encryptor = cipher.encryptor()

        chunk_index = 0
        bytes_written = 0

        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break

            encrypted_chunk = encryptor.update(chunk)
            fout.write(encrypted_chunk)
            bytes_written += len(encrypted_chunk)

            # Ilerleme goster
            progress = (bytes_written / file_size) * 100 if file_size > 0 else 100
            mb_done = bytes_written / (1024 * 1024)
            mb_total = file_size / (1024 * 1024)
            print(f"\r  {progress:.1f}% - {mb_done:.0f}/{mb_total:.0f} MB", end="", flush=True)

            chunk_index += 1

        # Finalize
        fout.write(encryptor.finalize())

    print()
    print(f"Sifrelendi: {output_path} ({output_path.stat().st_size / 1e9:.2f} GB)")
    return metadata


def decrypt_file_to_memory(encrypted_path: str, password: str) -> bytes:
    """Sifreli dosyayi bellege coz (eski CBC modu icin)."""
    if not HAS_CRYPTO:
        raise RuntimeError("cryptography paketi yuklu degil")

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
        # CTR modu - streaming cozum
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
    return plaintext


def decrypt_file_streaming(encrypted_path: str, password: str, output_path: str, progress_callback=None) -> bool:
    """
    Sifreli dosyayi streaming ile coz ve disk'e yaz.
    Buyuk dosyalar icin RAM dostu.
    """
    if not HAS_CRYPTO:
        raise RuntimeError("cryptography paketi yuklu degil")

    encrypted_path = Path(encrypted_path)
    output_path = Path(output_path)

    with open(encrypted_path, 'rb') as f:
        metadata_len = int.from_bytes(f.read(4), 'big')
        metadata_bytes = f.read(metadata_len)
        metadata = json.loads(metadata_bytes.decode('utf-8'))

    salt = bytes.fromhex(metadata['salt'])
    key = derive_key(password, salt)
    algorithm = metadata.get('algorithm', 'AES-256-CBC')
    original_size = metadata['original_size']

    if algorithm == 'AES-256-CTR':
        nonce = bytes.fromhex(metadata['nonce'])
        initial_counter = bytes.fromhex(metadata['initial_counter'])
        counter_block = bytearray(nonce + initial_counter)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Streaming cozme: {encrypted_path} -> {output_path}")

        with open(encrypted_path, 'rb') as fin, open(output_path, 'wb') as fout:
            # Metadata'yi atla
            fin.read(4 + metadata_len)

            cipher = Cipher(algorithms.AES(key), modes.CTR(bytes(counter_block)), backend=default_backend())
            decryptor = cipher.decryptor()

            enc_size = metadata.get('encrypted_size', original_size)
            bytes_read = 0

            while True:
                chunk = fin.read(CHUNK_SIZE)
                if not chunk:
                    break

                decrypted_chunk = decryptor.update(chunk)
                fout.write(decrypted_chunk)
                bytes_read += len(chunk)

                if progress_callback:
                    progress_callback(bytes_read, enc_size)
                else:
                    progress = (bytes_read / enc_size) * 100 if enc_size > 0 else 100
                    print(f"\r  {progress:.1f}%", end="", flush=True)

            fout.write(decryptor.finalize())

        print()
        actual_size = output_path.stat().st_size
        assert actual_size == original_size, f"Boyut uyumsuzlugu: {actual_size} != {original_size}"
        print(f"Cozuldu: {output_path} ({actual_size / 1e9:.2f} GB)")
        return True

    else:
        # CBC - eski yontem (dosyayi bellege oku)
        with open(encrypted_path, 'rb') as f:
            f.read(4 + metadata_len)  # metadata'yı atla
            ciphertext = f.read()

        iv = bytes.fromhex(metadata['iv'])
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = sym_padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded) + unpadder.finalize()

        assert len(plaintext) == original_size, "Boyut uyumsuzlugu!"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(plaintext)

        print(f"Cozuldu: {output_path} ({original_size / 1e9:.2f} GB)")
        return True


def generate_key_file(password: str, output_path: str):
    """Anahtar dosyasi olustur."""
    key_hash = hashlib.sha256(password.encode()).hexdigest()
    metadata = {
        "key_hash": key_hash,
        "algorithm": "AES-256 (CBC + CTR streaming)",
        "note": "Bu dosyayi guvende tutun. Model dosyasini acmak icin gerekli.",
    }
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Anahtar dosyasi: {output_path}")


def batch_encrypt(input_dir: str, output_dir: str, password: str, streaming: bool = None):
    """Toplu sifreleme."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extensions = ('.gguf', '.safetensors', '.bin', '.pt', '.pth')
    files = [f for f in input_dir.iterdir() if f.suffix.lower() in extensions]

    if not files:
        print(f"{input_dir} icinde sifrelenecek model dosyasi bulunamadi")
        return

    print(f"{len(files)} dosya bulundu")
    for f in files:
        output_file = output_dir / f"{f.stem}.enc"
        encrypt_file(str(f), str(output_file), password, streaming=streaming)


def main():
    parser = argparse.ArgumentParser(description='Model Sifreleme Araci')
    parser.add_argument('--input', '-i', help='Sifrelenecek dosya yolu')
    parser.add_argument('--output', '-o', help='Cikti dosya yolu (.enc)')
    parser.add_argument('--key', '-k', help='Sifreleme anahtari (yoksa rastgele uretilir)')
    parser.add_argument('--batch', action='store_true', help='Toplu sifreleme modu')
    parser.add_argument('--input-dir', help='Toplu mod: girdi klasoru')
    parser.add_argument('--output-dir', help='Toplu mod: cikti klasoru')
    parser.add_argument('--generate-key', action='store_true', help='Anahtar dosyasi olustur')
    parser.add_argument('--streaming', action='store_true', help='Zorla streaming modu (buyuk dosyalar icin)')
    parser.add_argument('--no-streaming', action='store_true', help='Zorla CBC modu (kucuk dosyalar icin)')
    parser.add_argument('--decrypt', action='store_true', help='Sifre cozme modu')
    parser.add_argument('--password', '-p', help='Sifre cozme anahtari')

    args = parser.parse_args()

    if not args.key:
        args.key = secrets.token_urlsafe(32)
        print(f"Uretilen anahtar: {args.key}")
        print(f"   Bu anahtari GUVENLI bir yere kaydedin!")

    streaming = None
    if args.streaming:
        streaming = True
    elif args.no_streaming:
        streaming = False

    if args.decrypt:
        if not args.input or not args.password:
            print("Sifre cozme icin --input ve --password gerekli")
            sys.exit(1)
        output = args.output or args.input.replace('.enc', '.dec')
        decrypt_file_streaming(args.input, args.password, output)
    elif args.batch:
        if not args.input_dir or not args.output_dir:
            print("Toplu mod icin --input-dir ve --output-dir gerekli")
            sys.exit(1)
        batch_encrypt(args.input_dir, args.output_dir, args.key, streaming=streaming)
    elif args.input:
        if not args.output:
            args.output = args.input + '.enc'
        encrypt_file(args.input, args.output, args.key, streaming=streaming)
    else:
        parser.print_help()
        sys.exit(1)

    if args.generate_key:
        generate_key_file(args.key, 'model_key.json')


if __name__ == '__main__':
    main()
