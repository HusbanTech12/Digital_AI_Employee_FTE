@echo off
REM Silver Tier Live Test
REM Tests the complete Silver Tier workflow with Ollama

echo ============================================================
echo Silver Tier LIVE Test
echo Testing Ollama Processing Workflow
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run live test
echo Running live processing test...
echo.
cd scripts
python test_silver_tier_live.py

echo.
echo ============================================================
echo Test Complete
echo ============================================================
echo.
echo Check the following folders for results:
echo   - AI_Employee_Vault\Plans\       (AI-generated plans)
echo   - AI_Employee_Vault\Done\        (Processed files)
echo   - AI_Employee_Vault\Logs\        (Processing logs)
echo   - AI_Employee_Vault\Dashboard.md (Updated status)
echo.
pause
