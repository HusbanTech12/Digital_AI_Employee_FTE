"""
File System Watcher Module

Monitors a drop folder for new files and creates action files for Claude to process.
This is the Bronze Tier watcher implementation.

Note: Uses polling method (no external dependencies required).
For better performance, install watchdog: pip install watchdog
"""

import shutil
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from base_watcher import BaseWatcher


class FileDropItem:
    """Represents a file dropped for processing."""

    def __init__(self, source_path: Path):
        self.source_path = source_path
        self.name = source_path.name
        self.size = source_path.stat().st_size
        self.size_human = self._human_readable_size(self.size)
        self.created = source_path.stat().st_ctime
        self.modified = source_path.stat().st_mtime
        self.content_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate MD5 hash of file content."""
        hash_md5 = hashlib.md5()
        with open(self.source_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for metadata."""
        return {
            'original_name': self.name,
            'size': self.size,
            'size_human': self.size_human,
            'created': datetime.fromtimestamp(self.created).isoformat(),
            'modified': datetime.fromtimestamp(self.modified).isoformat(),
            'content_hash': self.content_hash,
        }

    @staticmethod
    def _human_readable_size(size: int) -> str:
        """Convert bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.2f} {unit}'
            size /= 1024
        return f'{size:.2f} TB'


class FilesystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files and creates action files.
    
    Usage:
        Drop files into the /Inbox folder, and this watcher will:
        1. Detect the new file
        2. Copy it to the vault
        3. Create an action file in /Needs_Action
        4. Claude will process the action file
    """
    
    def __init__(
        self,
        vault_path: str,
        drop_folder: Optional[str] = None,
        check_interval: int = 30,
        processed_file: Optional[str] = None
    ):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            drop_folder: Path to the drop folder (defaults to vault/Inbox)
            check_interval: Seconds between checks (default: 30)
            processed_file: Path to file tracking processed files (for persistence)
        """
        super().__init__(vault_path, check_interval)
        
        # Setup drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.inbox
        
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup processed files tracking
        if processed_file:
            self.processed_file = Path(processed_file)
        else:
            self.processed_file = self.logs / 'filesystem_processed.txt'
        
        # Load previously processed files
        self.processed_hashes = self._load_processed_hashes()
        
        # File type configurations
        self.file_handlers = {
            '.txt': self._handle_text_file,
            '.md': self._handle_markdown_file,
            '.pdf': self._handle_pdf_file,
            '.doc': self._handle_document_file,
            '.docx': self._handle_document_file,
            '.xls': self._handle_spreadsheet_file,
            '.xlsx': self._handle_spreadsheet_file,
            '.csv': self._handle_csv_file,
            '.jpg': self._handle_image_file,
            '.jpeg': self._handle_image_file,
            '.png': self._handle_image_file,
            '.json': self._handle_json_file,
        }
        
        self.logger.info(f'Drop folder: {self.drop_folder}')
    
    def _load_processed_hashes(self) -> set:
        """Load hashes of previously processed files."""
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                return set(line.strip() for line in f)
        return set()
    
    def _save_processed_hash(self, file_hash: str):
        """Save a file hash to the processed list."""
        with open(self.processed_file, 'a') as f:
            f.write(f'{file_hash}\n')
    
    def check_for_updates(self) -> List[FileDropItem]:
        """
        Check the drop folder for new files.
        
        Returns:
            List of new FileDropItem objects
        """
        new_items = []
        
        if not self.drop_folder.exists():
            self.logger.warning(f'Drop folder does not exist: {self.drop_folder}')
            return []
        
        # Get all files in drop folder
        files = [f for f in self.drop_folder.iterdir() if f.is_file()]
        
        for file_path in files:
            try:
                item = FileDropItem(file_path)
                
                # Skip if already processed
                if item.content_hash in self.processed_hashes:
                    self.logger.debug(f'Skipping already processed: {item.name}')
                    continue
                
                # Skip temporary files
                if item.name.startswith('~') or item.name.endswith('.tmp'):
                    continue
                
                new_items.append(item)
                self.logger.info(f'New file detected: {item.name} ({item.size_human})')
                
            except Exception as e:
                self.logger.error(f'Error processing file {file_path}: {e}')
        
        return new_items
    
    def create_action_file(self, item: FileDropItem) -> Optional[Path]:
        """
        Create an action file for the dropped file.
        
        Args:
            item: FileDropItem to create action file for
            
        Returns:
            Path to created action file
        """
        try:
            # Copy file to vault
            dest_folder = self.vault_path / 'Files'
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_path = dest_folder / item.name
            
            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = Path(item.name).stem
                suffix = Path(item.name).suffix
                dest_path = dest_folder / f'{stem}_{counter}{suffix}'
                counter += 1
            
            shutil.copy2(item.source_path, dest_path)
            self.logger.info(f'Copied file to vault: {dest_path.name}')
            
            # Get handler-specific content and actions
            handler = self.file_handlers.get(
                Path(item.name).suffix.lower(),
                self._handle_unknown_file
            )
            content, actions, file_type = handler(item, dest_path)
            
            # Create metadata
            metadata = item.to_dict()
            metadata['copied_to'] = str(dest_path)
            metadata['file_type'] = file_type
            
            # Create action file
            action_file = self.create_standard_action_file(
                prefix='FILE',
                unique_id=Path(item.name).stem[:20],  # Truncate long names
                item_type='file_drop',
                content=content,
                suggested_actions=actions,
                metadata=metadata
            )
            
            # Mark as processed
            self.processed_hashes.add(item.content_hash)
            self._save_processed_hash(item.content_hash)
            
            # Optionally remove from drop folder after processing
            # item.source_path.unlink()  # Uncomment to auto-delete from drop folder
            
            return action_file
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _handle_text_file(self, item: FileDropItem, dest_path: Path) -> tuple:
        """Handle text files."""
        try:
            content = dest_path.read_text(encoding='utf-8', errors='replace')
            # Truncate long content
            if len(content) > 2000:
                content = content[:2000] + '\n\n... [content truncated]'
        except Exception:
            content = '[Unable to read text content]'
        
        actions = [
            'Review file content',
            'Extract key information',
            'Take necessary action',
            'Archive after processing'
        ]
        
        return content, actions, 'text'
    
    def _handle_markdown_file(self, item: FileDropItem, dest_path: Path) -> tuple:
        """Handle markdown files."""
        try:
            content = dest_path.read_text(encoding='utf-8', errors='replace')
        except Exception:
            content = '[Unable to read markdown content]'
        
        actions = [
            'Review markdown content',
            'Merge with existing notes if needed',
            'Take necessary action',
            'Archive after processing'
        ]
        
        return content, actions, 'markdown'
    
    def _handle_pdf_file(self, item: FileDropItem, dest_path: Path) -> tuple:
        """Handle PDF files."""
        content = f'''PDF Document: {item.name}
Size: {item.size_human}
Location: {dest_path}

Note: PDF content extraction requires additional tools.
Please open the PDF and summarize its contents for action.

Suggested: Use Adobe Reader or browser to review.'''
        
        actions = [
            'Open and review PDF',
            'Summarize key points',
            'Extract action items',
            'Archive after processing'
        ]
        
        return content, actions, 'pdf'
    
    def _handle_document_file(self, item: FileDropItem, dest_path: Path) -> tuple:
        """Handle Word documents."""
        content = f'''Document: {item.name}
Size: {item.size_human}
Location: {dest_path}

Note: Document content extraction requires additional tools.
Please open the document and summarize its contents.'''
        
        actions = [
            'Open and review document',
            'Summarize key points',
            'Extract action items',
            'Archive after processing'
        ]
        
        return content, actions, 'document'
    
    def _handle_spreadsheet_file(self, item: FileDropItem, dest_path: Path) -> tuple:
        """Handle Excel files."""
        content = f'''Spreadsheet: {item.name}
Size: {item.size_human}
Location: {dest_path}

Note: Spreadsheet content extraction requires additional tools.
Please open the spreadsheet and summarize its contents.'''
        
        actions = [
            'Open and review spreadsheet',
            'Analyze data',
            'Extract key metrics',
            'Archive after processing'
        ]
        
        return content, actions, 'spreadsheet'
    
    def _handle_csv_file(self, item: FileDropItem, dest_path: Path) -> tuple:
        """Handle CSV files."""
        try:
            content = dest_path.read_text(encoding='utf-8', errors='replace')
            # Show first few lines
            lines = content.split('\n')[:20]
            content = '\n'.join(lines)
            if len(content) > 1000:
                content = content[:1000] + '\n\n... [content truncated]'
        except Exception:
            content = '[Unable to read CSV content]'
        
        actions = [
            'Review CSV data',
            'Analyze trends/metrics',
            'Extract key insights',
            'Archive after processing'
        ]
        
        return content, actions, 'csv'
    
    def _handle_image_file(self, item: FileDropItem, dest_path: Path) -> tuple:
        """Handle image files."""
        content = f'''Image: {item.name}
Size: {item.size_human}
Location: {dest_path}

Note: Image content analysis requires vision capabilities.
Please review the image and describe its contents.'''
        
        actions = [
            'Review image',
            'Describe contents',
            'Extract relevant information',
            'Archive after processing'
        ]
        
        return content, actions, 'image'
    
    def _handle_json_file(self, item: FileDropItem, dest_path: Path) -> tuple:
        """Handle JSON files."""
        try:
            content = dest_path.read_text(encoding='utf-8', errors='replace')
            # Truncate if too long
            if len(content) > 2000:
                content = content[:2000] + '\n\n... [content truncated]'
        except Exception:
            content = '[Unable to read JSON content]'
        
        actions = [
            'Parse JSON data',
            'Extract key information',
            'Take necessary action',
            'Archive after processing'
        ]
        
        return content, actions, 'json'
    
    def _handle_unknown_file(self, item: FileDropItem, dest_path: Path) -> tuple:
        """Handle unknown file types."""
        content = f'''Unknown File Type: {item.name}
Size: {item.size_human}
Location: {dest_path}
Extension: {Path(item.name).suffix}

Note: Unknown file type. Please review manually.'''
        
        actions = [
            'Identify file type',
            'Review contents',
            'Determine appropriate action',
            'Archive after processing'
        ]
        
        return content, actions, 'unknown'


if __name__ == '__main__':
    import sys
    
    # Default vault path
    vault_path = r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault'
    
    # Allow override via command line
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    
    # Create and run watcher
    watcher = FilesystemWatcher(
        vault_path=vault_path,
        check_interval=30  # Check every 30 seconds
    )
    
    print(f'Filesystem Watcher starting...')
    print(f'Watching: {watcher.drop_folder}')
    print(f'Press Ctrl+C to stop')
    print()
    
    watcher.run()
