@echo off
chcp 65001 >nul 2>&1
title Glassescat AI - Build System

echo.
echo  =============================================
echo       NIKO AI - EXE BUILD ARACI
echo  =============================================
echo.

REM Check if PyInstaller is installed
.venv\Scripts\pip.exe show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo  [1/3] PyInstaller kuruluyor...
    .venv\Scripts\pip.exe install pyinstaller
)

REM Clean previous builds
echo  [2/3] Onceki buildler temizleniyor...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Create spec file content
echo  [3/3] Build hazirlaniyor...
echo.

REM Build command
.venv\Scripts\pyinstaller.exe ^
    --name="NikoAI" ^
    --onefile ^
    --windowed ^
    --icon="assets\niko.ico" ^
    --add-data="web;web" ^
    --add-data="templates;templates" ^
    --hidden-import=customtkinter ^
    --hidden-import=pyautogui ^
    --hidden-import=psutil ^
    --hidden-import=requests ^
    --hidden-import=pytesseract ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --collect-all=customtkinter ^
    niko_gui.py ^
    --noconfirm

if %errorlevel% equ 0 (
    echo.
    echo  =============================================
    echo       BUILD BASARILI!
    echo  =============================================
    echo.
    echo  EXE Konumu: dist\NikoAI.exe
    echo.
    echo  Uygulamayi calistirmak icin:
    echo    dist\NikoAI.exe
    echo.
    pause
) else (
    echo.
    echo  [HATA] Build basarisiz oldu!
    echo.
    pause
)
