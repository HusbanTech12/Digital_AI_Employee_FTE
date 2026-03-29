"""
Test Script for Silver Tier Ollama + Qwen-Agent Integration

This script tests the complete integration of Ollama and qwen-agent
in the Silver Tier architecture.

Run: python test_ollama_integration.py
"""

import sys
import os
from pathlib import Path

# Get project root (parent of scripts directory)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    print("⚠️  python-dotenv not installed")
    pass

print("=" * 70)
print("Silver Tier: Ollama + Qwen-Agent Integration Test")
print("=" * 70)
print()

# Test results tracking
tests_passed = 0
tests_failed = 0
tests_total = 0

def test_result(name, passed, message=""):
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if message:
        print(f"   {message}")
    if passed:
        tests_passed += 1
    else:
        tests_failed += 1

# Test 1: Environment Variables
print("1. Environment Configuration")
print("-" * 40)
ai_provider = os.environ.get('AI_PROVIDER', 'ollama')
ollama_model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:7b')
dashscope_key = os.environ.get('DASHSCOPE_API_KEY')

test_result("AI_PROVIDER set", ai_provider in ['ollama', 'dashscope'], f"Value: {ai_provider}")
test_result("OLLAMA_MODEL set", ollama_model is not None, f"Value: {ollama_model}")
test_result("DASHSCOPE_API_KEY available", dashscope_key is not None, "Optional for Ollama mode")
print()

# Test 2: Python Packages
print("2. Python Package Imports")
print("-" * 40)

try:
    import ollama
    test_result("ollama package", True, f"Version: {ollama.__version__ if hasattr(ollama, '__version__') else 'unknown'}")
except ImportError as e:
    test_result("ollama package", False, str(e))

try:
    from qwen_agent.agent import Agent
    test_result("qwen-agent package", True, "Available")
except ImportError as e:
    test_result("qwen-agent package", False, str(e))

try:
    from dotenv import load_dotenv
    test_result("python-dotenv package", True, "Available")
except ImportError as e:
    test_result("python-dotenv package", False, str(e))

try:
    import watchdog
    test_result("watchdog package", True, "Available")
except ImportError as e:
    test_result("watchdog package", False, str(e))

print()

# Test 3: Ollama Service
print("3. Ollama Service Test")
print("-" * 40)

try:
    import ollama
    models = ollama.list()
    if models and 'models' in models:
        model_names = [m['name'] for m in models['models']]
        test_result("Ollama service running", True, f"Models available: {len(model_names)}")
        test_result(f"Model '{ollama_model}' installed", ollama_model in model_names, f"Installed: {', '.join(model_names)}")
    else:
        test_result("Ollama service running", False, "No models found")
except Exception as e:
    test_result("Ollama service running", False, str(e))

print()

# Test 4: Qwen Agent Config
print("4. Qwen Agent Configuration")
print("-" * 40)

try:
    from qwen_agent_config import QwenAgentProvider, OLLAMA_AVAILABLE, QWEN_AGENT_AVAILABLE
    
    test_result("qwen_agent_config imports", True, "Module loaded")
    test_result("OLLAMA_AVAILABLE", OLLAMA_AVAILABLE, "Ollama support ready")
    test_result("QWEN_AGENT_AVAILABLE", QWEN_AGENT_AVAILABLE, "DashScope support ready")
    
    # Test provider initialization
    provider = QwenAgentProvider(provider='ollama')
    test_result("QwenAgentProvider init", True, f"Provider: {provider.provider}")
    
except Exception as e:
    test_result("qwen_agent_config", False, str(e))

print()

# Test 5: Orchestrator
print("5. Orchestrator Module")
print("-" * 40)

