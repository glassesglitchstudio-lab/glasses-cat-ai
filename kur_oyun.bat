@echo off
title GlassesCat - Oyun Kurulum
color 0A
cls

echo ========================================
echo   OYUN GELISTIRME BAGIMLILIKLARI
echo ========================================
echo.

echo 1. Python surumu kontrol ediliyor...
python --version

echo.
echo 2. Pygame yerine Ursina kuruluyor...
echo    (Ursina - 3D oyunlar icin, Pygame degil!)
pip install ursina

echo.
echo 3. Ek paketler kuruluyor...
pip install numpy pillow

echo.
echo ========================================
echo   KURULUM TAMAMLANDI!
echo ========================================
echo.
echo 3D FPS oyunlar icin artik hazirsin!
echo.
pause