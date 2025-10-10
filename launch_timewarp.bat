@echo off
REM TimeWarp IDE Launch Script for Windows
REM Cross-platform launcher with Python detection

echo 🚀 Launching TimeWarp IDE 1,1...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Found Python
    python TimeWarp.py
    goto :end
)

REM Try python3 command
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Found Python 3
    python3 TimeWarp.py
    goto :end
)

REM Try py launcher
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Found Python launcher
    py TimeWarp.py
    goto :end
)

echo ❌ Python not found!
echo Please install Python 3 to run TimeWarp IDE
echo Visit: https://www.python.org/downloads/
pause
exit /b 1

:end
echo 👋 TimeWarp IDE session ended.
pause