# Free AI Setup - Ollama + Qwen (Local, No API Key Required)

This guide shows you how to run the AI Employee completely **FREE** using local models.

## Quick Summary

| Option | Cost | Setup Time | Quality |
|--------|------|------------|---------|
| **Ollama (Local)** | 100% Free | 10 minutes | Good |
| **Manual Mode** | 100% Free | 0 minutes | You decide |

---

## Option 1: Ollama (Recommended - Free Local AI)

### Step 1: Install Ollama

**Windows:**
1. Download from: https://ollama.com/download
2. Run installer (OllamaSetup.exe)
3. Wait for installation to complete
4. Verify: Open Command Prompt and run:
   ```bash
   ollama --version
   ```

### Step 2: Download Qwen Model

```bash
# Small model (4GB RAM) - Fast, good for simple tasks
ollama pull qwen2.5:7b

# Check available models
ollama list

# Test it works
ollama run qwen2.5:7b "Hello, are you working?"
```

**Expected output:**
```
Hello! Yes, I'm working and ready to help you with your tasks...
```

### Step 3: Install Python Package

```bash
cd C:\Project\Hackathon_0\Digital_AI_Employee_FTE\scripts
pip install ollama
```

### Step 4: Run Orchestrator with Ollama

```bash
# Using --ollama flag
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once

# Or set environment variable
set AI_PROVIDER=ollama
python orchestrator.py --vault ..\AI_Employee_Vault --once

# Use different model
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --model qwen2.5:14b --once
```

---

## Option 2: Manual Mode (No AI Required)

The Bronze Tier works **without any AI** - you just execute tasks manually!

### How it works:

1. **Watcher** detects files → Creates action files in `Needs_Action/`
2. **Orchestrator** creates `Plan.md` with checkboxes
3. **You** read the plan and execute tasks manually
4. **You** move completed files to `Done/`

### Commands:

```bash
# Start watcher
cd scripts
python filesystem_watcher.py ..\AI_Employee_Vault

# In another terminal, run orchestrator (creates plans)
python orchestrator.py --vault ..\AI_Employee_Vault --once
```

### This is FREE and always available!

No API key, no installation, just works.

---

## Available Qwen Models (Ollama)

| Model | Size | RAM Required | Speed | Quality |
|-------|------|--------------|-------|---------|
| qwen2.5:3b | 2GB | 4GB | Fast | Basic |
| qwen2.5:7b | 4GB | 8GB | Fast | Good |
| qwen2.5:14b | 8GB | 16GB | Medium | Better |
| qwen2.5:32b | 18GB | 32GB | Slow | Best |

**Recommendation:** Start with `qwen2.5:7b`, upgrade if you need better quality.

---

## Complete Setup Script

Save as `setup-ollama.bat`:

```batch
@echo off
echo Installing Ollama support...
pip install ollama
echo.
echo Downloading Qwen model (this may take a few minutes)...
ollama pull qwen2.5:7b
echo.
echo Testing...
ollama run qwen2.5:7b "Say hello in one sentence"
echo.
echo Done! Ollama is ready.
echo Run: python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
pause
```

---

## Comparison

| Option | Cost | Speed | Quality | Setup | Best For |
|--------|------|-------|---------|-------|----------|
| **Ollama** | Free | Fast | Good | Easy | Everyone |
| **Manual** | Free | N/A | You decide | None | Testing |
| **DashScope** | Free credits | Fast | Excellent | Easy | Production |
| **Hugging Face** | Free tier | Medium | Good | Medium | Developers |

---

## Quick Test

```bash
# Test Ollama is working
ollama run qwen2.5:7b "Hello, are you working?"

# Expected response:
# Hello! Yes, I'm working and ready to help...
```

---

## Troubleshooting

### "ollama: command not found"
- Ollama not installed or not on PATH
- Restart terminal after installation
- Check: `ollama --version`
- Reinstall from: https://ollama.com/download

### "Model not found"
```bash
# Download model
ollama pull qwen2.5:7b

# Check available models
ollama list
```

### "Out of memory"
- Use smaller model: `ollama pull qwen2.5:3b`
- Close other applications
- Increase virtual memory (Windows)

### "Connection refused"
- Ollama service not running
- Start Ollama: Just run `ollama serve` or restart computer
- Check: `ollama list` (should work if service is running)

### "pip install ollama fails"
```bash
# Try upgrading pip
python -m pip install --upgrade pip
pip install ollama
```

---

*AI Employee v0.1 - Bronze Tier*
*Free Setup Guide*
