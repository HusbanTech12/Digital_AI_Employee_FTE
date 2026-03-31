@echo off
REM Setup Social Media Automation
REM This script installs dependencies and configures social media posting

echo ============================================================
echo Social Media Automation Setup
echo ============================================================
echo.

cd /d "%~dp0"

echo Step 1: Installing Playwright...
echo ------------------------------------------------------------
pip install playwright
echo.

echo Step 2: Installing Chromium browser...
echo ------------------------------------------------------------
playwright install chromium
echo.

echo Step 3: Checking configuration...
echo ------------------------------------------------------------
python scripts\social_media_manager.py AI_Employee_Vault setup
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next Steps:
echo 1. Create your first post:
echo    python scripts\social_media_manager.py AI_Employee_Vault post
echo.
echo 2. Or drop a file in AI_Employee_Vault\Inbox\ with:
echo    "Create social media posts about [your topic]"
echo.
echo 3. Approve posts by moving files:
echo    Needs_Action ^> Pending_Approval ^> Approved
echo.
echo 4. Posts will be published automatically!
echo.
echo Documentation: SOCIAL_MEDIA_AUTOMATION.md
echo.
pause
