"""
Social Media Manager - Unified Automation

Manages automated posting to LinkedIn, Facebook, and Instagram from a single interface.
Gold Tier Feature: Cross-platform social media automation with AI-generated content.

Usage:
    python social_media_manager.py [vault_path] [action]

Actions:
    - post: Create and schedule posts
    - status: Check posting status
    - summary: Generate weekly summary
    - setup: Initial setup and authentication
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import platform-specific posters
try:
    from linkedin_poster import LinkedInPoster, LinkedInPost
    LINKEDIN_AVAILABLE = True
except ImportError:
    LINKEDIN_AVAILABLE = False
    print("Warning: LinkedIn poster not available")

try:
    # Don't import the watcher class, just check if module exists
    import facebook_instagram_watcher
    FACEBOOK_INSTAGRAM_AVAILABLE = True
except ImportError:
    FACEBOOK_INSTAGRAM_AVAILABLE = False
    print("Warning: Facebook/Instagram watcher not available")


class SocialMediaManager:
    """
    Unified manager for social media automation across all platforms.

    Features:
    - Create posts for all platforms from single input
    - Cross-platform posting coordination
    - Approval workflow
    - Performance tracking
    - Weekly summaries
    """

    def __init__(self, vault_path: str):
        """
        Initialize the social media manager.

        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.files = self.vault_path / 'Files'

        # Ensure directories exist
        for folder in [self.needs_action, self.pending_approval, self.approved, 
                       self.done, self.logs, self.files]:
            folder.mkdir(parents=True, exist_ok=True)

        # Initialize platform posters
        self.linkedin_poster = None
        self.fb_ig_watcher = None

        if LINKEDIN_AVAILABLE:
            self.linkedin_poster = LinkedInPoster(
                vault_path=str(vault_path),
                approval_required=True
            )

        if FACEBOOK_INSTAGRAM_AVAILABLE:
            # Import here to avoid circular imports
            from facebook_instagram_watcher import FacebookInstagramWatcher
            self.fb_ig_watcher = FacebookInstagramWatcher(
                vault_path=str(vault_path),
                check_interval=60
            )

        # Setup logging
        self.logger = self._setup_logging()
        self.logger.info(f'Social Media Manager initialized')

    def _setup_logging(self):
        """Setup logging."""
        import logging

        log_file = self.logs / f'social_media_{datetime.now().strftime("%Y-%m-%d")}.log'

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logger = logging.getLogger('SocialMediaManager')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def create_cross_platform_post(
        self,
        topic: str,
        content: str,
        platforms: List[str] = None,
        hashtags: List[str] = None,
        schedule_time: Optional[str] = None
    ) -> Dict[str, Path]:
        """
        Create posts for multiple platforms from single input.

        Args:
            topic: Post topic/title
            content: Main content
            platforms: List of platforms ['linkedin', 'facebook', 'instagram']
            hashtags: List of hashtags
            schedule_time: Optional scheduled time

        Returns:
            Dictionary of platform -> post file path
        """
        if platforms is None:
            platforms = ['linkedin', 'facebook', 'instagram']

        if hashtags is None:
            hashtags = ['#Business', '#Innovation', '#Growth']

        created_files = {}

        # Create LinkedIn post
        if 'linkedin' in platforms:
            linkedin_file = self._create_linkedin_post(topic, content, hashtags, schedule_time)
            if linkedin_file:
                created_files['linkedin'] = linkedin_file

        # Create Facebook post
        if 'facebook' in platforms:
            facebook_file = self._create_facebook_post(topic, content, hashtags, schedule_time)
            if facebook_file:
                created_files['facebook'] = facebook_file

        # Create Instagram post
        if 'instagram' in platforms:
            instagram_file = self._create_instagram_post(topic, content, hashtags, schedule_time)
            if instagram_file:
                created_files['instagram'] = instagram_file

        self.logger.info(f'Created {len(created_files)} post files')
        return created_files

    def _create_linkedin_post(
        self,
        topic: str,
        content: str,
        hashtags: List[str],
        schedule_time: Optional[str] = None
    ) -> Optional[Path]:
        """Create a LinkedIn post file."""
        try:
            # Format content for LinkedIn (professional tone)
            linkedin_content = self._format_for_linkedin(content, hashtags)

            post_content = f'''---
type: social_media_post
platform: linkedin
title: {topic}
created: {datetime.now().isoformat()}
status: draft
{f"scheduled_time: {schedule_time}" if schedule_time else ""}
---

# LinkedIn Post: {topic}

## Content
{linkedin_content}

## Posting Instructions
1. Review the content above
2. Move this file to /Pending_Approval for approval
3. Once approved, move to /Approved for posting
4. Post will be published automatically

## Notes
- Professional tone optimized for LinkedIn
- Includes relevant hashtags
- Character count: {len(linkedin_content)}
'''

            filename = f"LINKEDIN_{topic.replace(' ', '_')[:30]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            file_path = self.needs_action / filename
            file_path.write_text(post_content, encoding='utf-8')

            self.logger.info(f'Created LinkedIn post: {filename}')
            return file_path

        except Exception as e:
            self.logger.error(f'Error creating LinkedIn post: {e}')
            return None

    def _create_facebook_post(
        self,
        topic: str,
        content: str,
        hashtags: List[str],
        schedule_time: Optional[str] = None
    ) -> Optional[Path]:
        """Create a Facebook post file."""
        try:
            # Format content for Facebook (casual tone)
            facebook_content = self._format_for_facebook(content, hashtags)

            post_content = f'''---
type: social_media_post
platform: facebook
title: {topic}
created: {datetime.now().isoformat()}
status: draft
{f"scheduled_time: {schedule_time}" if schedule_time else ""}
---

# Facebook Post: {topic}

## Content
{facebook_content}

## Posting Instructions
1. Review the content above
2. Move this file to /Pending_Approval for approval
3. Once approved, move to /Approved for posting
4. Post will be published automatically

## Notes
- Casual tone optimized for Facebook
- Includes relevant hashtags
- Character count: {len(facebook_content)}
'''

            filename = f"FACEBOOK_{topic.replace(' ', '_')[:30]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            file_path = self.needs_action / filename
            file_path.write_text(post_content, encoding='utf-8')

            self.logger.info(f'Created Facebook post: {filename}')
            return file_path

        except Exception as e:
            self.logger.error(f'Error creating Facebook post: {e}')
            return None

    def _create_instagram_post(
        self,
        topic: str,
        content: str,
        hashtags: List[str],
        schedule_time: Optional[str] = None
    ) -> Optional[Path]:
        """Create an Instagram post file."""
        try:
            # Format content for Instagram (visual-focused, emoji-friendly)
            instagram_content = self._format_for_instagram(content, hashtags)

            post_content = f'''---
type: social_media_post
platform: instagram
title: {topic}
created: {datetime.now().isoformat()}
status: draft
{f"scheduled_time: {schedule_time}" if schedule_time else ""}
images: []  # Add image paths here
---

# Instagram Post: {topic}

## Content
{instagram_content}

## Posting Instructions
1. Review the content above
2. Add image URLs or paths in the images field above
3. Move this file to /Pending_Approval for approval
4. Once approved, move to /Approved for posting
5. Note: Instagram requires images - manual upload may be needed

## Notes
- Visual-focused content with emojis
- Hashtags optimized for Instagram
- Character count: {len(instagram_content)}
'''

            filename = f"INSTAGRAM_{topic.replace(' ', '_')[:30]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            file_path = self.needs_action / filename
            file_path.write_text(post_content, encoding='utf-8')

            self.logger.info(f'Created Instagram post: {filename}')
            return file_path

        except Exception as e:
            self.logger.error(f'Error creating Instagram post: {e}')
            return None

    def _format_for_linkedin(self, content: str, hashtags: List[str]) -> str:
        """Format content for LinkedIn (professional)."""
        formatted = f"""{content}

---
Read more about our work and innovations.

{' '.join(hashtags)}"""
        return formatted

    def _format_for_facebook(self, content: str, hashtags: List[str]) -> str:
        """Format content for Facebook (casual)."""
        formatted = f"""📢 {content}

---
Share with your friends! 👍

{' '.join(hashtags)}"""
        return formatted

    def _format_for_instagram(self, content: str, hashtags: List[str]) -> str:
        """Format content for Instagram (visual, emoji-friendly)."""
        formatted = f"""✨ {content}

---
📸 Double tap if you agree!
💬 Comment your thoughts below!
🔗 Link in bio for more!

{' '.join(hashtags)}
#InstaDaily #Explore"""
        return formatted

    def process_all_platforms(self) -> Dict[str, List[Dict]]:
        """
        Process approved posts for all platforms.

        Returns:
            Dictionary of platform -> posting results
        """
        results = {}

        # Process LinkedIn
        if self.linkedin_poster:
            self.logger.info('Processing LinkedIn posts...')
            results['linkedin'] = self.linkedin_poster.process_approved_posts()

        # Process Facebook and Instagram
        if self.fb_ig_watcher:
            self.logger.info('Processing Facebook/Instagram posts...')
            # Note: Facebook/Instagram watcher needs to be extended to process approved posts
            # For now, we'll just log that it's ready
            results['facebook'] = []
            results['instagram'] = []

        return results

    def generate_weekly_summary(self) -> Dict[str, Any]:
        """
        Generate a weekly summary of all social media activity.

        Returns:
            Summary dictionary
        """
        summary = {
            'generated': datetime.now().isoformat(),
            'period': 'weekly',
            'platforms': {},
            'total_posts': 0,
            'total_engagement': {
                'likes': 0,
                'comments': 0,
                'shares': 0,
            },
        }

        # LinkedIn summary
        if self.linkedin_poster:
            linkedin_log = self.logs / 'linkedin_posts.jsonl'
            if linkedin_log.exists():
                linkedin_posts = self._count_posts(linkedin_log)
                summary['platforms']['linkedin'] = linkedin_posts
                summary['total_posts'] += linkedin_posts['count']

        # Facebook summary
        if self.fb_ig_watcher:
            fb_summary = self.fb_ig_watcher.generate_summary('facebook')
            summary['platforms']['facebook'] = {
                'count': fb_summary['posts_this_week'],
                'engagement': fb_summary['total_engagement'],
            }
            summary['total_posts'] += fb_summary['posts_this_week']

            # Instagram summary
            ig_summary = self.fb_ig_watcher.generate_summary('instagram')
            summary['platforms']['instagram'] = {
                'count': ig_summary['posts_this_week'],
                'engagement': ig_summary['total_engagement'],
            }
            summary['total_posts'] += ig_summary['posts_this_week']

        # Save summary
        summary_file = self.logs / f'social_media_summary_{datetime.now().strftime("%Y-%m-%d")}.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f'Weekly summary generated: {summary["total_posts"]} total posts')
        return summary

    def _count_posts(self, log_file: Path) -> Dict:
        """Count posts from log file."""
        count = 0
        now = datetime.now()

        try:
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        post_data = json.loads(line)
                        post_date = datetime.fromisoformat(post_data.get('timestamp', ''))
                        if (now - post_date).days <= 7:
                            count += 1
                    except:
                        continue
        except:
            pass

        return {
            'count': count,
            'period': 'weekly',
        }

    def setup_platforms(self):
        """
        Guide user through platform setup.

        Returns:
            Setup status dictionary
        """
        setup_status = {
            'linkedin': False,
            'facebook': False,
            'instagram': False,
        }

        print("\n" + "=" * 60)
        print("Social Media Platform Setup")
        print("=" * 60)

        # LinkedIn setup
        print("\n1. LinkedIn Setup")
        print("-" * 40)
        if LINKEDIN_AVAILABLE:
            print("✅ LinkedIn poster is available")
            print("📝 First run will require manual login")
            print("📝 Session will be saved for future runs")
            setup_status['linkedin'] = True
        else:
            print("❌ LinkedIn poster not available")
            print("💡 Install: pip install playwright && playwright install chromium")

        # Facebook setup
        print("\n2. Facebook Setup")
        print("-" * 40)
        if FACEBOOK_INSTAGRAM_AVAILABLE:
            print("✅ Facebook watcher is available")
            print("📝 First run will require manual login")
            print("📝 Session will be saved for future runs")
            setup_status['facebook'] = True
        else:
            print("❌ Facebook watcher not available")
            print("💡 Install: pip install playwright && playwright install chromium")

        # Instagram setup
        print("\n3. Instagram Setup")
        print("-" * 40)
        if FACEBOOK_INSTAGRAM_AVAILABLE:
            print("✅ Instagram watcher is available")
            print("📝 First run will require manual login")
            print("📝 Session will be saved for future runs")
            print("⚠️  Note: Instagram requires images for posts")
            setup_status['instagram'] = True
        else:
            print("❌ Instagram watcher not available")
            print("💡 Install: pip install playwright && playwright install chromium")

        print("\n" + "=" * 60)
        print("Setup Complete!")
        print("=" * 60)

        return setup_status


