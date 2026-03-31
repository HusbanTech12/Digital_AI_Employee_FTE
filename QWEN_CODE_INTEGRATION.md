# Qwen Code CLI Integration Guide

**Date:** March 31, 2026  
**Status:** Complete  
**AI Provider:** Qwen Code CLI (Full-featured agent)

---

## Overview

This guide explains how to integrate **Qwen Code CLI** as the reasoning engine for your AI Employee system, replacing Ollama and Claude Code.

### What is Qwen Code CLI?

Qwen Code CLI is a powerful command-line AI assistant that provides:
- **Full agent capabilities** - Can read files, write code, execute commands
- **Large context window** - Can process entire codebases
- **Tool integration** - Built-in file operations, shell commands, web search
- **OAuth authentication** - Secure, token-based access
- **Cross-platform** - Works on Windows, macOS, and Linux

### Architecture Comparison

| Component | Previous (Ollama) | New (Qwen Code CLI) |
|-----------|-------------------|---------------------|
| **AI Engine** | Qwen2.5 via Ollama | Qwen Code (full agent) |
| **Execution** | Python `ollama` package | CLI subprocess calls |
| **Context** | Limited (model-dependent) | 1M+ tokens |
| **Tools** | None | Files, Shell, Search |
| **Authentication** | None (local) | OAuth |
| **Cost** | Free (local compute) | Free tier available |

---

## Installation

### Step 1: Install Qwen Code CLI

**Option A: Download from Official Website (Recommended)**
```
1. Visit: https://chat.qwen.ai
2. Download the Qwen Code application
3. Follow installation instructions for your platform
```

**Option B: Install via npm (requires Node.js)**
```bash
npm install -g @qwen-code/cli
```

### Step 2: Verify Installation

```bash
qwen-code --version
```

Expected output: `0.13.2` or similar

### Step 3: Authenticate

```bash
qwen-code auth
```

Follow the authentication prompts to set up OAuth credentials.

---

## Quick Start

### 1. Run Configuration Script

```bash
# Windows
configure-qwen-code.bat

# Linux/macOS
python scripts/configure_qwen_code.py
```

This script:
- Checks if Qwen Code CLI is installed
- Tests the connection
- Creates the vault structure
- Configures the `.env` file

### 2. Test Integration

```bash
python scripts/test_qwen_code_integration.py
```

Expected output: All 9 tests should pass

### 3. Start the AI Employee

```bash
# Windows
start-qwen-code-ai.bat

# Linux/macOS
python scripts/orchestrator.py --vault AI_Employee_Vault --qwen-code --continuous
```

---

## Configuration

### Environment Variables (.env)

```bash
# AI Provider Configuration
AI_PROVIDER=qwen_code_cli

# Qwen Code CLI Model
QWEN_CODE_MODEL=qwen-plus

# Optional: Custom CLI path (auto-detected if in PATH)
# QWEN_CODE_PATH=/usr/local/bin/qwen-code

# Vault path
AI_EMPLOYEE_VAULT=./AI_Employee_Vault
```

### Command-Line Options

```bash
# Run with Qwen Code CLI
python scripts/orchestrator.py --qwen-code --once

# Specify model
python scripts/orchestrator.py --qwen-code --model qwen-max

# Continuous mode
python scripts/orchestrator.py --qwen-code --continuous --interval 60

# Dry run (test without executing)
python scripts/orchestrator.py --qwen-code --dry-run --once
```

---

## How It Works

### Integration Flow

```
┌─────────────────┐
│ File Watcher    │
│ (monitors Inbox)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Orchestrator    │
│ (coordinates)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ QwenCodeProvider│
│ (CLI wrapper)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Qwen Code CLI   │
│ (subprocess)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Qwen Cloud API  │
│ (processing)    │
└─────────────────┘
```

### File Processing Example

1. **User drops file** in `AI_Employee_Vault/Inbox/`
2. **File Watcher** detects new file, creates action file in `Needs_Action/`
3. **Orchestrator** picks up action file
4. **QwenCodeProvider** builds prompt with file content
5. **Qwen Code CLI** processes the prompt:
   - Reads action file
   - Creates plan in `Plans/`
   - Executes tasks
   - Moves file to `Done/`
6. **Dashboard** is updated with activity

---

## Usage Examples

### Example 1: Process Email Draft

**Drop file in Inbox:**
```markdown
---
type: email_draft
to: client@example.com
subject: Project Update
---

Please draft a professional email updating the client on project progress.
Key points:
- Completed phase 1
- Starting phase 2 next week
- On schedule and budget
```

