"""
Ollama Configuration Script for Silver & Gold Tiers

This script:
1. Verifies Ollama installation
2. Checks installed models
3. Tests Ollama connectivity
4. Configures .env file
5. Validates Silver and Gold tier setup

Run: python configure_ollama_tiers.py
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, Dict, List

# Project root
PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / '.env'
VAULT_PATH = PROJECT_ROOT / 'AI_Employee_Vault'

print("=" * 70)
print("Ollama Configuration for Silver & Gold Tiers")
print("=" * 70)
print()

# Configuration storage
config = {
    'ollama_installed': False,
    'ollama_version': '',
    'models': [],
    'default_model': '',
    'env_configured': False,
    'vault_exists': False,
}

def run_command(cmd: List[str]) -> tuple:
    """Run command and return (success, output)"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def check_ollama() -> bool:
    """Check if Ollama is installed"""
    print("1. Checking Ollama Installation")
    print("-" * 40)
    
    success, output = run_command(['ollama', '--version'])
    if success:
        config['ollama_installed'] = True
        config['ollama_version'] = output
        print(f"✅ Ollama is installed")
        print(f"   Version: {output}")
    else:
        print(f"❌ Ollama is not installed")
        print(f"   Download from: https://ollama.com/download")
    print()
    return config['ollama_installed']

def list_models() -> List[str]:
    """List installed Ollama models"""
    print("2. Installed Ollama Models")
    print("-" * 40)
    
    if not config['ollama_installed']:
        print("⚠️  Ollama not installed, skipping model check")
        return []
    
    success, output = run_command(['ollama', 'list'])
    if success and output:
        # Parse model list
        lines = output.split('\n')[1:]  # Skip header
        models = []
        for line in lines:
            if line.strip():
                parts = line.split()
                if parts:
                    model_name = parts[0]
                    models.append(model_name)
        
        config['models'] = models
        
        if models:
            print(f"✅ Found {len(models)} model(s):")
            for model in models:
                print(f"   - {model}")
            
            # Set default model
            if 'qwen2.5:7b' in models:
                config['default_model'] = 'qwen2.5:7b'
            elif 'qwen2.5:1.5b' in models:
                config['default_model'] = 'qwen2.5:1.5b'
            elif 'qwen2.5:3b' in models:
                config['default_model'] = 'qwen2.5:3b'
            else:
                config['default_model'] = models[0]
        else:
            print("⚠️  No models installed")
    else:
        print("❌ Could not list models")
    
    print()
    return config['models']

def test_model(model: str) -> bool:
    """Test a specific model"""
    print(f"3. Testing Model: {model}")
    print("-" * 40)
    
    if not config['ollama_installed']:
        print("❌ Ollama not installed")
        return False
    
    prompt = "Say 'Ollama is working!' in exactly 3 words."
    success, output = run_command(['ollama', 'run', model, prompt])
    
    if success:
        print(f"✅ Model '{model}' is working")
        print(f"   Response: {output[:100]}...")
    else:
        print(f"❌ Model '{model}' test failed")
        print(f"   Error: {output}")
    
    print()
    return success

def check_vault() -> bool:
    """Check if vault exists"""
    print("4. Checking Vault Structure")
    print("-" * 40)
    
    if VAULT_PATH.exists():
        config['vault_exists'] = True
        print(f"✅ Vault exists: {VAULT_PATH}")
        
        # Check required folders
        required_folders = ['Inbox', 'Needs_Action', 'Plans', 'Done', 'Pending_Approval', 'Approved', 'Rejected', 'Logs']
        missing = []
        for folder in required_folders:
            if not (VAULT_PATH / folder).exists():
                missing.append(folder)
        
        if missing:
            print(f"⚠️  Missing folders: {', '.join(missing)}")
        else:
            print(f"✅ All required folders exist")
        
        # Check required files
        required_files = ['Dashboard.md', 'Company_Handbook.md', 'Business_Goals.md']
        missing_files = []
        for file in required_files:
            if not (VAULT_PATH / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"⚠️  Missing files: {', '.join(missing_files)}")
        else:
            print(f"✅ All required files exist")
    else:
        print(f"❌ Vault does not exist: {VAULT_PATH}")
        print(f"   Creating vault structure...")
        create_vault()
    
    print()
    return config['vault_exists']

def create_vault():
    """Create vault structure"""
    try:
        VAULT_PATH.mkdir(parents=True, exist_ok=True)
        
        folders = ['Inbox', 'Needs_Action', 'Plans', 'Done', 'Pending_Approval', 'Approved', 'Rejected', 'Logs', 'Files', 'Briefings', 'Audits']
        for folder in folders:
            (VAULT_PATH / folder).mkdir(parents=True, exist_ok=True)
        
        # Create Dashboard.md
        dashboard_content = '''---
last_updated: 2026-03-29T00:00:00Z
status: active
tier: silver
---

# AI Employee Dashboard

## Status
- **Tier:** Silver
- **AI Provider:** Ollama
- **Status:** Active

## Quick Stats
- Tasks Pending: 0
- Tasks Completed: 0
- Last Activity: N/A

## Recent Activity
- System initialized

## Folders
- [[Inbox]] - Drop files here
- [[Needs_Action]] - Items to process
- [[Plans]] - Action plans
- [[Done]] - Completed tasks
- [[Pending_Approval]] - Awaiting approval
- [[Approved]] - Ready to execute
- [[Rejected]] - Declined actions

## Configuration
- Model: qwen2.5:1.5b
- Provider: Ollama (Local)
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
        
        print(f"✅ Vault structure created")
        config['vault_exists'] = True
    except Exception as e:
        print(f"❌ Failed to create vault: {e}")

def configure_env() -> bool:
    """Configure .env file"""
    print("5. Configuring .env File")
    print("-" * 40)
    
    if not config['default_model']:
        config['default_model'] = 'qwen2.5:1.5b'
    
    env_content = f'''# AI Employee Environment Variables
