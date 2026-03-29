@echo off
REM Platinum Tier Live Test
REM Tests the complete Platinum Tier implementation

echo ============================================================
echo Platinum Tier LIVE Test
echo Testing Cloud Deployment, Vault Sync, and Health Monitor
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
echo Running Platinum Tier live test...
echo This will test:
echo   - Cloud deployment scripts
echo   - Vault sync system
echo   - Health monitor
echo   - Work-zone specialization
echo   - Security rules
echo   - Gold Tier prerequisites
echo   - Live sync operations
echo.
python scripts\test_platinum_tier_live.py

echo.
echo ============================================================
echo Test Complete
echo ============================================================
echo.
echo Check the following for results:
echo   - platinum_tier_live_results.json (test results)
echo   - AI_Employee_Vault\Updates\     (sync updates)
echo   - AI_Employee_Vault\Signals\     (inter-agent signals)
echo   - AI_Employee_Vault\Logs\        (sync and health logs)
echo.
echo Next Steps for Cloud Deployment:
echo   1. Get a cloud VM (Oracle Cloud Free Tier or AWS EC2)
echo   2. Copy deploy-cloud.sh to VM
echo   3. Run: ./deploy-cloud.sh your@email.com your-domain.com
echo   4. Setup Git sync between Cloud and Local
echo   5. Configure .env.local on Local machine
echo.
pause
