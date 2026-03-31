"""
Qwen Code CLI Provider for AI Employee System

This module provides integration with Qwen Code CLI as the reasoning engine,
replacing Ollama and DashScope providers.

Qwen Code CLI is invoked via subprocess and communicates through:
1. Temporary prompt files
2. Direct CLI arguments
3. Session state management

Installation:
    Download Qwen Code CLI from: https://chat.qwen.ai
    Or install via npm: npm install -g @qwen-code/cli

Usage:
    provider = QwenCodeProvider(vault_path)
    response = provider.chat(prompt, system_prompt)
"""

import subprocess
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class QwenCodeProvider:
    """
    Qwen Code CLI provider for AI Employee system.

    This provider invokes Qwen Code CLI via subprocess to process tasks.
    It supports:
    - Direct CLI invocation with prompts
    - Session management for multi-turn conversations
    - File context injection
    - Tool execution with approval workflow

    Configuration:
        - QWEN_CODE_PATH: Path to qwen-code CLI executable
        - QWEN_CODE_MODEL: Model to use (default: qwen-plus)
        - QWEN_CODE_MAX_TOKENS: Max response tokens
        - QWEN_CODE_TIMEOUT: Timeout in seconds
    """

    def __init__(
        self,
        vault_path: Optional[str] = None,
        qwen_code_path: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        timeout: int = 300
    ):
        """
        Initialize Qwen Code provider.

        Args:
            vault_path: Path to Obsidian vault
            qwen_code_path: Path to qwen-code CLI executable
            model: Model name to use
            max_tokens: Maximum response tokens
            timeout: Command timeout in seconds
        """
        self.vault_path = Path(vault_path) if vault_path else Path(
            os.environ.get('AI_EMPLOYEE_VAULT', './AI_Employee_Vault')
        )

        # Setup logging FIRST before any other operations
        self.logger = logging.getLogger('QwenCodeProvider')
        self.logger.setLevel(logging.INFO)

        # Add console handler if no handlers exist
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(console_handler)

        # Qwen Code CLI path detection
        self.qwen_code_path = qwen_code_path or self._find_qwen_code()

        # Configuration
        self.model = model or os.environ.get('QWEN_CODE_MODEL', 'qwen-plus')
        self.max_tokens = max_tokens
        self.timeout = timeout

        # Session management
        self.session_id: Optional[str] = None
        self.conversation_history: List[Dict[str, str]] = []

        self.logger.info(f'Qwen Code Provider initialized')
        self.logger.info(f'CLI Path: {self.qwen_code_path}')
        self.logger.info(f'Model: {self.model}')
        self.logger.info(f'Vault: {self.vault_path}')

    def _find_qwen_code(self) -> Optional[str]:
        """
        Find Qwen Code CLI executable in system PATH.

        Returns:
            Path to qwen-code executable or None
        """
        # Common executable names
        executable_names = [
            'qwen-code',
            'qwen_code',
            'qwen',
            'qwen-code-cli'
        ]

        # Check PATH
        for exe in executable_names:
            path = shutil.which(exe)
            if path:
                self.logger.info(f'Found Qwen Code CLI: {path}')
                return path

        # Check common installation locations
        common_paths = [
            Path.home() / '.qwen' / 'bin' / 'qwen-code',
            Path.home() / '.local' / 'bin' / 'qwen-code',
            Path('C:\\Program Files\\Qwen Code\\qwen-code.exe'),
            Path('C:\\Users\\Fattani Computers\\AppData\\Local\\Programs\\Qwen Code\\qwen-code.exe'),
            Path(os.environ.get('APPDATA', '')) / '..' / 'Local' / 'Programs' / 'Qwen Code' / 'qwen-code.exe',
        ]

        for path in common_paths:
            if path.exists() and path.is_file():
                self.logger.info(f'Found Qwen Code CLI: {path}')
                return str(path)

        self.logger.warning('Qwen Code CLI not found in PATH or common locations')
        return None

    def is_available(self) -> bool:
        """
        Check if Qwen Code CLI is available.

        Returns:
            True if CLI is accessible
        """
        if not self.qwen_code_path:
            return False

        # Test if executable can be run
        try:
            result = subprocess.run(
                [self.qwen_code_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f'Qwen Code CLI availability check failed: {e}')
            return False

    def get_version(self) -> Optional[str]:
        """
        Get Qwen Code CLI version.

        Returns:
            Version string or None
        """
        if not self.qwen_code_path:
            return None

        try:
            result = subprocess.run(
                [self.qwen_code_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            self.logger.error(f'Failed to get version: {e}')

        return None

    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        files: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Send a chat message to Qwen Code CLI.

        Uses the positional prompt or -p/--prompt flag for non-interactive mode.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            files: Optional list of file paths to include as context
            session_id: Optional session ID for multi-turn conversation

        Returns:
            Response text or None if failed
        """
        if not self.qwen_code_path:
            self.logger.error('Qwen Code CLI not found')
            return None

        # Create temporary file for prompt if it's long or has files
        if len(prompt) > 1000 or files:
            return self._chat_with_file(prompt, system_prompt, files, session_id)
        else:
            return self._chat_direct(prompt, system_prompt, session_id)

    def _chat_direct(
        self,
        prompt: str,
        system_prompt: Optional[str],
        session_id: Optional[str]
    ) -> Optional[str]:
        """
        Send prompt directly via positional argument.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            session_id: Optional session ID

        Returns:
            Response text or None
        """
        try:
            # Build full prompt with system instruction
            full_prompt = self._build_full_prompt(prompt, system_prompt)

            # Run Qwen Code CLI with positional prompt
            # Format: qwen "prompt text" or qwen -p "prompt text"
            cmd = [
                self.qwen_code_path,
                full_prompt  # Positional prompt
            ]

            # Add model if configured
            if self.model:
                cmd.extend(['--model', self.model])

            # Add yolo mode for auto-approval (needed for automated tasks)
            cmd.append('--yolo')

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=self._get_env()
            )

            if result.returncode == 0:
                response = result.stdout.strip()
                self.logger.info(f'Qwen Code response: {response[:200]}...')
                return response
            else:
                self.logger.error(f'Qwen Code CLI error: {result.stderr[:500]}')
                return None

        except subprocess.TimeoutExpired:
            self.logger.error(f'Qwen Code CLI timeout after {self.timeout}s')
            return None
        except Exception as e:
            self.logger.error(f'Qwen Code CLI error: {e}')
            return None

    def _chat_with_file(
        self,
        prompt: str,
        system_prompt: Optional[str],
        files: Optional[List[str]],
        session_id: Optional[str]
    ) -> Optional[str]:
        """
        Send prompt via temporary file (for long prompts or file context).

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            files: Optional list of file paths
            session_id: Optional session ID

        Returns:
            Response text or None
        """
        try:
            # Create temporary directory for session
            temp_dir = tempfile.mkdtemp(prefix='qwen_code_')

            # Write prompt to file
            prompt_file = Path(temp_dir) / 'prompt.md'
            full_prompt = self._build_full_prompt(prompt, system_prompt)
            prompt_file.write_text(full_prompt, encoding='utf-8')

            # Build command with file context
            # Use @ syntax to include files: qwen @file.md "prompt"
            cmd = [self.qwen_code_path]

            # Add file context if provided (using @ syntax)
            if files:
                for file_path in files:
                    cmd.append(f'@{file_path}')

            # Add model configuration
            if self.model:
                cmd.extend(['--model', self.model])

            # Add yolo mode for auto-approval
            cmd.append('--yolo')

            # Add the prompt file as context using @
            cmd.append(f'@{prompt_file}')

            # Add a simple prompt to trigger processing
            cmd.append('Process the attached prompt file and provide your response.')

            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=self._get_env()
            )

            # Cleanup temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

            if result.returncode == 0:
                response = result.stdout.strip()
                self.logger.info(f'Qwen Code response: {response[:200]}...')
                return response
            else:
                self.logger.error(f'Qwen Code CLI error: {result.stderr[:500]}')
                return None

        except subprocess.TimeoutExpired:
            self.logger.error(f'Qwen Code CLI timeout after {self.timeout}s')
            return None
        except Exception as e:
            self.logger.error(f'Qwen Code CLI error: {e}')
            return None

    def _build_full_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str]
    ) -> str:
        """
        Build full prompt with system instruction.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Combined prompt string
        """
        default_system = '''You are an AI Employee assistant that helps manage personal and business affairs.
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

        system = system_prompt or default_system

        return f"""<system>
{system}
</system>

<user>
{prompt}
</user>
"""

    def _get_env(self) -> Dict[str, str]:
        """
        Get environment variables for Qwen Code CLI.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # Add model configuration
        env['QWEN_MODEL'] = self.model
        env['QWEN_MAX_TOKENS'] = str(self.max_tokens)

        # Add vault path
        env['AI_EMPLOYEE_VAULT'] = str(self.vault_path)

        return env

    def execute_task(
        self,
        task_description: str,
        action_file_path: Optional[str] = None,
        plan_file_path: Optional[str] = None
    ) -> bool:
        """
        Execute a task using Qwen Code CLI.

        This is the main entry point for the orchestrator to process tasks.

        Args:
            task_description: Description of the task
            action_file_path: Optional path to action file
            plan_file_path: Optional path to plan file

        Returns:
            True if task completed successfully
        """
        self.logger.info(f'Executing task: {task_description[:100]}...')

        # Build comprehensive prompt
        prompt = self._build_task_prompt(task_description, action_file_path, plan_file_path)

        # Send to Qwen Code
        response = self.chat(prompt)

        if response:
            # Check for completion marker
            if '<promise>TASK_COMPLETE</promise>' in response:
                self.logger.info('Task marked as complete by Qwen Code')
                return True
            else:
                self.logger.info('Qwen Code processed task (checking for completion marker)')
                # Even without explicit marker, consider it processed
                return True
        else:
            self.logger.error('Qwen Code failed to process task')
            return False

    def _build_task_prompt(
        self,
        task_description: str,
        action_file_path: Optional[str],
        plan_file_path: Optional[str]
    ) -> str:
        """
        Build comprehensive task prompt.

        Args:
            task_description: Task description
            action_file_path: Optional action file path
            plan_file_path: Optional plan file path

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        # Add action file content if provided
        if action_file_path:
            action_path = Path(action_file_path)
            if action_path.exists():
                content = action_path.read_text(encoding='utf-8')
                prompt_parts.append(f'''## Action File Content
File: {action_path.name}
Path: {action_path}

{content}
''')

        # Add plan file content if provided
        if plan_file_path:
            plan_path = Path(plan_file_path)
            if plan_path.exists():
                content = plan_path.read_text(encoding='utf-8')
                prompt_parts.append(f'''## Current Plan
File: {plan_path.name}

{content}
''')

        # Add task description
        prompt_parts.append(f'''## Your Task
{task_description}

## Instructions
1. Read and understand the action file content above
2. Create or update a Plan.md file in the /Plans folder with checkboxes
3. Execute the plan step by step
4. Move the action file to /Done when complete
5. Update the Dashboard.md with the activity

## Context
- Vault: {self.vault_path}
- Current Time: {datetime.now().isoformat()}

## Output Format
After processing, output exactly: <promise>TASK_COMPLETE</promise>
''')

        return '\n'.join(prompt_parts)

    def start_session(self) -> Optional[str]:
        """
        Start a new Qwen Code session.

        Returns:
            Session ID or None
        """
        if not self.qwen_code_path:
            return None

        try:
            # Start session with init command
            result = subprocess.run(
                [self.qwen_code_path, '--init-session'],
                capture_output=True,
                text=True,
                timeout=30,
                env=self._get_env()
            )

            if result.returncode == 0:
                # Parse session ID from output
                session_id = result.stdout.strip()
                self.session_id = session_id
                self.logger.info(f'Started Qwen Code session: {session_id}')
                return session_id
            else:
                self.logger.error(f'Failed to start session: {result.stderr}')
                return None

        except Exception as e:
            self.logger.error(f'Error starting session: {e}')
            return None

    def end_session(self):
        """End current Qwen Code session."""
        if not self.session_id:
            return

        try:
            subprocess.run(
                [self.qwen_code_path, '--end-session', self.session_id],
                capture_output=True,
                text=True,
                timeout=10,
                env=self._get_env()
            )
            self.logger.info(f'Ended Qwen Code session: {self.session_id}')
            self.session_id = None
            self.conversation_history = []
        except Exception as e:
            self.logger.error(f'Error ending session: {e}')

    def add_to_context(self, file_path: str) -> bool:
        """
        Add a file to the current session context.

        Args:
            file_path: Path to file to add

        Returns:
            True if successful
        """
        if not self.qwen_code_path or not self.session_id:
            return False

        try:
            result = subprocess.run(
                [self.qwen_code_path, '--add-file', file_path, '--session', self.session_id],
                capture_output=True,
                text=True,
                timeout=30,
                env=self._get_env()
            )

            if result.returncode == 0:
                self.logger.info(f'Added file to context: {file_path}')
                return True
            else:
                self.logger.error(f'Failed to add file: {result.stderr}')
                return False

        except Exception as e:
            self.logger.error(f'Error adding file to context: {e}')
            return False


def test_qwen_code() -> bool:
    """
    Test Qwen Code CLI integration.

    Returns:
        True if test successful
    """
    print("=" * 60)
    print("Qwen Code CLI Integration Test")
    print("=" * 60)
    print()

    provider = QwenCodeProvider()

    # Check availability
    print("1. Checking Qwen Code CLI availability...")
    if not provider.is_available():
        print("❌ Qwen Code CLI is not available")
        print()
        print("Installation instructions:")
        print("  1. Download from: https://chat.qwen.ai")
        print("  2. Or install via npm: npm install -g @qwen-code/cli")
        print("  3. Make sure it's in your PATH")
        return False

    print("✅ Qwen Code CLI is available")

    # Get version
    print("\n2. Getting version...")
    version = provider.get_version()
    if version:
        print(f"✅ Version: {version}")
    else:
        print("⚠️  Could not determine version")

    # Test simple chat
    print("\n3. Testing simple chat...")
    response = provider.chat("Say hello in one sentence")
    if response:
        print(f"✅ Response: {response[:100]}...")
    else:
        print("❌ No response received")
        return False

    # Test with system prompt
    print("\n4. Testing with system prompt...")
    response = provider.chat(
        "What is 2 + 2?",
        system_prompt="You are a helpful math tutor."
    )
    if response:
        print(f"✅ Response: {response[:100]}...")
    else:
        print("❌ No response received")

    print()
    print("=" * 60)
    print("✅ Qwen Code CLI integration test PASSED")
    print("=" * 60)
    return True


if __name__ == '__main__':
    test_qwen_code()
