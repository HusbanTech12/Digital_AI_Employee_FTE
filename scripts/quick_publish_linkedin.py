"""
Quick LinkedIn Post Publisher

Directly publishes LinkedIn posts from the Approved folder.
Opens browser for semi-automatic posting.

Usage:
    python quick_publish_linkedin.py [vault_path]
"""

import sys
import time
from pathlib import Path

# Add scripts directory to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ Playwright not installed!")
    sys.exit(1)


def publish_linkedin_post(post_file: Path, session_path: str) -> bool:
    """Publish a single post to LinkedIn."""
    print(f"\n📝 Publishing: {post_file.name}")
    print("-" * 60)
    
    # Read post content
    content = post_file.read_text(encoding='utf-8')
    
    # Extract content from markdown
    if '## Content' in content:
        post_text = content.split('## Content')[1].split('##')[0].strip()
    else:
        # Remove frontmatter
        lines = content.split('\n')
        in_frontmatter = False
        post_text = []
        for line in lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
            elif not in_frontmatter and not line.startswith('#'):
                post_text.append(line)
        post_text = '\n'.join(post_text).strip()
    
    print(f"📄 Post content ({len(post_text)} chars):")
    print(f"   {post_text[:200]}...")
    print()
    
    with sync_playwright() as p:
        # Launch browser with persistent context
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,  # Show browser for visibility
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Navigate to LinkedIn
        print("🔗 Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(3)
        
        # Check if logged in
        if 'login' in page.url.lower():
            print("❌ Not logged in to LinkedIn!")
            print("   Please run: python scripts\\login_social_media.py linkedin")
            browser.close()
            return False
        
        # Show the LinkedIn feed for manual posting
        print("✅ Logged in to LinkedIn")
        print()
        print("=" * 60)
        print("📋 MANUAL POSTING INSTRUCTIONS")
        print("=" * 60)
        print()
        print("The LinkedIn post composer requires interaction.")
        print("Please post manually using the content below:")
        print()
        print("-" * 60)
        print("COPY THIS CONTENT:")
        print("-" * 60)
        print(post_text)
        print("-" * 60)
        print()
        print("STEPS TO POST:")
        print("  1. Click 'Start a post' at the top of your feed")
        print("  2. Paste the content above")
        print("  3. Click 'Post' button")
        print("  4. Close the browser when done")
        print()
        print("⏳ Waiting for you to post... (close browser when done)")
        
        # Wait for user to post manually - keep browser open
        try:
            # Simple approach: wait for browser context to close
            page.wait_for_event('close')
        except:
            # If wait fails, just wait indefinitely with sleep
            for _ in range(600):  # Max 10 minutes
                time.sleep(1)
        
        
        browser.close()
        
        print()
        print("=" * 60)
        print("✅ Browser closed!")
        print("=" * 60)
        print()
        
        # Move post to Done
        done_file = post_file.parent.parent / 'Done' / post_file.name
        try:
            post_file.rename(done_file)
            print(f"✅ Moved post to Done folder")
        except Exception as e:
            print(f"⚠️  Could not move file: {e}")
        
        return True


def main():
    """Main function."""
    vault_path = PROJECT_ROOT / 'AI_Employee_Vault'
    
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    
    approved_folder = vault_path / 'Approved'
    session_path = str(PROJECT_ROOT / 'linkedin_session')
    
    print("=" * 60)
    print("Quick LinkedIn Publisher")
    print("=" * 60)
    print()
    
    # Check for approved LinkedIn posts
    linkedin_posts = list(approved_folder.glob('LINKEDIN_*.md'))
    
    if not linkedin_posts:
        print("❌ No LinkedIn posts found in Approved folder!")
        print()
        print("To create posts, run:")
        print("  python scripts\\social_media_manager.py AI_Employee_Vault post")
        print()
        return
    
    print(f"✅ Found {len(linkedin_posts)} LinkedIn post(s) to publish")
    print()
    
    # Publish each post
    success_count = 0
    for post_file in linkedin_posts:
        success = publish_linkedin_post(post_file, session_path)
        if success:
            success_count += 1
        print()
    
    # Summary
    print("=" * 60)
    print("Publishing Summary")
    print("=" * 60)
    print(f"Posts processed: {len(linkedin_posts)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(linkedin_posts) - success_count}")
    print()
    
    if success_count > 0:
        print("🎉 Success! Check your LinkedIn profile!")
    else:
        print("⚠️  No posts were published successfully")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
