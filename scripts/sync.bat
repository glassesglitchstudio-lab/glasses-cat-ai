@echo off
chcp 65001 >nul
title GlassesCat - Sync from GitHub

echo ========================================
echo   GlassesCat - Pull from GitHub
echo ========================================
echo %date% %time%
echo.

:: Stash local changes before pulling
git stash push -m "auto-stash-%date%-%time%" --include-untracked 2>nul
if errorlevel 1 echo Stash onemsiz veya bos

:: Pull
git pull origin main
if errorlevel 1 (
    echo HATA: Pull basarisiz!
    echo.
    echo Cozum: Conflict varsa su dosyalari kontrol et:
    git status --short
    pause
    exit /b 1
)

:: Stash geri al
git stash pop 2>nul

echo.
echo ========================================
echo   SENKRONIZASYON TAMAM!
echo ========================================
echo.
