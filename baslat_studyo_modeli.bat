@echo off
chcp 65001 >nul
title GlassesGlitchStudio - ShadowCat-R1 14B Yerel Stüdyo Sunucusu
echo ===================================================================
echo   👑 GlassesGlitchStudio & Elytra-ai — ShadowCat-R1 14B Yerel Motor
echo ===================================================================
echo.
echo [1/2] ShadowCat-R1 14B LoRA mimarisi başlatılıyor...
echo [2/2] Sunucu Portu: http://localhost:7860
echo.
cd /d "%~dp0..\shadowcat-r1"
python server.py
pause
