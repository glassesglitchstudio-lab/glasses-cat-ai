@echo off
setlocal enabledelayedexpansion

title Glassescat AI - Baslangic

:VENV_KONTROL
if not exist ".venv\Scripts\python.exe" (
    echo [HATA] .venv klasoru bulunamadi!
    echo Lutfen: python -m venv .venv
    echo.
    pause
    exit /b 1
)

set "PYTHON=.venv\Scripts\python.exe"
set "PIP=.venv\Scripts\pip.exe"

:ANA_MENU
cls
echo.
echo  ===============================================
echo           NIKO AI - SISTEM BASLATICI
echo  ===============================================
echo.
call :PORT_KONTROL
echo.
echo  [1] Ollama AI Baslat
echo  [2] Flask Web Sunucu (port 5000)
echo  [3] FastAPI Sunucu (port 8000)
echo  [4] Hepsini Baslat
echo  [S] Sistem Bilgisi
echo  [R] Gerekli Paketlari Kontrol Et
echo  [M] Main.py Baslat
echo  [L] Log Dosyasini Goster
echo  [K] Servisleri Yeniden Baslat
echo  [5] Glassescat AI Agent (Hermes)
echo  [6] Glassescat AI GUI (Desktop App)
echo  [7] Web App (new - Flask + Tema)
echo  [A] Servisleri Akilli Baslat (Ollama kontrol + Web)
echo  [B] Build EXE
echo  [0] Cikis
echo  ===============================================
echo.

set /p SECIM="  Seciminiz: "

if "%SECIM%"=="0" goto CIKIS
if "%SECIM%"=="1" goto OLLAMA
if "%SECIM%"=="2" goto FLASK
if "%SECIM%"=="3" goto FASTAPI
if "%SECIM%"=="4" goto HEPSINI
if /i "%SECIM%"=="S" goto STATUS
if /i "%SECIM%"=="R" goto REQUIREMENTS
if /i "%SECIM%"=="M" goto MAIN
if /i "%SECIM%"=="L" goto LOGS
if /i "%SECIM%"=="K" goto RESTART
if "%SECIM%"=="5" goto NIKO_AGENT
if "%SECIM%"=="6" goto NIKO_GUI
if "%SECIM%"=="7" goto WEB_APP
if /i "%SECIM%"=="A" goto SMART_START
if /i "%SECIM%"=="B" goto BUILD_EXE

echo.
echo  [!] Gecersiz secim!
timeout /t 1 >nul
goto ANA_MENU

:PORT_KONTROL
echo  [PORT DURUMU]
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:5000') | Out-Null; Write-Host '  [5000] Flask:   AKTIF' -ForegroundColor Green } catch { Write-Host '  [5000] Flask:   PASIF' -ForegroundColor Red }" 2>nul
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:8000') | Out-Null; Write-Host '  [8000] FastAPI: AKTIF' -ForegroundColor Green } catch { Write-Host '  [8000] FastAPI: PASIF' -ForegroundColor Red }" 2>nul
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:11434/api/tags') | Out-Null; Write-Host '  [11434] Ollama: AKTIF' -ForegroundColor Green } catch { Write-Host '  [11434] Ollama: PASIF' -ForegroundColor Red }" 2>nul
goto :eof

:OLLAMA
cls
echo.
echo  === OLLAMA AI ===
echo.
ollama list 2>nul
if errorlevel 1 (
    echo.
    echo  [HATA] Ollama kurulu degil!
    echo  Kurulum: https://ollama.ai/download
    echo.
    pause
    goto ANA_MENU
)
echo.
echo  [1] Servisi Baslat
echo  [2] Geri
echo.
set /p OLL_SEC="Secim: "
if "%OLL_SEC%"=="1" (
    start cmd /k "title Ollama AI && ollama serve"
    echo.
    echo  [OK] Ollama baslatildi!
    timeout /t 2 >nul
    goto ANA_MENU
)
if "%OLL_SEC%"=="2" goto ANA_MENU
goto OLLAMA

