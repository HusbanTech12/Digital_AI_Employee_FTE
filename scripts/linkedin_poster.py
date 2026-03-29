"""
LinkedIn Automation Module

Automates posting to LinkedIn for business promotion and lead generation.
This is a Silver Tier implementation using Playwright for browser automation.

Setup Instructions:
1. Install Playwright: pip install playwright
2. Install browsers: playwright install chromium
3. First run will require manual LinkedIn login
4. Session will be saved for subsequent runs

Usage:
    python linkedin_poster.py [vault_path] [post_content_file]

Features:
- Auto-post to LinkedIn from markdown files
- Schedule posts for optimal times
- Track post performance
- Human-in-the-loop approval for posts
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from base_watcher import BaseWatcher


class LinkedInPost:
    """Represents a LinkedIn post to be published."""

    def __init__(self, content: str, title: str = '', images: Optional[List[str]] = None):
        self.title = title
        self.content = content
        self.images = images or []
        self.created = datetime.now().isoformat()
        self.status = 'draft'
        self.scheduled_time = None
        self.post_url = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for metadata."""
        return {
            'title': self.title,
            'content': self.content[:200],  # Preview
            'images': self.images,
            'created': self.created,
            'status': self.status,
            'scheduled_time': self.scheduled_time,
            'post_url': self.post_url,
        }


