@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo ========================================================
echo   Chrome Profile Creator - Build
echo ========================================================
echo.

echo [1/3] Installing dependencies...
python -m pip install --upgrade pip -q
python -m pip install . pyinstaller -q
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [2/3] Building executable...
python build.py
if errorlevel 1 (
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Done! (build and __pycache__ cleaned up)
echo Output folder: %~dp0ChromeProfileTool
echo.
pause
exit /b 0
