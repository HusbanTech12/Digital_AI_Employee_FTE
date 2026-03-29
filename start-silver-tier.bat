@echo off
REM Silver Tier Launcher Script
REM Starts all Silver Tier watchers and services

echo ========================================
echo AI Employee - Silver Tier
echo Starting all watchers and services...
echo ========================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
set VAULT_DIR=%SCRIPT_DIR%AI_Employee_Vault
set SCRIPTS_DIR=%SCRIPT_DIR%scripts

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.13+
    pause
    exit /b 1
)

echo Vault: %VAULT_DIR%
echo Scripts: %SCRIPTS_DIR%
echo.

REM Create Logs folder if not exists
if not exist "%VAULT_DIR%Logs" mkdir "%VAULT_DIR%Logs"

REM Start watchers in background
echo Starting Filesystem Watcher...
start "FS_Watcher" python "%SCRIPTS_DIR%filesystem_watcher.py" "%VAULT_DIR%"

echo Starting Gmail Watcher...
start "Gmail_Watcher" python "%SCRIPTS_DIR%gmail_watcher.py" "%VAULT_DIR%"

echo Starting WhatsApp Watcher...
start "WhatsApp_Watcher" python "%SCRIPTS_DIR%whatsapp_watcher.py" "%VAULT_DIR%"

echo Starting LinkedIn Post Processor...
start "LinkedIn_Poster" python "%SCRIPTS_DIR%linkedin_poster.py" "%VAULT_DIR%"

echo.
echo ========================================
echo All Silver Tier services started!
echo ========================================
echo.
echo Running Services:
echo   - Filesystem Watcher (watching Inbox folder)
echo   - Gmail Watcher (checking every 2 minutes)
echo   - WhatsApp Watcher (checking every 30 seconds)
echo   - LinkedIn Post Processor (checking Approved folder)
echo.
echo To stop all services:
echo   1. Open Task Manager
echo   2. End all Python tasks
echo   OR
echo   3. Close each console window
echo.
echo To check status:
echo   python %SCRIPTS_DIR%scheduler.py status
echo.
echo To run tests:
echo   python %SCRIPTS_DIR%test_silver_tier.py
echo.
pause
