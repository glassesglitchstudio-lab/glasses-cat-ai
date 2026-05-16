
@echo off
cd /d "%~dp0"
echo.
echo ========================================
echo   Installing Niko Requirements...
echo   Directory: %~dp0
echo ========================================
echo.
python -m pip install --upgrade pip
echo.
python -m pip install -r "%~dp0requirements.txt"
echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
pause
