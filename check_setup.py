"""
AI Employee - Complete Setup Verification Script

This script verifies that everything is set up correctly for using Ollama
with the AI Employee system.
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_check(name, status, details=""):
    symbol = "✓" if status else "✗"
    status_text = "PASS" if status else "FAIL"
    print(f"  {symbol} {name}: {status_text}")
    if details:
        print(f"    → {details}")

def check_python():
    """Check Python version."""
    print_header("Step 1: Python Check")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print_check("Python Version", True, f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_check("Python Version", False, f"Python {version.major}.{version.minor} (need 3.10+)")
        return False

def check_packages():
    """Check required Python packages."""
    print_header("Step 2: Python Packages Check")
    
    packages = {
        'ollama': 'Ollama Python client',
        'dotenv': 'Environment variable support',
    }
    
    all_ok = True
    for package, name in packages.items():
        try:
            __import__(package)
            print_check(name, True, f"{package} installed")
        except ImportError:
            print_check(name, False, f"{package} not found")
            all_ok = False
    
    return all_ok

def check_ollama():
    """Check if Ollama is installed and running."""
    print_header("Step 3: Ollama Check")
    
    # Check if Ollama command exists
    try:
        result = subprocess.run(
            ['ollama', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_check("Ollama CLI", True, result.stdout.strip())
            ollama_installed = True
        else:
            print_check("Ollama CLI", False, "Command not found")
            ollama_installed = False
    except FileNotFoundError:
        print_check("Ollama CLI", False, "Not installed")
        print("\n  Install Ollama from: https://ollama.com/download")
        print("  1. Download OllamaSetup.exe")
        print("  2. Run the installer")
        print("  3. Open NEW Command Prompt")
        print("  4. Run: ollama --version")
        ollama_installed = False
    
    # Check if Ollama service is running
    if ollama_installed:
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print_check("Ollama Service", True, "Running")
                
                # Check for models
                if 'qwen' in result.stdout.lower():
                    print_check("Qwen Model", True, "Installed")
                    return True
                else:
                    print_check("Qwen Model", False, "Not downloaded")
                    print("\n  Download Qwen model with:")
                    print("  ollama pull qwen2.5:7b")
                    return False
            else:
                print_check("Ollama Service", False, "Not running")
                print("\n  Start Ollama service:")
                print("  ollama serve")
                return False
        except Exception as e:
            print_check("Ollama Service", False, str(e))
            return False
    
    return False

def check_vault():
    """Check AI Employee vault structure."""
    print_header("Step 4: Vault Structure Check")
    
    vault_path = Path('./AI_Employee_Vault')
    if not vault_path.exists():
        print_check("Vault Folder", False, "Not found")
        return False
    
    print_check("Vault Folder", True, str(vault_path))
    
    required_folders = [
        'Inbox', 'Needs_Action', 'Plans', 'Done',
        'Pending_Approval', 'Approved', 'Rejected', 'Logs'
    ]
    
    all_ok = True
    for folder in required_folders:
        folder_path = vault_path / folder
        if folder_path.exists():
            print_check(f"  {folder}/", True)
        else:
            print_check(f"  {folder}/", False)
            all_ok = False
    
    required_files = ['Dashboard.md', 'Company_Handbook.md', 'Business_Goals.md']
    for file in required_files:
        file_path = vault_path / file
        if file_path.exists():
            print_check(f"  {file}", True)
        else:
            print_check(f"  {file}", False)
            all_ok = False
    
    return all_ok

def check_scripts():
    """Check AI Employee scripts."""
    print_header("Step 5: Scripts Check")
    
    scripts_path = Path('./scripts')
    required_scripts = [
        'orchestrator.py',
        'filesystem_watcher.py',
        'base_watcher.py'
    ]
    
    all_ok = True
    for script in required_scripts:
        script_path = scripts_path / script
        if script_path.exists():
            print_check(f"  {script}", True)
        else:
            print_check(f"  {script}", False)
            all_ok = False
    
    return all_ok

def test_ollama_connection():
    """Test actual Ollama connection."""
    print_header("Step 6: Ollama Connection Test")
    
    try:
        import ollama
        
        # Try a simple request
        print("  Testing Ollama connection...")
        response = ollama.chat(model='qwen2.5:7b', messages=[
            {'role': 'user', 'content': 'Say OK in one word'}
        ])
        
        if response and 'message' in response:
            content = response['message']['content']
            print_check("Ollama Chat", True, f"Response: {content[:50]}")
            return True
        else:
            print_check("Ollama Chat", False, "No response")
            return False
            
    except Exception as e:
        print_check("Ollama Chat", False, str(e))
        print("\n  Make sure:")
        print("  1. Ollama is installed")
        print("  2. Ollama service is running (ollama serve)")
        print("  3. Qwen model is downloaded (ollama pull qwen2.5:7b)")
        return False

def main():
    """Run all checks."""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     AI Employee - Complete Setup Verification            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    results = []
    
    # Run checks
    results.append(("Python", check_python()))
    results.append(("Packages", check_packages()))
    results.append(("Ollama", check_ollama()))
    results.append(("Vault", check_vault()))
    results.append(("Scripts", check_scripts()))
    
    # Test Ollama connection if available
    ollama_ok = results[2][1]  # Ollama check passed
    if ollama_ok:
        results.append(("Connection", test_ollama_connection()))
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"  Result: {passed}/{total} checks passed")
    print()
    
    if passed == total:
        print("  🎉 SUCCESS! All checks passed!")
        print()
        print("  Next steps:")
        print("  1. Start watcher: cd scripts && python filesystem_watcher.py ..\\AI_Employee_Vault")
        print("  2. Drop a file in: AI_Employee_Vault\\Inbox\\")
        print("  3. Process with: python orchestrator.py --vault ..\\AI_Employee_Vault --ollama --once")
        print()
        return 0
    else:
        print("  ⚠ Some checks failed. Please review the output above.")
        print()
        
        if not results[2][1]:  # Ollama failed
            print("  To install Ollama:")
            print("  1. Visit: https://ollama.com/download")
            print("  2. Download and run OllamaSetup.exe")
            print("  3. Open NEW Command Prompt")
            print("  4. Run: ollama pull qwen2.5:7b")
            print("  5. Run this script again")
            print()
        
        return 1

if __name__ == '__main__':
    sys.exit(main())
