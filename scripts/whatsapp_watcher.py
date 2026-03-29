"""
WhatsApp Watcher Module

Monitors WhatsApp Web for new messages and creates action files for Claude to process.
This is a Silver Tier watcher implementation using Playwright for browser automation.

Setup Instructions:
1. Install Playwright: pip install playwright
2. Install browsers: playwright install chromium
3. First run will require QR code scan to authenticate WhatsApp Web
4. Session will be saved for subsequent runs

Usage:
    python whatsapp_watcher.py [vault_path]

Note: Be aware of WhatsApp's terms of service when using automation.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from base_watcher import BaseWatcher


class WhatsAppMessage:
    """Represents a WhatsApp message."""

    def __init__(self, chat_name: str, message_text: str, timestamp: str):
        self.chat_name = chat_name
        self.message_text = message_text
        self.timestamp = timestamp
        self.is_group = False
        self.sender_name = ''
        self.has_media = False
        self.message_type = 'text'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for metadata."""
        return {
            'chat_name': self.chat_name,
            'sender_name': self.sender_name,
            'message_text': self.message_text,
            'timestamp': self.timestamp,
            'is_group': self.is_group,
            'has_media': self.has_media,
            'message_type': self.message_type,
        }


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for new messages and creates action files.

    Features:
    - Monitors unread messages
    - Filters by keywords for prioritization
    - Supports group and individual chats
    - Session persistence for re-authentication
    - Tracks processed messages
    """

    def __init__(
        self,
        vault_path: str,
        session_path: Optional[str] = None,
        check_interval: int = 30,
        keywords: Optional[List[str]] = None
    ):
        """
        Initialize the WhatsApp watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            session_path: Path to store browser session (default: vault parent / whatsapp_session)
            check_interval: Seconds between checks (default: 30)
            keywords: List of keywords to prioritize (default: ['urgent', 'asap', 'invoice', 'payment', 'help'])
        """
        super().__init__(vault_path, check_interval)

        # Setup session path
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = self.vault_path.parent / 'whatsapp_session'

        self.session_path.mkdir(parents=True, exist_ok=True)

        # Keywords for prioritization
        self.keywords = keywords or ['urgent', 'asap', 'invoice', 'payment', 'help', 'important', 'deadline']

        # Track processed messages
        self.processed_file = self.logs / 'whatsapp_processed.txt'
        self.processed_messages = self._load_processed_messages()

        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Priority keywords: {self.keywords}')

    def _load_processed_messages(self) -> set:
        """Load hashes of previously processed messages."""
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                return set(line.strip() for line in f)
        return set()

    def _save_processed_message(self, message_hash: str):
        """Save a message hash to the processed list."""
        with open(self.processed_file, 'a') as f:
            f.write(f'{message_hash}\n')

    def _generate_message_hash(self, message: WhatsAppMessage) -> str:
        """Generate a unique hash for a message."""
        import hashlib
        content = f"{message.chat_name}:{message.message_text}:{message.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()

    def check_for_updates(self) -> List[WhatsAppMessage]:
        """
        Check WhatsApp Web for new messages.

        Returns:
            List of new WhatsAppMessage objects
        """
        try:
            from playwright.sync_api import sync_playwright

            messages = []

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
                    # Navigate to WhatsApp Web
                    page.goto('https://web.whatsapp.com', timeout=60000)

                    # Wait for chat list to load (indicates successful authentication)
                    try:
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                    except Exception:
                        self.logger.warning('WhatsApp Web not authenticated. Please scan QR code.')
                        self.logger.warning('Session will be available for next run after authentication.')
                        browser.close()
                        return []

                    # Small delay for page to fully load
                    time.sleep(2)

                    # Find all chat items with unread messages
                    unread_chats = page.query_selector_all('[aria-label*="unread"], [data-testid="unread-mark"]')

                    self.logger.info(f'Found {len(unread_chats)} unread chat(s)')

                    for chat in unread_chats:
                        try:
                            # Extract chat information
                            chat_element = chat.locator('..').locator('..').locator('..')
                            chat_name_element = chat_element.locator('[data-testid="chat-info"]')

                            if chat_name_element.count() > 0:
                                chat_name = chat_name_element.inner_text()
                            else:
                                # Fallback: try different selector
                                chat_name_element = chat_element.locator('span[title]')
                                if chat_name_element.count() > 0:
                                    chat_name = chat_name_element.first.inner_text()
                                else:
                                    chat_name = 'Unknown Chat'

                            # Get message preview text
                            message_text = chat.inner_text()

                            # Check if message contains priority keywords
                            if any(keyword in message_text.lower() for keyword in self.keywords):
                                message = WhatsAppMessage(
                                    chat_name=chat_name,
                                    message_text=message_text,
                                    timestamp=datetime.now().isoformat()
                                )

                                # Check if it's a group message
                                if 'group' in chat_name.lower() or chat_element.get_attribute('data-testid', timeout=1000) == 'group':
                                    message.is_group = True

                                # Generate hash and check if already processed
                                msg_hash = self._generate_message_hash(message)
                                if msg_hash not in self.processed_messages:
                                    messages.append(message)
                                    self.logger.info(f'New WhatsApp message from {chat_name}: {message_text[:50]}...')

                        except Exception as e:
                            self.logger.debug(f'Error processing chat: {e}')
                            continue

                except Exception as e:
                    self.logger.error(f'Error accessing WhatsApp Web: {e}')
                finally:
                    browser.close()

            return messages

        except ImportError:
            self.logger.error('Playwright not installed. Run: pip install playwright && playwright install chromium')
            return []
        except Exception as e:
            self.logger.error(f'Error in WhatsApp watcher: {e}')
            return []

    def create_action_file(self, message: WhatsAppMessage) -> Optional[Path]:
        """
        Create an action file for the WhatsApp message.

        Args:
            message: WhatsAppMessage object

        Returns:
            Path to created action file
        """
        try:
            # Determine priority
            priority = 'high' if self._is_priority(message) else 'normal'

            # Build suggested actions based on content
            suggested_actions = self._generate_suggested_actions(message)

            # Build metadata
            metadata = message.to_dict()
            metadata['priority'] = priority

            # Build content
            content = f'''Chat: {message.chat_name}
Sender: {message.sender_name or 'N/A'}
Timestamp: {message.timestamp}
Priority: {priority.upper()}
Message Type: {message.message_type}
Is Group: {'Yes' if message.is_group else 'No'}

## Message Content
{message.message_text}

## Context
This message was flagged based on keyword detection.
Please review and respond appropriately.
'''

            # Create action file
            action_file = self.create_standard_action_file(
                prefix='WHATSAPP',
                unique_id=message.chat_name[:20].replace(' ', '_'),
                item_type='whatsapp_message',
                content=content,
                suggested_actions=suggested_actions,
                metadata=metadata
            )

            # Mark as processed
            msg_hash = self._generate_message_hash(message)
            self.processed_messages.add(msg_hash)
            self._save_processed_message(msg_hash)

            return action_file

        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None

    def _is_priority(self, message: WhatsAppMessage) -> bool:
        """Check if message contains priority keywords."""
        text = message.message_text.lower()
        return any(keyword in text for keyword in self.keywords)

    def _generate_suggested_actions(self, message: WhatsAppMessage) -> List[str]:
        """Generate suggested actions based on message content."""
        actions = []
        text_lower = message.message_text.lower()

        # Check for common patterns
        if any(word in text_lower for word in ['invoice', 'payment', 'bill', 'money']):
            actions.extend([
                'Review payment/invoice request',
                'Verify amount and details',
                'Process payment or request approval',
                'Confirm payment sent',
                'Archive after processing'
            ])
        elif any(word in text_lower for word in ['meeting', 'call', 'schedule', 'time']):
            actions.extend([
                'Check availability',
                'Respond with available times',
                'Schedule meeting/call',
                'Add to calendar',
                'Archive after processing'
            ])
        elif any(word in text_lower for word in ['urgent', 'asap', 'emergency', 'help']):
            actions.extend([
                'URGENT: Respond immediately',
                'Address the request',
                'Follow up as needed',
                'Archive after processing'
            ])
        elif any(word in text_lower for word in ['question', 'ask', 'need', 'want']):
            actions.extend([
                'Review question/request',
                'Prepare response',
                'Send reply via WhatsApp',
                'Archive after processing'
            ])
        else:
            actions.extend([
                'Review message',
                'Determine if response needed',
                'Reply via WhatsApp if appropriate',
                'Archive after processing'
            ])

        return actions


if __name__ == '__main__':
    import sys

    # Default vault path
    vault_path = r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault'

    # Allow override via command line
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    # Create and run watcher
    watcher = WhatsAppWatcher(
        vault_path=vault_path,
        check_interval=30  # Check every 30 seconds
    )

    print('WhatsApp Watcher starting...')
    print(f'Vault path: {vault_path}')
    print(f'Session path: {watcher.session_path}')
    print(f'Check interval: 30s')
    print()
    print('NOTE: First run requires QR code scan:')
    print('1. Open WhatsApp on your phone')
    print('2. Go to Settings > Linked Devices')
    print('3. Scan the QR code that will appear')
    print('4. Session will be saved for future runs')
    print()
    print('Press Ctrl+C to stop')
    print()

    watcher.run()
