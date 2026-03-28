# Qwen Code Configuration for AI Employee

This file configures Qwen Code to work with the AI Employee system.

## Setup Instructions

### Option 1: Using Qwen-Agent (Recommended)

```bash
# Install qwen-agent
pip install qwen-agent

# Verify installation
qwen --version
```

### Option 2: Using Qwen API

```bash
# Install required packages
pip install dashscope

# Set your API key
export DASHSCOPE_API_KEY="your-api-key-here"
```

### Option 3: Local Qwen Model

```bash
# Install transformers and related packages
pip install transformers torch accelerate

# Download and run Qwen locally
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('Qwen/Qwen-7B-Chat')"
```

## Configuration File

Create a `.qwen-config.json` in your vault root:

```json
{
  "vault_path": "C:\\Project\\Hackathon_0\\Digital_AI_Employee_FTE\\AI_Employee_Vault",
  "model": "qwen-plus",
  "temperature": 0.7,
  "max_tokens": 4096,
  "skills_directory": "./skills",
  "folders": {
    "inbox": "Inbox",
    "needs_action": "Needs_Action",
    "plans": "Plans",
    "done": "Done",
    "pending_approval": "Pending_Approval",
    "approved": "Approved",
    "rejected": "Rejected",
    "logs": "Logs"
  },
  "rules": {
    "auto_approve_threshold": 50,
    "require_approval_for": ["payment", "email_new_contact", "delete"],
    "max_iterations": 10
  }
}
```

## Using Qwen Code with AI Employee

### Basic Usage

```bash
# Process a single task
qwen "Process the file FILE_test_file_20260328.md in Needs_Action folder"

# Process all pending tasks
qwen "Check Needs_Action folder and process all pending items"

# Update dashboard
qwen "Update Dashboard.md with recent activity from Logs"
```

### Using Skills

```bash
# Use file processor skill
qwen --skill file-processor "Process all files in Inbox"

# Use task manager skill
qwen --skill task-manager "Process pending tasks"

# Use dashboard updater skill
qwen --skill dashboard-updater "Refresh the dashboard"

# Use approval handler skill
qwen --skill approval-handler "Check for approved items"
```

### Interactive Mode

```bash
# Start interactive session in vault directory
cd AI_Employee_Vault
qwen --interactive

# Then prompt:
# > Check Needs_Action folder and create plans for pending items
```

## Prompt Templates

### Process Action File

```
You are an AI Employee assistant. Process the following action file.

## Context
- Vault: {vault_path}
- Action File: {action_file_name}
- Current Time: {timestamp}

## Your Task
1. Read the action file content below
2. Understand what needs to be done
3. Create a Plan.md file in the /Plans folder with checkboxes for each step
4. Execute the plan step by step
5. Move the action file to /Done when complete
6. Update the Dashboard.md with the activity

## Action File Content
{action_file_content}

## Instructions
- Be thorough and methodical
- Create a Plan.md file before taking action
- Check off items as you complete them
- If you need human approval, create a file in /Pending_Approval
- Log all actions taken
- Move completed files to /Done

## Output Format
After processing, output exactly: <promise>TASK_COMPLETE</promise>
```

### Daily Briefing

```
Generate a daily briefing based on the AI Employee activity.

## Tasks
1. Review all files in Done folder from today
2. Count completed tasks
3. Review Logs for any errors
4. Check Pending_Approval for stale items
5. Update Dashboard.md with summary

## Output
Create a briefing file in Briefings folder with:
- Tasks completed
- Issues encountered
- Items awaiting approval
- Recommendations
```

## Environment Variables

```bash
# Qwen API Key (if using API)
export DASHSCOPE_API_KEY="your-api-key"

# Model selection
export QWEN_MODEL="qwen-plus"

# Vault path
export AI_EMPLOYEE_VAULT="C:\\Project\\Hackathon_0\\Digital_AI_Employee_FTE\\AI_Employee_Vault"
```

## Integration with Orchestrator

The orchestrator.py script automatically uses Qwen Code:

```bash
# Run with default settings
python orchestrator.py --vault ../AI_Employee_Vault --once

# Specify custom Qwen command
python orchestrator.py --qwen-command "qwen" --vault ../AI_Employee_Vault --once

# Dry run mode
python orchestrator.py --vault ../AI_Employee_Vault --dry-run --once
```

## Troubleshooting

### Qwen not found
```bash
# Install qwen-agent
pip install qwen-agent

# Or add to PATH if installed elsewhere
export PATH="$PATH:/path/to/qwen"
```

### API errors
```bash
# Check API key
echo $DASHSCOPE_API_KEY

# Test connection
python -c "import dashscope; print(dashscope.__version__)"
```

### Model errors
```bash
# Check available models
python -c "import dashscope; print(dashscope.Models.list())"

# Try different model
export QWEN_MODEL="qwen-turbo"
```

## Best Practices

1. **Always review plans** before Qwen executes complex tasks
2. **Use HITL** for sensitive actions (payments, emails to new contacts)
3. **Check logs regularly** for any errors or unexpected behavior
4. **Start with dry-run** mode when testing new workflows
5. **Keep skills updated** as your needs evolve

---

*AI Employee v0.1 - Bronze Tier*
*Qwen Code Configuration*
