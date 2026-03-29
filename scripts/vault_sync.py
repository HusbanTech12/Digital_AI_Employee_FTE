"""
Vault Sync Script for Platinum Tier

Syncs vault between Cloud and Local using Git.
Implements claim-by-move rule and single-writer Dashboard.md rule.

Usage:
    python vault_sync.py ../AI_Employee_Vault
"""

import subprocess
import time
import os
import sys
from pathlib import Path
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class VaultSync:
    """
    Vault synchronization between Cloud and Local.
    
    Features:
    - Git-based sync
    - Claim-by-move rule
    - Single-writer Dashboard.md
    - Updates folder for Cloud→Local communication
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize vault sync.
        
        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.git_remote = os.environ.get('GIT_REMOTE_URL', '')
        self.sync_interval = int(os.environ.get('SYNC_INTERVAL', 300))
        self.agent_name = os.environ.get('AGENT_NAME', 'cloud-agent')
        
        # Setup logging
        self.logs_path = self.vault_path / 'Logs'
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self.log_file = self.logs_path / f'vault_sync_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        # Directories for Platinum Tier workflow
        self.needs_action_cloud = self.vault_path / 'Needs_Action' / 'Cloud'
        self.needs_action_local = self.vault_path / 'Needs_Action' / 'Local'
        self.in_progress = self.vault_path / 'In_Progress'
        self.updates = self.vault_path / 'Updates'
        self.signals = self.vault_path / 'Signals'
        
        # Ensure directories exist
        for folder in [self.needs_action_cloud, self.needs_action_local, 
                       self.in_progress, self.updates, self.signals]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.log(f"Vault Sync initialized")
        self.log(f"  Vault: {self.vault_path}")
        self.log(f"  Agent: {self.agent_name}")
        self.log(f"  Remote: {self.git_remote}")
        self.log(f"  Interval: {self.sync_interval}s")
    
    def log(self, message: str):
        """Log a message."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
        except Exception as e:
            print(f"  Warning: Could not write to log file: {e}")
    
    def git_pull(self) -> bool:
        """
        Pull latest changes from remote.
        
        Returns:
            True if successful
        """
        try:
            self.log("Pulling latest changes from Git...")
            
            result = subprocess.run(
                ['git', 'pull', '--rebase'],
                cwd=str(self.vault_path),
                check=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            self.log(f"Git pull successful: {result.stdout.strip()[:100]}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Git pull failed: {e}")
            self.log(f"  stderr: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            self.log("Git pull timed out")
            return False
        except Exception as e:
            self.log(f"Git pull error: {e}")
            return False
    
    def git_push(self) -> bool:
        """
        Push local changes to remote.
        
        Returns:
            True if successful
        """
        try:
            # Check if there are changes to commit
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if not status_result.stdout.strip():
                self.log("No changes to push")
                return True
            
            self.log("Pushing changes to Git...")
            
            # Add changes
            subprocess.run(
                ['git', 'add', '.'],
                cwd=str(self.vault_path),
                check=True,
                capture_output=True,
                timeout=30
            )
            
            # Commit changes
            timestamp = datetime.now().isoformat()
            subprocess.run(
                ['git', 'commit', '-m', f'Auto-sync {timestamp}'],
                cwd=str(self.vault_path),
                check=True,
                capture_output=True,
                timeout=30
            )
            
            # Push changes
            subprocess.run(
                ['git', 'push'],
                cwd=str(self.vault_path),
                check=True,
                capture_output=True,
                timeout=60
            )
            
            self.log("Git push successful")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Git push failed: {e}")
            return False
        except subprocess.TimeoutExpired:
            self.log("Git push timed out")
            return False
        except Exception as e:
            self.log(f"Git push error: {e}")
            return False
    
    def claim_task(self, task_file: Path) -> bool:
        """
        Claim a task by moving it to In_Progress/<agent>/.
        
        Claim-by-move rule: First agent to move task owns it.
        Other agents must ignore it.
        
        Args:
            task_file: Path to task file
            
        Returns:
            True if successfully claimed
        """
        if not task_file.exists():
            self.log(f"Task file does not exist: {task_file.name}")
            return False
        
        # Create agent folder if needed
        agent_folder = self.in_progress / self.agent_name
        agent_folder.mkdir(parents=True, exist_ok=True)
        
        try:
            dest = agent_folder / task_file.name
            task_file.rename(dest)
            self.log(f"Task claimed by {self.agent_name}: {task_file.name}")
            return True
        except Exception as e:
            self.log(f"Failed to claim task: {e}")
            return False
    
    def release_task(self, task_name: str, destination: str = 'Done'):
        """
        Release a claimed task after completion.
        
        Args:
            task_name: Name of task file
            destination: Destination folder (Done, Needs_Action, etc.)
        """
        task_file = self.in_progress / self.agent_name / task_name
        
        if not task_file.exists():
            self.log(f"Task not found in In_Progress: {task_name}")
            return
        
        dest_folder = self.vault_path / destination
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        try:
            dest = dest_folder / task_name
            task_file.rename(dest)
            self.log(f"Task released to {destination}: {task_name}")
        except Exception as e:
            self.log(f"Failed to release task: {e}")
    
    def write_update(self, update_type: str, content: str, metadata: dict = None):
        """
        Write an update to Updates/ folder for Local to merge.
        
        Cloud writes updates here, Local merges into Dashboard.md.
        
        Args:
            update_type: Type of update (activity, stats, alert, etc.)
            content: Update content
            metadata: Optional metadata dict
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        update_file = self.updates / f'{update_type}_{timestamp}.md'
        
        metadata_yaml = ""
        if metadata:
            for key, value in metadata.items():
                metadata_yaml += f"{key}: {value}\n"
        
        update_content = f"""---
type: {update_type}
created: {datetime.now().isoformat()}
source: {self.agent_name}
{metadata_yaml}
---

# {update_type.title()} Update

{content}
"""
        try:
            update_file.write_text(update_content, encoding='utf-8')
            self.log(f"Update written: {update_file.name}")
        except Exception as e:
            self.log(f"Failed to write update: {e}")
    
    def write_signal(self, signal_type: str, target_agent: str, content: str):
        """
        Write a signal for inter-agent communication.
        
        Args:
            signal_type: Type of signal (request, response, notification)
            target_agent: Target agent name
            content: Signal content
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        signal_file = self.signals / f'{signal_type}_{target_agent}_{timestamp}.md'
        
        signal_content = f"""---
type: {signal_type}
target_agent: {target_agent}
source_agent: {self.agent_name}
created: {datetime.now().isoformat()}
status: pending
---

# {signal_type.title()}

{content}
"""
        try:
            signal_file.write_text(signal_content, encoding='utf-8')
            self.log(f"Signal written: {signal_file.name}")
        except Exception as e:
            self.log(f"Failed to write signal: {e}")
    
    def read_signals(self) -> list:
        """
        Read signals addressed to this agent.
        
        Returns:
            List of signal file paths
        """
        signals = []
        
        if not self.signals.exists():
            return signals
        
        for signal_file in self.signals.glob(f'*_{self.agent_name}_*.md'):
            signals.append(signal_file)
        
        return signals
    
    def process_signals(self):
        """Process incoming signals."""
        signals = self.read_signals()
        
        for signal_file in signals:
            self.log(f"Processing signal: {signal_file.name}")
            
            # Read signal
            content = signal_file.read_text(encoding='utf-8')
            
            # TODO: Process signal based on type
            # For now, just log it
            self.log(f"  Signal content: {content[:200]}...")
            
            # Mark as processed
            processed_file = self.signals / f'processed_{signal_file.name}'
            try:
                signal_file.rename(processed_file)
            except Exception as e:
                self.log(f"Failed to mark signal as processed: {e}")
    
    def check_vault_health(self) -> dict:
        """
        Check vault health and sync status.
        
        Returns:
            Health status dict
        """
        health = {
            'timestamp': datetime.now().isoformat(),
            'vault_path': str(self.vault_path),
            'git_status': 'unknown',
            'pending_updates': 0,
            'pending_signals': 0,
            'in_progress_tasks': 0,
        }
        
        # Check Git status
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                health['git_status'] = 'clean' if not result.stdout.strip() else 'has_changes'
            else:
                health['git_status'] = 'error'
        except Exception as e:
            health['git_status'] = f'error: {e}'
        
        # Count pending updates
        if self.updates.exists():
            health['pending_updates'] = len(list(self.updates.glob('*.md')))
        
        # Count pending signals
        if self.signals.exists():
            health['pending_signals'] = len(list(self.signals.glob('*.md')))
        
        # Count in-progress tasks
        if self.in_progress.exists():
            health['in_progress_tasks'] = len(list(self.in_progress.glob('**/*.md')))
        
        return health
    
    def run(self):
        """Run sync loop."""
        self.log("=" * 60)
        self.log("Vault Sync started")
        self.log("=" * 60)
        
        try:
            while True:
                # Pull latest changes
                self.git_pull()
                
                # Process incoming signals
                self.process_signals()
                
                # Push any updates
                if any(self.updates.iterdir()) or any(self.signals.iterdir()):
                    self.git_push()
                
                # Check health
                health = self.check_vault_health()
                self.log(f"Health: git={health['git_status']}, updates={health['pending_updates']}, signals={health['pending_signals']}")
                
                time.sleep(self.sync_interval)
                
        except KeyboardInterrupt:
            self.log("Stopped by user")
        except Exception as e:
            self.log(f"Fatal error: {e}")
            raise


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Vault Sync for Platinum Tier')
    parser.add_argument('vault_path', help='Path to vault')
    parser.add_argument('--agent', '-a', default=None, help='Agent name (cloud-agent or local-agent)')
    parser.add_argument('--interval', '-i', type=int, default=None, help='Sync interval in seconds')
    args = parser.parse_args()
    
    # Override from args
    if args.agent:
        os.environ['AGENT_NAME'] = args.agent
    if args.interval:
        os.environ['SYNC_INTERVAL'] = str(args.interval)
    
    # Create and run sync
    sync = VaultSync(args.vault_path)
    sync.run()


if __name__ == '__main__':
    main()
