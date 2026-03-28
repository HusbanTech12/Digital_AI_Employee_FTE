# AI Employee - Bronze Tier Verification Script
# Run this to verify your setup is complete

import sys
import os
from pathlib import Path

def check_mark(color, message):
    print(f"✓ {message}")

def cross_mark(message):
    print(f"✗ {message}")

def main():
    print("=" * 60)
    print("AI Employee - Bronze Tier Verification")
    print("=" * 60)
    print()
    
    # Get base directory
    base_dir = Path(__file__).parent
    vault_dir = base_dir / "AI_Employee_Vault"
    scripts_dir = base_dir / "scripts"
    skills_dir = base_dir / "skills"
    
    all_passed = True
    
    # Check Python version
    print("1. Python Version")
    print("-" * 40)
    if sys.version_info >= (3, 10):
        check_mark(True, f"Python {sys.version_info.major}.{sys.version_info.minor} found")
    else:
        cross_mark(f"Python 3.10+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        all_passed = False
    print()
    
    # Check vault structure
    print("2. Vault Structure")
    print("-" * 40)
    required_folders = [
        "Inbox", "Needs_Action", "Plans", "Done",
        "Pending_Approval", "Approved", "Rejected",
        "Logs", "Files", "Invoices", "Briefings"
    ]
    
    for folder in required_folders:
        folder_path = vault_dir / folder
        if folder_path.exists() and folder_path.is_dir():
            check_mark(True, f"{folder}/")
        else:
            cross_mark(f"{folder}/ - MISSING")
            all_passed = False
    print()
    
    # Check vault files
    print("3. Vault Files")
    print("-" * 40)
    required_files = [
        "Dashboard.md",
        "Company_Handbook.md",
        "Business_Goals.md"
    ]
    
    for file in required_files:
        file_path = vault_dir / file
        if file_path.exists():
            check_mark(True, f"{file}")
        else:
            cross_mark(f"{file} - MISSING")
            all_passed = False
    print()
    
    # Check scripts
    print("4. Python Scripts")
    print("-" * 40)
    required_scripts = [
        "base_watcher.py",
        "filesystem_watcher.py",
        "orchestrator.py",
        "requirements.txt"
    ]
    
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            check_mark(True, f"{script}")
        else:
            cross_mark(f"{script} - MISSING")
            all_passed = False
    print()
    
    # Test script imports
    print("5. Script Imports")
    print("-" * 40)
    try:
        sys.path.insert(0, str(scripts_dir))
        from base_watcher import BaseWatcher
        check_mark(True, "base_watcher.py imports correctly")
    except Exception as e:
        cross_mark(f"base_watcher.py import failed: {e}")
        all_passed = False
    
    try:
        from filesystem_watcher import FilesystemWatcher
        check_mark(True, "filesystem_watcher.py imports correctly")
    except Exception as e:
        cross_mark(f"filesystem_watcher.py import failed: {e}")
        all_passed = False
    
    try:
        from orchestrator import Orchestrator
        check_mark(True, "orchestrator.py imports correctly")
    except Exception as e:
        cross_mark(f"orchestrator.py import failed: {e}")
        all_passed = False
    print()
    
    # Check skills
    print("6. Agent Skills")
    print("-" * 40)
    required_skills = [
        "SKILL.md",
        "file-processor/SKILL.md",
        "task-manager/SKILL.md",
        "dashboard-updater/SKILL.md",
        "approval-handler/SKILL.md"
    ]
    
    for skill in required_skills:
        skill_path = skills_dir / skill
        if skill_path.exists():
            check_mark(True, f"{skill}")
        else:
            cross_mark(f"{skill} - MISSING")
            all_passed = False
    print()
    
    # Check configuration files
    print("7. Configuration Files")
    print("-" * 40)
    config_files = [
        "README.md",
        "QWEN_CONFIG.md",
        ".gitignore"
    ]
    
    for config in config_files:
        config_path = base_dir / config
        if config_path.exists():
            check_mark(True, f"{config}")
        else:
            cross_mark(f"{config} - MISSING")
            all_passed = False
    print()
    
    # Check Qwen availability
    print("8. Qwen Code Check")
    print("-" * 40)
    import subprocess
    try:
        result = subprocess.run(["qwen", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            check_mark(True, f"Qwen Code found: {result.stdout.strip()}")
        else:
            cross_mark("Qwen Code not found - will need installation")
            print("  Install with: pip install qwen-agent")
    except FileNotFoundError:
        cross_mark("Qwen Code not found in PATH")
        print("  Install with: pip install qwen-agent")
        print("  Or see QWEN_CONFIG.md for setup options")
    except Exception as e:
        cross_mark(f"Qwen check failed: {e}")
    print()
    
    # Final summary
    print("=" * 60)
    if all_passed:
        print("✓ All checks passed! Your Bronze Tier setup is complete.")
        print()
        print("Next steps:")
        print("1. Install Qwen Code: pip install qwen-agent")
        print("2. Open AI_Employee_Vault in Obsidian")
        print("3. Run: python scripts/filesystem_watcher.py")
        print("4. Drop a file in AI_Employee_Vault/Inbox/")
        print("5. Run: python scripts/orchestrator.py --once")
    else:
        print("✗ Some checks failed. Please review the output above.")
        print()
        print("Common fixes:")
        print("- Run: pip install -r scripts/requirements.txt")
        print("- Check that all folders exist in AI_Employee_Vault/")
        print("- Ensure scripts are in the scripts/ folder")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
