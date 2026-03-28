# Qwen Agent Configuration for AI Employee
# This file configures the qwen-agent library for use with the AI Employee system

from qwen_agent.agent import Agent
from qwen_agent.llm import get_chat_model

# Configuration
AI_EMPLOYEE_CONFIG = {
    'model': 'qwen-plus',  # or 'qwen-turbo', 'qwen-max'
    'api_key': None,  # Set via DASHSCOPE_API_KEY environment variable
    'vault_path': './AI_Employee_Vault',
    'skills_directory': './skills',
}

# Folders configuration
FOLDERS = {
    'inbox': 'Inbox',
    'needs_action': 'Needs_Action',
    'plans': 'Plans',
    'done': 'Done',
    'pending_approval': 'Pending_Approval',
    'approved': 'Approved',
    'rejected': 'Rejected',
    'logs': 'Logs',
    'files': 'Files',
}

# Rules configuration
RULES = {
    'auto_approve_threshold': 50,  # Auto-approve payments under $50
    'require_approval_for': ['payment', 'email_new_contact', 'delete'],
    'max_iterations': 10,
}


def create_ai_employee_agent():
    """
    Create and configure the AI Employee agent using qwen-agent.
    """
    # Define the system prompt for the AI Employee
    system_prompt = '''You are an AI Employee assistant that helps manage personal and business affairs.
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

    # Create the agent
    agent = Agent(
        function_call=True,
        system_message=system_prompt,
        llm=get_chat_model({
            'model': AI_EMPLOYEE_CONFIG['model'],
            'model_server': 'dashscope',
        })
    )

    return agent


def process_action_file(agent, action_file_path: str) -> str:
    """
    Process an action file using the AI Employee agent.

    Args:
        agent: The AI Employee agent
        action_file_path: Path to the action file

    Returns:
        Result of processing
    """
    from pathlib import Path

    # Read the action file
    action_file = Path(action_file_path)
    if not action_file.exists():
        return f"Error: Action file not found: {action_file_path}"

    content = action_file.read_text(encoding='utf-8')

    # Create the prompt
    prompt = f'''Process this action file:

{content}

## Your Tasks:
1. Understand what needs to be done
2. Create a Plan.md in /Plans with checkboxes
3. Execute the plan step by step
4. Move this file to /Done when complete
5. Update Dashboard.md with the activity

Remember to output <promise>TASK_COMPLETE</promise> when done.
'''

    # Run the agent
    messages = [{'role': 'user', 'content': prompt}]
    response = agent.run(messages=messages)

    return response


if __name__ == '__main__':
    # Example usage
    print("AI Employee Agent Configuration")
    print("=" * 40)
    print(f"Model: {AI_EMPLOYEE_CONFIG['model']}")
    print(f"Vault: {AI_EMPLOYEE_CONFIG['vault_path']}")
    print(f"Skills: {AI_EMPLOYEE_CONFIG['skills_directory']}")
    print()
    print("To use:")
    print("1. Set DASHSCOPE_API_KEY environment variable")
    print("2. Import: from qwen_agent_config import create_ai_employee_agent")
    print("3. Create agent: agent = create_ai_employee_agent()")
    print("4. Process: process_action_file(agent, 'path/to/action.md')")
