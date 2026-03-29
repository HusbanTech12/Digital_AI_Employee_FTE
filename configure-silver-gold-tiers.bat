@echo off
REM Configure Ollama for Silver & Gold Tiers
REM This script verifies and configures everything

echo ============================================================
echo AI Employee - Ollama Configuration
echo Silver ^& Gold Tier Ready
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run configuration
echo Running configuration...
echo.
python configure_ollama_tiers.py

echo.
echo ============================================================
echo Configuration Complete!
echo ============================================================
echo.
echo You can now:
echo   1. Run: python scripts\test_ollama_integration.py
echo   2. Run: python scripts\orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
echo   3. Or use: run-ollama.bat
echo.
pause
