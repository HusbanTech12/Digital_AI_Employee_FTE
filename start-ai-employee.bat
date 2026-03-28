@echo off
REM AI Employee - Quick Start Script for Windows
REM This script starts the File System Watcher and Orchestrator

echo ============================================
echo AI Employee - Bronze Tier (Qwen Code)
echo ============================================
echo.

REM Set the vault path
set VAULT_PATH=%~dp0AI_Employee_Vault
set SCRIPTS_PATH=%~dp0scripts

echo Vault: %VAULT_PATH%
echo Scripts: %SCRIPTS_PATH%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13+ from https://python.org
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if Qwen is available
qwen --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Qwen Code not found in PATH
    echo Install with: pip install qwen-agent
    echo The orchestrator will work in dry-run mode
    echo.
)

REM Start the File System Watcher in background
echo Starting File System Watcher...
cd /d "%SCRIPTS_PATH%"
start "AI Employee Watcher" python filesystem_watcher.py "%VAULT_PATH%"

echo Watcher started!
echo.
echo ============================================
echo AI Employee is now running!
echo.
echo To process tasks manually, run:
echo   python orchestrator.py --vault "%VAULT_PATH%" --once
echo.
echo To stop the watcher, close the watcher window
echo ============================================
echo.

REM Wait for user to press a key
pause
