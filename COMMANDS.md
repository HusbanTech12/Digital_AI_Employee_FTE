# AI Employee - Quick Command Reference

## From Project Root Directory

### Start File Watcher
```bash
cd scripts
python filesystem_watcher.py ..\AI_Employee_Vault
```

Or use the batch file:
```bash
start-ai-employee.bat
```

### Run Orchestrator (Process Tasks)
```bash
cd scripts
python orchestrator.py --vault ..\AI_Employee_Vault --once
```

Or use the batch file:
```bash
run-orchestrator.bat
```

### Run Orchestrator with API Key
```bash
cd scripts
python orchestrator.py --vault ..\AI_Employee_Vault --api-key "your_api_key_here"
```

### Set API Key Permanently (Session)
**Command Prompt:**
```cmd
set DASHSCOPE_API_KEY=your_api_key_here
```

**PowerShell:**
```powershell
$env:DASHSCOPE_API_KEY="your_api_key_here"
```

### Verify Setup
```bash
python verify_setup.py
python test_qwen_setup.py
```

---

## From scripts Directory

All commands assume you're in the `scripts` folder:

```bash
cd scripts
```

### Watcher
```bash
python filesystem_watcher.py ..\AI_Employee_Vault
```

### Orchestrator
```bash
# Process once
python orchestrator.py --vault ..\AI_Employee_Vault --once

# Continuous mode
python orchestrator.py --vault ..\AI_Employee_Vault --continuous --interval 60

# Dry run
python orchestrator.py --vault ..\AI_Employee_Vault --dry-run --once

# With API key
python orchestrator.py --vault ..\AI_Employee_Vault --api-key "sk-..." --once
```

---

## Common Workflows

### Workflow 1: Manual Processing (No API Key)
1. Start watcher: `python filesystem_watcher.py ..\AI_Employee_Vault`
2. Drop file in `AI_Employee_Vault/Inbox/`
3. Watcher creates action file in `Needs_Action/`
4. Run orchestrator: `python orchestrator.py --vault ..\AI_Employee_Vault --once`
5. Orchestrator creates Plan.md
6. **Manually execute tasks in Obsidian**
7. Move completed files to `Done/`

### Workflow 2: Automated Processing (With API Key)
1. Set API key: `set DASHSCOPE_API_KEY=your_key`
2. Start watcher: `python filesystem_watcher.py ..\AI_Employee_Vault`
3. Drop file in `AI_Employee_Vault/Inbox/`
4. Watcher creates action file
5. Run orchestrator: `python orchestrator.py --vault ..\AI_Employee_Vault --once`
6. Qwen Agent processes tasks automatically
7. Files moved to `Done/` automatically

---

## Troubleshooting

### "can't open file 'orchestrator.py'"
You're in the wrong directory. Run from `scripts` folder:
```bash
cd scripts
python orchestrator.py ...
```

### "DASHSCOPE_API_KEY not set"
Set your API key:
```bash
set DASHSCOPE_API_KEY=your_key_here
```

Or create `.env` file:
```bash
copy .env.example .env
# Edit .env and add your API key
```

### "ModuleNotFoundError: No module named 'qwen_agent'"
Install dependencies:
```bash
pip install qwen-agent dashscope python-dotenv
```

### Watcher not detecting files
- Check file is in `AI_Employee_Vault/Inbox/`
- Check watcher logs in `AI_Employee_Vault/Logs/`
- Restart watcher

---

## File Locations

| File | Location |
|------|----------|
| Orchestrator | `scripts/orchestrator.py` |
| File Watcher | `scripts/filesystem_watcher.py` |
| Base Watcher | `scripts/base_watcher.py` |
| Vault | `AI_Employee_Vault/` |
| Dashboard | `AI_Employee_Vault/Dashboard.md` |
| Action Files | `AI_Employee_Vault/Needs_Action/` |
| Plans | `AI_Employee_Vault/Plans/` |
| Completed | `AI_Employee_Vault/Done/` |
| Logs | `AI_Employee_Vault/Logs/` |

---

*AI Employee v0.1 - Bronze Tier (Qwen Code)*
