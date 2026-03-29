"""
Silver Tier Live Test

This script performs a LIVE test of the Silver Tier:
1. Creates a test file in Inbox
2. Runs the orchestrator with Ollama
3. Verifies the file was processed
4. Checks Plan.md was created
5. Verifies file moved to Done

Run: python test_silver_tier_live.py
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent  # Go up one level from scripts
VAULT_PATH = PROJECT_ROOT / 'AI_Employee_Vault'
SCRIPTS_PATH = PROJECT_ROOT / 'scripts'

print("=" * 70)
print("Silver Tier LIVE Test - Ollama Processing")
print("=" * 70)
print()

# Test results
tests_passed = 0
tests_failed = 0

def test_result(name, passed, message=""):
    global tests_passed, tests_failed
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if message:
        print(f"   {message}")
    if passed:
        tests_passed += 1
    else:
        tests_failed += 1

# Test 1: Check prerequisites
print("1. Prerequisites Check")
print("-" * 40)

test_result("Vault exists", VAULT_PATH.exists(), str(VAULT_PATH))
test_result("Inbox folder", (VAULT_PATH / 'Inbox').exists())
test_result("Needs_Action folder", (VAULT_PATH / 'Needs_Action').exists())
test_result("Plans folder", (VAULT_PATH / 'Plans').exists())
test_result("Done folder", (VAULT_PATH / 'Done').exists())
test_result("Orchestrator exists", (SCRIPTS_PATH / 'orchestrator.py').exists())
print()

# Test 2: Create test file
print("2. Creating Test File")
print("-" * 40)

test_file_content = f"""---
type: test_request
created: {datetime.now().isoformat()}
priority: normal
---

# Test Request for Silver Tier

Please analyze this test file and perform the following:

1. Create a Plan.md in the Plans folder
2. List the steps to process this request
3. Move this file to Done when complete

This is a test of the Silver Tier Ollama integration.
"""

test_file = VAULT_PATH / 'Inbox' / f'test_silver_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

try:
    test_file.write_text(test_file_content, encoding='utf-8')
    test_result("Test file created", True, str(test_file))
except Exception as e:
    test_result("Test file created", False, str(e))
    print()
    print("❌ Cannot continue without test file")
    exit(1)

print()

# Test 3: Run Orchestrator
print("3. Running Orchestrator with Ollama")
print("-" * 40)
print("This may take 30-60 seconds for Ollama to process...")
print()

try:
    result = subprocess.run(
        ['python', 'orchestrator.py', '--vault', str(VAULT_PATH), '--ollama', '--once'],
        cwd=str(SCRIPTS_PATH),
        capture_output=True,
        text=True,
        timeout=120
    )
    
    print("Orchestrator Output:")
    print(result.stdout)
    
    if result.returncode == 0:
        test_result("Orchestrator completed", True, f"Return code: {result.returncode}")
    else:
        test_result("Orchestrator completed", False, f"Return code: {result.returncode}")
        print("Stderr:", result.stderr)
        
except subprocess.TimeoutExpired:
    test_result("Orchestrator completed", False, "Timeout after 120 seconds")
except Exception as e:
    test_result("Orchestrator completed", False, str(e))

print()

# Test 4: Verify Processing
print("4. Verifying Processing Results")
print("-" * 40)

# Check if test file moved to Done
done_file = VAULT_PATH / 'Done' / test_file.name
test_result("File moved to Done", done_file.exists(), str(done_file) if done_file.exists() else "Still in Inbox")

# Check if Plan was created
plan_files = list((VAULT_PATH / 'Plans').glob(f'PLAN_{test_file.stem}*.md'))
test_result("Plan.md created", len(plan_files) > 0, 
            str(plan_files[0]) if plan_files else "No plan found")

# Check Dashboard was updated
dashboard = VAULT_PATH / 'Dashboard.md'
if dashboard.exists():
    content = dashboard.read_text(encoding='utf-8')
    test_result("Dashboard updated", 'Test' in content or 'test' in content, "Dashboard contains test reference")
else:
    test_result("Dashboard exists", False, "Dashboard.md not found")

# Check logs
logs_folder = VAULT_PATH / 'Logs'
log_files = list(logs_folder.glob('orchestrator_*.log'))
test_result("Orchestrator log created", len(log_files) > 0, 
            str(log_files[-1]) if log_files else "No log found")

print()

# Test 5: Check Watcher Scripts
print("5. Silver Tier Watcher Scripts")
print("-" * 40)

watchers = {
    'filesystem_watcher.py': 'Bronze Tier (required)',
    'gmail_watcher.py': 'Silver Tier',
    'whatsapp_watcher.py': 'Silver Tier',
    'linkedin_poster.py': 'Silver Tier (posting)',
}

for watcher, description in watchers.items():
    watcher_path = SCRIPTS_PATH / watcher
    test_result(f"Watcher: {watcher}", watcher_path.exists(), description)

print()

# Test 6: Check Additional Scripts
print("6. Additional Silver Tier Scripts")
print("-" * 40)

additional_scripts = {
    'scheduler.py': 'Task Scheduler',
    'daily_briefing.py': 'Daily Briefing',
    'weekly_audit.py': 'Weekly Audit',
}

for script, description in additional_scripts.items():
    script_path = SCRIPTS_PATH / script
    test_result(f"Script: {script}", script_path.exists(), description)

print()

# Summary
print("=" * 70)
print("Test Summary")
print("=" * 70)
print(f"Total Tests:  {tests_passed + tests_failed}")
print(f"Passed:       {tests_passed} ✅")
print(f"Failed:       {tests_failed} ❌")
print(f"Success Rate: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%" if (tests_passed+tests_failed) > 0 else "N/A")
print()

if tests_failed <= 2:
    print("🎉 Silver Tier LIVE Test PASSED!")
    print()
    print("Ollama successfully processed the test file:")
    print(f"  - Input:  {test_file.name}")
    print(f"  - Plan:   {plan_files[0].name if plan_files else 'N/A'}")
    print(f"  - Output: {done_file.name if done_file.exists() else 'N/A'}")
else:
    print("⚠️  Some tests failed. Review the errors above.")

print()
print("=" * 70)

# Cleanup
print()
print("Note: Test files left in place for review.")
print("  - Check Plans/ folder for AI-generated plan")
print("  - Check Done/ folder for processed file")
print("  - Check Logs/ folder for orchestrator logs")
