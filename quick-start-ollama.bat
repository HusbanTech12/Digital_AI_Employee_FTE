@echo off
REM ============================================
REM Quick Start - Ollama (Free Local AI)
REM ============================================

set OLLAMA=C:\Users\FATTAN~1\AppData\Local\Programs\Ollama\ollama.exe
set VAULT=%~dp0AI_Employee_Vault

echo.
echo ============================================================
echo AI Employee - Ollama Quick Start
echo ============================================================
echo.

echo [1/4] Checking Ollama...
powershell -Command "& { & '%OLLAMA%' --version }" 2>nul
if errorlevel 1 (
    echo ERROR: Ollama not installed!
    echo Download from: https://ollama.com/download
    pause
    exit /b 1
)
echo.

echo [2/4] Checking models...
powershell -Command "& { & '%OLLAMA%' list }" 2>nul
echo.
echo If no models listed above, download one:
echo   powershell -Command "^& { ^& '%OLLAMA%' pull qwen2.5:1.5b }"
echo.
echo Model sizes:
echo   - qwen2.5:1.5b  = 1GB  (fast, recommended for testing)
echo   - qwen2.5:3b    = 2GB  (balanced)
echo   - qwen2.5:7b    = 4.7GB (better quality, slower)
echo.

echo [3/4] Checking Python ollama package...
cd /d "%~dp0scripts"
python -c "import ollama; print('OK - ollama package installed')" 2>nul
if errorlevel 1 (
    echo Installing ollama package...
    pip install ollama
)
echo.

echo [4/4] Vault structure...
if not exist "%VAULT%\Inbox" mkdir "%VAULT%\Inbox"
if not exist "%VAULT%\Needs_Action" mkdir "%VAULT%\Needs_Action"
if not exist "%VAULT%\Plans" mkdir "%VAULT%\Plans"
if not exist "%VAULT%\Done" mkdir "%VAULT%\Done"
echo Vault folders ready.
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo To use AI Employee:
echo.
echo 1. Start watcher (Terminal 1):
echo    cd scripts
echo    python filesystem_watcher.py
echo.
echo 2. Drop a file in: %VAULT%\Inbox\
echo.
echo 3. Run orchestrator (Terminal 2):
echo    cd scripts
echo    python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
echo.
echo ============================================================
echo.
pause
