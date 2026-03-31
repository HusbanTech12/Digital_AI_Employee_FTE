@echo off
REM Configure Qwen Code CLI for AI Employee System
REM This script runs the Qwen Code CLI configuration

echo ============================================================
echo Qwen Code CLI Configuration
echo ============================================================
echo.

cd /d "%~dp0"

echo Running configuration script...
python scripts\configure_qwen_code.py

echo.
echo ============================================================
echo Configuration Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. If Qwen Code CLI is not installed, follow the installation instructions above
echo 2. Run: python scripts\test_qwen_code_integration.py
echo 3. Run: python scripts\orchestrator.py --vault ..\AI_Employee_Vault --qwen-code --once
echo.
pause
