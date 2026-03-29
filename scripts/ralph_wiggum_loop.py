"""
Ralph Wiggum Loop Implementation

Gold Tier Feature: Autonomous multi-step task completion.
The "Stop Hook" pattern that keeps Claude working until tasks are complete.

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

Usage:
    from ralph_wiggum_loop import RalphWiggumLoop
    
    loop = RalphWiggumLoop(vault_path)
    loop.run("Process all emails in Needs_Action folder")
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging


class TaskStatus(Enum):
    """Task status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskState:
    """Represents the state of a task being processed."""
    
    task_id: str
    prompt: str
    status: str
    created: str
    updated: str
    iteration: int = 0
    max_iterations: int = 10
    completion_criteria: Optional[str] = None
    output_files: List[str] = None
    errors: List[str] = None
    notes: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class RalphWiggumLoop:
    """
    Ralph Wiggum Loop implementation for autonomous task completion.

    The loop works as follows:
    1. Create a task state file with the prompt
    2. Run Claude Code with the prompt
    3. When Claude tries to exit, the stop hook checks:
       - Is the task complete? (completion criteria met)
       - If YES → Allow exit
       - If NO → Block exit, re-inject prompt with context
    4. Repeat until complete or max iterations reached

    Features:
    - Automatic iteration until completion
    - Progress tracking
    - Error recovery
    - Completion verification
    """

    def __init__(self, vault_path: str):
        """
        Initialize the Ralph Wiggum Loop.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.plans_dir = self.vault_path / 'Plans'
        self.done_dir = self.vault_path / 'Done'
        self.needs_action_dir = self.vault_path / 'Needs_Action'
        self.logs_dir = self.vault_path / 'Logs'
        self.ralph_dir = self.logs_dir / 'Ralph_Loop'

        # Ensure directories exist
        for dir_path in [self.plans_dir, self.done_dir, self.needs_action_dir, 
                         self.logs_dir, self.ralph_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logging()

        # Active tasks
        self.active_tasks: Dict[str, TaskState] = {}

        # Completion checkers (registered callbacks)
        self.completion_checkers: Dict[str, Callable[[TaskState], bool]] = {}

        self.logger.info('Ralph Wiggum Loop initialized')

    def _setup_logging(self):
        """Setup Ralph Loop logging."""
        log_file = self.ralph_dir / f'ralph_{datetime.now().strftime("%Y-%m-%d")}.log'

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logger = logging.getLogger('RalphWiggumLoop')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def create_task(
        self,
        prompt: str,
        task_id: Optional[str] = None,
        max_iterations: int = 10,
        completion_criteria: Optional[str] = None
    ) -> TaskState:
        """
        Create a new task for the Ralph Wiggum Loop.

        Args:
            prompt: The task prompt for Claude
            task_id: Optional custom task ID
            max_iterations: Maximum iterations before giving up
            completion_criteria: Description of what "done" looks like

        Returns:
            TaskState object
        """
        if task_id is None:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        now = datetime.now().isoformat()

        task = TaskState(
            task_id=task_id,
            prompt=prompt,
            status=TaskStatus.PENDING.value,
            created=now,
            updated=now,
            max_iterations=max_iterations,
            completion_criteria=completion_criteria,
            output_files=[],
            errors=[],
            notes=[]
        )

        # Save task state
        self._save_task_state(task)
        self.active_tasks[task_id] = task

        self.logger.info(f'Created task: {task_id}')
        self.logger.info(f'Prompt: {prompt[:100]}...')

        return task

    def _save_task_state(self, task: TaskState):
        """Save task state to file."""
        task_file = self.ralph_dir / f'{task.task_id}.json'
        with open(task_file, 'w') as f:
            f.write(task.to_json())

    def _load_task_state(self, task_id: str) -> Optional[TaskState]:
        """Load task state from file."""
        task_file = self.ralph_dir / f'{task_id}.json'
        if task_file.exists():
            with open(task_file, 'r') as f:
                data = json.load(f)
                return TaskState(**data)
        return None

    def update_task(self, task: TaskState, **kwargs):
        """
        Update task state.

        Args:
            task: TaskState to update
            **kwargs: Fields to update
        """
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.updated = datetime.now().isoformat()
        self._save_task_state(task)

    def register_completion_checker(
        self,
        task_type: str,
        checker: Callable[[TaskState], bool]
    ):
        """
        Register a completion checker for a task type.

        Args:
            task_type: Type of task (e.g., 'email_processing', 'file_processing')
            checker: Function that returns True if task is complete
        """
        self.completion_checkers[task_type] = checker
        self.logger.info(f'Registered completion checker for: {task_type}')

    def check_completion(self, task: TaskState) -> bool:
        """
        Check if a task is complete.

        Args:
            task: TaskState to check

        Returns:
            True if task is complete
        """
        # First check completion criteria if specified
        if task.completion_criteria:
            # Check if files mentioned in criteria exist in Done folder
            if 'Done/' in task.completion_criteria or '/Done' in task.completion_criteria:
                # Count files moved to Done
                done_count = len(list(self.done_dir.glob('*.md')))
                if done_count > 0:
                    self.logger.info(f'Completion criteria check: {done_count} files in Done/')
                    return True

        # Check using registered completion checkers
        for task_type, checker in self.completion_checkers.items():
            if task_type in task.prompt.lower():
                try:
                    if checker(task):
                        self.logger.info(f'Completion checker for {task_type} returned True')
                        return True
                except Exception as e:
                    self.logger.error(f'Completion checker error: {e}')

        # Default: check if Needs_Action is empty (for processing tasks)
        if 'process' in task.prompt.lower() and 'Needs_Action' in task.prompt:
            pending_count = len(list(self.needs_action_dir.glob('*.md')))
            if pending_count == 0:
                self.logger.info('Needs_Action folder is empty - task complete')
                return True

        return False

    def generate_iteration_prompt(self, task: TaskState, previous_output: str) -> str:
        """
        Generate prompt for next iteration.

        Args:
            task: Current task state
            previous_output: Output from previous iteration

        Returns:
            Prompt string for next iteration
        """
        iteration = task.iteration + 1

        prompt = f"""
