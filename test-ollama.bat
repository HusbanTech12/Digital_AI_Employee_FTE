@echo off
REM ============================================
REM Test Ollama with AI Employee
REM ============================================

set OLLAMA=C:\Users\FATTAN~1\AppData\Local\Programs\Ollama\ollama.exe

echo.
echo ============================================================
echo Testing Ollama Configuration
echo ============================================================
echo.

echo Step 1: Check Ollama version...
powershell -Command "& { & '%OLLAMA%' --version }"
echo.

echo Step 2: List installed models...
powershell -Command "& { & '%OLLAMA%' list }"
echo.

echo Step 3: Check if Ollama is running...
powershell -Command "& { & '%OLLAMA%' ps }"
echo.

echo Step 4: Quick test with installed model...
echo.
echo If no models installed, run:
echo   powershell -Command "^& { ^& '%OLLAMA%' pull qwen2.5:1.5b }"
echo.

echo ============================================================
echo Testing Python ollama package...
echo ============================================================
echo.
cd /d "%~dp0scripts"
python -c "import ollama; print('ollama package version:', ollama.__version__)" 2>nul
if errorlevel 1 (
    echo ERROR: Python ollama package not installed
    echo Run: pip install ollama
) else (
    echo SUCCESS: Python ollama package installed
)
echo.

echo ============================================================
echo Next Steps:
echo ============================================================
echo.
echo 1. Download a model (if not already downloading):
echo    powershell -Command "^& { ^& '%OLLAMA%' pull qwen2.5:1.5b }"
echo.
echo 2. Start the watcher:
echo    cd scripts
echo    python filesystem_watcher.py
echo.
echo 3. Drop a test file in AI_Employee_Vault\Inbox\
echo.
echo 4. Run orchestrator:
echo    python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
echo.
echo ============================================================
pause
