"""
Silver Tier Test Script

Tests all Silver Tier requirements:
1. Two or more Watcher scripts (Gmail + WhatsApp + LinkedIn)
2. Auto-posting to LinkedIn
3. Claude reasoning loop that creates Plan.md files
4. One working MCP server for external action
5. Human-in-the-loop approval workflow
6. Basic scheduling via Task Scheduler

Usage:
    python test_silver_tier.py [--vault PATH] [--skip-external]
"""

import sys
import json
from pathlib import Path
from datetime import datetime


class SilverTierTester:
    """Tests Silver Tier requirements."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.base_path = vault_path.parent
        self.scripts_path = self.base_path / 'scripts'
        self.skills_path = self.base_path / 'skills'
        self.mcp_path = self.base_path / 'mcp-servers'
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'vault_path': str(vault_path),
            'tests': [],
            'passed': 0,
            'failed': 0,
            'warnings': 0,
        }

    def log_result(self, name: str, passed: bool, message: str = '', warning: bool = False):
        """Log a test result."""
        self.results['tests'].append({
            'name': name,
            'passed': passed,
            'message': message,
            'warning': warning,
        })
        
        if passed:
            self.results['passed'] += 1
            status = "✓ PASS"
        elif warning:
            self.results['warnings'] += 1
            status = "⚠ WARNING"
        else:
            self.results['failed'] += 1
            status = "✗ FAIL"
        
        print(f"{status}: {name}")
        if message:
            print(f"       {message}")

    def test_watcher_scripts(self):
        """Test 1: Check for required watcher scripts."""
        print("\n" + "=" * 60)
        print("TEST 1: Watcher Scripts (Silver Tier requires 2+)")
        print("=" * 60)
        
        watchers = {
            'filesystem_watcher.py': 'Bronze Tier (required)',
            'gmail_watcher.py': 'Silver Tier',
            'whatsapp_watcher.py': 'Silver Tier',
            'linkedin_poster.py': 'Silver Tier (posting)',
        }
        
        found_watchers = 0
        silver_watchers = 0
        
        for watcher, description in watchers.items():
            path = self.scripts_path / watcher
            if path.exists():
                found_watchers += 1
                if 'gmail' in watcher or 'whatsapp' in watcher:
                    silver_watchers += 1
                self.log_result(
                    f"Watcher: {watcher}",
                    True,
                    f"Found - {description}"
                )
            else:
                self.log_result(
                    f"Watcher: {watcher}",
                    False,
                    f"Missing - {description}"
                )
        
        # Check requirement
        if silver_watchers >= 2:
            self.log_result(
                "Silver Tier Watcher Requirement",
                True,
                f"Found {silver_watchers} Silver tier watchers (Gmail/WhatsApp)"
            )
        else:
            self.log_result(
                "Silver Tier Watcher Requirement",
                False,
                f"Need 2+ Silver watchers, found {silver_watchers}"
            )

    def test_mcp_server(self):
        """Test 2: Check for MCP server."""
        print("\n" + "=" * 60)
        print("TEST 2: MCP Server for External Actions")
        print("=" * 60)
        
        mcp_email = self.mcp_path / 'email-mcp'
        
        if mcp_email.exists():
            self.log_result(
                "MCP Server Directory",
                True,
                f"Found: {mcp_email}"
            )
            
            # Check required files
            required_files = ['package.json', 'index.js']
            for file in required_files:
                path = mcp_email / file
                if path.exists():
                    self.log_result(
                        f"MCP File: {file}",
                        True,
                        "Present"
                    )
                else:
                    self.log_result(
                        f"MCP File: {file}",
                        False,
                        "Missing"
                    )
            
            # Check package.json content
            pkg_json = mcp_email / 'package.json'
            if pkg_json.exists():
                try:
                    pkg = json.loads(pkg_json.read_text())
                    if 'nodemailer' in pkg.get('dependencies', {}):
                        self.log_result(
                            "MCP Dependencies",
                            True,
                            "nodemailer found in dependencies"
                        )
                    else:
                        self.log_result(
                            "MCP Dependencies",
                            False,
                            "nodemailer not found"
                        )
                except Exception as e:
                    self.log_result(
                        "MCP package.json",
                        False,
                        f"Parse error: {e}"
                    )
        else:
            self.log_result(
                "MCP Server: email-mcp",
                False,
                "Directory not found"
            )

    def test_approval_workflow(self):
        """Test 3: Check approval workflow setup."""
        print("\n" + "=" * 60)
        print("TEST 3: Human-in-the-Loop Approval Workflow")
        print("=" * 60)
        
        # Check folders
        folders = {
            'Pending_Approval': 'Approval requests',
            'Approved': 'Approved actions',
            'Rejected': 'Rejected actions',
        }
        
        for folder, description in folders.items():
            path = self.vault_path / folder
            if path.exists():
                self.log_result(
                    f"Folder: {folder}",
                    True,
                    f"{description} folder exists"
                )
            else:
                self.log_result(
                    f"Folder: {folder}",
                    False,
                    f"{description} folder missing"
                )
        
        # Check approval-handler skill
        skill_path = self.skills_path / 'approval-handler' / 'SKILL.md'
        if skill_path.exists():
            content = skill_path.read_text()
            
            checks = {
                'Version: 2.0': 'Silver Tier version',
                'auto_approve': 'Auto-approval rules',
                'audit': 'Audit logging',
                'escalat': 'Escalation handling',
            }
            
            for pattern, description in checks.items():
                if pattern.lower() in content.lower():
                    self.log_result(
                        f"Approval Skill: {description}",
                        True,
                        f"Found: {pattern}"
                    )
                else:
                    self.log_result(
                        f"Approval Skill: {description}",
                        False,
                        f"Missing: {pattern}",
                        warning=True
                    )
        else:
            self.log_result(
                "Approval Handler Skill",
                False,
                "SKILL.md not found"
            )

    def test_plan_generator(self):
        """Test 4: Check Plan.md generator skill."""
        print("\n" + "=" * 60)
        print("TEST 4: Plan.md Generator (Claude Reasoning Loop)")
        print("=" * 60)
        
        plan_skill = self.skills_path / 'plan-generator' / 'SKILL.md'
        
        if plan_skill.exists():
            self.log_result(
                "Plan Generator Skill",
                True,
                f"Found: {plan_skill}"
            )
            
            content = plan_skill.read_text()
            
            # Check for required elements
            required = {
                'type: plan': 'Plan frontmatter',
                'Steps': 'Step breakdown',
                'Success Criteria': 'Success criteria',
                'Dependencies': 'Step dependencies',
            }
            
            for pattern, description in required.items():
                if pattern in content:
                    self.log_result(
                        f"Plan Template: {description}",
                        True,
                        f"Found: {pattern}"
                    )
                else:
                    self.log_result(
                        f"Plan Template: {description}",
                        False,
                        f"Missing: {pattern}",
                        warning=True
                    )
        else:
            self.log_result(
                "Plan Generator Skill",
                False,
                "SKILL.md not found"
            )

    def test_scheduling(self):
        """Test 5: Check scheduling setup."""
        print("\n" + "=" * 60)
        print("TEST 5: Basic Scheduling (Task Scheduler)")
        print("=" * 60)
        
        scheduler = self.scripts_path / 'scheduler.py'
        
        if scheduler.exists():
            self.log_result(
                "Scheduler Script",
                True,
                f"Found: {scheduler}"
            )
            
            # Check for required functions
            content = scheduler.read_text()
            
            functions = {
                'def install': 'Install tasks',
                'def remove': 'Remove tasks',
                'def status': 'Status check',
                'schtasks': 'Windows Task Scheduler',
            }
            
            for pattern, description in functions.items():
                if pattern in content:
                    self.log_result(
                        f"Scheduler: {description}",
                        True,
                        f"Found: {pattern}"
                    )
                else:
                    self.log_result(
                        f"Scheduler: {description}",
                        False,
                        f"Missing: {pattern}"
                    )
        else:
            self.log_result(
                "Scheduler Script",
                False,
                "scheduler.py not found"
            )
        
        # Check for scheduled task scripts
        scheduled_scripts = {
            'daily_briefing.py': 'Daily CEO Briefing',
            'weekly_audit.py': 'Weekly Business Audit',
        }
        
        for script, description in scheduled_scripts.items():
            path = self.scripts_path / script
            if path.exists():
                self.log_result(
                    f"Scheduled Script: {description}",
                    True,
                    f"Found: {script}"
                )
            else:
                self.log_result(
                    f"Scheduled Script: {description}",
                    False,
                    f"Missing: {script}"
                )

    def test_vault_structure(self):
        """Test 6: Check vault structure for Silver Tier."""
        print("\n" + "=" * 60)
        print("TEST 6: Vault Structure (Silver Tier)")
        print("=" * 60)
        
        required_folders = {
            'Needs_Action': 'Pending items to process',
            'Plans': 'Claude action plans',
            'Done': 'Completed tasks',
            'Pending_Approval': 'Awaiting approval',
            'Approved': 'Approved actions',
            'Rejected': 'Rejected actions',
            'Logs': 'Audit logs',
            'Briefings': 'Daily/Weekly briefings',
        }
        
        for folder, description in required_folders.items():
            path = self.vault_path / folder
            if path.exists():
                self.log_result(
                    f"Vault Folder: {folder}",
                    True,
                    f"{description}"
                )
            else:
                self.log_result(
                    f"Vault Folder: {folder}",
                    False,
                    f"Missing - {description}"
                )
        
        # Check required files
        required_files = {
            'Dashboard.md': 'Main dashboard',
            'Company_Handbook.md': 'Rules and contacts',
            'Business_Goals.md': 'Business objectives',
        }
        
        for file, description in required_files.items():
            path = self.vault_path / file
            if path.exists():
                self.log_result(
                    f"Vault File: {file}",
                    True,
                    f"{description}"
                )
            else:
                self.log_result(
                    f"Vault File: {file}",
                    False,
                    f"Missing - {description}"
                )

    def test_dependencies(self):
        """Test 7: Check Python dependencies."""
        print("\n" + "=" * 60)
        print("TEST 7: Python Dependencies")
        print("=" * 60)
        
        requirements = self.scripts_path / 'requirements.txt'
        
        if requirements.exists():
            content = requirements.read_text()
            
            # Silver tier dependencies
            deps = {
                'playwright': 'WhatsApp/LinkedIn automation',
                'google-api-python-client': 'Gmail API',
                'google-auth': 'Google authentication',
            }
            
            for dep, description in deps.items():
                # Check if dependency is listed and not commented out
                lines = content.split('\n')
                found = False
                for line in lines:
                    if dep in line and not line.strip().startswith('#'):
                        found = True
                        break
                
                if found:
                    self.log_result(
                        f"Dependency: {dep}",
                        True,
                        f"Listed - {description}"
                    )
                else:
                    self.log_result(
                        f"Dependency: {dep}",
                        False,
                        f"Not listed - {description}",
                        warning=True
                    )
        else:
            self.log_result(
                "requirements.txt",
                False,
                "File not found"
            )

    def run_all_tests(self):
        """Run all Silver Tier tests."""
        print("\n" + "=" * 60)
        print("SILVER TIER TEST SUITE")
        print("Personal AI Employee Hackathon 0")
        print("=" * 60)
        print(f"Vault Path: {self.vault_path}")
        print(f"Timestamp: {self.results['timestamp']}")
        
        self.test_watcher_scripts()
        self.test_mcp_server()
        self.test_approval_workflow()
        self.test_plan_generator()
        self.test_scheduling()
        self.test_vault_structure()
        self.test_dependencies()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total = self.results['passed'] + self.results['failed']
        print(f"Total Tests: {total}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Warnings: {self.results['warnings']}")
        
        if self.results['failed'] == 0:
            print("\n✓ SILVER TIER REQUIREMENTS MET!")
            print("All core requirements are satisfied.")
        else:
            print(f"\n✗ {self.results['failed']} requirement(s) not met.")
            print("Review failed tests above.")
        
        # Save results
        results_file = self.base_path / 'silver_tier_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
        
        return self.results['failed'] == 0


def main():
    import argparse
    
    # Default paths
    base_path = Path(r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE')
    vault_path = base_path / 'AI_Employee_Vault'
    
    parser = argparse.ArgumentParser(description='Silver Tier Test Suite')
    parser.add_argument('--vault', type=str, default=str(vault_path),
                        help='Path to vault')
    
    args = parser.parse_args()
    
    tester = SilverTierTester(Path(args.vault))
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
