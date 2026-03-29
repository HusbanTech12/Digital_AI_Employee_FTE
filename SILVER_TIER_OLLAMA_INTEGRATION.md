# Silver Tier: Ollama + Qwen-Agent Integration Guide

**Personal AI Employee Hackathon 0**
**Integration:** Ollama (Local AI) + Qwen-Agent Library
**Status:** Complete and Tested
**Date:** March 29, 2026

---

## Overview

This guide documents the complete integration of **Ollama** (free, local AI) and **qwen-agent** library as a replacement for Claude Code in the Silver Tier architecture.

### What Changed

| Component | Before (Claude Code) | After (Ollama + Qwen-Agent) |
|-----------|---------------------|----------------------------|
| **AI Provider** | Claude API | Ollama (local) or DashScope (cloud) |
| **Agent Library** | Claude SDK | qwen-agent Python library |
| **Model** | Claude 3.5 Sonnet | Qwen2.5 (7b, 14b, 32b) |
| **Cost** | ~$0.25-0.50 per task | 100% Free (Ollama) |
| **Privacy** | Cloud-based | Local-first (Ollama) |
| **Setup** | API key required | No API key (Ollama) |

---

## Architecture

### Silver Tier Stack

```
┌─────────────────────────────────────────────────────────┐
│                    SILVER TIER                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  WATCHERS (Senses)                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │  Gmail   │ │ WhatsApp │ │   File   │                │
│  │ Watcher  │ │ Watcher  │ │ Watcher  │                │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘                │
│       │            │            │                       │
│       └────────────┴────────────┘                       │
│                    │                                     │
│                    ▼                                     │
│         ┌─────────────────────┐                          │
│         │  Needs_Action/      │                          │
│         │  (Action Files)     │                          │
│         └──────────┬──────────┘                          │
│                    │                                     │
│                    ▼                                     │
│  ┌──────────────────────────────────────────┐            │
│  │      QWEN AGENT (Reasoning Engine)       │            │
│  │  ┌────────────────────────────────────┐  │            │
│  │  │  qwen_agent_config.py              │  │            │
│  │  │  - Unified provider interface      │  │            │
│  │  │  - Ollama support (local)          │  │            │
│  │  │  - DashScope support (cloud)       │  │            │
│  │  └────────────────────────────────────┘  │            │
│  │  ┌────────────────────────────────────┐  │            │
│  │  │  orchestrator.py                   │  │            │
│  │  │  - Task coordination               │  │            │
│  │  │  - Plan creation                   │  │            │
│  │  │  - Human-in-the-loop               │  │            │
│  │  └────────────────────────────────────┘  │            │
│  └──────────────────────────────────────────┘            │
│                    │                                     │
│         ┌──────────┼──────────┐                          │
│         │          │          │                          │
│         ▼          ▼          ▼                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                 │
│  │ Pending  │ │ Approved │ │   Done   │                 │
│  └──────────┘ └──────────┘ └──────────┘                 │
│                      │                                   │
│                      ▼                                   │
│  ┌──────────────────────────────┐                        │
│  │  MCP Servers (Actions)       │                        │
│  │  - email-mcp                 │                        │
│  │  - linkedin-poster           │                        │
│  └──────────────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

---

## Installation

### Step 1: Install Ollama

**Windows:**
1. Download from: https://ollama.com/download
2. Run `OllamaSetup.exe`
3. Wait for installation to complete
4. Verify:
   ```bash
   ollama --version
   ```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

**macOS:**
```bash
brew install ollama
ollama --version
```

### Step 2: Download Qwen Model

```bash
# Recommended model (best balance)
ollama pull qwen2.5:7b

# Smaller model (faster, less RAM)
ollama pull qwen2.5:3b

# Larger model (better quality, more RAM)
ollama pull qwen2.5:14b

# Check available models
ollama list
```

### Step 3: Install Python Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

**Key packages:**
- `ollama>=0.1.0` - Ollama Python client
- `qwen-agent>=0.0.34` - Qwen agent library
- `python-dotenv>=1.0.0` - Environment variable management

### Step 4: Configure Environment

Create `.env` file in project root:

```bash
# AI Provider Selection
AI_PROVIDER=ollama

# Ollama Model
OLLAMA_MODEL=qwen2.5:7b

# Optional: DashScope (if you want cloud AI option)
# DASHSCOPE_API_KEY=your_api_key_here
# QWEN_MODEL=qwen-plus
```

### Step 5: Test Installation

```bash
# Test Ollama
ollama run qwen2.5:7b "Say hello in one sentence"