def main():
    """Main entry point."""
    vault_path = r'D:\Quarter_4\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault'

    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    manager = SocialMediaManager(vault_path=vault_path)

    if len(sys.argv) > 2:
        action = sys.argv[2]
    else:
        action = 'status'

    if action == 'setup':
        manager.setup_platforms()

    elif action == 'summary':
        summary = manager.generate_weekly_summary()
        print("\nWeekly Social Media Summary")
        print("=" * 40)
        print(f"Total Posts: {summary['total_posts']}")
        for platform, data in summary['platforms'].items():
            print(f"{platform.capitalize()}: {data.get('count', 0)} posts")

    elif action == 'post':
        # Create a test post
        print("\nCreating test cross-platform post...")
        files = manager.create_cross_platform_post(
            topic='AI Employee Update',
            content='Excited to share our latest progress on automating business tasks with AI!',
            platforms=['linkedin', 'facebook', 'instagram'],
            hashtags=['#AI', '#Automation', '#Innovation']
        )
        print(f"Created {len(files)} post files:")
        for platform, file_path in files.items():
            print(f"  {platform}: {file_path.name}")

    else:
        # Status
        print("\nSocial Media Manager Status")
        print("=" * 40)
        print(f"LinkedIn: {'✅' if LINKEDIN_AVAILABLE else '❌'}")
        print(f"Facebook: {'✅' if FACEBOOK_INSTAGRAM_AVAILABLE else '❌'}")
        print(f"Instagram: {'✅' if FACEBOOK_INSTAGRAM_AVAILABLE else '❌'}")
        print(f"\nVault: {vault_path}")


if __name__ == '__main__':
    main()
