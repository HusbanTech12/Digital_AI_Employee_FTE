@echo off
REM Quick Start for AI Employee with Qwen Code CLI
REM This script starts the AI Employee system using Qwen Code CLI

echo ============================================================
echo AI Employee System - Qwen Code CLI
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo.
)

REM Start file watcher in a new window
echo Starting File Watcher...
start "AI Employee - File Watcher" cmd /k "cd /d %~dp0 && python scripts\filesystem_watcher.py AI_Employee_Vault"

REM Wait a moment for watcher to start
timeout /t 2 /nobreak > nul

REM Run orchestrator
echo.
echo Running Orchestrator with Qwen Code CLI...
python scripts\orchestrator.py --vault AI_Employee_Vault --qwen-code --continuous --interval 30

echo.
echo ============================================================
echo AI Employee System Stopped
echo ============================================================
echo.
pause
