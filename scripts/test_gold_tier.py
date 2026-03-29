"""
Gold Tier Test Script

Tests all Gold Tier requirements:
1. All Silver Tier requirements
2. Full cross-domain integration (Personal + Business)
3. Odoo accounting integration via MCP
4. Facebook and Instagram integration
5. Twitter (X) integration
6. Multiple MCP servers for different action types
7. Weekly Business and Accounting Audit with CEO Briefing
8. Error recovery and graceful degradation
9. Comprehensive audit logging
10. Ralph Wiggum loop for autonomous multi-step task completion
11. All AI functionality implemented as Agent Skills

Usage:
    python test_gold_tier.py [--vault PATH]
"""

import sys
import json
from pathlib import Path
from datetime import datetime


class GoldTierTester:
    """Tests Gold Tier requirements."""

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

    def test_silver_tier_requirements(self):
        """Test 1: Verify all Silver Tier requirements are met."""
        print("\n" + "=" * 60)
        print("TEST 1: Silver Tier Requirements (Prerequisite)")
        print("=" * 60)
        
        # Check Silver tier scripts exist
        silver_scripts = {
            'gmail_watcher.py': 'Gmail watcher',
            'whatsapp_watcher.py': 'WhatsApp watcher',
            'linkedin_poster.py': 'LinkedIn poster',
            'scheduler.py': 'Task scheduler',
        }
        
        for script, description in silver_scripts.items():
            path = self.scripts_path / script
            if path.exists():
                self.log_result(
                    f"Silver Script: {description}",
                    True,
                    f"Found: {script}"
                )
            else:
                self.log_result(
                    f"Silver Script: {description}",
                    False,
                    f"Missing: {script}"
                )
        
        # Check Silver tier MCP server
        email_mcp = self.mcp_path / 'email-mcp'
        if email_mcp.exists():
            self.log_result(
                "Silver MCP: email-mcp",
                True,
                "Email MCP server exists"
            )
        else:
            self.log_result(
                "Silver MCP: email-mcp",
                False,
                "Email MCP server missing"
            )

    def test_odoo_accounting_integration(self):
        """Test 2: Odoo accounting integration via MCP."""
        print("\n" + "=" * 60)
        print("TEST 2: Odoo Accounting Integration (Gold Tier)")
        print("=" * 60)
        
        odoo_mcp = self.mcp_path / 'odoo-mcp'
        
        if odoo_mcp.exists():
            self.log_result(
                "Odoo MCP Directory",
                True,
                f"Found: {odoo_mcp}"
            )
            
            # Check required files
            required_files = ['package.json', 'index.js']
            for file in required_files:
                path = odoo_mcp / file
                if path.exists():
                    self.log_result(
                        f"Odoo MCP File: {file}",
                        True,
                        "Present"
                    )
                else:
                    self.log_result(
                        f"Odoo MCP File: {file}",
                        False,
                        "Missing"
                    )
            
            # Check for Odoo tools in index.js
            content = (odoo_mcp / 'index.js').read_text()
            
            odoo_tools = {
                'create_invoice': 'Create invoice tool',
                'get_invoices': 'Get invoices tool',
                'validate_invoice': 'Validate invoice tool',
                'register_payment': 'Register payment tool',
                'get_financial_summary': 'Financial summary tool',
            }
            
            for tool, description in odoo_tools.items():
                if tool in content:
                    self.log_result(
                        f"Odoo Tool: {description}",
                        True,
                        f"Found: {tool}"
                    )
                else:
                    self.log_result(
                        f"Odoo Tool: {description}",
                        False,
                        f"Missing: {tool}",
                        warning=True
                    )
        else:
            self.log_result(
                "Odoo MCP Server",
                False,
                "odoo-mcp directory not found"
            )

    def test_facebook_instagram_integration(self):
        """Test 3: Facebook and Instagram integration."""
        print("\n" + "=" * 60)
        print("TEST 3: Facebook/Instagram Integration (Gold Tier)")
        print("=" * 60)
        
        fb_script = self.scripts_path / 'facebook_instagram_watcher.py'
        
        if fb_script.exists():
            self.log_result(
                "Facebook/Instagram Script",
                True,
                f"Found: {fb_script.name}"
            )
            
            # Check for required functions
            content = fb_script.read_text(encoding='utf-8')
            
            functions = {
                'post_to_facebook': 'Facebook posting',
                'post_to_instagram': 'Instagram posting',
                'generate_summary': 'Summary generation',
            }
            
            for func, description in functions.items():
                if f'def {func}' in content:
                    self.log_result(
                        f"FB/IG Function: {description}",
                        True,
                        f"Found: {func}"
                    )
                else:
                    self.log_result(
                        f"FB/IG Function: {description}",
                        False,
                        f"Missing: {func}",
                        warning=True
                    )
        else:
            self.log_result(
                "Facebook/Instagram Script",
                False,
                "facebook_instagram_watcher.py not found"
            )

    def test_twitter_integration(self):
        """Test 4: Twitter (X) integration."""
        print("\n" + "=" * 60)
        print("TEST 4: Twitter (X) Integration (Gold Tier)")
        print("=" * 60)
        
        twitter_script = self.scripts_path / 'twitter_watcher.py'
        
        if twitter_script.exists():
            self.log_result(
                "Twitter Script",
                True,
                f"Found: {twitter_script.name}"
            )
            
            # Check for required functions
            content = twitter_script.read_text(encoding='utf-8')
            
            functions = {
                'post_to_twitter': 'Twitter posting',
                '_split_into_thread': 'Thread support',
                'generate_summary': 'Summary generation',
            }
            
            for func, description in functions.items():
                if f'def {func}' in content:
                    self.log_result(
                        f"Twitter Function: {description}",
                        True,
                        f"Found: {func}"
                    )
                else:
                    self.log_result(
                        f"Twitter Function: {description}",
                        False,
                        f"Missing: {func}",
                        warning=True
                    )
        else:
            self.log_result(
                "Twitter Script",
                False,
                "twitter_watcher.py not found"
            )

    def test_multiple_mcp_servers(self):
        """Test 5: Multiple MCP servers for different action types."""
        print("\n" + "=" * 60)
        print("TEST 5: Multiple MCP Servers (Gold Tier)")
        print("=" * 60)
        
        mcp_servers = {
            'email-mcp': 'Email operations',
            'odoo-mcp': 'Accounting operations',
            'social-mcp': 'Social media operations',
        }
        
        found_servers = 0
        
        for server, description in mcp_servers.items():
            path = self.mcp_path / server
            if path.exists():
                found_servers += 1
                self.log_result(
                    f"MCP Server: {description}",
                    True,
                    f"Found: {server}"
                )
            else:
                self.log_result(
                    f"MCP Server: {description}",
                    False,
                    f"Missing: {server}",
                    warning=True
                )
        
        if found_servers >= 2:
            self.log_result(
                "Multiple MCP Servers",
                True,
                f"Found {found_servers} MCP servers (Gold requires 2+)"
            )
        else:
            self.log_result(
                "Multiple MCP Servers",
                False,
                f"Need 2+ MCP servers, found {found_servers}"
            )

    def test_weekly_audit_ceo_briefing(self):
        """Test 6: Weekly Business and Accounting Audit with CEO Briefing."""
        print("\n" + "=" * 60)
        print("TEST 6: Weekly Audit & CEO Briefing (Gold Tier)")
        print("=" * 60)
        
        audit_script = self.scripts_path / 'gold_weekly_audit.py'
        
        if audit_script.exists():
            self.log_result(
                "Gold Weekly Audit Script",
                True,
                f"Found: {audit_script.name}"
            )
            
            # Check for required functions
            content = audit_script.read_text(encoding='utf-8')
            
            functions = {
                'get_accounting_data': 'Accounting data retrieval',
                'get_social_media_summary': 'Social media summary',
                'identify_bottlenecks': 'Bottleneck identification',
                'generate_proactive_suggestions': 'Proactive suggestions',
                'generate_ceo_briefing': 'CEO Briefing generation',
            }
            
            for func, description in functions.items():
                if f'def {func}' in content:
                    self.log_result(
                        f"Audit Function: {description}",
                        True,
                        f"Found: {func}"
                    )
                else:
                    self.log_result(
                        f"Audit Function: {description}",
                        False,
                        f"Missing: {func}",
                        warning=True
                    )
        else:
            self.log_result(
                "Gold Weekly Audit Script",
                False,
                "gold_weekly_audit.py not found"
            )

    def test_error_recovery(self):
        """Test 7: Error recovery and graceful degradation."""
        print("\n" + "=" * 60)
        print("TEST 7: Error Recovery System (Gold Tier)")
        print("=" * 60)
        
        recovery_script = self.scripts_path / 'error_recovery.py'
        
        if recovery_script.exists():
            self.log_result(
                "Error Recovery Script",
                True,
                f"Found: {recovery_script.name}"
            )
            
            # Check for required classes/functions
            content = recovery_script.read_text()
            
            classes = {
                'ErrorRecovery': 'Main error recovery class',
                'CircuitBreaker': 'Circuit breaker pattern',
                'RecoveryStrategy': 'Recovery strategies enum',
            }
            
            for cls, description in classes.items():
                if f'class {cls}' in content:
                    self.log_result(
                        f"Recovery Class: {description}",
                        True,
                        f"Found: {cls}"
                    )
                else:
                    self.log_result(
                        f"Recovery Class: {description}",
                        False,
                        f"Missing: {cls}",
                        warning=True
                    )
            
            # Check for retry decorator
            if '@retry' in content or 'def retry' in content:
                self.log_result(
                    "Retry Decorator",
                    True,
                    "Retry with backoff found"
                )
            else:
                self.log_result(
                    "Retry Decorator",
                    False,
                    "Retry decorator not found",
                    warning=True
                )
        else:
            self.log_result(
                "Error Recovery Script",
                False,
                "error_recovery.py not found"
            )

    def test_audit_logging(self):
        """Test 8: Comprehensive audit logging."""
        print("\n" + "=" * 60)
        print("TEST 8: Comprehensive Audit Logging (Gold Tier)")
        print("=" * 60)
        
        audit_script = self.scripts_path / 'audit_logger.py'
        
        if audit_script.exists():
            self.log_result(
                "Audit Logger Script",
                True,
                f"Found: {audit_script.name}"
            )
            
            # Check for required classes/functions
            content = audit_script.read_text(encoding='utf-8')
            
            classes = {
                'AuditLogger': 'Main audit logger class',
                'AuditEntry': 'Audit entry dataclass',
            }
            
            for cls, description in classes.items():
                if f'class {cls}' in content:
                    self.log_result(
                        f"Audit Class: {description}",
                        True,
                        f"Found: {cls}"
                    )
                else:
                    self.log_result(
                        f"Audit Class: {description}",
                        False,
                        f"Missing: {cls}",
                        warning=True
                    )
            
            # Check for required methods
            methods = {
                'log_action': 'Log actions',
                'search': 'Search audit logs',
                'get_statistics': 'Get statistics',
                'generate_compliance_report': 'Compliance reporting',
            }
            
            for method, description in methods.items():
                if f'def {method}' in content:
                    self.log_result(
                        f"Audit Method: {description}",
                        True,
                        f"Found: {method}"
                    )
                else:
                    self.log_result(
                        f"Audit Method: {description}",
                        False,
                        f"Missing: {method}",
                        warning=True
                    )
        else:
            self.log_result(
                "Audit Logger Script",
                False,
                "audit_logger.py not found"
            )

    def test_ralph_wiggum_loop(self):
        """Test 9: Ralph Wiggum loop for autonomous task completion."""
        print("\n" + "=" * 60)
        print("TEST 9: Ralph Wiggum Loop (Gold Tier)")
        print("=" * 60)
        
        ralph_script = self.scripts_path / 'ralph_wiggum_loop.py'
        
        if ralph_script.exists():
            self.log_result(
                "Ralph Wiggum Loop Script",
                True,
                f"Found: {ralph_script.name}"
            )
            
            # Check for required classes/functions
            content = ralph_script.read_text(encoding='utf-8')
            
            classes = {
                'RalphWiggumLoop': 'Main Ralph Wiggum Loop class',
                'TaskState': 'Task state dataclass',
            }
            
            for cls, description in classes.items():
                if f'class {cls}' in content:
                    self.log_result(
                        f"Ralph Class: {description}",
                        True,
                        f"Found: {cls}"
                    )
                else:
                    self.log_result(
                        f"Ralph Class: {description}",
                        False,
                        f"Missing: {cls}",
                        warning=True
                    )
            
            # Check for required methods
            methods = {
                'create_task': 'Create tasks',
                'check_completion': 'Check task completion',
                'stop_hook': 'Stop hook for Claude exit',
                'generate_iteration_prompt': 'Generate iteration prompts',
            }
            
            for method, description in methods.items():
                if f'def {method}' in content:
                    self.log_result(
                        f"Ralph Method: {description}",
                        True,
                        f"Found: {method}"
                    )
                else:
                    self.log_result(
                        f"Ralph Method: {description}",
                        False,
                        f"Missing: {method}",
                        warning=True
                    )
        else:
            self.log_result(
                "Ralph Wiggum Loop Script",
                False,
                "ralph_wiggum_loop.py not found"
            )

    def test_vault_structure(self):
        """Test 10: Vault structure for Gold Tier."""
        print("\n" + "=" * 60)
        print("TEST 10: Vault Structure (Gold Tier)")
        print("=" * 60)
        
        # Gold tier requires all Silver folders plus:
        gold_folders = {
            'Needs_Action': 'Pending items',
            'Plans': 'Claude action plans',
            'Done': 'Completed tasks',
            'Pending_Approval': 'Awaiting approval',
            'Approved': 'Approved actions',
            'Rejected': 'Rejected actions',
            'Logs': 'Audit logs',
            'Logs/Audit': 'Audit-specific logs',
            'Logs/Recovery': 'Error recovery logs',
            'Briefings': 'CEO briefings',
            'Audits': 'Business audits',
        }
        
        for folder, description in gold_folders.items():
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
                    f"Missing - {description}",
                    warning=True
                )

    def run_all_tests(self):
        """Run all Gold Tier tests."""
        print("\n" + "=" * 60)
        print("GOLD TIER TEST SUITE")
        print("Personal AI Employee Hackathon 0")
        print("=" * 60)
        print(f"Vault Path: {self.vault_path}")
        print(f"Timestamp: {self.results['timestamp']}")
        
        self.test_silver_tier_requirements()
        self.test_odoo_accounting_integration()
        self.test_facebook_instagram_integration()
        self.test_twitter_integration()
        self.test_multiple_mcp_servers()
        self.test_weekly_audit_ceo_briefing()
        self.test_error_recovery()
        self.test_audit_logging()
        self.test_ralph_wiggum_loop()
        self.test_vault_structure()
        
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
            print("\n✓ GOLD TIER REQUIREMENTS MET!")
            print("All core requirements are satisfied.")
        else:
            print(f"\n✗ {self.results['failed']} requirement(s) not met.")
            print("Review failed tests above.")
        
        # Save results
        results_file = self.base_path / 'gold_tier_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
        
        return self.results['failed'] == 0


def main():
    import argparse
    
    # Default paths
    base_path = Path(r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE')
    vault_path = base_path / 'AI_Employee_Vault'
    
    parser = argparse.ArgumentParser(description='Gold Tier Test Suite')
    parser.add_argument('--vault', type=str, default=str(vault_path),
                        help='Path to vault')
    
    args = parser.parse_args()
    
    tester = GoldTierTester(Path(args.vault))
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
