@echo off
REM ============================================
REM Full Bronze Tier Test
REM ============================================

set VAULT=%~dp0AI_Employee_Vault
set SCRIPTS=%~dp0scripts

echo.
echo ============================================================
echo Bronze Tier - Full System Test
echo ============================================================
echo.

REM Create test file
echo [TEST] Creating test file...
echo Please analyze this task and create a plan with action items. > "%VAULT%\Inbox\bronze_test_%RANDOM%.txt"
echo Test file created in Inbox
echo.

echo [TEST] Starting File Watcher (will run for 60 seconds)...
cd /d "%SCRIPTS%"
start "Watcher" cmd /k "timeout /t 2 && python filesystem_watcher.py"
echo Watcher started in background window
echo.

echo Waiting 45 seconds for watcher to detect file...
timeout /t 45 /nobreak
echo.

echo [TEST] Checking if action file was created...
dir "%VAULT%\Needs_Action\*.md" 2>nul
if errorlevel 1 (
    echo WARNING: No action files detected yet
) else (
    echo SUCCESS: Action file created!
)
echo.

echo [TEST] Running Orchestrator with Ollama...
cd /d "%SCRIPTS%"
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
echo.

echo [TEST] Checking results...
echo.
echo Needs_Action folder:
dir "%VAULT%\Needs_Action" 2>nul || echo (empty)
echo.
echo Plans folder:
dir "%VAULT%\Plans" 2>nul || echo (empty)
echo.
echo Done folder:
dir "%VAULT%\Done" 2>nul || echo (empty)
echo.

echo ============================================================
echo Test Complete!
echo ============================================================
echo.
echo Check the following:
echo   1. Plans folder - Should have a PLAN_*.md file
echo   2. Done folder - Should have the processed task
echo   3. Dashboard.md - Should show recent activity
echo.
echo To stop the watcher, close its terminal window.
echo.
pause