:FLASK
cls
echo.
echo  === FLASK WEB SUNUCU ===
echo.
echo  Flask baslatiliyor...
start /min cmd /k "title GlassesCat Web App && cd /d %CD% && %PYTHON% web/app.py"
echo.
echo  [OK] Web App baslatildi (arka planda)
echo  Adres: http://localhost:5000
echo.
pause
goto ANA_MENU

:FASTAPI
cls
echo.
echo  === FASTAPI SUNUCU ===
echo.
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:8000') | Out-Null; exit 0 } catch { exit 1 }" 2>nul
if not errorlevel 1 (
    echo  [UYARI] FastAPI zaten calisiyor!
    echo.
    pause
    goto ANA_MENU
)
echo  FastAPI port 8000'de baslatiliyor...
start cmd /k "title FastAPI Server && %PYTHON% -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 >nul
echo.
echo  [OK] FastAPI baslatildi!
echo  API: http://localhost:8000
echo  Docs: http://localhost:8000/docs
echo.
pause
goto ANA_MENU

:HEPSINI
cls
echo.
echo  === TUM SERVISLERI BASLATMA ===
echo.
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:11434') | Out-Null; exit 0 } catch { exit 1 }" 2>nul
if errorlevel 1 (
    echo  [1/3] Ollama baslatiliyor...
    start cmd /k "title Ollama AI && ollama serve"
    timeout /t 1 >nul
)
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:5000/login') | Out-Null; exit 0 } catch { exit 1 }" 2>nul
if errorlevel 1 (
    echo  [2/3] Web App baslatiliyor...
    start cmd /k "title GlassesCat Web App && cd /d %CD% && %PYTHON% web/app.py"
    timeout /t 5 >nul
)
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:8000') | Out-Null; exit 0 } catch { exit 1 }" 2>nul
if errorlevel 1 (
    echo  [3/3] FastAPI baslatiliyor...
    start cmd /k "title FastAPI Server && %PYTHON% -m uvicorn server:app --host 0.0.0.0 --port 8000"
    timeout /t 1 >nul
)
echo.
echo  Tum servisler baslatildi!
echo  Ollama:  http://localhost:11434
echo  Web App: http://localhost:5000
echo  FastAPI: http://localhost:8000
echo.
pause
goto ANA_MENU

:STATUS
cls
echo.
echo  === SISTEM DURUMU ===
echo.
echo  Python:
%PYTHON% --version 2>nul
echo.
echo  Pip:
%PIP% --version 2>nul
echo.
echo  Ollama:
ollama list 2>nul
echo.
echo  Port Durumlari:
call :PORT_KONTROL
echo.
pause
goto ANA_MENU

:MAIN
cls
echo.
echo  === MAIN.PY BASLATMA ===
echo  Main.py baslatiliyor...
start cmd /k "title Glassescat AI - Main && %PYTHON% main.py"
timeout /t 2 >nul
echo  [OK] Main.py baslatildi!
pause
goto ANA_MENU

:LOGS
cls
echo.
echo  === LOG DOSYALARI ===
echo.
dir /b *.log 2>nul
echo.
echo  [G] Geri
set /p LOG_SEC="Secim: "
if /i "%LOG_SEC%"=="G" goto ANA_MENU
goto LOGS

