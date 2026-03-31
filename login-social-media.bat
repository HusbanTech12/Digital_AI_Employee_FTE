@echo off
REM Social Media Login Helper
REM This script opens browsers for you to login to LinkedIn, Facebook, and Instagram

echo ============================================================
echo Social Media Login - First Time Setup
echo ============================================================
echo.
echo This will open browsers for you to login to your social media accounts.
echo Your sessions will be saved for automatic posting in the future.
echo.
echo ============================================================
echo.

cd /d "%~dp0"

echo Opening LinkedIn Login...
echo ------------------------------------------------------------
python scripts\login_social_media.py linkedin
echo.

echo ============================================================
echo.
set /p continue_facebook="Continue to Facebook login? (Y/N): "
if /i "%continue_facebook%"=="Y" (
    echo Opening Facebook Login...
    echo ------------------------------------------------------------
    python scripts\login_social_media.py facebook
    echo.
)

echo ============================================================
echo.
set /p continue_instagram="Continue to Instagram login? (Y/N): "
if /i "%continue_instagram%"=="Y" (
    echo Opening Instagram Login...
    echo ------------------------------------------------------------
    python scripts\login_social_media.py instagram
    echo.
)

echo ============================================================
echo Login Complete!
echo ============================================================
echo.
echo ✅ Your sessions are saved!
echo.
echo Next Steps:
echo   1. Run: publish-social-media.bat
echo   2. Or run: python scripts\orchestrator.py --vault AI_Employee_Vault --qwen-code --once
echo.
echo Your AI Employee posts will be published automatically! 🚀
echo.
pause
