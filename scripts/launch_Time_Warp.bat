@echo off
REM Time_Warp IDE Launch Script for Windows
REM Cross-platform launcher with Python detection

echo 🚀 Launching Time_Warp IDE 1.1...

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Found Python
    python Time_Warp.py
    goto :end
)

REM Try python3 command
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Found Python 3
    python3 Time_Warp.py
    goto :end
)

REM Try py launcher
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Found Python launcher
    py Time_Warp.py
    goto :end
)

echo ❌ Python not found!
echo Please install Python 3 to run Time_Warp IDE
echo Visit: https://www.python.org/downloads/
pause
exit /b 1

:end
echo 👋 Time_Warp IDE session ended.
pause