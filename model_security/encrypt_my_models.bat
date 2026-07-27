@echo off
chcp 65001 >nul
echo ====================================================
echo   Glasses Software - Model Sifreleme (Streaming)
echo ====================================================
echo.

python -c "from cryptography.hazmat.primitives.ciphers import Cipher" 2>nul
if errorlevel 1 (
    echo [!] cryptography yukleniyor...
    pip install cryptography --quiet
)

echo === Mevcut modeller ===
echo.
echo 1) x_fable_coder (8.37 GB) - Qwen2.5-Coder 14B Fine-tune
echo 2) glitch_opus (6.14 GB) - Qwen3.5 9B Fine-tune  
echo 3) Tum modelleri sifrele
echo.
set /p choice="Secim (1-3): "

if "%choice%"=="1" goto encrypt_xfc
if "%choice%"=="2" goto encrypt_glitch
if "%choice%"=="3" goto encrypt_all
echo Gecersiz secim
goto end

:encrypt_xfc
echo.
echo === x_fable_coder Sifreleniyor (STREAMING - RAM dostu) ===
set /p key="Sifreleme anahtari girin: "
python encrypt_model.py -i "C:\Users\ErCuM\.ollama\models\blobs\sha256-ac9bc7a69dab38da1c790838955f1293420b55ab555ef6b4615efa1c1507b1ed" -o "encrypted_models\x_fable_coder.enc" -k "%key%" --streaming
echo.
echo Anahtar: %key%
echo Bu anahtari GUVENLI bir yere kaydedin!
goto end

:encrypt_glitch
echo.
echo === glitch_opus Sifreleniyor (STREAMING - RAM dostu) ===
set /p key="Sifreleme anahtari girin: "
python encrypt_model.py -i "C:\Users\ErCuM\.ollama\models\blobs\sha256-dec52a44569a2a25341c4e4d3fee25846eed4f6f0b936278e3a3c900bb99d37c" -o "encrypted_models\glitch_opus.enc" -k "%key%" --streaming
echo.
echo Anahtar: %key%
goto end

:encrypt_all
echo.
echo === Tum Modeller Sifreleniyor (STREAMING - RAM dostu) ===
set /p key="Sifreleme anahtari girin: "
mkdir encrypted_models 2>nul
echo.
echo [1/2] x_fable_coder sifreleniyor...
python encrypt_model.py -i "C:\Users\ErCuM\.ollama\models\blobs\sha256-ac9bc7a69dab38da1c790838955f1293420b55ab555ef6b4615efa1c1507b1ed" -o "encrypted_models\x_fable_coder.enc" -k "%key%" --streaming
echo.
echo [2/2] glitch_opus sifreleniyor...
python encrypt_model.py -i "C:\Users\ErCuM\.ollama\models\blobs\sha256-dec52a44569a2a25341c4e4d3fee25846eed4f6f0b936278e3a3c900bb99d37c" -o "encrypted_models\glitch_opus.enc" -k "%key%" --streaming
echo.
echo Anahtar: %key%
goto end

:end
echo.
echo ====================================================
echo   TAMAMLANDI!
echo ====================================================
pause
