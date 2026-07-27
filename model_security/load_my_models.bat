@echo off
chcp 65001 >nul
echo ====================================================
echo   Glasses Software - Model Yukleyici (Streaming)
echo ====================================================
echo.

python -c "from cryptography.hazmat.primitives.ciphers import Cipher" 2>nul
if errorlevel 1 (
    echo [!] cryptography yukleniyor...
    pip install cryptography --quiet
)

echo === Sifreli model dosyalari ===
echo.

set found=0
if exist "encrypted_models\x_fable_coder.enc" (
    echo [1] x_fable_coder.enc - Bulundu
    set found=1
)
if exist "encrypted_models\glitch_opus.enc" (
    echo [2] glitch_opus.enc - Bulundu
    set found=1
)
if exist "x_fable_coder.enc" (
    echo [1] x_fable_coder.enc - Bulundu
    set found=1
)
if exist "glitch_opus.enc" (
    echo [2] glitch_opus.enc - Bulundu
    set found=1
)

if %found%==0 (
    echo [!] Hicbir .enc dosyasi bulunamadi.
    echo     Once encrypt_my_models.bat ile modelleri sifreleyin.
    pause
    goto end
)

echo.
echo Bu sifreyi Discord'dan ogrenin: https://discord.gg/glassesglitchstudio
echo.
set /p key="Sifre cozme anahtari: "
echo.

echo [1] x_fable_coder yukleniyor (STREAMING)...
if exist "encrypted_models\x_fable_coder.enc" (
    python model_loader.py --enc "encrypted_models\x_fable_coder.enc" --password "%key%" --name "x_fable_coder" --tag "secure"
) else (
    python model_loader.py --enc "x_fable_coder.enc" --password "%key%" --name "x_fable_coder" --tag "secure"
)

echo.
echo [2] glitch_opus yukleniyor (STREAMING)...
if exist "encrypted_models\glitch_opus.enc" (
    python model_loader.py --enc "encrypted_models\glitch_opus.enc" --password "%key%" --name "glitch_opus" --tag "secure"
) else (
    python model_loader.py --enc "glitch_opus.enc" --password "%key%" --name "glitch_opus" --tag "secure"
)

echo.
echo ====================================================
echo   TAMAMLANDI!
echo   Modeller: x_fable_coder:secure, glitch_opus:secure
echo   Kullanim: ollama run x_fable_coder:secure
echo ====================================================
pause

:end
