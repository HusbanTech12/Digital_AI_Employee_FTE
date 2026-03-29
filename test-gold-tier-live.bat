@echo off
REM Gold Tier Live Test
REM Tests the complete Gold Tier workflow with Ollama

echo ============================================================
echo Gold Tier LIVE Test
echo Testing Advanced Features with Ollama
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
echo Running Gold Tier live processing test...
echo This will test:
echo   - Audit Logger
echo   - Error Recovery
echo   - Ralph Wiggum Loop
echo   - Gold Weekly Audit
echo   - Facebook/Instagram Watcher
echo   - Twitter Watcher
echo   - MCP Servers
echo   - Live Ollama Processing
echo.
cd scripts
python test_gold_tier_live.py

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
echo Results saved to: gold_tier_live_results.json
echo.
pause
