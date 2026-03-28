# AI Employee - Complete Ollama Setup Guide

## Current Status

✅ Python 3.13 installed  
✅ Python packages (ollama, dotenv) installed  
✅ Vault structure created  
✅ Scripts ready  
❌ **Ollama CLI - NEEDS INSTALLATION**

---

## INSTALL OLLAMA NOW (Required Step)

### Step 1: Download Ollama

1. **Visit:** https://ollama.com/download
2. **Click:** "Download for Windows"
3. **Save:** `OllamaSetup.exe` will download

### Step 2: Install Ollama

1. **Run:** Double-click `OllamaSetup.exe`
2. **Accept:** Click "Install"
3. **Wait:** Installation takes 2-3 minutes
4. **Finish:** Click "Done"

### Step 3: Verify Installation

**IMPORTANT:** Open a **NEW** Command Prompt window (close any open ones first)

```bash
ollama --version
```

You should see:
```
ollama version 0.5.x
```

---

## After Ollama is Installed

### Step 4: Download Qwen Model

In the new Command Prompt:

```bash
ollama pull qwen2.5:7b
```

This downloads about 4GB. Wait for completion.

Verify:
```bash
ollama list
```

You should see:
```
NAME              ID           SIZE
qwen2.5:7b        ...          4.7 GB
```

### Step 5: Test Ollama

```bash
ollama run qwen2.5:7b "Hello, are you ready to help?"
```

Expected response:
```
Hello! Yes, I'm ready to help you with your tasks...
```

### Step 6: Run Setup Verification

Back in your project folder:

```bash
cd C:\Project\Hackathon_0\Digital_AI_Employee_FTE
python check_setup.py
```

All checks should pass!

---

## Using AI Employee with Ollama

### Start File Watcher

```bash
cd scripts
python filesystem_watcher.py ..\AI_Employee_Vault
```

Keep this running in the background.

### Process Tasks with AI

In a new terminal:

```bash
cd scripts
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
```

### Complete Workflow Test

1. **Create a test file:**
   ```
   AI_Employee_Vault\Inbox\test.txt
   ```
   
   Content:
   ```
   Please create a plan to organize this project.
   ```

2. **Wait 30 seconds** (watcher checks every 30s)

3. **Run orchestrator:**
   ```bash
   cd scripts
   python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
   ```

4. **Check results:**
   - `Plans/` - New plan created by Ollama
   - `Done/` - Completed task
   - `Dashboard.md` - Updated

---

## Quick Reference

### Ollama Commands

```bash
# Check version
ollama --version

# List models
ollama list

# Download model
ollama pull qwen2.5:7b

# Test model
ollama run qwen2.5:7b "Hello"

# Start server (if not auto-started)
ollama serve

# Stop server
ollama serve (then Ctrl+C)
```

### AI Employee Commands

```bash
# Check setup
python check_setup.py

# Start watcher
cd scripts
python filesystem_watcher.py ..\AI_Employee_Vault

# Process tasks (with Ollama)
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once

# Process tasks (manual mode, no AI)
python orchestrator.py --vault ..\AI_Employee_Vault --once

# Continuous mode
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --continuous --interval 60
```

---

## Troubleshooting

### "ollama is not recognized"

1. Make sure Ollama is installed
2. **Close** all Command Prompt windows
3. Open a **NEW** Command Prompt
4. Try again: `ollama --version`

### "Connection refused"

Ollama service not running:
```bash
ollama serve
```

Or restart your computer (Ollama auto-starts on boot).

### "Model not found"

Download the model:
```bash
ollama pull qwen2.5:7b
```

### "Out of memory"

Use a smaller model:
```bash
ollama pull qwen2.5:3b
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --model qwen2.5:3b --once
```

### Python script errors

Re-run verification:
```bash
python check_setup.py
```

---

## Summary

| Step | Command | Status |
|------|---------|--------|
| 1. Install Ollama | Download from website | ⏳ **YOU MUST DO THIS** |
| 2. Verify | `ollama --version` | ⏳ After install |
| 3. Download model | `ollama pull qwen2.5:7b` | ⏳ After verify |
| 4. Test | `ollama run qwen2.5:7b "Hello"` | ⏳ After download |
| 5. Verify setup | `python check_setup.py` | ⏳ After test |
| 6. Use AI | `python orchestrator.py --ollama` | ⏳ After verify |

---

## What's Ready Now

✅ Python and all packages installed  
✅ AI Employee vault created  
✅ All scripts ready  
✅ Orchestrator configured for Ollama  
✅ File watcher ready  

## What You Need to Do

⏳ Install Ollama CLI (one-time, 5 minutes)  
⏳ Download Qwen model (one-time, 4GB download)  
⏳ Run `python check_setup.py` to verify  

---

**After installing Ollama, run:**
```bash
python check_setup.py
```

**If all checks pass, you're ready to go!** 🎉

---

*AI Employee v0.1 - Bronze Tier*
*Complete Ollama Setup Guide*
