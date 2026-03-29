# Qwen Agent Configuration for AI Employee
# This file configures the qwen-agent library for use with the AI Employee system
# Supports both Ollama (free, local) and DashScope (API) providers

import os
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    from qwen_agent.agent import Agent
    from qwen_agent.llm import get_chat_model
    QWEN_AGENT_AVAILABLE = True
except ImportError:
    QWEN_AGENT_AVAILABLE = False
    print("Note: qwen-agent not installed. Install with: pip install qwen-agent")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Note: ollama package not installed. Install with: pip install ollama")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration
AI_EMPLOYEE_CONFIG = {
    'model': os.environ.get('QWEN_MODEL', 'qwen-plus'),
    'api_key': os.environ.get('DASHSCOPE_API_KEY'),
    'vault_path': os.environ.get('AI_EMPLOYEE_VAULT', './AI_Employee_Vault'),
    'skills_directory': './skills',
    'provider': os.environ.get('AI_PROVIDER', 'ollama').lower(),  # 'ollama' or 'dashscope'
    'ollama_model': os.environ.get('OLLAMA_MODEL', 'qwen2.5:7b'),
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

# System prompt for AI Employee
SYSTEM_PROMPT = '''You are an AI Employee assistant that helps manage personal and business affairs.
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


class QwenAgentProvider:
    """
    Unified AI provider supporting both Ollama (local) and DashScope (API).
    
    Usage:
        provider = QwenAgentProvider(vault_path)
        response = provider.chat(prompt)
    """
    
    def __init__(self, vault_path: Optional[str] = None, provider: Optional[str] = None):
        """
        Initialize the AI provider.
        
        Args:
            vault_path: Path to the Obsidian vault
            provider: 'ollama' or 'dashscope' (auto-detected from env if not specified)
        """
        self.vault_path = Path(vault_path) if vault_path else Path(AI_EMPLOYEE_CONFIG['vault_path'])
        
        # Determine provider
        if provider:
            self.provider = provider.lower()
        else:
            self.provider = AI_EMPLOYEE_CONFIG['provider']
        
        # Auto-detect if needed
        if self.provider == 'ollama' and not OLLAMA_AVAILABLE:
            print("Warning: Ollama package not available, falling back to DashScope")
            self.provider = 'dashscope'
        
        if self.provider == 'dashscope' and not QWEN_AGENT_AVAILABLE:
            print("Warning: qwen-agent not available, falling back to Ollama")
            self.provider = 'ollama'
        
        print(f"AI Provider initialized: {self.provider}")
    
    def chat(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Send a chat message and get response.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt (uses default if not provided)
        
        Returns:
            Response text or None if failed
        """
        if system_prompt is None:
            system_prompt = SYSTEM_PROMPT
        
        if self.provider == 'ollama':
            return self._chat_ollama(prompt, system_prompt)
        elif self.provider == 'dashscope':
            return self._chat_dashscope(prompt, system_prompt)
        else:
            print(f"Unknown provider: {self.provider}")
            return None
    
    def _chat_ollama(self, prompt: str, system_prompt: str) -> Optional[str]:
        """
        Chat using Ollama (local, free).
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
        
        Returns:
            Response text or None
        """
        if not OLLAMA_AVAILABLE:
            print("Ollama package not installed")
            return None
        
        try:
            model = AI_EMPLOYEE_CONFIG['ollama_model']
            print(f"Using Ollama model: {model}")
            
            response = ollama.chat(model=model, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ])
            
            return response['message']['content']
        
        except Exception as e:
            print(f"Ollama error: {e}")
            print("Make sure Ollama is running: ollama serve")
            return None
    
    def _chat_dashscope(self, prompt: str, system_prompt: str) -> Optional[str]:
        """
        Chat using DashScope API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
        
        Returns:
            Response text or None
        """
        if not QWEN_AGENT_AVAILABLE:
            print("qwen-agent package not installed")
            return None
        
        api_key = AI_EMPLOYEE_CONFIG.get('api_key') or os.environ.get('DASHSCOPE_API_KEY')
        if not api_key:
            print("DASHSCOPE_API_KEY not set")
            return None
        
        try:
            model = AI_EMPLOYEE_CONFIG['model']
            print(f"Using DashScope model: {model}")
            
            agent = Agent(
                function_call=True,
                system_message=system_prompt,
                llm=get_chat_model({
                    'model': model,
                    'model_server': 'dashscope',
                })
            )
            
            messages = [{'role': 'user', 'content': prompt}]
            response = agent.run(messages=messages)
            
            return response
        
        except Exception as e:
            print(f"DashScope error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if AI provider is available."""
        if self.provider == 'ollama':
            return OLLAMA_AVAILABLE
        elif self.provider == 'dashscope':
            return QWEN_AGENT_AVAILABLE and os.environ.get('DASHSCOPE_API_KEY')
        return False


def create_ai_employee_agent(vault_path: Optional[str] = None) -> Optional[Agent]:
    """
    Create and configure the AI Employee agent using qwen-agent.
    
    Args:
        vault_path: Path to the Obsidian vault
    
    Returns:
        Configured agent or None if not available
    """
    if not QWEN_AGENT_AVAILABLE:
        print("qwen-agent not available")
        return None
    
    api_key = AI_EMPLOYEE_CONFIG.get('api_key') or os.environ.get('DASHSCOPE_API_KEY')
    if not api_key:
        print("DASHSCOPE_API_KEY not set")
        return None
    
    agent = Agent(
        function_call=True,
        system_message=SYSTEM_PROMPT,
        llm=get_chat_model({
            'model': AI_EMPLOYEE_CONFIG['model'],
            'model_server': 'dashscope',
        })
    )
    
    return agent


def process_action_file(
    action_file_path: str,
    vault_path: Optional[str] = None,
    provider: Optional[str] = None
) -> Optional[str]:
    """
    Process an action file using the AI Employee agent.
    
    Args:
        action_file_path: Path to the action file
        vault_path: Path to the Obsidian vault
        provider: 'ollama' or 'dashscope'
    
    Returns:
        Result of processing or None
    """
    ai_provider = QwenAgentProvider(vault_path=vault_path, provider=provider)
    
    if not ai_provider.is_available():
        print("AI provider not available")
        return None
    
    # Read the action file
    action_file = Path(action_file_path)
    if not action_file.exists():
        print(f"Error: Action file not found: {action_file_path}")
        return None
    
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
    
    # Get response from AI
    response = ai_provider.chat(prompt)
    
    return response


def run_ollama_test() -> bool:
    """
    Test Ollama connection and model.
    
    Returns:
        True if test successful
    """
    if not OLLAMA_AVAILABLE:
        print("❌ Ollama package not installed")
        return False
    
    try:
        model = AI_EMPLOYEE_CONFIG['ollama_model']
        print(f"Testing Ollama model: {model}")
        
        response = ollama.chat(model=model, messages=[
            {'role': 'user', 'content': 'Say hello in one sentence'}
        ])
        
        print(f"✅ Ollama response: {response['message']['content']}")
        return True
    
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False


def run_dashscope_test() -> bool:
    """
    Test DashScope API connection.
    
    Returns:
        True if test successful
    """
    if not QWEN_AGENT_AVAILABLE:
        print("❌ qwen-agent package not installed")
        return False
    
    api_key = os.environ.get('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ DASHSCOPE_API_KEY not set")
        return False
    
    try:
        model = AI_EMPLOYEE_CONFIG['model']
        print(f"Testing DashScope model: {model}")
        
        agent = Agent(
            function_call=True,
            system_message="You are a helpful assistant.",
            llm=get_chat_model({
                'model': model,
                'model_server': 'dashscope',
            })
        )
        
        messages = [{'role': 'user', 'content': 'Say hello in one sentence'}]
        response = agent.run(messages=messages)
        
        print(f"✅ DashScope response: {response}")
        return True
    
    except Exception as e:
        print(f"❌ DashScope test failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("AI Employee Agent Configuration")
    print("=" * 60)
    print()
    print(f"Provider: {AI_EMPLOYEE_CONFIG['provider']}")
    print(f"Vault: {AI_EMPLOYEE_CONFIG['vault_path']}")
    print(f"Skills: {AI_EMPLOYEE_CONFIG['skills_directory']}")
    print()
    
    if AI_EMPLOYEE_CONFIG['provider'] == 'ollama':
        print(f"Ollama Model: {AI_EMPLOYEE_CONFIG['ollama_model']}")
        print(f"Ollama Available: {OLLAMA_AVAILABLE}")
        run_ollama_test()
    else:
        print(f"DashScope Model: {AI_EMPLOYEE_CONFIG['model']}")
        print(f"API Key Set: {'Yes' if os.environ.get('DASHSCOPE_API_KEY') else 'No'}")
        print(f"qwen-agent Available: {QWEN_AGENT_AVAILABLE}")
        run_dashscope_test()
    
    print()
    print("=" * 60)
    print("Usage:")
    print("1. Set environment variables in .env file")
    print("2. Import: from qwen_agent_config import QwenAgentProvider")
    print("3. Create provider: provider = QwenAgentProvider()")
    print("4. Chat: response = provider.chat('Your prompt here')")
    print("=" * 60)
