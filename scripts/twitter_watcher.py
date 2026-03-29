"""
Twitter (X) Integration Module

Monitors and posts to Twitter (X) using Playwright browser automation.
Gold Tier Feature: Social media integration with summary generation.

Setup Instructions:
1. Install Playwright: pip install playwright
2. Install browsers: playwright install chromium
3. First run will require manual login to Twitter/X
4. Session will be saved for subsequent runs

Usage:
    python twitter_watcher.py [vault_path]

Note: Twitter has strict automation policies. Use responsibly.
For production, consider using Twitter API v2 with developer account.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from base_watcher import BaseWatcher


class TwitterPost:
    """Represents a Twitter/X post (tweet)."""

    def __init__(self, content: str, title: str = ''):
        self.title = title
        self.content = content
        self.created = datetime.now().isoformat()
        self.status = 'draft'
        self.images = []
        self.post_url = None
        self.engagement = {
            'likes': 0,
            'retweets': 0,
            'replies': 0,
            'views': 0,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for metadata."""
        return {
            'title': self.title,
            'content': self.content[:200],  # Preview
            'created': self.created,
            'status': self.status,
            'post_url': self.post_url,
            'engagement': self.engagement,
        }


class TwitterWatcher(BaseWatcher):
    """
    Watches and posts to Twitter (X).

    Features:
    - Session persistence
    - Tweet creation and posting
    - Thread support
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
        Initialize the Twitter watcher.

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
            self.session_path = self.vault_path.parent / 'twitter_session'

        self.session_path.mkdir(parents=True, exist_ok=True)

        # Track processed posts
        self.processed_file = self.logs / 'twitter_posts.jsonl'

        # Twitter character limit
        self.max_length = 280

        self.logger.info(f'Twitter Watcher initialized')
        self.logger.info(f'Session path: {self.session_path}')

    def check_for_posts(self) -> List[TwitterPost]:
        """
        Check for posts to publish in Needs_Action folder.

        Returns:
            List of TwitterPost objects
        """
        posts = []

        if not self.needs_action.exists():
            return posts

        # Find Twitter post files
        for file_path in self.needs_action.glob('TWITTER_*.md'):
            try:
                post = self._parse_post_file(file_path)
                if post:
                    posts.append(post)
            except Exception as e:
                self.logger.error(f'Error parsing Twitter post file {file_path}: {e}')

        return posts

    def _parse_post_file(self, file_path: Path) -> Optional[TwitterPost]:
        """Parse a markdown file into a TwitterPost."""
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
            post = TwitterPost(
                content=post_content,
                title=metadata.get('title', file_path.stem)
            )

            # Parse images if specified
            if metadata.get('images'):
                post.images = metadata['images'].split(',')

            return post

        except Exception as e:
            self.logger.error(f'Error parsing post file: {e}')
            return None

    def _split_into_thread(self, content: str) -> List[str]:
        """
        Split long content into a Twitter thread.

        Args:
            content: Full content to post

        Returns:
            List of tweet texts (each <= 280 chars)
        """
        tweets = []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        current_tweet = ''
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If paragraph fits in current tweet
            if len(current_tweet) + len(para) + 2 <= self.max_length:
                if current_tweet:
                    current_tweet += '\n\n' + para
                else:
                    current_tweet = para
            else:
                # Save current tweet and start new one
                if current_tweet:
                    tweets.append(current_tweet)
                current_tweet = para
                
                # If single paragraph is too long, split by sentences
                if len(current_tweet) > self.max_length:
                    sentences = current_tweet.split('. ')
                    current_tweet = ''
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                        if len(current_tweet) + len(sentence) + 2 <= self.max_length:
                            if current_tweet:
                                current_tweet += '. ' + sentence
                            else:
                                current_tweet = sentence
                        else:
                            if current_tweet:
                                tweets.append(current_tweet)
                            current_tweet = sentence
        
        # Don't forget the last tweet
        if current_tweet:
            tweets.append(current_tweet)
        
        return tweets

    def post_to_twitter(self, post: TwitterPost) -> bool:
        """
        Post content to Twitter (X) using browser automation.

        Args:
            post: TwitterPost object to publish

        Returns:
            True if successful, False otherwise
        """
        try:
            from playwright.sync_api import sync_playwright

            self.logger.info('Starting Twitter post process...')

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
                    # Navigate to Twitter
                    page.goto('https://twitter.com', timeout=60000)
                    time.sleep(3)

                    # Check if logged in
                    if 'login' in page.url.lower() or 'welcome' in page.url.lower():
                        self.logger.warning('Not logged in to Twitter. Please login manually.')
                        browser.close()
                        return False

                    # Click on "What is happening?!" box
                    try:
                        # Try different selectors for the tweet box
                        post_box = None
                        selectors = [
                            '[data-testid="tweetTextarea_0"]',
                            '[aria-label="Tweet text"]',
                            'div[contenteditable="true"]'
                        ]
                        
                        for selector in selectors:
                            try:
                                post_box = page.wait_for_selector(selector, timeout=5000)
                                if post_box:
                                    break
                            except:
                                continue
                        
                        if not post_box:
                            self.logger.error('Could not find tweet composition box')
                            browser.close()
                            return False
                        
                        post_box.click()
                        time.sleep(1)

                    except Exception as e:
                        self.logger.error(f'Error finding tweet box: {e}')
                        browser.close()
                        return False

                    # Check if we need to create a thread
                    tweets = self._split_into_thread(post.content)
                    
                    if len(tweets) > 1:
                        self.logger.info(f'Creating thread with {len(tweets)} tweets')
                    
                    # Enter first tweet content
                    for char in tweets[0][:self.max_length]:
                        page.keyboard.type(char, delay=10)
                        time.sleep(0.01)

                    # Add additional tweets for thread
                    for i, tweet_text in enumerate(tweets[1:], 1):
                        try:
                            # Click "Add" button to add another tweet
                            add_button = page.wait_for_selector('[aria-label="Add a new Tweet"]', timeout=5000)
                            if add_button:
                                add_button.click()
                                time.sleep(1)
                                
                                # Find the new textarea and enter content
                                textareas = page.query_selector_all('[data-testid="tweetTextarea_0"]')
                                if len(textareas) > i:
                                    textareas[i].click()
                                    page.keyboard.press('Control+A')
                                    page.keyboard.press('Delete')
                                    for char in tweet_text[:self.max_length]:
                                        page.keyboard.type(char, delay=10)
                                        time.sleep(0.01)
                        except Exception as e:
                            self.logger.warning(f'Could not add tweet {i} to thread: {e}')

                    time.sleep(2)

                    # Click Tweet button
                    try:
                        tweet_button = page.wait_for_selector('[data-testid="tweetButton"]', timeout=10000)
                        if tweet_button:
                            tweet_button.click()
                            time.sleep(3)
                            self.logger.info('Tweet(s) published!')
                            post.status = 'published'
                            return True
                    except Exception as e:
                        self.logger.error(f'Error clicking tweet button: {e}')

                    browser.close()
                    return False

                except Exception as e:
                    self.logger.error(f'Error during Twitter posting: {e}')
                    browser.close()
                    return False

        except ImportError:
            self.logger.error('Playwright not installed')
            return False
        except Exception as e:
            self.logger.error(f'Unexpected error posting to Twitter: {e}')
            return False

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of Twitter activity.

        Returns:
            Summary dictionary
        """
        summary = {
            'platform': 'twitter',
            'generated': datetime.now().isoformat(),
            'tweets_this_week': 0,
            'tweets_this_month': 0,
            'threads_this_month': 0,
            'total_engagement': {
                'likes': 0,
                'retweets': 0,
                'replies': 0,
                'views': 0,
            },
            'recent_tweets': [],
        }

        # Read posts log
        log_file = self.logs / 'twitter_posts.jsonl'
        if log_file.exists():
            with open(log_file, 'r') as f:
                now = datetime.now()
                for line in f:
                    try:
                        post_data = json.loads(line)
                        post_date = datetime.fromisoformat(post_data.get('timestamp', ''))
                        
                        # Count tweets this week
                        if (now - post_date).days <= 7:
                            summary['tweets_this_week'] += 1
                        
                        # Count tweets this month
                        if (now - post_date).days <= 30:
                            summary['tweets_this_month'] += 1
                        
                        # Add to recent tweets (last 5)
                        if len(summary['recent_tweets']) < 5:
                            summary['recent_tweets'].append({
                                'content': post_data.get('content', '')[:100],
                                'timestamp': post_data.get('timestamp', ''),
                                'status': post_data.get('status', 'unknown'),
                                'is_thread': post_data.get('is_thread', False),
                            })
                    except:
                        continue

        return summary

    def _log_post_result(self, result: Dict):
        """Log post result to file."""
        log_file = self.logs / 'twitter_posts.jsonl'
        result['platform'] = 'twitter'

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
    watcher = TwitterWatcher(
        vault_path=vault_path,
        check_interval=60
    )

    print('Twitter (X) Watcher')
    print('===================')
    print()
    print('NOTE: First run requires manual login.')
    print('      Session will be saved for future runs.')
    print()
    print('WARNING: Twitter has strict automation policies.')
    print('         Use responsibly and consider using official API.')
    print()

    # Generate summary
    summary = watcher.generate_summary()

    print(f'Twitter Summary:')
    print(f'  Tweets this week: {summary["tweets_this_week"]}')
    print(f'  Tweets this month: {summary["tweets_this_month"]}')
    print(f'  Threads this month: {summary["threads_this_month"]}')