## Ralph Wiggum Loop - Iteration {iteration}/{task.max_iterations}

**Task ID:** {task.task_id}

**Original Prompt:**
{task.prompt}

**Completion Criteria:**
{task.completion_criteria or 'Complete all items and move to Done/'}

**Previous Output:**
{previous_output[:2000] if previous_output else 'No previous output'}

**Current State:**
- Needs_Action items: {len(list(self.needs_action_dir.glob('*.md')))}
- Done items: {len(list(self.done_dir.glob('*.md')))}
- Plans: {len(list(self.plans_dir.glob('*.md')))}

**Instructions:**
1. Review what was accomplished in the previous iteration
2. Identify what still needs to be done
3. Continue working on the task
4. When complete, move all processed files to Done/
5. Output "<promise>TASK_COMPLETE</promise>" when finished

**Important:** Do not exit until the task is fully complete.
"""
        return prompt

    def stop_hook(self, task: TaskState, claude_output: str) -> Dict[str, Any]:
        """
        Stop hook that intercepts Claude's exit attempt.

        This is called when Claude tries to exit. It checks if the task
        is complete and either allows exit or re-injects the prompt.

        Args:
            task: Current task state
            claude_output: Claude's output

        Returns:
            Decision dictionary with 'allow_exit' and optional 'new_prompt'
        """
        self.logger.info(f'Stop hook called for task {task.task_id}')
        self.logger.info(f'Iteration: {task.iteration}/{task.max_iterations}')

        # Check completion
        is_complete = self.check_completion(task)

        if is_complete:
            self.logger.info('Task complete - allowing exit')
            self.update_task(task, status=TaskStatus.COMPLETED.value)
            return {
                'allow_exit': True,
                'status': 'completed',
                'message': 'Task completed successfully'
            }

        # Check max iterations
        if task.iteration >= task.max_iterations:
            self.logger.warning('Max iterations reached - forcing exit')
            self.update_task(task, status=TaskStatus.FAILED.value)
            return {
                'allow_exit': True,
                'status': 'failed',
                'message': f'Max iterations ({task.max_iterations}) reached'
            }

        # Task not complete - block exit and generate new prompt
        task.iteration += 1
        self.update_task(task, status=TaskStatus.IN_PROGRESS.value)

        new_prompt = self.generate_iteration_prompt(task, claude_output)

        self.logger.info(f'Blocking exit - continuing to iteration {task.iteration}')

        return {
            'allow_exit': False,
            'status': 'continue',
            'new_prompt': new_prompt,
            'message': f'Task not complete. Continuing to iteration {task.iteration}.'
        }

    def run(
        self,
        prompt: str,
        task_id: Optional[str] = None,
        max_iterations: int = 10,
        completion_criteria: Optional[str] = None
    ) -> TaskState:
        """
        Run the Ralph Wiggum Loop for a task.

        This is the main entry point. It creates a task and runs the loop.

        Args:
            prompt: Task prompt
            task_id: Optional custom task ID
            max_iterations: Maximum iterations
            completion_criteria: What "done" looks like

        Returns:
            Final TaskState
        """
        # Create task
        task = self.create_task(
            prompt=prompt,
            task_id=task_id,
            max_iterations=max_iterations,
            completion_criteria=completion_criteria
        )

        self.logger.info(f'Starting Ralph Wiggum Loop for task: {task.task_id}')

        # In a real implementation, this would:
        # 1. Start Claude Code with the prompt
        # 2. Capture Claude's output
        # 3. Call stop_hook when Claude tries to exit
        # 4. If stop_hook returns allow_exit=False, re-inject new_prompt
        # 5. Repeat until complete

        # For this implementation, we simulate the loop
        # In production, this integrates with Claude Code's plugin system

        print(f"\n{'='*60}")
        print(f"Ralph Wiggum Loop - Task: {task.task_id}")
        print(f"{'='*60}")
        print(f"Prompt: {prompt[:200]}...")
        print(f"Max iterations: {max_iterations}")
        print(f"Completion criteria: {completion_criteria or 'Process all items'}")
        print(f"{'='*60}\n")

        # Simulate iterations
        while task.iteration < max_iterations:
            task.iteration += 1
            self.update_task(task, status=TaskStatus.IN_PROGRESS.value)

            print(f"\n[Iteration {task.iteration}/{max_iterations}]")
            print(f"  Needs_Action: {len(list(self.needs_action_dir.glob('*.md')))} items")
            print(f"  Done: {len(list(self.done_dir.glob('*.md')))} items")

            # Check completion
            is_complete = self.check_completion(task)

            if is_complete:
                print(f"\n✓ Task completed!")
                self.update_task(task, status=TaskStatus.COMPLETED.value)
                break

            print(f"  Task not complete, continuing...")

            # In real implementation, Claude would work here
            time.sleep(0.5)  # Simulated work

        # Final status
        if task.status != TaskStatus.COMPLETED.value:
            if task.iteration >= max_iterations:
                task.status = TaskStatus.FAILED.value
                print(f"\n✗ Task failed - max iterations reached")
            else:
                task.status = TaskStatus.CANCELLED.value
                print(f"\n✗ Task cancelled")

        self.update_task(task)

        print(f"\n{'='*60}")
        print(f"Final Status: {task.status}")
        print(f"Total Iterations: {task.iteration}")
        print(f"{'='*60}\n")

        return task

    def get_task_report(self, task_id: str) -> str:
        """
        Generate a report for a task.

        Args:
            task_id: Task ID to report on

        Returns:
            Markdown formatted report
        """
        task = self._load_task_state(task_id)
        if not task:
            return f"Task not found: {task_id}"

        report = f"""# Ralph Wiggum Loop - Task Report

