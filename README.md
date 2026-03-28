# AI Employee - Bronze Tier

**Personal AI Employee Hackathon 0: Building Autonomous FTEs in 2026**

A local-first AI employee that proactively manages your personal and business affairs using Qwen Code and Obsidian.

## Overview

This Bronze Tier implementation provides the foundation for your AI Employee:

- ✅ Obsidian vault with Dashboard.md and Company_Handbook.md
- ✅ File System Watcher for monitoring dropped files
- ✅ Qwen Code integration for processing tasks
- ✅ Basic folder structure for task management
- ✅ Orchestrator for coordinating workflows

## Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |

## AI Provider Options

| Option | Cost | Setup | Best For |
|--------|------|-------|----------|
| **Ollama (Local)** | 100% Free | Easy | Everyone - Recommended |
| **Manual Mode** | 100% Free | None | Testing, no AI needed |
| **DashScope API** | Free credits | Easy | Production use |

See [FREE_SETUP.md](./FREE_SETUP.md) for detailed setup instructions.

## Quick Start

### 1. Install Python Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### 2. Open Vault in Obsidian

Open the `AI_Employee_Vault` folder in Obsidian:
- File → Open Folder → Select `AI_Employee_Vault`

### 3. Choose AI Provider

**Option A: Ollama (Free, Local) - Recommended**
```bash
# Run setup script (Windows)
setup-ollama.bat

# Or manually
pip install ollama
ollama pull qwen2.5:7b
```

**Option B: Manual Mode (No AI)**
- No setup required!
- Tasks are created for manual execution

**Option C: DashScope API**
- Get API key: https://dashscope.console.aliyun.com/
- Set: `set DASHSCOPE_API_KEY=your_key`

### 4. Start the File System Watcher

```bash
cd scripts
python filesystem_watcher.py
```

The watcher will monitor the `Inbox` folder for new files.

### 5. Test the System

1. Drop a file into `AI_Employee_Vault/Inbox/`
2. The watcher will detect it and create an action file
3. Run the orchestrator to process:

```bash
python orchestrator.py --vault ../AI_Employee_Vault --once
```

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md           # Main dashboard
├── Company_Handbook.md    # Rules of engagement
├── Business_Goals.md      # Business objectives
├── Inbox/                 # Drop folder for new files
├── Needs_Action/          # Items requiring action
├── Plans/                 # Qwen's action plans
├── Done/                  # Completed tasks
├── Pending_Approval/      # Awaiting human decision
├── Approved/              # Ready for execution
├── Rejected/              # Declined actions
├── Logs/                  # Audit logs
├── Files/                 # Processed files
├── Invoices/              # Generated invoices
└── Briefings/             # CEO briefings
```

## Components

### File System Watcher (`filesystem_watcher.py`)

Monitors the Inbox folder for new files and creates action files.

```bash
# Run watcher
python filesystem_watcher.py

# Custom vault path
python filesystem_watcher.py /path/to/vault

# Custom check interval (seconds)
# Edit the script: check_interval=30
```

**How it works:**
1. Watches `Inbox/` folder every 30 seconds
2. Detects new files
3. Copies files to `Files/` folder
4. Creates action file in `Needs_Action/`
5. Tracks processed files to avoid duplicates

### Orchestrator (`orchestrator.py`)

Coordinates task processing with Qwen Agent.

```bash
# Run once (process all pending items)
cd scripts
python orchestrator.py --vault ..\AI_Employee_Vault --once

# Continuous mode
python orchestrator.py --vault ..\AI_Employee_Vault --continuous --interval 60

# Dry run (no actual changes)
python orchestrator.py --vault ..\AI_Employee_Vault --dry-run --once

# With API key
python orchestrator.py --vault ..\AI_Employee_Vault --api-key "your_api_key" --once
```

**Options:**
- `--vault`: Path to Obsidian vault
- `--once`: Run once and exit
- `--continuous`: Run continuously
- `--interval`: Check interval in seconds
- `--dry-run`: Log without making changes
- `--api-key`: DashScope API key (or set DASHSCOPE_API_KEY env var)

**Note:** The orchestrator uses the qwen-agent Python library. Set `DASHSCOPE_API_KEY` environment variable or provide `--api-key` to enable AI processing. Without API key, tasks are created but require manual execution.

## Usage Examples

### Example 1: Process a Text File

1. Create a text file `task.txt`:
```
Please review this and summarize the key points.
Also, create a follow-up task for next week.
```

2. Drop it into `AI_Employee_Vault/Inbox/`

3. Watcher detects and creates action file

4. Run orchestrator:
```bash
python orchestrator.py --vault ../AI_Employee_Vault --once
```

5. Check `Plans/` for Qwen's plan
6. Check `Done/` for completed action file

### Example 2: Process a CSV File

1. Drop a CSV file with data into `Inbox/`

2. Watcher creates action file with CSV preview

3. Qwen analyzes and creates insights

4. Results logged to Dashboard

## Human-in-the-Loop Workflow

For sensitive actions, Qwen creates approval requests:

1. Qwen creates file in `Pending_Approval/`
2. You review the file
3. Move to `Approved/` to execute
4. Move to `Rejected/` to decline
5. Orchestrator processes approved items

## Logging

All activity is logged to `Logs/`:

- `watcher_YYYY-MM-DD.log`: File watcher activity
- `orchestrator_YYYY-MM-DD.log`: Orchestration activity
- `filesystem_processed.txt`: Track processed files

## Troubleshooting

### Qwen Code not found

```bash
# Install Qwen Code (via pip)
pip install qwen-agent

# Or use the appropriate installation method for your setup
# Verify installation
qwen --version
```

### Watcher not detecting files

1. Check the Inbox folder path
2. Ensure file permissions allow reading
3. Check watcher logs in `Logs/`

### Orchestrator fails to process

1. Check Qwen Code is working: `qwen --version`
2. Check vault path is correct
3. Review orchestrator logs

## Security Notes

- **Never commit credentials** to the vault
- Use environment variables for API keys
- Review all actions in `Pending_Approval/`
- Regularly audit logs in `Logs/`

## Next Steps (Silver Tier)

To upgrade to Silver Tier, add:
- [ ] Gmail Watcher for email monitoring
- [ ] WhatsApp Watcher for message monitoring
- [ ] MCP server for sending emails
- [ ] Scheduled tasks via cron/Task Scheduler
- [ ] LinkedIn auto-posting

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  File Watcher   │────▶│  Needs_Action/   │────▶│   Qwen Code     │
│  (Python)       │     │  (Action Files)  │     │  (Reasoning)    │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌──────────────────┐     ┌────────▼────────┐
│  Dashboard.md   │◀────│  Plans/Done/     │◀────│  Orchestrator   │
│  (Status)       │     │  (State)         │     │  (Coordinator)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Resources

- [Hackathon Document](../Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md)
- [Qwen Code GitHub](https://github.com/QwenLM/Qwen)
- [Obsidian Help](https://help.obsidian.md/)
- [Wednesday Research Meeting](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
  - Wednesdays 10:00 PM
  - Meeting ID: 871 8870 7642
  - Passcode: 744832

## License

This project is part of the Personal AI Employee Hackathon 0.

---

*AI Employee v0.1 - Bronze Tier*
*Built with Qwen Code + Obsidian*
