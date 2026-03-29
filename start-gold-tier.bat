@echo off
REM Gold Tier Launcher Script
REM Starts all Gold Tier watchers and services

echo ========================================
echo AI Employee - Gold Tier
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

REM Create Logs folders if not exists
if not exist "%VAULT_DIR%Logs" mkdir "%VAULT_DIR%Logs"
if not exist "%VAULT_DIR%Logs\Audit" mkdir "%VAULT_DIR%Logs\Audit"
if not exist "%VAULT_DIR%Logs\Recovery" mkdir "%VAULT_DIR%Logs\Recovery"
if not exist "%VAULT_DIR%Logs\Ralph_Loop" mkdir "%VAULT_DIR%Logs\Ralph_Loop"

REM Start Silver tier watchers in background
echo Starting Filesystem Watcher...
start "FS_Watcher" python "%SCRIPTS_DIR%filesystem_watcher.py" "%VAULT_DIR%"

echo Starting Gmail Watcher...
start "Gmail_Watcher" python "%SCRIPTS_DIR%gmail_watcher.py" "%VAULT_DIR%"

echo Starting WhatsApp Watcher...
start "WhatsApp_Watcher" python "%SCRIPTS_DIR%whatsapp_watcher.py" "%VAULT_DIR%"

echo Starting LinkedIn Post Processor...
start "LinkedIn_Poster" python "%SCRIPTS_DIR%linkedin_poster.py" "%VAULT_DIR%"

REM Start Gold tier watchers
echo Starting Facebook/Instagram Watcher...
start "FB_IG_Watcher" python "%SCRIPTS_DIR%facebook_instagram_watcher.py" "%VAULT_DIR%"

echo Starting Twitter Watcher...
start "Twitter_Watcher" python "%SCRIPTS_DIR%twitter_watcher.py" "%VAULT_DIR%"

echo.
echo ========================================
echo All Gold Tier services started!
echo ========================================
echo.
echo Running Services:
echo   Silver Tier:
echo   - Filesystem Watcher (watching Inbox folder)
echo   - Gmail Watcher (checking every 2 minutes)
echo   - WhatsApp Watcher (checking every 30 seconds)
echo   - LinkedIn Post Processor (checking Approved folder)
echo.
echo   Gold Tier:
echo   - Facebook/Instagram Watcher (checking every 60 seconds)
echo   - Twitter Watcher (checking every 60 seconds)
echo   - Audit Logger (logging all actions)
echo   - Error Recovery (graceful degradation)
echo   - Ralph Wiggum Loop (autonomous completion)
echo.
echo To stop all services:
echo   1. Open Task Manager
echo   2. End all Python tasks
echo   OR
echo   3. Close each console window
echo.
echo Gold Tier Commands:
echo   python %SCRIPTS_DIR%gold_weekly_audit.py    - Generate CEO briefing
echo   python %SCRIPTS_DIR%test_gold_tier.py       - Run Gold Tier tests
echo   python %SCRIPTS_DIR%scheduler.py status     - Check scheduled tasks
echo.
pause
