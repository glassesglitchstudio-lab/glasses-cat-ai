@echo off
chcp 65001 >nul
title GlassesCat - Tek Tusla Push

setlocal enabledelayedexpansion

echo ========================================
echo   GlassesCat - Push to GitHub ^& Ollama
echo ========================================
echo.

echo [1/4] Git add...
git add -A

:: Akilli commit mesaji - degisen dosyalara bak
set commit_msg=update
for /f "tokens=2 delims= " %%f in ('git status --short 2^>nul') do (
    set "first_file=%%f"
    goto :found
)
:found
if defined first_file (
    for %%x in ("!first_file!") do set "ext=%%~xx"
    if "!ext!"==".py" set commit_msg=python
    if "!ext!"==".bat" set commit_msg=windows
    if "!ext!"==".sh" set commit_msg=linux
    if "!ext!"==".md" set commit_msg=docs
    if "!ext!"==".js" set commit_msg=javascript
    if "!ext!"==".yml" set commit_msg=config
    if "!ext!"==".json" set commit_msg=config
    if "!ext!"==".ps1" set commit_msg=powershell
    set commit_msg=!commit_msg!: !first_file!
) else (
    set commit_msg=V5_AUTO: %date% %time%
)

echo [2/4] Git commit...
git commit -m "!commit_msg!"
if errorlevel 1 (
    echo HATA: Commit basarisiz. Muhtemelen degisiklik yok.
    pause
    exit /b 1
)

echo [3/4] Git push...
git push origin main
if errorlevel 1 (
    echo HATA: Push basarisiz. Internet baglantisi kontrol et.
    pause
    exit /b 1
)

echo [4/4] Ollama model push...
cd /d "%~dp0..\gulmzcetiner"
if exist Modelfile (
    echo Ollama model olusturuluyor...
    ollama create glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE -f Modelfile
    if errorlevel 1 (
        echo Ollama create basarisiz (model zaten var olabilir)
    ) else (
        echo Ollama push...
        ollama push glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE
    )
)

cd /d "%~dp0.."
echo.
echo ========================================
echo   BASARILI! GitHub ^& Ollama guncellendi.
echo   Link: https://github.com/gulmzcetiner/glasses-cat-ai
echo ========================================
pause