**Qwen Code will:**
1. Read the file
2. Draft the email
3. Save to `Files/`
4. Create action plan
5. Move to `Done/`

### Example 2: Invoice Generation

**Drop file in Inbox:**
```markdown
---
type: invoice
client: ABC Corp
amount: 1500.00
services:
  - Web development: 10 hours @ $100/hour
  - Consulting: 5 hours @ $100/hour
---

Generate and send invoice.
```

**Qwen Code will:**
1. Read the file
2. Check approval requirements (amount > $50)
3. Create approval request in `Pending_Approval/`
4. Wait for human approval
5. Generate invoice PDF
6. Send via email (if MCP configured)

---

## Troubleshooting

### "Qwen Code CLI not found"

**Solution:**
```bash
# Check if installed
qwen-code --version

# If not found, install:
npm install -g @qwen-code/cli

# Or download from: https://chat.qwen.ai
```

### "Authentication failed"

**Solution:**
```bash
# Re-authenticate
qwen-code auth

# Clear credentials and retry
rm ~/.qwen/oauth_creds.json  # Linux/macOS
del %APPDATA%\..qwen\oauth_creds.json  # Windows
```

### "Telemetry error"

**Solution:**
Disable telemetry in settings:
```bash
qwen-code --telemetry=false
```

Or in `.qwen/settings.json`:
```json
{
  "telemetry": {
    "enabled": false
  }
}
```

### "Model not responding"

**Solutions:**
1. Check internet connection
2. Verify authentication: `qwen-code auth`
3. Try different model: `--model qwen-turbo`
4. Increase timeout in provider

---

## Performance Comparison

| Metric | Ollama (qwen2.5:7b) | Qwen Code CLI (qwen-plus) |
|--------|---------------------|---------------------------|
| Response Time | 5-30 seconds | 2-10 seconds |
| Context Window | 32K tokens | 1M+ tokens |
| Tool Support | None | Files, Shell, Search |
| Quality | Good | Excellent |
| Cost | Free (local) | Free tier + paid |
| Setup Complexity | Medium | Low |

---

## Security Considerations

### Credential Management

- OAuth tokens stored in: `~/.qwen/oauth_creds.json`
- Never commit credentials to version control
- Rotate tokens monthly

### Approval Workflow

Sensitive actions require human approval:
- Payments > $50
- Emails to new contacts
- File deletions
- External API calls

### Audit Logging

All actions are logged in:
```
AI_Employee_Vault/Logs/orchestrator_YYYY-MM-DD.log
```

Review logs weekly for unusual activity.

---

## Advanced Configuration

### Custom Sandbox Configuration

```bash
# Run in sandbox mode
python scripts/orchestrator.py --qwen-code --sandbox
```

### Allowed Tools

```bash
# Allow specific tools
python scripts/orchestrator.py --qwen-code --allowed-tools Read,Write,Shell
```

### Model Selection

```bash
# Use qwen-max for best quality
python scripts/orchestrator.py --qwen-code --model qwen-max

# Use qwen-turbo for fastest response
python scripts/orchestrator.py --qwen-code --model qwen-turbo
```

---

## Migration from Ollama

### Step 1: Backup Current Setup

```bash
cp .env .env.ollama.backup
```

### Step 2: Update .env

```bash
# Change AI provider
AI_PROVIDER=qwen_code_cli

# Keep Ollama as backup
# OLLAMA_MODEL=qwen2.5:7b
```

### Step 3: Test Side-by-Side

```bash
# Test with Ollama
python scripts/orchestrator.py --ollama --once

# Test with Qwen Code CLI
python scripts/orchestrator.py --qwen-code --once
```

### Step 4: Switch Completely

Once Qwen Code CLI is working, remove Ollama dependencies:
```bash
pip uninstall ollama
```

---

## Resources

- **Qwen Code Docs:** https://qwenlm.github.io/qwen-code-docs/
- **Official Website:** https://chat.qwen.ai
- **npm Package:** https://www.npmjs.com/package/@qwen-code/cli
- **Hackathon Docs:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`

---

## Support

**Wednesday Meetings:**
- Time: 10:00 PM on Zoom
- Meeting ID: 871 8870 7642
- Passcode: 744832
- YouTube: https://www.youtube.com/@panaversity

---

*AI Employee v1.0 - Powered by Qwen Code CLI*
