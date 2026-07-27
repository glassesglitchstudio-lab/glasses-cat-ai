@echo off
chcp 65001 >nul
title Glasses Secure Setup
color 0A

echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║     🔐 GLASSES SECURE SETUP                             ║
echo ║     Model Güvenlik Sistemi                              ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Bağımlılık kontrol
python -c "from cryptography.hazmat.primitives.ciphers import Cipher" 2>nul
if errorlevel 1 (
    echo [!] cryptography yükleniyor...
    pip install cryptography --quiet
)

REM Ana scripti çalıştır
python setup.py

pause
