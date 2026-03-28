"""
Base Watcher Module

Abstract base class for all watcher scripts in the AI Employee system.
All watchers follow the same pattern: monitor, detect, create action files.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher scripts.
    
    Watchers are lightweight Python scripts that run continuously in the background,
    monitoring various inputs and creating actionable files for Claude to process.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
        self.logger.info(f'{self.__class__.__name__} initialized')
    
    def _setup_logging(self):
        """Setup logging to file and console."""
        log_file = self.logs / f'watcher_{datetime.now().strftime("%Y-%m-%d")}.log'
        
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
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items to process.
        
        Returns:
            List of new items that need action
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file, or None if failed
        """
        pass
    
    def generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a unique filename for an action file.
        
        Args:
            prefix: File prefix (e.g., 'EMAIL', 'FILE', 'WHATSAPP')
            unique_id: Unique identifier for the item
            
        Returns:
            Filename string
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{prefix}_{unique_id}_{timestamp}.md'
    
    def create_standard_action_file(
        self,
        prefix: str,
        unique_id: str,
        item_type: str,
        content: str,
        suggested_actions: List[str],
        metadata: Optional[dict] = None
    ) -> Path:
        """
        Create a standard formatted action file.
        
        Args:
            prefix: File prefix
            unique_id: Unique identifier
            item_type: Type of item (email, file, message, etc.)
            content: Main content of the item
            suggested_actions: List of suggested actions as markdown checkboxes
            metadata: Additional metadata for frontmatter
            
        Returns:
            Path to the created file
        """
        # Build frontmatter
        frontmatter = [
            '---',
            f'type: {item_type}',
            f'created: {datetime.now().isoformat()}',
            'status: pending',
        ]
        
        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                frontmatter.append(f'{key}: {value}')
        
        frontmatter.append('---')
        
        # Build suggested actions section
        actions_text = '\n'.join([f'- [ ] {action}' for action in suggested_actions])
        
        # Combine all content
        full_content = f'''{'\n'.join(frontmatter)}

## Content
{content}

## Suggested Actions
{actions_text}

## Notes
Add any additional context or notes here.
'''
        
        # Write file
        filepath = self.needs_action / self.generate_filename(prefix, unique_id)
        filepath.write_text(full_content, encoding='utf-8')
        
        self.logger.info(f'Created action file: {filepath.name}')
        return filepath
    
    def run(self):
        """
        Main run loop for the watcher.
        
        Continuously checks for updates and creates action files.
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s) to process')
                        for item in items:
                            try:
                                self.create_action_file(item)
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new items found')
                        
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
        finally:
            self.logger.info(f'{self.__class__.__name__} shutting down')
    
    def stop(self):
        """Stop the watcher gracefully."""
        self.logger.info(f'Stopping {self.__class__.__name__}')


if __name__ == '__main__':
    # Example usage (for testing)
    print("BaseWatcher is an abstract class. Subclass it to create a specific watcher.")
    print("Example: FilesystemWatcher, GmailWatcher, WhatsAppWatcher")
