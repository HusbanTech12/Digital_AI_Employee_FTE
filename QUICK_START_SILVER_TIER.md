# 🚀 Quick Start: Silver Tier with Ollama

**Get your AI Employee running in 5 minutes!**

---

## Prerequisites

- ✅ Python 3.13+ installed
- ✅ 8GB+ RAM recommended
- ✅ 10GB+ free disk space

---

## Step 1: Install Ollama (2 minutes)

### Windows
1. Download: https://ollama.com/download
2. Run `OllamaSetup.exe`
3. Wait for installation

### Verify
```bash
ollama --version
```

---

## Step 2: Download Qwen Model (3 minutes)

```bash
# Recommended model (best balance)
ollama pull qwen2.5:7b
```

**Wait for download to complete** (~4.7GB)

### Verify
```bash
ollama list
# Should show qwen2.5:7b
```

---

## Step 3: Install Python Dependencies (1 minute)

```bash
cd D:\Quarter_4\Hackathon_0\Digital_AI_Employee_FTE\scripts
pip install -r requirements.txt
```

---

## Step 4: Configure Environment (30 seconds)

Create `.env` file in project root:

```bash
AI_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b
```

---

## Step 5: Test Integration (1 minute)

```bash
# Run test suite
cd D:\Quarter_4\Hackathon_0\Digital_AI_Employee_FTE
python scripts\test_ollama_integration.py
```

**Expected:** 85%+ tests passing

---

## Step 6: Run Your First Task

### Option A: Drop a Test File

1. Create a text file: `AI_Employee_Vault\Inbox\test.txt`
2. Write: `Please analyze this and create action items`
3. Run orchestrator:

```bash
cd scripts
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
```

### Option B: Use Batch File

```bash
# Run once
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once

# Or continuous mode
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --continuous
```

---

## Verify It Works

Check these folders:
- `AI_Employee_Vault/Plans/` - Should have new plan files
- `AI_Employee_Vault/Done/` - Should have processed files
- `AI_Employee_Vault/Dashboard.md` - Should be updated

---

## Troubleshooting

### "Model not found"
```bash
ollama pull qwen2.5:7b
```

### "ollama package not installed"
```bash
pip install ollama
```

### "Connection refused"
```bash
# Ollama service not running
# Restart computer or run:
ollama serve
```

### "Out of memory"
```bash
# Use smaller model
ollama pull qwen2.5:3b
# Update .env
OLLAMA_MODEL=qwen2.5:3b
```

---

## What's Next?

### Silver Tier Features Available

✅ **File System Watcher** - Monitors Inbox folder
✅ **Gmail Watcher** - Monitors Gmail (requires setup)
✅ **WhatsApp Watcher** - Monitors WhatsApp (requires setup)
✅ **LinkedIn Poster** - Auto-post to LinkedIn
✅ **Human-in-the-Loop** - Approval workflow
✅ **Dashboard Updates** - Automatic status updates

### Setup Watchers

See `SILVER_TIER.md` for detailed watcher setup instructions.

---

## Commands Reference

```bash
# Run once (process all pending)
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once

# Continuous mode
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --continuous --interval 60

# Different model
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --model qwen2.5:14b --once

# Dry run (test without changes)
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once --dry-run

# Run tests
python scripts\test_ollama_integration.py
```

---

## Model Options

| Model | Size | Speed | Quality | Command |
|-------|------|-------|---------|---------|
| qwen2.5:3b | 2GB | Fast | Good | `ollama pull qwen2.5:3b` |
| **qwen2.5:7b** | 4GB | Medium | Better | `ollama pull qwen2.5:7b` |
| qwen2.5:14b | 8GB | Slow | Best | `ollama pull qwen2.5:14b` |

---

## Support

- **Full Documentation:** `SILVER_TIER_OLLAMA_INTEGRATION.md`
- **Test Suite:** `test-silver-tier.bat`
- **Hackathon Docs:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Wednesday Meetings:** 10:00 PM Zoom (ID: 871 8870 7642)

---

## Success Checklist

- [ ] Ollama installed
- [ ] Qwen2.5:7b model downloaded
- [ ] Python dependencies installed
- [ ] `.env` file configured
- [ ] Tests passing (85%+)
- [ ] First task processed

**All checked? You're ready to go! 🎉**

---

*AI Employee v0.2 - Silver Tier*
*Powered by Ollama + Qwen-Agent + Obsidian*
