@echo off
REM AI Employee - Run Orchestrator
REM This script runs the orchestrator to process pending tasks

echo ============================================
echo AI Employee - Orchestrator
echo ============================================
echo.

cd /d "%~dp0scripts"

python orchestrator.py --vault "..\AI_Employee_Vault" %*

echo.
echo ============================================
echo Done.
echo ============================================
pause
