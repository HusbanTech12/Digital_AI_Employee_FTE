"""
Facebook/Instagram Watcher and Poster Module

Monitors and posts to Facebook and Instagram using Playwright browser automation.
Gold Tier Feature: Social media integration with summary generation.

Setup Instructions:
1. Install Playwright: pip install playwright
2. Install browsers: playwright install chromium
3. First run will require manual login to Facebook/Instagram
4. Session will be saved for subsequent runs

Usage:
    python facebook_instagram_watcher.py [vault_path]
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from base_watcher import BaseWatcher


class SocialMediaPost:
    """Represents a social media post."""

    def __init__(self, content: str, platform: str, title: str = ''):
        self.title = title
        self.content = content
        self.platform = platform  # 'facebook' or 'instagram'
        self.created = datetime.now().isoformat()
        self.status = 'draft'
        self.images = []
        self.post_url = None
        self.engagement = {
            'likes': 0,
            'comments': 0,
            'shares': 0,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for metadata."""
        return {
            'title': self.title,
            'content': self.content[:200],  # Preview
            'platform': self.platform,
            'created': self.created,
            'status': self.status,
            'post_url': self.post_url,
            'engagement': self.engagement,
        }


class FacebookInstagramWatcher(BaseWatcher):
    """
    Watches and posts to Facebook and Instagram.

    Features:
    - Session persistence
    - Post creation and scheduling
    - Engagement tracking
    - Summary generation
    """

    def __init__(
        self,
        vault_path: str,
        session_path: Optional[str] = None,
        check_interval: int = 60
    ):
        """
        Initialize the Facebook/Instagram watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            session_path: Path to store browser session
            check_interval: Seconds between checks
        """
        super().__init__(vault_path, check_interval)

        # Setup session path
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = self.vault_path.parent / 'facebook_session'

        self.session_path.mkdir(parents=True, exist_ok=True)

        # Track processed posts
        self.processed_file = self.logs / 'facebook_posts.jsonl'

        self.logger.info(f'Facebook/Instagram Watcher initialized')
        self.logger.info(f'Session path: {self.session_path}')

    def check_for_posts(self) -> List[SocialMediaPost]:
        """
        Check for posts to publish in Needs_Action folder.

        Returns:
            List of SocialMediaPost objects
        """
        posts = []

        if not self.needs_action.exists():
            return posts

        # Find Facebook/Instagram post files
        for file_path in self.needs_action.glob('FACEBOOK_*.md'):
            try:
                post = self._parse_post_file(file_path, 'facebook')
                if post:
                    posts.append(post)
            except Exception as e:
                self.logger.error(f'Error parsing Facebook post file {file_path}: {e}')

        for file_path in self.needs_action.glob('INSTAGRAM_*.md'):
            try:
                post = self._parse_post_file(file_path, 'instagram')
                if post:
                    posts.append(post)
            except Exception as e:
                self.logger.error(f'Error parsing Instagram post file {file_path}: {e}')

        return posts

    def _parse_post_file(self, file_path: Path, platform: str) -> Optional[SocialMediaPost]:
        """Parse a markdown file into a SocialMediaPost."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            # Parse frontmatter
            metadata = {}
            in_frontmatter = False
            body_lines = []

            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue

                if in_frontmatter:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
                else:
                    body_lines.append(line)

            # Get post content
            post_content = '\n'.join(body_lines).strip()

            # Remove headers if present
            if post_content.startswith('##'):
                post_content = '\n'.join(post_content.split('\n')[1:]).strip()

            # Create post object
            post = SocialMediaPost(
                content=post_content,
                platform=platform,
                title=metadata.get('title', file_path.stem)
            )

            # Parse images if specified
            if metadata.get('images'):
                post.images = metadata['images'].split(',')

            return post

        except Exception as e:
            self.logger.error(f'Error parsing post file: {e}')
            return None

    def post_to_facebook(self, post: SocialMediaPost) -> bool:
        """
        Post content to Facebook using browser automation.

        Args:
            post: SocialMediaPost object to publish

        Returns:
            True if successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            self.logger.info('Starting Facebook post process...')

            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=True,
                    args=[
                        '--disable-gpu',
                        '--disable-dev-shm-usage',
                        '--disable-setuid-sandbox',
                        '--no-sandbox'
                    ]
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                try:
                    # Navigate to Facebook
                    page.goto('https://www.facebook.com', timeout=60000)
                    time.sleep(3)

                    # Check if logged in
                    if 'login' in page.url.lower():
                        self.logger.warning('Not logged in to Facebook. Please login manually.')
                        browser.close()
                        return False

                    # Click on "What's on your mind?" box
                    try:
                        post_box = page.wait_for_selector('[data-testid="create_post"]', timeout=10000)
                        post_box.click()
                        time.sleep(2)
                    except Exception:
                        self.logger.error('Could not find post creation box')
                        browser.close()
                        return False

                    # Enter post content
                    try:
                        editor = page.wait_for_selector('[data-testid="autocomposer-0"]', timeout=10000)
                        if editor:
                            editor.click()
                            page.keyboard.press('Control+A')
                            page.keyboard.press('Delete')
                            
                            # Type content
                            for char in post.content[:5000]:  # Facebook limit
                                page.keyboard.type(char, delay=10)
                                time.sleep(0.01)

                            time.sleep(2)

                            # Click Post button
                            post_button = page.wait_for_selector('[data-testid="react-composer-post-button"]', timeout=10000)
                            if post_button:
                                post_button.click()
                                time.sleep(3)
                                self.logger.info('Facebook post published!')
                                post.status = 'published'
                                return True
                    except Exception as e:
                        self.logger.error(f'Error posting to Facebook: {e}')

                    browser.close()
                    return False

                except Exception as e:
                    self.logger.error(f'Error during Facebook posting: {e}')
                    browser.close()
                    return False

        except ImportError:
            self.logger.error('Playwright not installed')
            return False
        except Exception as e:
            self.logger.error(f'Unexpected error posting to Facebook: {e}')
            return False

    def post_to_instagram(self, post: SocialMediaPost) -> bool:
        """
        Post content to Instagram using browser automation.

        Args:
            post: SocialMediaPost object to publish

        Returns:
            True if successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            self.logger.info('Starting Instagram post process...')

            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session_path / 'instagram',
                    headless=True,
                    args=[
                        '--disable-gpu',
                        '--disable-dev-shm-usage',
                        '--disable-setuid-sandbox',
                        '--no-sandbox'
                    ]
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                try:
                    # Navigate to Instagram
                    page.goto('https://www.instagram.com', timeout=60000)
                    time.sleep(3)

                    # Check if logged in
                    if 'login' in page.url.lower():
                        self.logger.warning('Not logged in to Instagram. Please login manually.')
                        browser.close()
                        return False

                    # Click on "New post" button
                    try:
                        new_post_btn = page.wait_for_selector('[aria-label="New post"]', timeout=10000)
                        new_post_btn.click()
                        time.sleep(2)
                    except Exception:
                        self.logger.error('Could not find new post button')
                        browser.close()
                        return False

                    # For Instagram, we need to handle image upload
                    # This is a simplified version - full implementation would handle file upload
                    self.logger.info('Instagram post creation started (manual image upload may be required)')
                    
                    # Note: Instagram requires images. This is a limitation of browser automation.
                    # For production, use Instagram Graph API instead.
                    
                    browser.close()
                    return False  # Requires manual intervention for image

                except Exception as e:
                    self.logger.error(f'Error during Instagram posting: {e}')
                    browser.close()
                    return False

        except ImportError:
            self.logger.error('Playwright not installed')
            return False
        except Exception as e:
            self.logger.error(f'Unexpected error posting to Instagram: {e}')
            return False

    def generate_summary(self, platform: str = 'facebook') -> Dict[str, Any]:
        """
        Generate a summary of social media activity.

        Args:
            platform: Platform to summarize

        Returns:
            Summary dictionary
        """
        summary = {
            'platform': platform,
            'generated': datetime.now().isoformat(),
            'posts_this_week': 0,
            'posts_this_month': 0,
            'total_engagement': {
                'likes': 0,
                'comments': 0,
                'shares': 0,
            },
            'recent_posts': [],
        }

        # Read posts log
        log_file = self.logs / f'{platform}_posts.jsonl'
        if log_file.exists():
            with open(log_file, 'r') as f:
                now = datetime.now()
                for line in f:
                    try:
                        post_data = json.loads(line)
                        post_date = datetime.fromisoformat(post_data.get('timestamp', ''))
                        
                        # Count posts this week
                        if (now - post_date).days <= 7:
                            summary['posts_this_week'] += 1
                        
                        # Count posts this month
                        if (now - post_date).days <= 30:
                            summary['posts_this_month'] += 1
                        
                        # Add to recent posts (last 5)
                        if len(summary['recent_posts']) < 5:
                            summary['recent_posts'].append({
                                'content': post_data.get('content', '')[:100],
                                'timestamp': post_data.get('timestamp', ''),
                                'status': post_data.get('status', 'unknown'),
                            })
                    except:
                        continue

        return summary

    def _log_post_result(self, result: Dict, platform: str):
        """Log post result to file."""
        log_file = self.logs / f'{platform}_posts.jsonl'
        result['platform'] = platform

        with open(log_file, 'a') as f:
            f.write(json.dumps(result) + '\n')


if __name__ == '__main__':
    import sys

    # Default vault path
    vault_path = r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault'

    # Allow override via command line
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    # Create watcher
    watcher = FacebookInstagramWatcher(
        vault_path=vault_path,
        check_interval=60
    )

    print('Facebook/Instagram Watcher')
    print('==========================')
    print()
    print('NOTE: First run requires manual login.')
    print('      Session will be saved for future runs.')
    print()

    # Generate summary
    fb_summary = watcher.generate_summary('facebook')
    ig_summary = watcher.generate_summary('instagram')

    print(f'Facebook Summary:')
    print(f'  Posts this week: {fb_summary["posts_this_week"]}')
    print(f'  Posts this month: {fb_summary["posts_this_month"]}')
    print()
    print(f'Instagram Summary:')
    print(f'  Posts this week: {ig_summary["posts_this_week"]}')
    print(f'  Posts this month: {ig_summary["posts_this_month"]}')
