"""
Social Media Login Helper Script

This script opens browsers for LinkedIn, Facebook, and Instagram
to help you login for the first time. Sessions are saved for future use.

Usage:
    python login_social_media.py [platform]
    
Platforms: linkedin, facebook, instagram, all
"""

import sys
import time
from pathlib import Path

# Add scripts directory to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ Playwright not installed!")
    print("Install with: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)


def open_linkedin_login(session_path: str):
    """Open LinkedIn login page with persistent session."""
    print("\n" + "=" * 60)
    print("LinkedIn Login")
    print("=" * 60)
    print()
    print("📝 Opening LinkedIn in browser...")
    print()
    
    with sync_playwright() as p:
        # Launch browser with persistent context
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,  # Show browser for manual login
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Navigate to LinkedIn login
        print("🔗 Navigate to: https://www.linkedin.com/login")
        print()
        page.goto('https://www.linkedin.com/login', timeout=60000)
        
        print("✅ Browser is open!")
        print()
        print("📋 Login Instructions:")
        print("   1. Enter your email/phone")
        print("   2. Enter your password")
        print("   3. Click 'Sign in'")
        print("   4. Complete any 2FA if enabled")
        print("   5. Once logged in, close the browser window")
        print()
        print("💡 Your session will be saved automatically!")
        print()
        print("⏳ Waiting for you to login... (close the browser window when done)")
        
        # Wait for user to login and close browser
        # Use simple sleep loop instead of wait_for_event to avoid timeout
        import signal
        
        def signal_handler(sig, frame):
            raise KeyboardInterrupt()
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            # Keep script running while browser is open
            while browser.is_connected():
                time.sleep(1)
        except (KeyboardInterrupt, Exception):
            print("\n✅ Login complete")
        finally:
            try:
                browser.close()
            except:
                pass
            print("✅ Browser closed")
            print("✅ Session saved to:", session_path)


def open_facebook_login(session_path: str):
    """Open Facebook login page with persistent session."""
    print("\n" + "=" * 60)
    print("Facebook Login")
    print("=" * 60)
    print()
    print("📝 Opening Facebook in browser...")
    print()
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("🔗 Navigate to: https://www.facebook.com")
        print()
        page.goto('https://www.facebook.com', timeout=60000)
        
        print("✅ Browser is open!")
        print()
        print("📋 Login Instructions:")
        print("   1. Enter your email or phone number")
        print("   2. Enter your password")
        print("   3. Click 'Log In'")
        print("   4. Complete any 2FA if enabled")
        print("   5. Once logged in, close the browser window")
        print()
        print("💡 Your session will be saved automatically!")
        print()
        print("⏳ Waiting for you to login... (press Ctrl+C when done)")
        
        try:
            while True:
                time.sleep(1)
                if not browser.is_connected():
                    break
        except KeyboardInterrupt:
            print("\n\n✅ Login process interrupted")
        finally:
            browser.close()
            print("✅ Browser closed")
            print("✅ Session saved to:", session_path)


def open_instagram_login(session_path: str):
    """Open Instagram login page with persistent session."""
    print("\n" + "=" * 60)
    print("Instagram Login")
    print("=" * 60)
    print()
    print("📝 Opening Instagram in browser...")
    print()
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("🔗 Navigate to: https://www.instagram.com")
        print()
        page.goto('https://www.instagram.com', timeout=60000)
        
        print("✅ Browser is open!")
        print()
        print("📋 Login Instructions:")
        print("   1. Enter your username, email, or phone")
        print("   2. Enter your password")
        print("   3. Click 'Log in'")
        print("   4. Complete any 2FA if enabled")
        print("   5. Once logged in, close the browser window")
        print()
        print("💡 Your session will be saved automatically!")
        print()
        print("⏳ Waiting for you to login... (press Ctrl+C when done)")
        
        try:
            while True:
                time.sleep(1)
                if not browser.is_connected():
                    break
        except KeyboardInterrupt:
            print("\n\n✅ Login process interrupted")
        finally:
            browser.close()
            print("✅ Browser closed")
            print("✅ Session saved to:", session_path)


def main():
    """Main function."""
    vault_path = PROJECT_ROOT / 'AI_Employee_Vault'
    session_base = vault_path.parent
    
    print("=" * 60)
    print("Social Media Login Helper")
    print("=" * 60)
    print()
    
    # Check Playwright
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not installed!")
        print()
        print("Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return
    
    # Get platform from command line
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
    else:
        platform = 'all'
    
    # Login to platforms
    if platform == 'linkedin' or platform == 'all':
        session_path = str(session_base / 'linkedin_session')
        open_linkedin_login(session_path)
        print()
        print("✅ LinkedIn login complete!")
        print()
    
    if platform == 'facebook' or platform == 'all':
        session_path = str(session_base / 'facebook_session')
        open_facebook_login(session_path)
        print()
        print("✅ Facebook login complete!")
        print()
    
    if platform == 'instagram' or platform == 'all':
        session_path = str(session_base / 'facebook_session' / 'instagram')
        open_instagram_login(session_path)
        print()
        print("✅ Instagram login complete!")
        print()
    
    print("=" * 60)
    print("All Logins Complete!")
    print("=" * 60)
    print()
    print("✅ Your sessions are saved!")
    print()
    print("Next Steps:")
    print(r"  1. Run: publish-social-media.bat")
    print(r"  2. Or run: python scripts\linkedin_poster.py AI_Employee_Vault")
    print()
    print("Your posts will be published automatically! 🚀")
    print()


if __name__ == '__main__':
    main()
