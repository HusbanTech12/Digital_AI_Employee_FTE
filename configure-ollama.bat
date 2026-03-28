@echo off
REM Configure Ollama for AI Employee Project
REM Handles path with spaces

set OLLAMA_PATH=C:\Users\FATTAN~1\AppData\Local\Programs\Ollama\ollama.exe

echo ============================================================
echo Configuring Ollama for AI Employee
echo ============================================================
echo.

echo Step 1: Testing Ollama...
powershell -Command "& { & '%OLLAMA_PATH%' --version }"
if errorlevel 1 (
    echo ERROR: Ollama not found!
    exit /b 1
)
echo.

echo Step 2: Downloading Qwen2.5:7b model (this may take 5-10 minutes)...
echo Model size: ~4GB
echo.
powershell -Command "& { & '%OLLAMA_PATH%' pull qwen2.5:7b }"
if errorlevel 1 (
    echo WARNING: Download may have failed. Retrying...
    powershell -Command "& { & '%OLLAMA_PATH%' pull qwen2.5:7b }"
)
echo.

echo Step 3: Testing model...
echo.
powershell -Command "& { & '%OLLAMA_PATH%' run qwen2.5:7b 'Say hello in one sentence' }"
echo.

echo Step 4: Creating .env file...
cd /d "%~dp0"
if not exist .env (
    echo AI_PROVIDER=ollama > .env
    echo OLLAMA_MODEL=qwen2.5:7b >> .env
    echo.
    echo Created .env file with Ollama configuration
) else (
    echo .env file already exists
)
echo.

echo ============================================================
echo Configuration Complete!
echo ============================================================
echo.
echo Ollama is configured for AI Employee.
echo.
echo To process tasks:
echo   cd scripts
echo   python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
echo.
echo Or use the batch file:
echo   run-orchestrator.bat
echo.
echo ============================================================
pause