:RESTART
cls
echo.
echo  === SERVISLERI YENIDEN BASLAT ===
echo.
echo  [1] Ollama yeniden baslat
echo  [2] Flask yeniden baslat
echo  [3] FastAPI yeniden baslat
echo  [4] Hepsi yeniden baslat
echo  [G] Geri
set /p RES_SEC="Secim: "
if "%RES_SEC%"=="1" (
    taskkill /F /IM ollama.exe 2>nul
    timeout /t 1 >nul
    start cmd /k "title Ollama AI && ollama serve"
    echo  [OK] Ollama yeniden baslatildi!
)
if "%RES_SEC%"=="2" (
    taskkill /F /FI "WINDOWTITLE eq GlassesCat*" 2>nul
    timeout /t 1 >nul
    start cmd /k "title GlassesCat Web App && cd /d %CD% && %PYTHON% web/app.py"
    echo  [OK] Web App yeniden baslatildi!
)
if "%RES_SEC%"=="3" (
    taskkill /F /FI "WINDOWTITLE eq FastAPI*" 2>nul
    timeout /t 1 >nul
    start cmd /k "title FastAPI Server && %PYTHON% -m uvicorn server:app --host 0.0.0.0 --port 8000"
    echo  [OK] FastAPI yeniden baslatildi!
)
if "%RES_SEC%"=="4" (
    taskkill /F /IM ollama.exe 2>nul
    taskkill /F /FI "WINDOWTITLE eq Flask*" 2>nul
    taskkill /F /FI "WINDOWTITLE eq FastAPI*" 2>nul
    timeout /t 2 >nul
    echo  Tum servisler yeniden baslatiliyor...
    start cmd /k "title Ollama AI && ollama serve"
    timeout /t 1 >nul
    start cmd /k "title Flask Server && cd /d %CD% && %PYTHON% server.py"
    timeout /t 1 >nul
    start cmd /k "title FastAPI Server && %PYTHON% -m uvicorn server:app --host 0.0.0.0 --port 8000"
    echo  [OK] Hepsi yeniden baslatildi!
)
if /i "%RES_SEC%"=="G" goto ANA_MENU
pause
goto ANA_MENU

:NIKO_AGENT
cls
echo.
echo  === NIKO AI AGENT (HERMES) ===
echo  Niko Agent baslatiliyor...
start cmd /k "title Glassescat AI - Hermes && %PYTHON% niko_agent.py"
timeout /t 2 >nul
echo  [OK] Glassescat AI Agent baslatildi!
pause
goto ANA_MENU

:NIKO_GUI
cls
echo.
echo  === NIKO AI GUI (DESKTOP APP) ===
echo  GUI baslatiliyor...
start cmd /k "title Glassescat AI - Desktop && %PYTHON% niko_gui.py"
timeout /t 2 >nul
echo  [OK] Glassescat AI GUI baslatildi!
pause
goto ANA_MENU

:WEB_APP
cls
echo.
echo  === WEB APP (FLASK + TEMA SISTEMI) ===
echo.
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:5000/login') | Out-Null; exit 0 } catch { exit 1 }" 2>nul
if not errorlevel 1 (
    echo  [OK] Web App calisiyor: http://localhost:5000
    echo.
    pause
    goto ANA_MENU
)
echo  Web App baslatiliyor (port 5000)...
start cmd /k "title GlassesCat Web App && cd /d %CD% && %PYTHON% web/app.py"
timeout /t 3 >nul
echo.
echo  [OK] Web App baslatildi!
echo  Adres: http://localhost:5000
echo.
pause
goto ANA_MENU

:SMART_START
cls
echo.
echo  ===============================================
echo      NIKO AI - AKILLI SERVIS BASLATICI
echo  ===============================================
echo.
echo  Servisler kontrol ediliyor...
echo.

:: Ollama kontrol
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:11434') | Out-Null; exit 0 } catch { exit 1 }" 2>nul
if errorlevel 1 (
    echo  [!] Ollama calismiyor!
    echo.
    echo  [1] Ollama'yı baslat
    echo  [2] Iptal et (Ollama olmadan calisamaz)
    echo.
    set /p OLL_CHOICE="Secim: "
    if "!OLL_CHOICE!"=="1" (
        echo.
        echo  Ollama baslatiliyor...
        start cmd /k "title Ollama AI && ollama serve"
        echo  Ollama basladi, yuklenmesi bekleniyor...
        timeout /t 5 >nul
        
        :: Ollama'nın hazır olmasını bekle
        echo  Ollama kontrol ediliyor...
        :WAIT_OLLAMA
        powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:11434') | Out-Null; exit 0 } catch { exit 1 }" 2>nul
        if errorlevel 1 (
            timeout /t 2 >nul
            set /a WAIT_COUNT+=1
            if !WAIT_COUNT! LSS 15 (
                goto WAIT_OLLAMA
            ) else (
                echo  [HATA] Ollama yuklenemedi! Lutfen manuel baslatin.
                pause
                goto ANA_MENU
            )
        )
        echo  [OK] Ollama hazir!
    ) else (
        goto ANA_MENU
    )
) else (
    echo  [OK] Ollama calisiyor!
)

