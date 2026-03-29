@echo off
REM Run AI Employee Orchestrator with Ollama
REM Silver & Gold Tier Ready

echo ============================================================
echo AI Employee Orchestrator - Ollama
echo ============================================================
echo.
echo Configuration:
echo   AI Provider: Ollama (Local)
echo   Model: qwen2.5:1.5b
echo   Vault: AI_Employee_Vault
echo.

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Running configuration script...
    python configure_ollama_tiers.py
    echo.
)

REM Run orchestrator
cd scripts
python orchestrator.py --vault ..\AI_Employee_Vault --ollama %*

echo.
echo ============================================================
echo Done!
echo ============================================================
pause
