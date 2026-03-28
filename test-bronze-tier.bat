@echo off
REM ============================================
REM Bronze Tier Test Script
REM ============================================
REM This script tests all Bronze Tier requirements

setlocal enabledelayedexpansion

set VAULT=%~dp0AI_Employee_Vault
set SCRIPTS=%~dp0scripts

echo.
echo ============================================
echo  Bronze Tier Test Suite
echo ============================================
echo.

REM Step 1: Check Python
echo [TEST 1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Python not found. Install Python 3.13+
    exit /b 1
)
echo [PASS] Python installed

REM Step 2: Check dependencies
echo.
echo [TEST 2/6] Checking Python dependencies...
cd /d "%SCRIPTS%"
pip show watchdog >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
) else (
    echo [PASS] Dependencies installed
)

REM Step 3: Check vault structure
echo.
echo [TEST 3/6] Checking vault structure...
set MISSING=0
for %%F in (Dashboard.md Company_Handbook.md Business_Goals.md) do (
    if not exist "%VAULT%\%%F" (
        echo [FAIL] Missing: %%F
        set MISSING=1
    )
)
for %%D in (Inbox Needs_Action Plans Done Pending_Approval Approved Rejected Logs Files) do (
    if not exist "%VAULT%\%%D" (
        echo [FAIL] Missing folder: %%D
        set MISSING=1
    )
)
if %MISSING%==0 (
    echo [PASS] Vault structure complete
)

REM Step 4: Check watcher script
echo.
echo [TEST 4/6] Checking watcher script...
if exist "%SCRIPTS%\filesystem_watcher.py" (
    echo [PASS] Filesystem watcher exists
) else (
    echo [FAIL] Filesystem watcher not found
    exit /b 1
)

REM Step 5: Check orchestrator
echo.
echo [TEST 5/6] Checking orchestrator...
if exist "%SCRIPTS%\orchestrator.py" (
    echo [PASS] Orchestrator exists
) else (
    echo [FAIL] Orchestrator not found
    exit /b 1
)

REM Step 6: Functional test - drop a file
echo.
echo [TEST 6/6] Running functional test...
echo Testing file drop detection...

REM Create test file
echo This is a Bronze Tier functional test. > "%VAULT%\Inbox\bronze_test_%RANDOM%.txt"
echo [INFO] Created test file in Inbox

echo.
echo ============================================
echo  Next Steps:
echo ============================================
echo.
echo 1. Start the watcher (in Terminal 1):
echo    cd "%SCRIPTS%"
echo    python filesystem_watcher.py
echo.
echo 2. Wait 30 seconds for watcher to detect file
echo.
echo 3. Run orchestrator (in Terminal 2):
echo    cd "%SCRIPTS%"
echo    python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
echo.
echo 4. Check results:
echo    dir "%VAULT%\Needs_Action"
echo    dir "%VAULT%\Plans"
echo    dir "%VAULT%\Done"
echo.
echo ============================================
echo  Test setup complete!
echo ============================================
echo.

endlocal
