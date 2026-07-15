@echo off
chcp 65001 >nul
title MAHALAKSMI AIOS v2.1.1

:: ============================================================================
:: MAHALAKSMI AIOS v2.1.1 - Windows One-Click Launcher
:: ============================================================================

cls
echo.
echo  ╔══════════════════════════════════════════════════════════════════════╗
echo  ║                                                                      ║
echo  ║   ███╗   ███╗██╗███████╗██╗ ██████╗ ███████╗                       ║
echo  ║   ████╗ ████║██║██╔════╝██║██╔════╝ ██╔════╝                       ║
echo  ║   ██╔████╔██║██║███████╗██║██║  ███╗█████╗                         ║
echo  ║   ██║╚██╔╝██║██║╚════██║██║██║   ██║██╔══╝                         ║
echo  ║   ██║ ╚═╝ ██║██║███████║██║╚██████╔╝███████╗                       ║
echo  ║   ╚═╝     ╚═╝╚═╝╚══════╝╚═╝ ╚═════╝ ╚══════╝                       ║
echo  ║                                                                      ║
echo  ║   ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ███████╗████████╗███████╗║
echo  ║  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██╔════╝║
echo  ║  ██║     ██║   ██║██╔████╔██║██████╔╝██║     █████╗     ██║   █████╗  ║
echo  ║  ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║   ██╔══╝ ║
echo  ║  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗███████╗   ██║   ███████╗║
echo  ║   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝   ╚══════╝║
echo  ║                                                                      ║
echo  ║                    Enterprise AI Operating System                     ║
echo  ║                         Version 2.1.1                                ║
echo  ║                                                                      ║
echo  ╚══════════════════════════════════════════════════════════════════════╝
echo.

:: Check for Python
echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo         Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Check for virtual environment
set VENV_PATH=.venv
set PYTHON_CMD=python

if exist "%VENV_PATH%\Scripts\activate.bat" (
    echo [*] Activating virtual environment...
    call "%VENV_PATH%\Scripts\activate.bat"
    set PYTHON_CMD=python
) else (
    echo [*] Using global Python...
)

:: Check for required packages
echo [*] Checking dependencies...
%PYTHON_CMD% -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [!] Installing required packages...
    %PYTHON_CMD% -m pip install fastapi uvicorn httpx --quiet
)

:: Start server
echo.
echo [+] Starting MAHALAKSMI AIOS Server...
echo [+] Dashboard will open at: http://localhost:5000/dashboard
echo.
echo    Press Ctrl+C to stop the server
echo.

:: Start uvicorn in background
start /B cmd /c "uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload"

:: Wait for server to start
echo [*] Waiting for server startup...
timeout /t 3 /nobreak >nul

:: Open browser
echo [+] Opening dashboard in browser...
start http://localhost:5000/dashboard

echo.
echo [+] MAHALAKSMI AIOS is running!
echo.
echo    Dashboard: http://localhost:5000/dashboard
echo    API Docs:  http://localhost:5000/docs
echo.

:: Keep terminal open
pause
