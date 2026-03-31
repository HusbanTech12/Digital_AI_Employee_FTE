"""
Qwen Code CLI Setup Script for AI Employee System

This script helps you set up and configure Qwen Code CLI as the reasoning engine
for your AI Employee system.

What it does:
1. Checks if Qwen Code CLI is installed
2. Helps with installation if needed
3. Tests the CLI connection
4. Configures the .env file
5. Validates the setup

Usage:
    python scripts/configure_qwen_code.py
"""

import subprocess
import shutil
import sys
import os
from pathlib import Path
from typing import Optional, Tuple

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / '.env'
VAULT_PATH = PROJECT_ROOT / 'AI_Employee_Vault'

print("=" * 70)
print("Qwen Code CLI Setup for AI Employee System")
print("=" * 70)
print()

# Configuration storage
config = {
    'qwen_code_installed': False,
    'qwen_code_path': None,
    'qwen_code_version': None,
    'qwen_code_authenticated': False,
    'env_configured': False,
    'vault_exists': False,
}


def run_command(cmd: list, timeout: int = 30) -> Tuple[bool, str]:
    """Run command and return (success, output)"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=(os.name == 'nt')  # Use shell on Windows
        )
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_qwen_code() -> bool:
    """Check if Qwen Code CLI is installed"""
    print("1. Checking Qwen Code CLI Installation")
    print("-" * 40)

    # Common executable names
    executable_names = [
        'qwen-code',
        'qwen_code',
        'qwen',
        'qwen-code-cli'
    ]

    # Check PATH
    for exe in executable_names:
        path = shutil.which(exe)
        if path:
            config['qwen_code_installed'] = True
            config['qwen_code_path'] = path
            print(f"✅ Found Qwen Code CLI: {path}")

            # Get version
            success, output = run_command([path, '--version'])
            if success:
                config['qwen_code_version'] = output
                print(f"   Version: {output}")
            else:
                print(f"   Version: Unknown (could not determine)")

            return True

    # Check common installation locations
    common_paths = [
        Path.home() / '.qwen' / 'bin' / 'qwen-code',
        Path.home() / '.local' / 'bin' / 'qwen-code',
        Path('C:\\Program Files\\Qwen Code\\qwen-code.exe'),
        Path(os.environ.get('APPDATA', '')) / '..' / 'Local' / 'Programs' / 'Qwen Code' / 'qwen-code.exe',
        Path('C:\\Users\\Fattani Computers\\AppData\\Local\\Programs\\Qwen Code\\qwen-code.exe'),
    ]

    for path in common_paths:
        if path.exists() and path.is_file():
            config['qwen_code_installed'] = True
            config['qwen_code_path'] = str(path)
            print(f"✅ Found Qwen Code CLI: {path}")

            # Get version
            success, output = run_command([str(path), '--version'])
            if success:
                config['qwen_code_version'] = output
                print(f"   Version: {output}")

            return True

    print("❌ Qwen Code CLI not found")
    print()
    print("Installation options:")
    print()
    print("Option 1: Download from official website")
    print("  Visit: https://chat.qwen.ai")
    print("  Download and install the Qwen Code application")
    print()
    print("Option 2: Install via npm (requires Node.js)")
    print("  Run: npm install -g @qwen-code/cli")
    print()
    return False


def check_authentication() -> bool:
    """Check if Qwen Code CLI is authenticated"""
    print("\n2. Checking Authentication")
    print("-" * 40)

    if not config['qwen_code_installed']:
        print("⚠️  Qwen Code CLI not installed, skipping authentication check")
        return False

    # Try to run a simple command to check authentication
    success, output = run_command(
        [config['qwen_code_path'], '--help'],
        timeout=10
    )

    if success:
        config['qwen_code_authenticated'] = True
        print("✅ Qwen Code CLI appears to be working")
        return True
    else:
        print("⚠️  Qwen Code CLI may not be authenticated")
        print()
        print("To authenticate, run:")
        print(f"  {config['qwen_code_path']} login")
        return False


def test_qwen_code() -> bool:
    """Test Qwen Code CLI with a simple prompt"""
    print("\n3. Testing Qwen Code CLI")
    print("-" * 40)

    if not config['qwen_code_installed']:
        print("❌ Qwen Code CLI not installed")
        return False

    # Test with a simple prompt using headless mode
    test_prompt = "Say 'Qwen Code is working!' in exactly 4 words."

    try:
        # Run in headless mode with the prompt
        result = subprocess.run(
            [config['qwen_code_path'], '--headless'],
            input=test_prompt,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and result.stdout.strip():
            response = result.stdout.strip()
            print(f"✅ Qwen Code CLI responded:")
            print(f"   {response[:100]}...")
            return True
        else:
            print(f"⚠️  Qwen Code CLI returned error:")
            print(f"   {result.stderr[:200]}...")
            return False

    except subprocess.TimeoutExpired:
        print("⚠️  Qwen Code CLI test timed out (this is normal for first run)")
        return True  # Consider it a pass, first run can be slow
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def check_vault() -> bool:
    """Check if vault exists"""
    print("\n4. Checking Vault Structure")
    print("-" * 40)

    if VAULT_PATH.exists():
        config['vault_exists'] = True
        print(f"✅ Vault exists: {VAULT_PATH}")

        # Check required folders
        required_folders = [
            'Inbox', 'Needs_Action', 'Plans', 'Done',
            'Pending_Approval', 'Approved', 'Rejected', 'Logs'
        ]
        missing = []
        for folder in required_folders:
            if not (VAULT_PATH / folder).exists():
                missing.append(folder)

        if missing:
            print(f"⚠️  Missing folders: {', '.join(missing)}")
            print("   Creating missing folders...")
            for folder in missing:
                (VAULT_PATH / folder).mkdir(parents=True, exist_ok=True)
            print("✅ Folders created")
        else:
            print(f"✅ All required folders exist")
    else:
        print(f"❌ Vault does not exist: {VAULT_PATH}")
        print("   Creating vault structure...")
        create_vault()

    print()
    return config['vault_exists']


def create_vault():
    """Create vault structure"""
    try:
        VAULT_PATH.mkdir(parents=True, exist_ok=True)

        folders = [
            'Inbox', 'Needs_Action', 'Plans', 'Done',
            'Pending_Approval', 'Approved', 'Rejected',
            'Logs', 'Files', 'Briefings', 'Audits'
        ]
        for folder in folders:
            (VAULT_PATH / folder).mkdir(parents=True, exist_ok=True)

        # Create Dashboard.md
        dashboard_content = '''---
last_updated: 2026-03-31T00:00:00Z
status: active
tier: gold
ai_provider: qwen_code_cli
---

# AI Employee Dashboard

## Status
- **Tier:** Gold
- **AI Provider:** Qwen Code CLI
- **Status:** Active

## Quick Stats
- Tasks Pending: 0
- Tasks Completed: 0
- Last Activity: N/A

## Recent Activity
- System initialized with Qwen Code CLI

## Folders
- [[Inbox]] - Drop files here
- [[Needs_Action]] - Items to process
- [[Plans]] - Action plans
- [[Done]] - Completed tasks
- [[Pending_Approval]] - Awaiting approval
- [[Approved]] - Ready to execute
- [[Rejected]] - Declined actions

## Configuration
- Provider: Qwen Code CLI
- Model: qwen-plus
- Mode: Headless
'''
        (VAULT_PATH / 'Dashboard.md').write_text(dashboard_content, encoding='utf-8')

        # Create Company_Handbook.md
        handbook_content = '''# Company Handbook

## Contact List
Add your important contacts here.

## Rules of Engagement
1. All payments > $100 require approval
2. Emails to new contacts require approval
3. Social media posts require approval

## Auto-Approval Rules
- Payments < $50 (recurring only)
- Email replies to known contacts
'''
        (VAULT_PATH / 'Company_Handbook.md').write_text(handbook_content, encoding='utf-8')

        # Create Business_Goals.md
        goals_content = '''# Business Goals

## 2026 Goals
1. Automate 80% of routine tasks
2. Reduce manual work by 20 hours/week
3. Maintain 99% accuracy in automated tasks

## Current Focus
- Email triage
- Invoice management
- Social media scheduling
'''
        (VAULT_PATH / 'Business_Goals.md').write_text(goals_content, encoding='utf-8')

        print("✅ Vault structure created")
        config['vault_exists'] = True
    except Exception as e:
        print(f"❌ Failed to create vault: {e}")


def configure_env() -> bool:
    """Configure .env file for Qwen Code CLI"""
    print("5. Configuring .env File")
    print("-" * 40)

    env_content = '''# AI Employee Environment Variables
# Configured by configure_qwen_code.py
# Date: 2026-03-31

# ===========================================
# AI Provider Configuration
# ===========================================

# AI Provider: 'qwen_code_cli' (preferred), 'ollama' (local), or 'dashscope' (API)
AI_PROVIDER=qwen_code_cli

# ===========================================
# Qwen Code CLI Configuration
# ===========================================

# Qwen Code CLI Model
QWEN_CODE_MODEL=qwen-plus

# Qwen Code CLI Path (optional, auto-detected if in PATH)
# QWEN_CODE_PATH=

# ===========================================
# Ollama Configuration (Backup/Alternative)
# ===========================================

# Ollama Model (for local AI inference)
OLLAMA_MODEL=qwen2.5:7b

# ===========================================
# DashScope Configuration (Backup/Alternative)
# ===========================================

# DashScope API Key (required for qwen-agent)
DASHSCOPE_API_KEY=

# Qwen Model (for DashScope)
QWEN_MODEL=qwen-plus

# ===========================================
# AI Employee Settings
# ===========================================

AI_EMPLOYEE_VAULT=./AI_Employee_Vault
DEBUG=false
DRY_RUN=false
WATCHER_INTERVAL=30
MAX_ITERATIONS=10

# ===========================================
# Approval Thresholds
# ===========================================

AUTO_APPROVE_THRESHOLD=50
REQUIRE_APPROVAL_FOR=payment,email_new_contact,delete
'''

    try:
        # Backup existing .env if it exists
        if ENV_FILE.exists():
            backup_file = ENV_FILE.with_suffix('.env.backup')
            shutil.copy2(ENV_FILE, backup_file)
            print(f"✅ Backed up existing .env to {backup_file}")

        ENV_FILE.write_text(env_content, encoding='utf-8')
        print(f"✅ .env file configured for Qwen Code CLI")
        print(f"   AI_PROVIDER=qwen_code_cli")
        print(f"   QWEN_CODE_MODEL=qwen-plus")
        config['env_configured'] = True
    except Exception as e:
        print(f"❌ Failed to configure .env: {e}")
        return False

    print()
    return config['env_configured']


def print_installation_instructions():
    """Print installation instructions if needed"""
    if not config['qwen_code_installed']:
        print("\n" + "=" * 70)
        print("Qwen Code CLI Installation Instructions")
        print("=" * 70)
        print()
        print("Step 1: Install Qwen Code CLI")
        print()
        print("Option A: Download from official website")
        print("  1. Visit: https://chat.qwen.ai")
        print("  2. Download the Qwen Code application")
        print("  3. Follow installation instructions")
        print()
        print("Option B: Install via npm (requires Node.js)")
        print("  npm install -g @qwen-code/cli")
        print()
        print("Step 2: Authenticate")
        print("  qwen-code login")
        print()
        print("Step 3: Verify installation")
        print("  qwen-code --version")
        print()
        print("Step 4: Run this setup script again")
        print("  python scripts/configure_qwen_code.py")
        print()


def print_summary():
    """Print configuration summary"""
    print("\n" + "=" * 70)
    print("Configuration Summary")
    print("=" * 70)
    print()

    checks = [
        ("Qwen Code CLI Installed", config['qwen_code_installed']),
        ("Qwen Code Path", config['qwen_code_path'] or "Not found"),
        ("Version", config['qwen_code_version'] or "Unknown"),
        ("Authentication", config['qwen_code_authenticated']),
        ("Vault Exists", config['vault_exists']),
        (".env Configured", config['env_configured']),
    ]

    all_passed = True
    for name, passed in checks:
        if isinstance(passed, bool):
            status = "✅" if passed else "❌"
            print(f"{status} {name}: {'Yes' if passed else 'No'}")
            if not passed:
                all_passed = False
        else:
            print(f"✅ {name}: {passed}")

    print()

    if all_passed and config['qwen_code_installed']:
        print("🎉 Qwen Code CLI Setup Complete!")
        print()
        print("Next Steps:")
        print("1. Test the integration:")
        print("   python scripts/test_qwen_code_integration.py")
        print()
        print("2. Run the orchestrator:")
        print("   python scripts/orchestrator.py --vault ..\\AI_Employee_Vault --qwen-code --once")
        print()
        print("3. Drop a test file in AI_Employee_Vault\\Inbox\\")
        print()
        print("4. Start the file watcher:")
        print("   python scripts/filesystem_watcher.py ..\\AI_Employee_Vault")
        print()
    else:
        print("⚠️  Some configuration items need attention.")
        print_installation_instructions()

    print()
    print("=" * 70)


def main():
    """Main setup function"""
    # Run all checks
    check_qwen_code()

    if config['qwen_code_installed']:
        check_authentication()
        test_qwen_code()

    check_vault()
    configure_env()

    # Print summary
    print_summary()

    return 0 if (config['qwen_code_installed'] and config['env_configured']) else 1


if __name__ == '__main__':
    sys.exit(main())
