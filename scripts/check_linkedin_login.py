"""
Check LinkedIn Login Status

This script checks if you're logged in to LinkedIn by testing the saved session.

Usage:
    python check_linkedin_login.py
"""

import sys
from pathlib import Path
import time

# Add scripts directory to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ Playwright not installed!")
    print("Install with: pip install playwright && playwright install chromium")
    sys.exit(1)


def check_linkedin_login():
    """Check if LinkedIn session is valid."""
    session_path = PROJECT_ROOT / 'linkedin_session'
    
    print("=" * 60)
    print("LinkedIn Login Status Check")
    print("=" * 60)
    print()
    
    # Check if session folder exists
    if not session_path.exists():
        print("❌ LinkedIn session folder not found!")
        print()
        print("You need to login first.")
        print()
        print("Run one of these:")
        print("  login-social-media.bat")
        print("  python scripts\\login_social_media.py linkedin")
        return False
    
    # Check if session has data
    session_files = list(session_path.glob('**/*'))
    if len(session_files) == 0:
        print("⚠️  LinkedIn session folder is empty!")
        print()
        print("Session not saved yet. You need to login.")
        print()
        print("Run one of these:")
        print("  login-social-media.bat")
        print("  python scripts\\login_social_media.py linkedin")
        return False
    
    print("✅ LinkedIn session folder found")
    print(f"   Location: {session_path}")
    print(f"   Files: {len(session_files)} items")
    print()
    
    # Try to use the session
    print("🔍 Testing LinkedIn session...")
    print()
    
    try:
        with sync_playwright() as p:
            # Launch browser with persistent context
            browser = p.chromium.launch_persistent_context(
                str(session_path),
                headless=True,  # Run in background
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Navigate to LinkedIn
            print("📡 Connecting to LinkedIn...")
            page.goto('https://www.linkedin.com/feed', timeout=30000)
            time.sleep(3)
            
            # Check if logged in
            current_url = page.url
            
            if 'login' in current_url.lower() or 'checkpoint' in current_url.lower():
                print("❌ NOT LOGGED IN")
                print()
                print("Session is invalid or expired.")
                print("You need to login again.")
                print()
                browser.close()
                return False
            
            # Try to find user profile icon (indicates logged in)
            try:
                # Look for common logged-in indicators
                is_logged_in = False
                
                # Check for feed (only visible when logged in)
                if 'feed' in current_url.lower():
                    is_logged_in = True
                
                # Check for profile menu
                if not is_logged_in:
                    profile_selector = '[data-testid="me-dropdown"]'
                    if page.query_selector(profile_selector):
                        is_logged_in = True
                
                # Check for "What's on your mind?" post box
                if not is_logged_in:
                    post_box = page.query_selector('[data-testid="update-editor-start"]')
                    if post_box:
                        is_logged_in = True
                
                if is_logged_in:
                    print("✅ LOGGED IN SUCCESSFULLY!")
                    print()
                    print(f"   Profile URL: {current_url}")
                    print("   Session is valid and working!")
                    print()
                    print("You can now post to LinkedIn automatically!")
                    print()
                    print("Next steps:")
                    print("  publish-social-media.bat")
                    print()
                    browser.close()
                    return True
                else:
                    print("⚠️  UNCERTAIN STATUS")
                    print()
                    print(f"   Current URL: {current_url}")
                    print("   May need to login again.")
                    print()
                    browser.close()
                    return False
                    
            except Exception as e:
                print(f"⚠️  Could not verify login status: {e}")
                print()
                browser.close()
                return False
                
    except Exception as e:
        print(f"❌ Error testing session: {e}")
        print()
        print("Session may be corrupted. Try logging in again.")
        print()
        print("Run:")
        print("  login-social-media.bat")
        return False


if __name__ == '__main__':
    is_logged_in = check_linkedin_login()
    
    print("=" * 60)
    
    if is_logged_in:
        print("✅ LinkedIn is ready for automatic posting!")
    else:
        print("❌ LinkedIn needs authentication!")
        print()
        print("To login, run:")
        print("  login-social-media.bat")
    
    print("=" * 60)
    
    sys.exit(0 if is_logged_in else 1)
