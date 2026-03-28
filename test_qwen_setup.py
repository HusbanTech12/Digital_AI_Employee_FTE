"""
Test script for Qwen Agent setup

This script verifies that qwen-agent is properly installed and configured.
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import qwen_agent
        print(f"  ✓ qwen_agent: v{qwen_agent.__version__}")
    except ImportError as e:
        print(f"  ✗ qwen_agent: {e}")
        return False
    
    try:
        import dashscope
        print(f"  ✓ dashscope: installed")
    except ImportError as e:
        print(f"  ✗ dashscope: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print(f"  ✓ python-dotenv: installed")
    except ImportError as e:
        print(f"  ✗ python-dotenv: {e}")
        return False
    
    return True


def test_config():
    """Test that configuration can be loaded."""
    print("\nTesting configuration...")
    
    try:
        from qwen_agent_config import AI_EMPLOYEE_CONFIG, FOLDERS, RULES
        print(f"  ✓ Configuration loaded")
        print(f"    - Model: {AI_EMPLOYEE_CONFIG['model']}")
        print(f"    - Vault: {AI_EMPLOYEE_CONFIG['vault_path']}")
        print(f"    - Skills: {AI_EMPLOYEE_CONFIG['skills_directory']}")
        return True
    except Exception as e:
        print(f"  ✗ Configuration: {e}")
        return False


def test_vault_structure():
    """Test that vault structure exists."""
    print("\nTesting vault structure...")
    
    vault_path = Path('./AI_Employee_Vault')
    if not vault_path.exists():
        print(f"  ✗ Vault not found: {vault_path}")
        return False
    
    print(f"  ✓ Vault found: {vault_path}")
    
    required_folders = ['Inbox', 'Needs_Action', 'Plans', 'Done', 
                       'Pending_Approval', 'Approved', 'Rejected', 'Logs']
    
    all_exist = True
    for folder in required_folders:
        folder_path = vault_path / folder
        if folder_path.exists():
            print(f"    ✓ {folder}/")
        else:
            print(f"    ✗ {folder}/ - MISSING")
            all_exist = False
    
    return all_exist


def test_api_key():
    """Test if API key is configured."""
    print("\nTesting API configuration...")
    
    api_key = os.environ.get('DASHSCOPE_API_KEY')
    if api_key:
        print(f"  ✓ DASHSCOPE_API_KEY is set")
        print(f"    (key starts with: {api_key[:8]}...)")
        return True
    else:
        print(f"  ⚠ DASHSCOPE_API_KEY not set")
        print(f"    Set it with: set DASHSCOPE_API_KEY=your_key")
        print(f"    Or create a .env file from .env.example")
        return False


def test_agent_creation():
    """Test that an agent can be created (requires API key)."""
    print("\nTesting agent creation...")
    
    api_key = os.environ.get('DASHSCOPE_API_KEY')
    if not api_key:
        print(f"  ⊘ Skipped (no API key)")
        return True
    
    try:
        from qwen_agent_config import create_ai_employee_agent
        agent = create_ai_employee_agent()
        print(f"  ✓ Agent created successfully")
        return True
    except Exception as e:
        print(f"  ✗ Agent creation: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Qwen Agent Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Vault Structure", test_vault_structure()))
    results.append(("API Key", test_api_key()))
    results.append(("Agent Creation", test_agent_creation()))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! Qwen Agent is ready to use.")
        print("\nNext steps:")
        print("1. Set DASHSCOPE_API_KEY environment variable")
        print("2. Run: python scripts/orchestrator.py --once")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