## Task Information
- **Task ID:** {task.task_id}
- **Status:** {task.status}
- **Created:** {task.created}
- **Last Updated:** {task.updated}
- **Iterations:** {task.iteration}/{task.max_iterations}

## Prompt
{task.prompt}

## Completion Criteria
{task.completion_criteria or 'Not specified'}

## Results
- **Output Files:** {len(task.output_files)}
- **Errors:** {len(task.errors)}
- **Notes:** {len(task.notes)}

"""

        if task.output_files:
            report += "### Output Files\n"
            for f in task.output_files:
                report += f"- {f}\n"

        if task.errors:
            report += "\n### Errors\n"
            for e in task.errors:
                report += f"- {e}\n"

        return report


# Global instance
_loop: Optional[RalphWiggumLoop] = None


def get_ralph_loop(vault_path: str) -> RalphWiggumLoop:
    """Get or create the global Ralph Wiggum Loop instance."""
    global _loop
    if _loop is None or _loop.vault_path != Path(vault_path):
        _loop = RalphWiggumLoop(vault_path)
    return _loop


if __name__ == '__main__':
    import sys

    vault_path = r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault'
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    loop = RalphWiggumLoop(vault_path)

    # Demo: Create and run a task
    print("Ralph Wiggum Loop Demo")
    print("=" * 60)

    # Register a completion checker
    def email_completion_checker(task: TaskState) -> bool:
        # Check if all EMAIL_ files have been processed
        email_files = list(loop.needs_action_dir.glob('EMAIL_*.md'))
        return len(email_files) == 0

    loop.register_completion_checker('email', email_completion_checker)

    # Run a demo task
    task = loop.run(
        prompt="Process all emails in Needs_Action folder",
        completion_criteria="Move all processed emails to Done/ folder",
        max_iterations=5
    )

    # Print report
    report = loop.get_task_report(task.task_id)
    print(report)
