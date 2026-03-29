"""
Orchestrator Module

Main orchestration script that:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Agent (via Ollama or DashScope) to process items
3. Manages task completion and file movement
4. Updates the Dashboard

This is the brain coordinator for the AI Employee system.

Silver Tier Integration:
- Uses qwen-agent library with Ollama (free, local) or DashScope (API)
- Supports both local AI (Ollama) and cloud AI (DashScope)
- Human-in-the-loop approval workflow
"""

import subprocess
import shutil
import logging
import argparse
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import re

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import AI provider
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from qwen_agent.agent import Agent
    from qwen_agent.llm import get_chat_model
    QWEN_AGENT_AVAILABLE = True
except ImportError:
    QWEN_AGENT_AVAILABLE = False


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Coordinates between watchers, Qwen Agent (Ollama/DashScope), and the vault.
    
    Silver Tier Features:
    - Ollama integration (free, local AI)
    - DashScope integration (API-based)
    - Human-in-the-loop approval handling
    - Continuous and one-shot processing modes
    """

    def __init__(
        self,
        vault_path: str,
        max_iterations: int = 10,
        dry_run: bool = False,
        ai_provider: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize the orchestrator.

        Args:
            vault_path: Path to the Obsidian vault
            max_iterations: Maximum iterations for persistence loop
            dry_run: If True, log actions without executing
            ai_provider: 'ollama' or 'dashscope' (auto-detected if not specified)
            model: Model name (auto-detected from env if not specified)
        """
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations
        self.dry_run = dry_run
        
        # AI Provider configuration
        self.ai_provider = ai_provider or os.environ.get('AI_PROVIDER', 'ollama').lower()
        self.model = model or os.environ.get('OLLAMA_MODEL', 'qwen2.5:7b')
        self.dashscope_model = os.environ.get('QWEN_MODEL', 'qwen-plus')

        # Setup paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Ensure directories exist
        for folder in [self.needs_action, self.plans, self.done,
                       self.pending_approval, self.approved, self.rejected, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        self.logger.info(f'Orchestrator initialized')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Dry run: {self.dry_run}')
        self.logger.info(f'AI Provider: {self.ai_provider}')
        self.logger.info(f'Model: {self.model}')

    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger = logging.getLogger('Orchestrator')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_pending_items(self) -> List[Path]:
        """
        Get all pending action files in Needs_Action folder.

        Returns:
            List of Path objects for pending files
        """
        if not self.needs_action.exists():
            return []

        return sorted(
            self.needs_action.glob('*.md'),
            key=lambda p: p.stat().st_mtime
        )

    def get_approved_items(self) -> List[Path]:
        """
        Get all approved action files ready for execution.

        Returns:
            List of Path objects for approved files
        """
        if not self.approved.exists():
            return []

        return list(self.approved.glob('*.md'))

    def _is_ai_available(self) -> bool:
        """
        Check if AI provider is available.
        
        Returns:
            True if AI provider is available
        """
        if self.ai_provider == 'ollama':
            return OLLAMA_AVAILABLE
        elif self.ai_provider == 'dashscope':
            api_key = os.environ.get('DASHSCOPE_API_KEY')
            return QWEN_AGENT_AVAILABLE and api_key is not None
        return False

    def process_with_qwen(self, action_file: Path) -> bool:
        """
        Process an action file with Qwen Agent (Ollama or DashScope).

        Silver Tier Integration:
        - Uses qwen-agent library with Ollama (free, local) or DashScope (API)
        - Creates action plans and executes tasks
        - Handles human-in-the-loop approval requests

        Args:
            action_file: Path to the action file to process

        Returns:
            True if processing completed successfully
        """
        self.logger.info(f'Processing: {action_file.name}')

        # Read the action file content
        content = action_file.read_text(encoding='utf-8')

        # Create a prompt for Qwen
        prompt = self._build_qwen_prompt(action_file, content)

        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would process: {action_file.name}')
            self.logger.info(f'[DRY RUN] Prompt: {prompt[:200]}...')
            return True

        # Check AI provider availability
        if not self._is_ai_available():
            self.logger.warning('No AI provider available. Task queued for manual processing.')
            self.logger.info('Install ollama (pip install ollama) or set DASHSCOPE_API_KEY')
            return False

        try:
            # Process with configured AI provider
            result = self._run_qwen_agent(prompt)

            if result is not None:
                # Log output
                self.logger.info(f'Qwen Agent response: {str(result)[:500]}...')
                
                # Check for task completion marker
                if '<promise>TASK_COMPLETE</promise>' in str(result):
                    self.logger.info('Task marked as complete by AI')
                    return True
                else:
                    self.logger.info('AI processed task (no completion marker found)')
                    return True
            else:
                self.logger.warning('AI returned no response. Task queued for manual processing.')
                return False

        except Exception as e:
            self.logger.error(f'Error processing with Qwen Agent: {e}')
            self.logger.info('Falling back to manual processing mode.')
            return False

    def _run_qwen_agent(self, prompt: str):
        """
        Run Qwen Agent with the given prompt.

        Silver Tier Integration:
        - Ollama (free, local) - Recommended for most users
        - DashScope (API key required) - For production use

        Args:
            prompt: The prompt to send to Qwen Agent

        Returns:
            Agent response or None if no AI provider available
        """
        # Use configured provider
        if self.ai_provider == 'ollama':
            return self._run_ollama(prompt)
        elif self.ai_provider == 'dashscope':
            return self._run_dashscope(prompt)
        else:
            self.logger.warning(f'Unknown provider: {self.ai_provider}')
            return None

    def _run_ollama(self, prompt: str) -> Optional[str]:
        """
        Run Qwen using Ollama (free, local AI).

        Silver Tier: This is the recommended provider for local development.

        Args:
            prompt: The prompt to send

        Returns:
            Response text or None if Ollama not available
        """
        if not OLLAMA_AVAILABLE:
            self.logger.warning('ollama package not installed. Install with: pip install ollama')
            return None
        
        try:
            self.logger.info(f'Using Ollama with model: {self.model}')

            # Run Ollama chat
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': self._get_system_prompt()},
                {'role': 'user', 'content': prompt}
            ])

            return response['message']['content']

        except Exception as e:
            self.logger.error(f'Ollama error: {e}')
            self.logger.info('Make sure Ollama is running: ollama serve')
            return None

    def _run_dashscope(self, prompt: str) -> Optional[str]:
        """
        Run Qwen using DashScope API.

        Silver Tier: Use for production when API key is available.

        Args:
            prompt: The prompt to send

        Returns:
            Response text or None if API error
        """
        if not QWEN_AGENT_AVAILABLE:
            self.logger.warning('qwen-agent not available. Install with: pip install qwen-agent')
            return None
        
        api_key = os.environ.get('DASHSCOPE_API_KEY')
        if not api_key:
            self.logger.warning('DASHSCOPE_API_KEY not set')
            return None
        
        try:
            self.logger.info(f'Using DashScope with model: {self.dashscope_model}')

            # Create agent
            agent = Agent(
                function_call=True,
                system_message=self._get_system_prompt(),
                llm=get_chat_model({
                    'model': self.dashscope_model,
                    'model_server': 'dashscope',
                })
            )

            # Run agent
            messages = [{'role': 'user', 'content': prompt}]
            response = agent.run(messages=messages)

            return response

        except Exception as e:
            self.logger.error(f'Qwen Agent error: {e}')
            return None

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the AI Employee agent.

        Returns:
            System prompt string
        """
        return '''You are an AI Employee assistant that helps manage personal and business affairs.
You work with an Obsidian vault to track tasks, plans, and activities.

## Your Responsibilities:
1. Process files dropped in the Inbox folder
2. Create action plans for tasks in Needs_Action
3. Execute tasks methodically
4. Request approval for sensitive actions
5. Update the Dashboard with activity
6. Move completed tasks to Done

## Rules:
- Always create a Plan.md before executing complex tasks
- Check off items as you complete them
- For payments > $50 or new recipients, create approval requests
- Log all actions taken
- Be thorough and methodical

## Output Format:
After completing a task, output: <promise>TASK_COMPLETE</promise>
'''

    def _build_qwen_prompt(self, action_file: Path, content: str) -> str:
        """
        Build a prompt for Qwen Code.

        Args:
            action_file: Path to the action file
            content: Content of the action file

        Returns:
            Formatted prompt string
        """
        return f'''You are an AI Employee assistant. Process the following action file.

## Context
- Vault: {self.vault_path}
- Action File: {action_file.name}
- Current Time: {datetime.now().isoformat()}

## Your Task
1. Read the action file content below
2. Understand what needs to be done
3. Create a Plan.md file in the /Plans folder with checkboxes for each step
4. Execute the plan step by step
5. Move the action file to /Done when complete
6. Update the Dashboard.md with the activity

## Action File Content
{content}

## Instructions
- Be thorough and methodical
- Create a Plan.md file before taking action
- Check off items as you complete them
- If you need human approval, create a file in /Pending_Approval
- Log all actions taken
- Move completed files to /Done

## Output Format
After processing, output exactly: <promise>TASK_COMPLETE</promise>
'''

    def create_plan(self, action_file: Path, objective: str) -> Path:
        """
        Create a Plan.md file for tracking progress.

        Args:
            action_file: Path to the action file
            objective: Objective description

        Returns:
            Path to created plan file
        """
        plan_content = f'''---
created: {datetime.now().isoformat()}
action_file: {action_file.name}
status: in_progress
iteration: 1
---

# Plan: {action_file.stem}

## Objective
{objective}

## Steps
- [ ] Read and understand the action file
- [ ] Identify required actions
- [ ] Execute actions
- [ ] Verify completion
- [ ] Move to Done folder

## Notes
Add notes here during execution.

## Completion
- Started: {datetime.now().isoformat()}
- Completed: [pending]
'''

        plan_path = self.plans / f'PLAN_{action_file.stem}.md'

        if not self.dry_run:
            plan_path.write_text(plan_content, encoding='utf-8')

        self.logger.info(f'Created plan: {plan_path.name}')
        return plan_path

    def move_to_done(self, action_file: Path):
        """
        Move a completed action file to the Done folder.

        Args:
            action_file: Path to the action file
        """
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would move to Done: {action_file.name}')
            return

        try:
            dest = self.done / action_file.name
            shutil.move(str(action_file), str(dest))
            self.logger.info(f'Moved to Done: {action_file.name}')
        except Exception as e:
            self.logger.error(f'Error moving to Done: {e}')

    def update_dashboard(self, activity: str):
        """
        Update the Dashboard.md with recent activity.

        Args:
            activity: Activity description to add
        """
        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would update dashboard: {activity}')
            return

        try:
            if not self.dashboard.exists():
                self.logger.warning('Dashboard.md not found')
                return

            content = self.dashboard.read_text(encoding='utf-8')

            # Add activity to Recent Activity section
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            activity_line = f'- [{timestamp}] {activity}'

            # Find the Recent Activity section and add the line
            if '## Recent Activity' in content:
                lines = content.split('\n')
                new_lines = []
                inserted = False

                for i, line in enumerate(lines):
                    new_lines.append(line)
                    if line == '## Recent Activity' and not inserted:
                        # Check if next line is empty or a table
                        if i + 1 < len(lines) and lines[i + 1].strip() == '':
                            new_lines.append(activity_line)
                            inserted = True
                        elif i + 1 < len(lines) and not lines[i + 1].startswith('*'):
                            new_lines.append(activity_line)
                            inserted = True

                if inserted:
                    content = '\n'.join(new_lines)
                else:
                    # Fallback: append to end
                    content = content.replace(
                        '## Recent Activity',
                        f'## Recent Activity\n{activity_line}'
                    )

            # Update last_updated timestamp
            content = re.sub(
                r'last_updated: .*',
                f'last_updated: {datetime.now().isoformat()}',
                content
            )

            self.dashboard.write_text(content, encoding='utf-8')
            self.logger.info('Dashboard updated')

        except Exception as e:
            self.logger.error(f'Error updating dashboard: {e}')

    def process_approved_items(self):
        """
        Process items in the Approved folder.

        These are actions that have received human approval and can be executed.
        """
        approved_items = self.get_approved_items()

        if not approved_items:
            self.logger.debug('No approved items to process')
            return

        self.logger.info(f'Found {len(approved_items)} approved item(s)')

        for approved_file in approved_items:
            self.logger.info(f'Processing approved: {approved_file.name}')

            # Read the approval
            content = approved_file.read_text(encoding='utf-8')

            # TODO: Execute the approved action based on type
            # For Bronze/Silver tier, we just move to Done and log

            self.update_dashboard(f'Executed approved action: {approved_file.stem}')
            self.move_to_done(approved_file)

    def run_once(self) -> int:
        """
        Run one iteration of processing.

        Returns:
            Number of items processed
        """
        items = self.get_pending_items()

        if not items:
            self.logger.debug('No pending items')
            return 0

        self.logger.info(f'Found {len(items)} pending item(s)')

        processed = 0
        for item in items:
            # Create a plan
            plan = self.create_plan(item, f'Process {item.name}')

            # Process with Qwen
            success = self.process_with_qwen(item)

            if success:
                self.move_to_done(item)
                self.update_dashboard(f'Processed: {item.stem}')
                processed += 1
            else:
                self.logger.error(f'Failed to process: {item.name}')

        # Also process any approved items
        self.process_approved_items()

        return processed

    def run_continuous(self, check_interval: int = 60):
        """
        Run continuously, checking for new items.

        Args:
            check_interval: Seconds between checks
        """
        self.logger.info(f'Starting continuous mode (interval: {check_interval}s)')

        try:
            while True:
                processed = self.run_once()

                if processed > 0:
                    self.logger.info(f'Processed {processed} item(s)')

                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.logger.info('Stopped by user')

    def run_ralph_loop(self, prompt: str, max_iterations: Optional[int] = None):
        """
        Run the Ralph Wiggum persistence loop.

        This keeps Claude working until a task is complete.

        Args:
            prompt: Initial prompt for Claude
            max_iterations: Override default max iterations
        """
        if max_iterations is None:
            max_iterations = self.max_iterations

        self.logger.info(f'Starting Ralph Wiggum loop (max: {max_iterations} iterations)')

        # Create a state file for tracking
        state_file = self.logs / f'ralph_state_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        state_content = f'''---
started: {datetime.now().isoformat()}
max_iterations: {max_iterations}
current_iteration: 0
status: in_progress
---

# Ralph Wiggum Loop State

## Task
{prompt}

## Iterations
'''
        state_file.write_text(state_content, encoding='utf-8')

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            self.logger.info(f'Iteration {iteration}/{max_iterations}')

            # Update state
            state_content = state_file.read_text(encoding='utf-8')
            state_content += f'\n- Iteration {iteration}: {datetime.now().isoformat()}'
            state_file.write_text(state_content, encoding='utf-8')

            # Run Qwen with the prompt
            # In a real implementation, this would check for completion
            # For Bronze tier, we just run once

            break  # For Bronze tier, just run once

        self.logger.info('Ralph Wiggum loop completed')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument(
        '--vault', '-v',
        default=r'D:\Quarter_4\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Dry run mode (no actual changes)'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuously'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Check interval in seconds (for continuous mode)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit'
    )
    parser.add_argument(
        '--api-key', '-k',
        default=None,
        help='DashScope API key (or set DASHSCOPE_API_KEY env var)'
    )
    parser.add_argument(
        '--ollama',
        action='store_true',
        help='Use Ollama (free, local) instead of DashScope'
    )
    parser.add_argument(
        '--model', '-m',
        default=None,
        help='Ollama model to use (default: load from .env or qwen2.5:7b)'
    )
    parser.add_argument(
        '--provider', '-p',
        default=None,
        help='AI provider: ollama or dashscope'
    )

    args = parser.parse_args()

    # Set API key if provided
    if args.api_key:
        os.environ['DASHSCOPE_API_KEY'] = args.api_key

    # Set provider
    if args.provider:
        os.environ['AI_PROVIDER'] = args.provider.lower()
    elif args.ollama:
        os.environ['AI_PROVIDER'] = 'ollama'

    # Set model if provided
    if args.model:
        os.environ['OLLAMA_MODEL'] = args.model

    # Create orchestrator
    orchestrator = Orchestrator(
        vault_path=args.vault,
        dry_run=args.dry_run,
        ai_provider=args.provider or ('ollama' if args.ollama else None),
        model=args.model
    )

    # Run
    if args.continuous:
        orchestrator.run_continuous(check_interval=args.interval)
    elif args.once:
        processed = orchestrator.run_once()
        print(f'Processed {processed} item(s)')
    else:
        # Default: run once
        processed = orchestrator.run_once()
        print(f'Processed {processed} item(s)')


if __name__ == '__main__':
    main()
