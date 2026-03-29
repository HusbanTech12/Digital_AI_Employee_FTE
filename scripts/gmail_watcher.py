"""
Gmail Watcher Module

Monitors Gmail for new unread messages and creates action files for Claude to process.
This is a Silver Tier watcher implementation.

Setup Instructions:
1. Enable Gmail API: https://developers.google.com/gmail/api/quickstart/python
2. Download credentials.json and place in project root
3. First run will open browser for OAuth authorization
4. Token will be saved as token.json

Usage:
    python gmail_watcher.py [vault_path]
"""

import os
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from base_watcher import BaseWatcher


class GmailMessage:
    """Represents a Gmail message."""

    def __init__(self, message_id: str, thread_id: str, internal_date: str):
        self.message_id = message_id
        self.thread_id = thread_id
        self.internal_date = internal_date
        self.subject = ''
        self.sender = ''
        self.recipients = ''
        self.date = ''
        self.body = ''
        self.snippet = ''
        self.labels = []
        self.attachments = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for metadata."""
        return {
            'message_id': self.message_id,
            'thread_id': self.thread_id,
            'subject': self.subject,
            'sender': self.sender,
            'recipients': self.recipients,
            'date': self.date,
            'snippet': self.snippet,
            'labels': ', '.join(self.labels),
            'has_attachments': len(self.attachments) > 0,
        }


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new unread messages and creates action files.

    Features:
    - Monitors unread messages
    - Filters by importance/keywords
    - Extracts full message content
    - Handles attachments
    - Tracks processed messages
    """

    def __init__(
        self,
        vault_path: str,
        credentials_path: Optional[str] = None,
        check_interval: int = 120,
        keywords: Optional[List[str]] = None
    ):
        """
        Initialize the Gmail watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            credentials_path: Path to Gmail credentials JSON (default: credentials.json)
            check_interval: Seconds between checks (default: 120)
            keywords: List of keywords to prioritize (default: ['urgent', 'asap', 'invoice', 'payment'])
        """
        super().__init__(vault_path, check_interval)

        # Setup credentials
        self.credentials_path = Path(credentials_path or 'credentials.json')
        self.token_path = self.vault_path.parent / 'token.json'

        # Keywords for prioritization
        self.keywords = keywords or ['urgent', 'asap', 'invoice', 'payment', 'important', 'deadline']

        # Gmail API service (initialized on first use)
        self.service = None

        # Load previously processed messages
        self.processed_file = self.logs / 'gmail_processed.txt'
        self.processed_ids = self._load_processed_ids()

        self.logger.info(f'Credentials path: {self.credentials_path}')
        self.logger.info(f'Priority keywords: {self.keywords}')

    def _load_processed_ids(self) -> set:
        """Load IDs of previously processed messages."""
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                return set(line.strip() for line in f)
        return set()

    def _save_processed_id(self, message_id: str):
        """Save a message ID to the processed list."""
        with open(self.processed_file, 'a') as f:
            f.write(f'{message_id}\n')

    def _authenticate(self):
        """Authenticate with Gmail API."""
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = None

        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(self.token_path, ['https://www.googleapis.com/auth/gmail.readonly'])

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    self.logger.error(f'Credentials file not found: {self.credentials_path}')
                    self.logger.error('Please download credentials.json from Google Cloud Console')
                    raise FileNotFoundError(f'Gmail credentials not found at {self.credentials_path}')

                self.logger.info('Opening browser for Gmail OAuth...')
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    ['https://www.googleapis.com/auth/gmail.readonly']
                )
                creds = flow.run_local_server(port=0)

            # Save token
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info('Gmail API authenticated successfully')

    def check_for_updates(self) -> List[GmailMessage]:
        """
        Check Gmail for new unread messages.

        Returns:
            List of new GmailMessage objects
        """
        if self.service is None:
            try:
                self._authenticate()
            except Exception as e:
                self.logger.error(f'Authentication failed: {e}')
                return []

        try:
            # Fetch unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=20
            ).execute()

            messages = results.get('messages', [])
            new_messages = []

            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    try:
                        message = self._fetch_message(msg['id'])
                        if message:
                            new_messages.append(message)
                            self.logger.info(f'New email: {message.subject} from {message.sender}')
                    except Exception as e:
                        self.logger.error(f'Error fetching message {msg["id"]}: {e}')

            return new_messages

        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []

    def _fetch_message(self, message_id: str) -> Optional[GmailMessage]:
        """Fetch full message details from Gmail API."""
        try:
            raw_message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='raw',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()

            # Decode body
            body_data = base64.urlsafe_b64decode(raw_message['raw'].encode('ASCII'))
            body_text = body_data.decode('utf-8', errors='replace')

            # Get headers
            headers = raw_message.get('payload', {}).get('headers', [])
            header_dict = {h['name']: h['value'] for h in headers}

            # Create message object
            message = GmailMessage(
                message_id=message_id,
                thread_id=raw_message.get('threadId', ''),
                internal_date=raw_message.get('internalDate', '')
            )

            message.subject = header_dict.get('Subject', 'No Subject')
            message.sender = header_dict.get('From', 'Unknown')
            message.recipients = header_dict.get('To', '')
            message.date = header_dict.get('Date', '')
            message.snippet = raw_message.get('snippet', '')
            message.body = body_text
            message.labels = raw_message.get('labelIds', [])

            # Check for attachments
            parts = self._get_attachments(raw_message.get('payload', {}))
            message.attachments = parts

            return message

        except Exception as e:
            self.logger.error(f'Error fetching message details: {e}')
            return None

    def _get_attachments(self, payload: Dict) -> List[Dict]:
        """Extract attachment information from message payload."""
        attachments = []

        if 'parts' in payload:
            for part in payload['parts']:
                if part['filename'] and part['body'].get('attachmentId'):
                    attachments.append({
                        'filename': part['filename'],
                        'attachment_id': part['body']['attachmentId'],
                        'mime_type': part.get('mimeType', 'application/octet-stream'),
                        'size': part['body'].get('size', 0)
                    })

        return attachments

    def _is_priority(self, message: GmailMessage) -> bool:
        """Check if message contains priority keywords."""
        text = f"{message.subject} {message.snippet}".lower()
        return any(keyword in text for keyword in self.keywords)

    def create_action_file(self, message: GmailMessage) -> Optional[Path]:
        """
        Create an action file for the email.

        Args:
            message: GmailMessage object

        Returns:
            Path to created action file
        """
        try:
            # Determine priority
            priority = 'high' if self._is_priority(message) else 'normal'

            # Check if sender is known (from Company Handbook or previous interactions)
            is_known_contact = self._check_known_contact(message.sender)

            # Build suggested actions based on content
            suggested_actions = self._generate_suggested_actions(message, is_known_contact)

            # Build metadata
            metadata = message.to_dict()
            metadata['priority'] = priority
            metadata['is_known_contact'] = is_known_contact

            # Build content
            content = f'''From: {message.sender}
To: {message.recipients}
Subject: {message.subject}
Date: {message.date}

## Email Body
{message.body}

## Attachments
{self._format_attachments(message.attachments)}

## Context
Priority Level: {priority.upper()}
Known Contact: {'Yes' if is_known_contact else 'No'}
'''

            # Create action file
            action_file = self.create_standard_action_file(
                prefix='EMAIL',
                unique_id=message.message_id[:12],
                item_type='email',
                content=content,
                suggested_actions=suggested_actions,
                metadata=metadata
            )

            # Mark as processed
            self.processed_ids.add(message.message_id)
            self._save_processed_id(message.message_id)

            # Mark message as read in Gmail
            self._mark_as_read(message.message_id)

            return action_file

        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None

    def _check_known_contact(self, sender: str) -> bool:
        """Check if sender is a known contact."""
        # Extract email from sender string
        import re
        email_match = re.search(r'<([^>]+)>', sender)
        email = email_match.group(1) if email_match else sender

        # Check Company Handbook for known contacts
        handbook_path = self.vault_path / 'Company_Handbook.md'
        if handbook_path.exists():
            content = handbook_path.read_text().lower()
            if email.lower() in content or sender.lower() in content:
                return True

        # Check Dashboard for known contacts
        dashboard_path = self.vault_path / 'Dashboard.md'
        if dashboard_path.exists():
            content = dashboard_path.read_text().lower()
            if email.lower() in content:
                return True

        return False

    def _generate_suggested_actions(self, message: GmailMessage, is_known_contact: bool) -> List[str]:
        """Generate suggested actions based on email content."""
        actions = []
        subject_lower = message.subject.lower()
        body_lower = message.body.lower()

        # Check for common patterns
        if any(word in subject_lower or word in body_lower for word in ['invoice', 'payment', 'bill']):
            actions.extend([
                'Review invoice details',
                'Verify amount and due date',
                'Process payment or forward to accounting',
                'Archive after processing'
            ])
        elif any(word in subject_lower or word in body_lower for word in ['meeting', 'schedule', 'calendar']):
            actions.extend([
                'Check availability',
                'Respond with available times',
                'Add to calendar if confirmed',
                'Archive after processing'
            ])
        elif any(word in subject_lower or word in body_lower for word in ['proposal', 'quote', 'estimate']):
            actions.extend([
                'Review proposal details',
                'Evaluate terms and pricing',
                'Prepare response or counter-proposal',
                'Archive after processing'
            ])
        elif any(word in subject_lower or word in body_lower for word in ['urgent', 'asap', 'emergency']):
            actions.extend([
                'URGENT: Review immediately',
                'Take necessary action',
                'Follow up as needed',
                'Archive after processing'
            ])
        elif is_known_contact:
            actions.extend([
                'Reply to sender',
                'Take necessary action',
                'Archive after processing'
            ])
        else:
            actions.extend([
                'Review email content',
                'Determine if action needed',
                'Reply or delegate as appropriate',
                'Archive after processing'
            ])

        return actions

    def _format_attachments(self, attachments: List[Dict]) -> str:
        """Format attachment list for display."""
        if not attachments:
            return 'No attachments'

        lines = ['Attachments:']
        for att in attachments:
            size_kb = att['size'] / 1024
            lines.append(f"  - {att['filename']} ({size_kb:.1f} KB)")
        return '\n'.join(lines)

    def _mark_as_read(self, message_id: str):
        """Mark a message as read in Gmail."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.debug(f'Marked message {message_id} as read')
        except Exception as e:
            self.logger.error(f'Error marking message as read: {e}')


if __name__ == '__main__':
    import sys

    # Default vault path
    vault_path = r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault'

    # Allow override via command line
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    # Check for credentials
    creds_path = Path('credentials.json')
    if not creds_path.exists():
        print('ERROR: credentials.json not found!')
        print('Please download Gmail credentials from Google Cloud Console:')
        print('https://developers.google.com/gmail/api/quickstart/python')
        print(f'Expected location: {creds_path.absolute()}')
        sys.exit(1)

    # Create and run watcher
    watcher = GmailWatcher(
        vault_path=vault_path,
        credentials_path=str(creds_path),
        check_interval=120  # Check every 2 minutes
    )

    print('Gmail Watcher starting...')
    print(f'Vault path: {vault_path}')
    print(f'Check interval: 120s')
    print('Press Ctrl+C to stop')
    print()

    watcher.run()