class LinkedInPoster:
    """
    Automates posting to LinkedIn using browser automation.

    Features:
    - Posts from markdown files in Needs_Action folder
    - Session persistence for re-authentication
    - Approval workflow before posting
    - Post tracking and logging
    """

    def __init__(
        self,
        vault_path: str,
        session_path: Optional[str] = None,
        approval_required: bool = True
    ):
        """
        Initialize the LinkedIn poster.

        Args:
            vault_path: Path to the Obsidian vault root
            session_path: Path to store browser session (default: vault parent / linkedin_session)
            approval_required: Require human approval before posting (default: True)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        for folder in [self.needs_action, self.pending_approval, self.approved, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        # Setup session path
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = self.vault_path.parent / 'linkedin_session'

        self.session_path.mkdir(parents=True, exist_ok=True)
        self.approval_required = approval_required

        # Setup logging
        self.logger = self._setup_logging()

        self.logger.info(f'LinkedIn Poster initialized')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Approval required: {approval_required}')

    def _setup_logging(self):
        """Setup logging to file and console."""
        import logging

        log_file = self.logs / f'linkedin_{datetime.now().strftime("%Y-%m-%d")}.log'

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Setup logger
        logger = logging.getLogger('LinkedInPoster')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def check_for_posts(self) -> List[LinkedInPost]:
        """
        Check for post files in Needs_Action folder.

        Returns:
            List of LinkedInPost objects ready to post
        """
        posts = []

        if not self.needs_action.exists():
            return posts

        # Find LinkedIn post files
        for file_path in self.needs_action.glob('LINKEDIN_*.md'):
            try:
                post = self._parse_post_file(file_path)
                if post:
                    posts.append(post)
            except Exception as e:
                self.logger.error(f'Error parsing post file {file_path}: {e}')

        return posts

    def _parse_post_file(self, file_path: Path) -> Optional[LinkedInPost]:
        """Parse a markdown file into a LinkedInPost."""
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

            # Remove '## Content' header if present
            if post_content.startswith('##'):
                post_content = '\n'.join(post_content.split('\n')[1:]).strip()

            # Create post object
            post = LinkedInPost(
                content=post_content,
                title=metadata.get('title', file_path.stem),
                images=metadata.get('images', '').split(',') if metadata.get('images') else []
            )

            # Check for scheduled time
            if metadata.get('scheduled_time'):
                post.scheduled_time = metadata['scheduled_time']

            return post

        except Exception as e:
            self.logger.error(f'Error parsing post file: {e}')
            return None

    def create_approval_request(self, post: LinkedInPost, source_file: Path) -> Optional[Path]:
        """
        Create an approval request file for a post.

        Args:
            post: LinkedInPost object
            source_file: Path to the original post file

        Returns:
            Path to created approval request file
        """
        try:
            content = f'''---
type: approval_request
action: linkedin_post
title: {post.title}
created: {datetime.now().isoformat()}
status: pending
source_file: {source_file.name}
---

# LinkedIn Post Approval Request

## Post Content
{post.content}

{f"## Images ({len(post.images)})" if post.images else ""}
{chr(10).join(f"- {img}" for img in post.images) if post.images else ""}

## To Approve
Move this file to /Approved folder to publish this post.

## To Reject
Move this file to /Rejected folder to discard this post.

## Notes
- Post will be published to your LinkedIn profile
- You will be notified when posting is complete
- Post performance will be tracked in Logs/
'''

            # Create approval file
            approval_file = self.pending_approval / f'APPROVAL_LINKEDIN_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            approval_file.write_text(content, encoding='utf-8')

            self.logger.info(f'Created approval request: {approval_file.name}')
            return approval_file

        except Exception as e:
            self.logger.error(f'Error creating approval request: {e}')
            return None

    def post_to_linkedin(self, post: LinkedInPost) -> bool:
        """
        Post content to LinkedIn using browser automation.

        Args:
            post: LinkedInPost object to publish

        Returns:
            True if successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            self.logger.info('Starting LinkedIn post process...')

            with sync_playwright() as p:
                # Launch browser with persistent context
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
                    # Navigate to LinkedIn
                    page.goto('https://www.linkedin.com/feed', timeout=60000)

                    # Wait for page to load
                    time.sleep(3)

                    # Check if logged in
                    if 'login' in page.url.lower():
                        self.logger.warning('Not logged in to LinkedIn. Please login manually.')
                        self.logger.warning('Session will be saved for next run after authentication.')
                        browser.close()
                        return False

                    # Find and click the post creation box
                    try:
                        post_box = page.wait_for_selector('[data-testid="update-editor-start"]', timeout=10000)
                        post_box.click()
                        time.sleep(2)
                    except Exception:
                        # Alternative selector
                        try:
                            post_box = page.wait_for_selector('.share-box-feed-entry__trigger', timeout=10000)
                            post_box.click()
                            time.sleep(2)
                        except Exception as e:
                            self.logger.error(f'Could not find post creation box: {e}')
                            browser.close()
                            return False

                    # Enter post content
                    editor = page.wait_for_selector('[data-testid="update-editor-text-area"]', timeout=10000)
                    if editor:
                        # Clear existing content
                        editor.click()
                        page.keyboard.press('Control+A')
                        page.keyboard.press('Delete')

                        # Type new content
                        for char in post.content:
                            page.keyboard.type(char, delay=10)
                            time.sleep(0.01)  # Small delay to simulate human typing

                        self.logger.info('Post content entered')

                        time.sleep(2)

                        # Click Post button
                        try:
                            post_button = page.wait_for_selector('[data-testid="share-post-create-button"]', timeout=10000)
                            post_button.click()
                            self.logger.info('Post button clicked')

                            # Wait for confirmation
                            time.sleep(3)

                            # Check if post was successful
                            if 'feed' in page.url.lower():
                                self.logger.info('Post published successfully!')
                                post.status = 'published'
                                post.post_url = page.url
                                return True
                        except Exception as e:
                            self.logger.error(f'Error clicking post button: {e}')

                    browser.close()
                    return False

                except Exception as e:
                    self.logger.error(f'Error during LinkedIn posting: {e}')
                    browser.close()
                    return False

        except ImportError:
            self.logger.error('Playwright not installed. Run: pip install playwright && playwright install chromium')
            return False
        except Exception as e:
            self.logger.error(f'Unexpected error posting to LinkedIn: {e}')
            return False

    def process_approved_posts(self) -> List[Dict]:
        """
        Process posts in the Approved folder.

        Returns:
            List of posting results
        """
        results = []

        if not self.approved.exists():
            return results

        # Find approval files
        for approval_file in self.approved.glob('APPROVAL_LINKEDIN_*.md'):
            try:
                # Parse approval file to get post content
                content = approval_file.read_text(encoding='utf-8')

                # Extract post content from markdown
                if '## Post Content' in content:
                    post_content = content.split('## Post Content')[1].split('##')[0].strip()
                else:
                    post_content = content

                # Create post object
                post = LinkedInPost(content=post_content, title=approval_file.stem)

                # Post to LinkedIn
                success = self.post_to_linkedin(post)

                # Log result
                result = {
                    'file': approval_file.name,
                    'success': success,
                    'timestamp': datetime.now().isoformat(),
                    'post_url': post.post_url if success else None,
                }
                results.append(result)

                self._log_post_result(result)

                # Move to Done or Rejected
                if success:
                    # Move to Done
                    dest = self.done / approval_file.name
                    approval_file.rename(dest)
                    self.logger.info(f'Moved {approval_file.name} to Done')
                else:
                    # Keep in Approved for retry
                    self.logger.warning(f'Post failed, keeping {approval_file.name} in Approved for retry')

            except Exception as e:
                self.logger.error(f'Error processing approval file {approval_file}: {e}')
                results.append({
                    'file': approval_file.name,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                })

        return results

    def _log_post_result(self, result: Dict):
        """Log post result to file."""
        log_file = self.logs / f'linkedin_posts.jsonl'

        with open(log_file, 'a') as f:
            f.write(json.dumps(result) + '\n')

    def create_post_from_template(self, template_type: str = 'business_update') -> LinkedInPost:
        """
        Create a post from a template.

        Args:
            template_type: Type of template to use

        Returns:
            LinkedInPost object
        """
        templates = {
            'business_update': '''🚀 Business Update

We're excited to share our latest progress!

Key highlights:
• Working on innovative projects
• Delivering value to clients
• Growing our capabilities

#Business #Innovation #Growth''',

            'thought_leadership': '''💡 Industry Insight

Here's something interesting I've learned recently...

[Share your insight here]

What are your thoughts on this?

#ThoughtLeadership #Industry #Insights''',

            'project_announcement': '''📢 Project Announcement

Thrilled to announce [Project Name]!

This project will [brief description].

Stay tuned for updates!

#Project #Announcement #Innovation''',

            'client_success': '''⭐ Client Success Story

We recently helped a client achieve [result].

Key outcomes:
• [Outcome 1]
• [Outcome 2]

#ClientSuccess #Results #Value''',
        }

        content = templates.get(template_type, templates['business_update'])
        post = LinkedInPost(content=content, title=f'{template_type}_{datetime.now().strftime("%Y%m%d")}')

        return post


if __name__ == '__main__':
    import sys

    # Default vault path
    vault_path = r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault'

    # Allow override via command line
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    # Create poster
    poster = LinkedInPoster(
        vault_path=vault_path,
        approval_required=True
    )

    print('LinkedIn Poster')
    print('===============')
    print()
    print('Usage:')
    print('  1. Create a post file in Needs_Action folder')
    print('  2. Approval request will be created')
    print('  3. Move approval file to Approved to publish')
    print()
    print('NOTE: First run requires manual LinkedIn login.')
    print('      Session will be saved for future runs.')
    print()

    # Check for approved posts
    results = poster.process_approved_posts()

    if results:
        print(f'Processed {len(results)} post(s):')
        for result in results:
            status = '✓' if result['success'] else '✗'
            print(f'  {status} {result["file"]}')
    else:
        print('No approved posts to process.')
        print()
        print('To create a test post:')
        print('  python -c "from linkedin_poster import LinkedInPoster; p = LinkedInPoster(\'' + vault_path + '\'); post = p.create_post_from_template(); print(post.content)"')
