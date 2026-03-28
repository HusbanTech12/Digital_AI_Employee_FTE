@echo off
REM ============================================
REM Quick Start - Bronze Tier
REM ============================================
REM Run this to start the complete system

set VAULT=%~dp0AI_Employee_Vault
set SCRIPTS=%~dp0scripts

echo.
echo ============================================
echo  Starting AI Employee - Bronze Tier
echo ============================================
echo.

REM Check if Ollama is setup
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Ollama not setup. Running setup...
    call "%~dp0setup-ollama.bat"
)

echo [INFO] Vault: %VAULT%
echo.

REM Start watcher in background
echo [1/2] Starting File Watcher...
start "AI Employee - File Watcher" cmd /k "cd /d '%SCRIPTS%' && python filesystem_watcher.py"
echo      Watcher started in new window

echo.
echo [2/2] Opening Obsidian Vault...
echo      Please open Obsidian and load the vault if not already open
echo.
echo ============================================
echo  System Started!
echo ============================================
echo.
echo Windows:
echo   - File Watcher: Running in background
echo   - Obsidian: Open manually (File ^> Open Folder ^> %VAULT%)
echo.
echo To test:
echo   1. Drop a file into: %VAULT%\Inbox\
echo   2. Wait 30 seconds
echo   3. Run: python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
echo.
echo To stop watcher: Close the "AI Employee - File Watcher" window
echo ============================================
echo.

start "" "obsidian://open?vault=%VAULT%"
timeout /t 3 /nobreak >nul