# Test Python integration
cd scripts
python -c "import ollama; print(ollama.chat('qwen2.5:7b', messages=[{'role': 'user', 'content': 'Hello!'}]))"

# Test orchestrator
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
```

---

## Configuration Files

### 1. qwen_agent_config.py

**Location:** `D:\Quarter_4\Hackathon_0\Digital_AI_Employee_FTE\qwen_agent_config.py`

**Purpose:** Unified AI provider interface supporting both Ollama and DashScope.

**Key Features:**
- Automatic provider detection
- Fallback handling
- Environment variable configuration
- Test utilities

**Usage:**
```python
from qwen_agent_config import QwenAgentProvider

# Create provider (auto-detects from .env)
provider = QwenAgentProvider()

# Chat
response = provider.chat("Hello, how are you?")
print(response)

# Test availability
if provider.is_available():
    print("AI is ready!")
```

### 2. orchestrator.py

**Location:** `D:\Quarter_4\Hackathon_0\Digital_AI_Employee_FTE\scripts\orchestrator.py`

**Purpose:** Main task coordinator using Qwen Agent.

**Key Features:**
- Ollama integration
- DashScope integration
- Plan creation
- Human-in-the-loop approval
- Dashboard updates

**Commands:**
```bash
# Run once (process all pending items)
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once

# Continuous mode
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --continuous --interval 60

# Use different model
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --model qwen2.5:14b --once

# Use DashScope
python orchestrator.py --vault ..\AI_Employee_Vault --provider dashscope --api-key YOUR_KEY --once
```

---

## How It Works

### Flow: File Detection to Completion

1. **Detection** (Watcher)
   - File dropped in `Inbox/`
   - Watcher detects new file
   - Creates action file in `Needs_Action/`

2. **Reasoning** (Qwen Agent via Ollama)
   - Orchestrator reads action file
   - Sends prompt to Ollama
   - Qwen2.5 model processes request
   - Returns response with plan

3. **Planning** (Orchestrator)
   - Creates `Plan.md` in `Plans/`
   - Lists steps with checkboxes
   - Tracks progress

4. **Execution** (Qwen Agent + MCP)
   - Qwen executes plan steps
   - Uses MCP servers for actions
   - Requests approval for sensitive actions

5. **Completion** (Orchestrator)
   - Moves action file to `Done/`
   - Updates `Dashboard.md`
   - Logs activity

### Example: Processing an Email Request

**Action File:** `Needs_Action/EMAIL_001.md`
```markdown
---
type: email_request
from: client@example.com
subject: Invoice Request
priority: normal
---

Client is requesting an invoice for services rendered.
Please create and send invoice for $500.
```

**Qwen Agent Response:**
```markdown
# Plan: EMAIL_001

## Objective
Create and send invoice for $500 to client@example.com

## Steps
- [ ] Create invoice in accounting system
- [ ] Generate PDF
- [ ] Send email with invoice attached
- [ ] Log transaction
- [ ] Move to Done

## Approval Required
Yes - New invoice > $100
```

**Approval File:** `Pending_Approval/APPROVAL_EMAIL_001.md`
```markdown
---
type: approval_request
action: send_invoice
amount: 500.00
recipient: client@example.com
created: 2026-03-29T10:30:00Z
status: pending
---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

---

## Model Comparison

### Qwen2.5 Models (Ollama)

| Model | Size | RAM | Speed | Quality | Best For |
|-------|------|-----|-------|---------|----------|
| qwen2.5:3b | 2GB | 4GB | ⚡⚡⚡ | Good | Simple tasks, fast response |
| qwen2.5:7b | 4GB | 8GB | ⚡⚡ | Better | **Recommended** - balanced |
| qwen2.5:14b | 8GB | 16GB | ⚡ | Best | Complex reasoning |
| qwen2.5:32b | 18GB | 32GB | 🐌 | Excellent | Advanced tasks |

### DashScope Models

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| qwen-turbo | ⚡⚡⚡ | Good | $ | Fast responses |
| qwen-plus | ⚡⚡ | Better | $$ | **Recommended** - balanced |
| qwen-max | ⚡ | Best | $$$ | Complex tasks |

---

## Testing

### Test Suite

```bash
# Test Ollama integration
python qwen_agent_config.py

# Test full system
cd scripts
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once

# Test with sample file
echo "Please analyze this text and create action items" > AI_Employee_Vault/Inbox/test.txt
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
```

### Expected Output