try:
    from orchestrator import Orchestrator, OLLAMA_AVAILABLE as ORCH_OLLAMA_AVAIL
    
    test_result("orchestrator imports", True, "Module loaded")
    
    # Check vault path - use PROJECT_ROOT
    vault_path = PROJECT_ROOT / 'AI_Employee_Vault'
    test_result("Vault folder exists", vault_path.exists(), f"Path: {vault_path}")
    
    # Test orchestrator initialization
    if vault_path.exists():
        orchestrator = Orchestrator(vault_path=str(vault_path), ai_provider='ollama')
        test_result("Orchestrator init", True, f"Provider: {orchestrator.ai_provider}")
        test_result("Needs_Action folder", orchestrator.needs_action.exists(), "Folder exists")
        test_result("Plans folder", orchestrator.plans.exists(), "Folder exists")
        test_result("Done folder", orchestrator.done.exists(), "Folder exists")
    else:
        test_result("Vault folder exists", False, "Create vault first")
    
except Exception as e:
    test_result("orchestrator", False, str(e))

print()

# Test 6: Ollama Chat Test
print("6. Ollama Chat Test (Live)")
print("-" * 40)

try:
    import ollama
    
    test_prompt = "Respond with exactly one word: READY"
    response = ollama.chat(model=ollama_model, messages=[
        {'role': 'user', 'content': test_prompt}
    ])
    
    content = response['message']['content']
    test_result("Ollama chat response", True, f"Response: {content[:50]}...")
    
    # Check if response is reasonable
    test_result("Response quality", len(content) > 0 and len(content) < 200, "Response length OK")
    
except Exception as e:
    test_result("Ollama chat", False, str(e))

print()

# Test 7: Vault Structure
print("7. Vault Structure")
print("-" * 40)

vault_path = PROJECT_ROOT / 'AI_Employee_Vault'

if vault_path.exists():
    required_folders = [
        'Inbox',
        'Needs_Action',
        'Plans',
        'Done',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Logs',
        'Files'
    ]
    
    for folder in required_folders:
        folder_path = vault_path / folder
        exists = folder_path.exists()
        test_result(f"Folder: {folder}", exists, "Exists" if exists else "Missing")
    
    # Check required files
    required_files = ['Dashboard.md', 'Company_Handbook.md', 'Business_Goals.md']
    for file in required_files:
        file_path = vault_path / file
        exists = file_path.exists()
        test_result(f"File: {file}", exists, "Exists" if exists else "Missing")
else:
    test_result("Vault exists", False, "Create vault folder first")

print()

# Test 8: Watcher Scripts
print("8. Watcher Scripts")
print("-" * 40)

watcher_scripts = [
    'filesystem_watcher.py',
    'gmail_watcher.py',
    'whatsapp_watcher.py',
    'linkedin_poster.py'
]

for script in watcher_scripts:
    script_path = Path(__file__).parent / script
    exists = script_path.exists()
    test_result(f"Script: {script}", exists, "Exists" if exists else "Missing")

print()

# Summary
print("=" * 70)
print("Test Summary")
print("=" * 70)
print(f"Total Tests:  {tests_total}")
print(f"Passed:       {tests_passed} ✅")
print(f"Failed:       {tests_failed} ❌")
print(f"Success Rate: {(tests_passed/tests_total*100):.1f}%" if tests_total > 0 else "N/A")
print()

if tests_failed == 0:
    print("🎉 All tests passed! Silver Tier integration is complete.")
    print()
    print("Next steps:")
    print("1. Drop a test file in AI_Employee_Vault/Inbox/")
    print("2. Run: python scripts/orchestrator.py --vault ..\\AI_Employee_Vault --ollama --once")
    print("3. Check AI_Employee_Vault/Done/ for processed files")
else:
    print("⚠️  Some tests failed. Review the errors above.")
    print()
    if "ollama" in str(tests_failed).lower():
        print("Ollama issues:")
        print("  - Install: pip install ollama")
        print("  - Download model: ollama pull qwen2.5:7b")
        print("  - Start service: ollama serve")

print()
print("=" * 70)

# Exit with appropriate code
sys.exit(0 if tests_failed == 0 else 1)
