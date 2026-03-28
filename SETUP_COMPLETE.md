# Qwen Agent Setup Complete!

## Installation Summary

✅ **qwen-agent** v0.0.34 installed  
✅ **dashscope** v1.25.15 installed  
✅ **python-dotenv** installed  
✅ **numpy** installed  
✅ **python-dateutil** installed  
✅ **soundfile** installed  

## Configuration Files Created

| File | Purpose |
|------|---------|
| `.qwen/settings.json` | Qwen Code settings and permissions |
| `qwen_agent_config.py` | Qwen Agent configuration for AI Employee |
| `.env.example` | Environment variable template |
| `prompts/README.md` | Prompt templates for AI Employee |
| `test_qwen_setup.py` | Setup verification script |

## Next Step: Set Your API Key

To use Qwen Agent, you need a DashScope API key.

### Option 1: Get DashScope API Key (Recommended)

1. Visit: https://dashscope.console.aliyun.com/
2. Sign up or log in
3. Create an API key
4. Copy your API key

### Option 2: Set API Key

**Windows (Command Prompt):**
```cmd
set DASHSCOPE_API_KEY=your_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:DASHSCOPE_API_KEY="your_api_key_here"
```

**Permanent (create .env file):**
```bash
# Copy .env.example to .env
copy .env.example .env

# Edit .env and add your API key
DASHSCOPE_API_KEY=your_api_key_here
```

## Verify Setup

Run the test script to verify everything is working:

```bash
python test_qwen_setup.py
```

Expected output (after setting API key):
```
✓ PASS: Imports
✓ PASS: Configuration
✓ PASS: Vault Structure
✓ PASS: API Key
✓ PASS: Agent Creation

Passed: 5/5
✓ All tests passed! Qwen Agent is ready to use.
```

## Using Qwen Agent with AI Employee

### Method 1: Using the Orchestrator

```bash
# Process pending tasks
cd scripts
python orchestrator.py --vault ..\AI_Employee_Vault --once

# Continuous mode
python orchestrator.py --vault ..\AI_Employee_Vault --continuous --interval 60
```

### Method 2: Using Qwen Agent Directly

```python
from qwen_agent_config import create_ai_employee_agent

# Create agent
agent = create_ai_employee_agent()

# Process action files
from qwen_agent_config import process_action_file
result = process_action_file(agent, 'AI_Employee_Vault/Needs_Action/FILE_task.md')
```

### Method 3: Using Prompt Templates

```python
from qwen_agent.agent import Agent
from qwen_agent.llm import get_chat_model

# Create agent with system prompt
system_prompt = """You are an AI Employee assistant..."""

agent = Agent(
    function_call=True,
    system_message=system_prompt,
    llm=get_chat_model({
        'model': 'qwen-plus',
        'model_server': 'dashscope',
    })
)

# Run agent
messages = [{'role': 'user', 'content': 'Process pending tasks'}]
response = agent.run(messages=messages)
```

## Quick Start Workflow

1. **Start the File Watcher:**
   ```bash
   cd scripts
   python filesystem_watcher.py ..\AI_Employee_Vault
   ```

2. **Drop a file in Inbox:**
   - Place any file in `AI_Employee_Vault/Inbox/`
   - The watcher will detect it and create an action file

3. **Process with Qwen:**
   ```bash
   python orchestrator.py --vault ..\AI_Employee_Vault --once
   ```

4. **Check Results:**
   - View `Plans/` for created plans
   - View `Done/` for completed tasks
   - View `Dashboard.md` for updated status

## Troubleshooting

### "ModuleNotFoundError: No module named 'qwen_agent'"
```bash
pip install qwen-agent dashscope
```

### "DASHSCOPE_API_KEY not set"
Set your API key as shown above.

### "Connection aborted" errors
- Check your internet connection
- The installation may need to retry
- Try: `pip install --retries 5 qwen-agent`

### Agent creation fails
- Verify API key is correct
- Check API key has sufficient credits
- Ensure firewall allows connections to DashScope

## Model Options

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| qwen-turbo | Fast | Good | Low | Quick tasks |
| qwen-plus | Balanced | Better | Medium | General use |
| qwen-max | Slow | Best | High | Complex tasks |

Change model in `qwen_agent_config.py`:
```python
AI_EMPLOYEE_CONFIG = {
    'model': 'qwen-plus',  # Change this
    ...
}
```

## Resources

- [Qwen Agent Documentation](https://github.com/QwenLM/Qwen-Agent)
- [DashScope Documentation](https://help.aliyun.com/zh/dashscope/)
- [AI Employee README](./README.md)
- [Qwen Configuration](./QWEN_CONFIG.md)

---

*AI Employee v0.1 - Bronze Tier (Qwen Code)*
*Setup completed: 2026-03-28*
