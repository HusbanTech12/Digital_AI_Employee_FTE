@echo off
REM AI Employee - Verify Setup After Ollama Installation
REM Run this AFTER you have installed Ollama

echo.
echo ============================================================
echo AI Employee - Setup Verification
echo ============================================================
echo.
echo This script checks if everything is ready for using Ollama
echo with the AI Employee system.
echo.
echo ============================================================
echo.

python check_setup.py

echo.
echo ============================================================
echo.
echo If all checks passed, you're ready to use AI Employee!
echo.
echo Quick Start:
echo   1. Start watcher:
echo      cd scripts
echo      python filesystem_watcher.py ..\AI_Employee_Vault
echo.
echo   2. Drop a file in: AI_Employee_Vault\Inbox\
echo.
echo   3. Process with AI:
echo      python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
echo.
echo ============================================================
pause
