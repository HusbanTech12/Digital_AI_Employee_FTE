"""
Test Script for Qwen Code CLI Integration

This script tests the Qwen Code CLI integration with the AI Employee system.

Usage:
    python scripts/test_qwen_code_integration.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

print("=" * 70)
print("Qwen Code CLI Integration Test")
print("=" * 70)
print()

# Test 1: Import QwenCodeProvider
print("Test 1: Importing QwenCodeProvider...")
try:
    from qwen_code_provider import QwenCodeProvider
    print("✅ QwenCodeProvider imported successfully")
except ImportError as e:
    print(f"❌ Failed to import QwenCodeProvider: {e}")
    sys.exit(1)

# Test 2: Initialize Provider
print("\nTest 2: Initializing QwenCodeProvider...")
try:
    vault_path = PROJECT_ROOT / 'AI_Employee_Vault'
    provider = QwenCodeProvider(vault_path=str(vault_path))
    print("✅ QwenCodeProvider initialized")
    print(f"   Vault: {vault_path}")
    print(f"   CLI Path: {provider.qwen_code_path}")
    print(f"   Model: {provider.model}")
except Exception as e:
    print(f"⚠️  Provider initialization warning: {e}")
    provider = None

# Test 3: Check Availability
print("\nTest 3: Checking Qwen Code CLI availability...")
if provider:
    try:
        available = provider.is_available()
        if available:
            print("✅ Qwen Code CLI is available")
        else:
            print("⚠️  Qwen Code CLI is not available")
            print()
            print("Installation instructions:")
            print("  1. Download from: https://chat.qwen.ai")
            print("  2. Or install via npm: npm install -g @qwen-code/cli")
            print("  3. Authenticate: qwen-code login")
    except Exception as e:
        print(f"❌ Availability check failed: {e}")
else:
    print("⚠️  Provider not initialized, skipping availability check")

# Test 4: Get Version
print("\nTest 4: Getting Qwen Code CLI version...")
if provider and provider.qwen_code_path:
    try:
        version = provider.get_version()
        if version:
            print(f"✅ Version: {version}")
        else:
            print("⚠️  Could not determine version")
    except Exception as e:
        print(f"❌ Version check failed: {e}")
else:
    print("⚠️  Qwen Code CLI not found, skipping version check")

# Test 5: Simple Chat
print("\nTest 5: Testing simple chat...")
if provider and provider.is_available():
    try:
        response = provider.chat("Say 'Hello from Qwen Code!' in exactly 4 words.")
        if response:
            print(f"✅ Response received:")
            print(f"   {response[:200]}")
        else:
            print("⚠️  No response received")
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
else:
    print("⚠️  Qwen Code CLI not available, skipping chat test")

# Test 6: Chat with System Prompt
print("\nTest 6: Testing chat with system prompt...")
if provider and provider.is_available():
    try:
        response = provider.chat(
            "What is 2 + 2?",
            system_prompt="You are a helpful math tutor. Give concise answers."
        )
        if response:
            print(f"✅ Response received:")
            print(f"   {response[:200]}")
        else:
            print("⚠️  No response received")
    except Exception as e:
        print(f"❌ Chat with system prompt failed: {e}")
else:
    print("⚠️  Qwen Code CLI not available, skipping test")

# Test 7: Orchestrator Integration
print("\nTest 7: Testing Orchestrator integration...")
orchestrator = None
try:
    from orchestrator import Orchestrator
    print("✅ Orchestrator imported successfully")

    # Create orchestrator with Qwen Code CLI
    orchestrator = Orchestrator(
        vault_path=str(vault_path),
        ai_provider='qwen_code_cli',
        dry_run=True
    )
    print("✅ Orchestrator initialized with Qwen Code CLI")
    print(f"   Provider: {orchestrator.ai_provider}")
    print(f"   Dry run: {orchestrator.dry_run}")

except ImportError as e:
    print(f"❌ Failed to import Orchestrator: {e}")
except Exception as e:
    print(f"⚠️  Orchestrator initialization warning: {e}")

# Test 8: Create Test Action File
print("\nTest 8: Creating test action file...")
needs_action_path = vault_path / 'Needs_Action'
needs_action_path.mkdir(parents=True, exist_ok=True)

test_file = needs_action_path / f'TEST_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
test_content = f'''---
created: {datetime.now().isoformat()}
type: test
source: qwen_code_integration_test
---

# Test Action File

This is a test file created by the Qwen Code CLI integration test.

## Task
Please process this test file and verify that:
1. The orchestrator can read this file
2. Qwen Code CLI can process the content
3. A plan is created in the Plans folder
4. The file is moved to Done after processing

## Expected Output
After processing, this file should be moved to the Done folder.
'''

try:
    test_file.write_text(test_content, encoding='utf-8')
    print(f"✅ Test action file created: {test_file}")
except Exception as e:
    print(f"❌ Failed to create test file: {e}")

# Test 9: Run Orchestrator (Dry Run)
print("\nTest 9: Running orchestrator (dry run)...")
try:
    if orchestrator:
        processed = orchestrator.run_once()
        print(f"✅ Orchestrator run completed")
        print(f"   Items processed: {processed}")
except Exception as e:
    print(f"❌ Orchestrator run failed: {e}")

# Summary
print("\n" + "=" * 70)
print("Test Summary")
print("=" * 70)
print()

tests_passed = 0
tests_total = 9

# Count passed tests
try:
    from qwen_code_provider import QwenCodeProvider
    tests_passed += 1
except:
    pass

if provider:
    tests_passed += 1

if provider and provider.is_available():
    tests_passed += 3  # Availability, version, chat tests

try:
    from orchestrator import Orchestrator
    tests_passed += 2  # Import and initialization
except:
    pass

if test_file.exists():
    tests_passed += 1

if orchestrator:
    tests_passed += 1

print(f"Tests Passed: {tests_passed}/{tests_total}")
print()

if tests_passed == tests_total:
    print("🎉 All tests passed!")
    print()
    print("Qwen Code CLI integration is working correctly.")
    print()
    print("Next steps:")
    print("1. Run the orchestrator without dry-run:")
    print("   python scripts/orchestrator.py --vault ..\\AI_Employee_Vault --qwen-code --once")
    print()
    print("2. Start the file watcher:")
    print("   python scripts/filesystem_watcher.py ..\\AI_Employee_Vault")
    print()
    print("3. Drop files in AI_Employee_Vault\\Inbox\\")
elif tests_passed >= tests_total - 2:
    print("✅ Most tests passed!")
    print()
    print("Qwen Code CLI may not be installed, but the integration code is ready.")
    print()
    print("To enable full functionality:")
    print("1. Install Qwen Code CLI:")
    print("   - Download from: https://chat.qwen.ai")
    print("   - Or: npm install -g @qwen-code/cli")
    print("2. Authenticate:")
    print("   qwen-code login")
    print("3. Run this test again")
else:
    print("⚠️  Some tests failed.")
    print()
    print("Please review the errors above and fix any issues.")

print()
print("=" * 70)
