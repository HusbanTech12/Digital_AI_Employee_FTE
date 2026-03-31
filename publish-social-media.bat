@echo off
REM Publish AI Employee FTE Posts to Social Media
REM This script guides you through the approval and publishing process

echo ============================================================
echo AI Employee FTE - Social Media Publishing
echo ============================================================
echo.

cd /d "%~dp0"

echo Step 1: Check Created Posts
echo ------------------------------------------------------------
dir AI_Employee_Vault\Needs_Action\LINKEDIN_AI_Employee_FTE*.md /B
dir AI_Employee_Vault\Needs_Action\FACEBOOK_AI_Employee_FTE*.md /B
dir AI_Employee_Vault\Needs_Action\INSTAGRAM_AI_Employee_FTE*.md /B
echo.

echo Step 2: Move Posts to Pending Approval
echo ------------------------------------------------------------
echo Moving LinkedIn post...
move AI_Employee_Vault\Needs_Action\LINKEDIN_AI_Employee_FTE*.md AI_Employee_Vault\Pending_Approval\ >nul 2>&1
if %errorlevel% == 0 (echo ✓ LinkedIn post moved) else (echo ✗ LinkedIn post not found or already moved)

echo Moving Facebook post...
move AI_Employee_Vault\Needs_Action\FACEBOOK_AI_Employee_FTE*.md AI_Employee_Vault\Pending_Approval\ >nul 2>&1
if %errorlevel% == 0 (echo ✓ Facebook post moved) else (echo ✗ Facebook post not found or already moved)

echo Moving Instagram post...
move AI_Employee_Vault\Needs_Action\INSTAGRAM_AI_Employee_FTE*.md AI_Employee_Vault\Pending_Approval\ >nul 2>&1
if %errorlevel% == 0 (echo ✓ Instagram post moved) else (echo ✗ Instagram post not found or already moved)
echo.

echo Step 3: Review Posts in Pending_Approval Folder
echo ------------------------------------------------------------
echo Please review the posts before approving:
echo - Open AI_Employee_Vault\Pending_Approval\ folder
echo - Check each post for accuracy
echo - Add images to Instagram post if you have any
echo.
pause

echo Step 4: Approve Posts for Publishing
echo ------------------------------------------------------------
echo Moving posts to Approved folder...

move AI_Employee_Vault\Pending_Approval\LINKEDIN_*.md AI_Employee_Vault\Approved\ >nul 2>&1
if %errorlevel% == 0 (echo ✓ LinkedIn post approved) else (echo ✗ LinkedIn post not found)

move AI_Employee_Vault\Pending_Approval\FACEBOOK_*.md AI_Employee_Vault\Approved\ >nul 2>&1
if %errorlevel% == 0 (echo ✓ Facebook post approved) else (echo ✗ Facebook post not found)

move AI_Employee_Vault\Pending_Approval\INSTAGRAM_*.md AI_Employee_Vault\Approved\ >nul 2>&1
if %errorlevel% == 0 (echo ✓ Instagram post approved) else (echo ✗ Instagram post not found)
echo.

echo Step 5: Publish to LinkedIn
echo ------------------------------------------------------------
echo Starting LinkedIn publisher...
echo NOTE: First run requires manual login to LinkedIn
echo.
python scripts\linkedin_poster.py AI_Employee_Vault
echo.

echo ============================================================
echo Publishing Complete!
echo ============================================================
echo.
echo Next Steps:
echo 1. Check AI_Employee_Vault\Done\ for published posts
echo 2. Check AI_Employee_Vault\Logs\ for activity logs
echo 3. Verify posts on your LinkedIn profile!
echo.
echo For Facebook and Instagram:
echo   python scripts\facebook_instagram_watcher.py AI_Employee_Vault
echo.
pause