# Configured by configure_ollama_tiers.py
# Date: 2026-03-29

# ===========================================
# AI Provider Configuration
# ===========================================

# AI Provider: 'ollama' (local/free) or 'dashscope' (cloud/api)
AI_PROVIDER=ollama

# Ollama Model
OLLAMA_MODEL={config['default_model']}

# ===========================================
# DashScope Configuration (Optional)
# ===========================================
DASHSCOPE_API_KEY=
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

# ===========================================
# Gold Tier Settings
# ===========================================
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=

ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=
'''
    
    try:
        ENV_FILE.write_text(env_content, encoding='utf-8')
        print(f"✅ .env file configured")
        print(f"   AI_PROVIDER=ollama")
        print(f"   OLLAMA_MODEL={config['default_model']}")
        config['env_configured'] = True
    except Exception as e:
        print(f"❌ Failed to configure .env: {e}")
    
    print()
    return config['env_configured']

def recommend_models():
    """Recommend better models"""
    print("6. Model Recommendations")
    print("-" * 40)
    
    current = config['default_model']
    print(f"Current model: {current}")
    print()
    
    if current == 'qwen2.5:1.5b':
        print("💡 Recommendation: Upgrade to qwen2.5:7b for better quality")
        print()
        print("To upgrade, run:")
        print("  ollama pull qwen2.5:7b")
        print()
        print("Then update .env:")
        print("  OLLAMA_MODEL=qwen2.5:7b")
        print()
        print("Model Comparison:")
        print("  qwen2.5:1.5b - 1GB RAM, Fast, Basic quality (current)")
        print("  qwen2.5:7b   - 4GB RAM, Medium, Better quality (recommended)")
        print("  qwen2.5:14b  - 8GB RAM, Slow, Best quality")
    else:
        print(f"✅ You're using {current}, which is a good model!")
    
    print()

def check_tier_requirements(tier: str) -> Dict:
    """Check requirements for specific tier"""
    print(f"7. Checking {tier} Tier Requirements")
    print("-" * 40)
    
    scripts_path = PROJECT_ROOT / 'scripts'
    requirements = {
        'orchestrator': False,
        'watchers': [],
        'skills': [],
        'mcp_servers': [],
    }
    
    # Check orchestrator
    if (scripts_path / 'orchestrator.py').exists():
        requirements['orchestrator'] = True
        print(f"✅ orchestrator.py exists")
    else:
        print(f"❌ orchestrator.py missing")
    
    # Check watchers
    watchers = {
        'Silver': ['filesystem_watcher.py', 'gmail_watcher.py', 'whatsapp_watcher.py', 'linkedin_poster.py'],
        'Gold': ['filesystem_watcher.py', 'gmail_watcher.py', 'whatsapp_watcher.py', 'linkedin_poster.py', 'facebook_instagram_watcher.py', 'twitter_watcher.py']
    }
    
    for watcher in watchers.get(tier, []):
        if (scripts_path / watcher).exists():
            requirements['watchers'].append(watcher)
            print(f"✅ {watcher} exists")
        else:
            print(f"⚠️  {watcher} missing")
    
    # Check MCP servers for Gold tier
    if tier == 'Gold':
        mcp_path = PROJECT_ROOT / 'mcp-servers'
        if mcp_path.exists():
            print(f"✅ mcp-servers folder exists")
            requirements['mcp_servers'] = list(mcp_path.iterdir())
        else:
            print(f"⚠️  mcp-servers folder missing")
    
    print()
    return requirements

def print_summary():
    """Print configuration summary"""
    print("=" * 70)
    print("Configuration Summary")
    print("=" * 70)
    print()
    
    checks = [
        ("Ollama Installed", config['ollama_installed']),
        ("Ollama Version", config['ollama_version'] if config['ollama_installed'] else False),
        ("Models Available", len(config['models']) > 0),
        ("Default Model", config['default_model']),
        ("Vault Exists", config['vault_exists']),
        (".env Configured", config['env_configured']),
    ]
    
    all_passed = True
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {passed if isinstance(passed, str) else 'Yes' if passed else 'No'}")
        if not passed and isinstance(passed, bool):
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 Configuration Complete!")
        print()
        print("Next Steps:")
        print("1. Test the system:")
        print("   python scripts\\test_ollama_integration.py")
        print()
        print("2. Run the orchestrator:")
        print("   python scripts\\orchestrator.py --vault ..\\AI_Employee_Vault --ollama --once")
        print()
        print("3. Drop a test file in AI_Employee_Vault\\Inbox\\")
        print()
        print("4. For Gold Tier, setup MCP servers:")
        print("   cd mcp-servers\\email-mcp")
        print("   npm install")
    else:
        print("⚠️  Some configuration items need attention.")
        print("   Review the errors above and fix them.")
    
    print()
    print("=" * 70)

def main():
    """Main configuration function"""
    # Run all checks
    check_ollama()
    list_models()
    
    if config['models']:
        test_model(config['default_model'])
    
    check_vault()
    configure_env()
    recommend_models()
    
    # Check tier requirements
    check_tier_requirements('Silver')
    check_tier_requirements('Gold')
    
    # Print summary
    print_summary()
    
    return 0 if all([
        config['ollama_installed'],
        config['models'],
        config['vault_exists'],
        config['env_configured']
    ]) else 1

if __name__ == '__main__':
    sys.exit(main())
