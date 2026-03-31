@echo off
REM Quick LinkedIn Login
REM This script opens LinkedIn for you to login

echo ============================================================
echo LinkedIn Login - Quick Start
echo ============================================================
echo.
echo This will open LinkedIn in a browser window.
echo Please login with your credentials.
echo.
echo ============================================================
echo.

cd /d "%~dp0"

echo Opening LinkedIn login page...
echo.

python -c "
from playwright.sync_api import sync_playwright
import time

print('🚀 Starting browser...')
with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        'linkedin_session',
        headless=False,
        args=['--disable-gpu', '--no-sandbox']
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print('📱 Opening LinkedIn...')
    page.goto('https://www.linkedin.com/login')
    
    print()
    print('✅ LinkedIn login page is open!')
    print()
    print('📋 Login Steps:')
    print('   1. Enter your email/phone')
    print('   2. Enter your password')
    print('   3. Click Sign in')
    print('   4. Complete 2FA if needed')
    print()
    print('💡 Once logged in to your feed, close the browser window.')
    print()
    print('⏳ Waiting for you to login...')
    
    try:
        page.wait_for_event('close')
    except:
        pass
    
    print()
    print('✅ Browser closed!')
    print('✅ Session saved!')
    print()
    print('Next: Run publish-social-media.bat to post!')
"

echo.
echo ============================================================
echo Login Complete!
echo ============================================================
echo.
echo Now you can publish your AI Employee posts!
echo.
echo Run: publish-social-media.bat
echo.
pause