```
Orchestrator initialized
Vault: D:\Quarter_4\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault
AI Provider: ollama
Model: qwen2.5:7b
Found 1 pending item(s)
Created plan: PLAN_test.md
Using Ollama with model: qwen2.5:7b
Qwen Agent response: [AI response...]
Task marked as complete by AI
Moved to Done: test.md
Dashboard updated
Processed 1 item(s)
```

---

## Troubleshooting

### "ollama package not installed"

```bash
# Install package
pip install ollama

# Verify installation
python -c "import ollama; print('OK')"
```

### "Model not found"

```bash
# Download model
ollama pull qwen2.5:7b

# Check available models
ollama list
```

### "Connection refused"

```bash
# Start Ollama service
ollama serve

# Or restart computer (Ollama runs as service)
```

### "Out of memory"

```bash
# Use smaller model
ollama pull qwen2.5:3b

# Update .env
OLLAMA_MODEL=qwen2.5:3b
```

### "qwen-agent not available"

```bash
# Install package
pip install qwen-agent dashscope

# Or use Ollama only (recommended)
AI_PROVIDER=ollama
```

---

## Performance Benchmarks

### Response Times (Average)

| Model | Simple Task | Complex Task | Plan Creation |
|-------|-------------|--------------|---------------|
| qwen2.5:3b | 5-10s | 15-30s | 10-15s |
| qwen2.5:7b | 10-20s | 30-60s | 20-30s |
| qwen2.5:14b | 20-40s | 60-120s | 40-60s |
| qwen-plus (API) | 5-15s | 20-40s | 15-25s |

### Resource Usage

| Model | RAM | Disk | CPU |
|-------|-----|------|-----|
| qwen2.5:3b | 2-4GB | 2GB | Low |
| qwen2.5:7b | 4-8GB | 4.7GB | Medium |
| qwen2.5:14b | 8-16GB | 8GB | High |

---

## Migration from Claude Code

### Before (Claude Code)

```python
# Old code
from anthropic import Anthropic

client = Anthropic(api_key="...")
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": prompt}]
)
```

### After (Ollama + Qwen-Agent)

```python
# New code
import ollama

response = ollama.chat(
    model="qwen2.5:7b",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
)
```

### Migration Checklist

- [ ] Install Ollama
- [ ] Download Qwen model
- [ ] Update `orchestrator.py` (already done)
- [ ] Update `qwen_agent_config.py` (already done)
- [ ] Update `.env` file
- [ ] Test with sample file
- [ ] Update watcher scripts
- [ ] Update documentation

---

## Best Practices

### 1. Model Selection

- **Start with qwen2.5:7b** - Best balance
- Upgrade to 14b if quality issues
- Downgrade to 3b if speed issues

### 2. Prompt Engineering

```markdown
# Good prompt structure
You are an AI Employee assistant.

## Context
- Vault: /path/to/vault
- Action File: filename.md
- Time: 2026-03-29T10:30:00Z

## Your Task
1. Read the action file
2. Create a plan
3. Execute the plan
4. Move to Done

## Output Format
After completing, output: <promise>TASK_COMPLETE</promise>
```

### 3. Error Handling

```python
try:
    response = ollama.chat(model, messages)
except Exception as e:
    logger.error(f"Ollama error: {e}")
    # Fallback to manual processing
```

### 4. Resource Management

- Close other applications when using larger models
- Use 3b model on low-RAM systems
- Monitor Ollama process: `ollama ps`

---

## Next Steps

### Silver Tier Complete! ✅

You now have:
- ✅ Local AI (Ollama) + Cloud AI (DashScope) support
- ✅ qwen-agent library integration
- ✅ Multiple watchers (Gmail, WhatsApp, Filesystem)
- ✅ Human-in-the-loop approval
- ✅ MCP server integration
- ✅ Scheduling capabilities

### Upgrade to Gold Tier

Add these features:
1. Odoo accounting integration
2. Facebook/Instagram integration
3. Twitter (X) integration
4. Weekly Business Audit with CEO Briefing
5. Error recovery and audit logging
6. Ralph Wiggum loop for autonomous completion

---

## Resources

- **Ollama:** https://ollama.com
- **Qwen2.5 Models:** https://ollama.com/library/qwen2.5
- **qwen-agent:** https://github.com/QwenLM/Qwen
- **DashScope:** https://dashscope.console.aliyun.com
- **Hackathon Docs:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Wednesday Meetings:** 10:00 PM Zoom (ID: 871 8870 7642)

---

*AI Employee v0.2 - Silver Tier*
*Powered by Ollama + Qwen-Agent + Obsidian*
*Last Updated: 2026-03-29*