:: Web App kontrol
echo.
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:5000') | Out-Null; exit 0 } catch { exit 1 }" 2>nul
if errorlevel 1 (
    echo  [!] Web App baslatiliyor...
    start /min cmd /k "title GlassesCat Web App && cd /d %CD% && %PYTHON% web/app.py"
    echo  [OK] Web App baslatildi (arka planda)
) else (
    echo  [OK] Web App calisiyor!
)

:: FastAPI kontrol
echo.
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:8000') | Out-Null; exit 0 } catch { exit 1 }" 2>nul
if errorlevel 1 (
    echo  [!] FastAPI calismiyor, baslatiliyor...
    start cmd /k "title FastAPI Server && %PYTHON% -m uvicorn main:app --host 0.0.0.0 --port 8000"
    timeout /t 3 >nul
    echo  [OK] FastAPI baslatildi!
) else (
    echo  [OK] FastAPI calisiyor!
)

:: Ozet
echo.
echo  ===============================================
echo            SERVIS DURUM RAPORU
echo  ===============================================
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:11434') | Out-Null; Write-Host '  Ollama:    AKTIF' -ForegroundColor Green } catch { Write-Host '  Ollama:    PASIF' -ForegroundColor Red }" 2>nul
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:5000') | Out-Null; Write-Host '  Web App:   AKTIF' -ForegroundColor Green } catch { Write-Host '  Web App:   PASIF' -ForegroundColor Red }" 2>nul
powershell -Command "try { $w = New-Object System.Net.WebClient; $w.DownloadString('http://localhost:8000') | Out-Null; Write-Host '  FastAPI:   AKTIF' -ForegroundColor Green } catch { Write-Host '  FastAPI:   PASIF' -ForegroundColor Red }" 2>nul
echo.
echo  Adresler:
echo  Web App:  http://localhost:5000
echo  FastAPI:  http://localhost:8000
echo.
pause
goto ANA_MENU

:BUILD_EXE
cls
echo.
echo  === NIKO AI EXE BUILD ===
echo.
call build_exe.bat
pause
goto ANA_MENU

:REQUIREMENTS
cls
echo.
echo  === PAKET KONTROLU ===
echo.
%PIP% list --format=freeze > "%TEMP%\pip_list.txt"
set "MISSING=0"
findstr /I /C:"flask" "%TEMP%\pip_list.txt" >nul
if errorlevel 1 (
    echo  [!] Flask eksik
    set "MISSING=1"
)
findstr /I /C:"fastapi" "%TEMP%\pip_list.txt" >nul
if errorlevel 1 (
    echo  [!] FastAPI eksik
    set "MISSING=1"
)
findstr /I /C:"pyautogui" "%TEMP%\pip_list.txt" >nul
if errorlevel 1 (
    echo  [!] PyAutoGUI eksik
    set "MISSING=1"
)
if "%MISSING%"=="0" (
    echo  [OK] Tum gerekli paketler kurulu!
) else (
    echo.
    echo  Eksik paketler kuruluyor...
    %PIP% install -r requirements.txt
)
echo.
pause
goto ANA_MENU

:CIKIS
cls
echo.
echo  Glassescat AI kapatiliyor...
echo  Hosca kalin!
timeout /t 1 >nul
exit
