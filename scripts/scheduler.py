"""
Scheduler Module

Windows Task Scheduler integration for the AI Employee system.
Creates and manages scheduled tasks for periodic operations.

Silver Tier Feature: Basic scheduling via cron or Task Scheduler

Usage:
    python scheduler.py install    - Install scheduled tasks
    python scheduler.py remove     - Remove scheduled tasks
    python scheduler.py status     - Show task status
    python scheduler.py run <task> - Run a specific task manually
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class TaskScheduler:
    """
    Windows Task Scheduler integration for AI Employee.
    
    Creates scheduled tasks for:
    - Daily briefing generation (8:00 AM)
    - Weekly business audit (Monday 7:00 AM)
    - Hourly watcher health checks
    - Email processing (every 15 minutes)
    """

    def __init__(self, vault_path: str, scripts_path: str):
        """
        Initialize the scheduler.

        Args:
            vault_path: Path to the Obsidian vault
            scripts_path: Path to the scripts directory
        """
        self.vault_path = Path(vault_path)
        self.scripts_path = Path(scripts_path)
        self.python_exe = sys.executable
        self.group_name = "AI_Employee"

        # Define scheduled tasks
        self.tasks = self._define_tasks()

    def _define_tasks(self) -> List[Dict]:
        """Define all scheduled tasks."""
        return [
            {
                'name': 'AI_Employee_Daily_Briefing',
                'description': 'Generate daily CEO briefing at 8:00 AM',
                'trigger': 'DAILY',
                'time': '08:00',
                'action': str(self.scripts_path / 'daily_briefing.py'),
                'enabled': True,
            },
            {
                'name': 'AI_Employee_Weekly_Audit',
                'description': 'Weekly business audit on Monday at 7:00 AM',
                'trigger': 'WEEKLY',
                'day': 'MON',
                'time': '07:00',
                'action': str(self.scripts_path / 'weekly_audit.py'),
                'enabled': True,
            },
            {
                'name': 'AI_Employee_Email_Processor',
                'description': 'Process emails every 15 minutes',
                'trigger': 'MINUTES',
                'interval': 15,
                'action': str(self.scripts_path / 'email_processor.py'),
                'enabled': True,
            },
            {
                'name': 'AI_Employee_Watcher_Health',
                'description': 'Check watcher health every hour',
                'trigger': 'MINUTES',
                'interval': 60,
                'action': str(self.scripts_path / 'health_check.py'),
                'enabled': True,
            },
            {
                'name': 'AI_Employee_LinkedIn_Poster',
                'description': 'Check for LinkedIn posts to publish every 30 minutes',
                'trigger': 'MINUTES',
                'interval': 30,
                'action': str(self.scripts_path / 'linkedin_poster.py'),
                'arguments': f'"{self.vault_path}"',
                'enabled': False,  # Disabled by default, enable after setup
            },
        ]

    def _run_schtasks(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run schtasks command with arguments."""
        cmd = ['schtasks'] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error running schtasks: {e.stderr}")
            raise

    def install(self) -> bool:
        """
        Install all scheduled tasks.

        Returns:
            True if all tasks installed successfully
        """
        print("Installing AI Employee scheduled tasks...")
        print(f"Vault path: {self.vault_path}")
        print(f"Scripts path: {self.scripts_path}")
        print()

        success_count = 0

        for task in self.tasks:
            try:
                self._create_task(task)
                print(f"✓ Installed: {task['name']}")
                success_count += 1
            except Exception as e:
                print(f"✗ Failed to install {task['name']}: {e}")

        print()
        print(f"Installed {success_count}/{len(self.tasks)} tasks")
        return success_count == len(self.tasks)

    def _create_task(self, task: Dict):
        """Create a single scheduled task."""
        # Build trigger argument
        if task['trigger'] == 'DAILY':
            trigger = f"/SC DAILY /ST {task['time']}"
        elif task['trigger'] == 'WEEKLY':
            trigger = f"/SC WEEKLY /D {task['day']} /ST {task['time']}"
        elif task['trigger'] == 'MINUTES':
            trigger = f"/SC MINUTE /MO {task['interval']}"
        else:
            raise ValueError(f"Unknown trigger type: {task['trigger']}")

        # Build command
        cmd = f'"{self.python_exe}" "{task["action"]}"'
        if task.get('arguments'):
            cmd += f' {task["arguments"]}'

        # Build schtasks command
        args = [
            '/Create',
            f'/TN {self.group_name}\\{task["name"]}',
            f'/TR {cmd}',
            trigger,
            '/RL HIGHEST',
            '/F',  # Force overwrite if exists
        ]

        if task.get('description'):
            args.append(f'/SD 01/01/2026')  # Start date
            args.append(f'/RU SYSTEM')  # Run as SYSTEM
            args.append(f'/SC {task["trigger"]}')

        # Execute
        result = self._run_schtasks(args, check=False)

        if result.returncode != 0:
            raise Exception(f"schtasks error: {result.stderr}")

    def remove(self) -> bool:
        """
        Remove all scheduled tasks.

        Returns:
            True if all tasks removed successfully
        """
        print("Removing AI Employee scheduled tasks...")

        success_count = 0

        for task in self.tasks:
            try:
                args = ['/Delete', f'/TN {self.group_name}\\{task["name"]}', '/F']
                self._run_schtasks(args, check=False)
                print(f"✓ Removed: {task['name']}")
                success_count += 1
            except Exception as e:
                print(f"✗ Failed to remove {task['name']}: {e}")

        print()
        print(f"Removed {success_count}/{len(self.tasks)} tasks")
        return success_count == len(self.tasks)

    def status(self) -> Dict:
        """
        Get status of all scheduled tasks.

        Returns:
            Dictionary with task statuses
        """
        print("AI Employee Scheduled Tasks Status")
        print("=" * 50)

        statuses = {}

        for task in self.tasks:
            try:
                # Query task
                args = ['/Query', f'/TN {self.group_name}\\{task["name"]}', '/XML']
                result = self._run_schtasks(args, check=False)

                if result.returncode == 0:
                    # Task exists, get more details
                    args = ['/Query', f'/TN {self.group_name}\\{task["name"]}', '/V', '/FO', 'CSV']
                    result = self._run_schtasks(args, check=False)

                    # Parse CSV output
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        # Last line contains status
                        status_line = lines[-1]
                        statuses[task['name']] = {
                            'exists': True,
                            'status': 'Running' if 'Ready' in status_line else 'Unknown',
                            'last_run': 'N/A',
                            'next_run': 'N/A',
                        }
                    else:
                        statuses[task['name']] = {'exists': True, 'status': 'Unknown'}

                    print(f"✓ {task['name']}: {statuses[task['name']]['status']}")
                else:
                    statuses[task['name']] = {'exists': False, 'status': 'Not Installed'}
                    print(f"✗ {task['name']}: Not Installed")

            except Exception as e:
                statuses[task['name']] = {'exists': False, 'status': f'Error: {e}'}
                print(f"✗ {task['name']}: Error - {e}")

        return statuses

    def run_task(self, task_name: str) -> bool:
        """
        Run a specific task manually.

        Args:
            task_name: Name of the task to run

        Returns:
            True if task started successfully
        """
        print(f"Running task: {task_name}")

        try:
            args = ['/Run', f'/TN {self.group_name}\\{task_name}']
            result = self._run_schtasks(args, check=False)

            if result.returncode == 0:
                print(f"✓ Task {task_name} started")
                return True
            else:
                print(f"✗ Failed to start task: {result.stderr}")
                return False

        except Exception as e:
            print(f"✗ Error: {e}")
            return False


def main():
    """Main entry point."""
    import argparse

    # Default paths
    base_path = Path(r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE')
    vault_path = base_path / 'AI_Employee_Vault'
    scripts_path = base_path / 'scripts'

    parser = argparse.ArgumentParser(description='AI Employee Task Scheduler')
    parser.add_argument('command', choices=['install', 'remove', 'status', 'run'],
                        help='Command to execute')
    parser.add_argument('task', nargs='?', help='Task name (for run command)')
    parser.add_argument('--vault', type=str, default=str(vault_path),
                        help='Path to vault')
    parser.add_argument('--scripts', type=str, default=str(scripts_path),
                        help='Path to scripts directory')

    args = parser.parse_args()

    scheduler = TaskScheduler(
        vault_path=args.vault,
        scripts_path=args.scripts
    )

    if args.command == 'install':
        success = scheduler.install()
        sys.exit(0 if success else 1)

    elif args.command == 'remove':
        success = scheduler.remove()
        sys.exit(0 if success else 1)

    elif args.command == 'status':
        scheduler.status()

    elif args.command == 'run':
        if not args.task:
            print("Error: task name required for run command")
            sys.exit(1)
        success = scheduler.run_task(args.task)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
