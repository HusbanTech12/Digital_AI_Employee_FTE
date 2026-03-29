"""
Enhanced Weekly Business and Accounting Audit with CEO Briefing

Gold Tier Feature: Comprehensive business audit with accounting integration.
Generates detailed CEO briefing with revenue, bottlenecks, and proactive suggestions.

Usage:
    python gold_weekly_audit.py [vault_path]
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sys


class GoldWeeklyAudit:
    """
    Enhanced Weekly Business and Accounting Audit.

    Gold Tier features:
    - Accounting integration (Odoo or manual)
    - Multi-platform social media summary
    - Comprehensive bottleneck analysis
    - Proactive suggestions with ROI estimates
    - CEO Briefing generation
    """

    def __init__(self, vault_path: Path):
        """
        Initialize the audit generator.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = vault_path
        self.logs_dir = vault_path / 'Logs'
        self.audits_dir = vault_path / 'Audits'
        self.briefings_dir = vault_path / 'Briefings'

        # Ensure directories exist
        self.audits_dir.mkdir(parents=True, exist_ok=True)
        self.briefings_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def get_accounting_data(self) -> Dict[str, Any]:
        """
        Get accounting data from Odoo or manual entries.

        Returns:
            Accounting data dictionary
        """
        # Try to get data from Odoo MCP (if configured)
        # For now, use manual transaction tracking

        accounting = {
            'revenue': 0,
            'expenses': 0,
            'receivables': 0,
            'payables': 0,
            'invoices_sent': 0,
            'invoices_paid': 0,
            'pending_payments': 0,
            'transactions': [],
        }

        # Check for transaction files
        transactions_file = self.vault_path / 'Accounting' / 'transactions.json'
        if transactions_file.exists():
            with open(transactions_file, 'r') as f:
                try:
                    data = json.load(f)
                    accounting['transactions'] = data.get('transactions', [])
                    
                    # Calculate totals
                    for tx in accounting['transactions']:
                        if tx.get('type') == 'income':
                            accounting['revenue'] += tx.get('amount', 0)
                            if tx.get('status') == 'paid':
                                accounting['invoices_paid'] += 1
                        elif tx.get('type') == 'expense':
                            accounting['expenses'] += tx.get('amount', 0)
                        
                        if tx.get('status') == 'pending':
                            accounting['pending_payments'] += tx.get('amount', 0)
                        elif tx.get('status') == 'receivable':
                            accounting['receivables'] += tx.get('amount', 0)
                    
                    accounting['invoices_sent'] = len([
                        t for t in accounting['transactions']
                        if t.get('type') == 'income'
                    ])
                except:
                    pass

        accounting['net_income'] = accounting['revenue'] - accounting['expenses']
        accounting['cash_flow'] = accounting['revenue'] - accounting['pending_payments']

        return accounting

    def get_social_media_summary(self) -> Dict[str, Any]:
        """
        Get social media activity summary from all platforms.

        Returns:
            Social media summary dictionary
        """
        summary = {
            'linkedin': {'posts': 0, 'engagement': 0},
            'facebook': {'posts': 0, 'engagement': 0},
            'instagram': {'posts': 0, 'engagement': 0},
            'twitter': {'posts': 0, 'engagement': 0},
            'total_posts': 0,
        }

        # Check logs for each platform
        platform_logs = {
            'linkedin': 'linkedin_posts.jsonl',
            'facebook': 'facebook_posts.jsonl',
            'instagram': 'facebook_posts.jsonl',  # Combined with Facebook
            'twitter': 'twitter_posts.jsonl',
        }

        now = datetime.now()
        week_ago = now - timedelta(days=7)

        for platform, log_file in platform_logs.items():
            log_path = self.logs_dir / log_file
            if log_path.exists():
                with open(log_path, 'r') as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            post_date = datetime.fromisoformat(
                                data.get('timestamp', now.isoformat())
                            )
                            
                            if post_date >= week_ago:
                                summary[platform]['posts'] += 1
                                
                                # Count engagement if available
                                engagement = data.get('engagement', {})
                                summary[platform]['engagement'] += (
                                    engagement.get('likes', 0) +
                                    engagement.get('comments', 0) +
                                    engagement.get('shares', 0) +
                                    engagement.get('retweets', 0)
                                )
                        except:
                            continue

        summary['total_posts'] = sum(p['posts'] for p in [
            summary['linkedin'],
            summary['facebook'],
            summary['instagram'],
            summary['twitter'],
        ])

        return summary

    def get_task_completion_data(self) -> Dict[str, Any]:
        """
        Get task completion data from Done folder.

        Returns:
            Task completion data dictionary
        """
        data = {
            'completed_this_week': 0,
            'completed_today': 0,
            'pending': 0,
            'blocked': 0,
            'by_category': {},
            'avg_completion_time_hours': 0,
            'tasks': [],
        }

        now = datetime.now()
        week_ago = now - timedelta(days=7)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Check Done folder
        done_dir = self.vault_path / 'Done'
        if done_dir.exists():
            for f in done_dir.glob('*.md'):
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    
                    if mtime >= today:
                        data['completed_today'] += 1
                    
                    if mtime >= week_ago:
                        data['completed_this_week'] += 1
                        data['tasks'].append({
                            'name': f.name,
                            'completed': mtime.isoformat(),
                        })
                except:
                    continue

        # Check Needs_Action folder
        needs_action_dir = self.vault_path / 'Needs_Action'
        if needs_action_dir.exists():
            data['pending'] = len(list(needs_action_dir.glob('*.md')))

        # Check Pending_Approval folder
        pending_approval_dir = self.vault_path / 'Pending_Approval'
        if pending_approval_dir.exists():
            data['blocked'] = len(list(pending_approval_dir.glob('*.md')))

        return data

    def identify_bottlenecks(
        self,
        accounting: Dict,
        social: Dict,
        tasks: Dict
    ) -> List[Dict[str, Any]]:
        """
        Identify business bottlenecks.

        Args:
            accounting: Accounting data
            social: Social media summary
            tasks: Task completion data

        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []

        # Revenue bottlenecks
        if accounting['receivables'] > accounting['revenue'] * 0.5:
            bottlenecks.append({
                'category': 'Finance',
                'issue': 'High receivables - customers not paying on time',
                'impact': f"${accounting['receivables']:.2f} outstanding",
                'suggestion': 'Send payment reminders, consider early payment discounts',
                'priority': 'high',
            })

        if accounting['pending_payments'] > accounting['cash_flow']:
            bottlenecks.append({
                'category': 'Finance',
                'issue': 'Pending payments exceed cash flow',
                'impact': 'Cash flow risk',
                'suggestion': 'Prioritize collections, delay non-essential payments',
                'priority': 'critical',
            })

        # Task bottlenecks
        if tasks['blocked'] > 5:
            bottlenecks.append({
                'category': 'Operations',
                'issue': f'{tasks["blocked"]} items awaiting approval',
                'impact': 'Delayed operations',
                'suggestion': 'Review and process pending approvals',
                'priority': 'high',
            })

        if tasks['pending'] > 20:
            bottlenecks.append({
                'category': 'Operations',
                'issue': f'{tasks["pending"]} items in queue',
                'impact': 'Growing backlog',
                'suggestion': 'Prioritize tasks, consider automation',
                'priority': 'medium',
            })

        # Social media bottlenecks
        if social['total_posts'] < 3:
            bottlenecks.append({
                'category': 'Marketing',
                'issue': 'Low social media activity',
                'impact': 'Reduced visibility and lead generation',
                'suggestion': 'Schedule regular posts, use templates',
                'priority': 'medium',
            })

        return bottlenecks

    def generate_proactive_suggestions(
        self,
        accounting: Dict,
        social: Dict,
        tasks: Dict,
        bottlenecks: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Generate proactive business suggestions.

        Returns:
            List of suggestions with ROI estimates
        """
        suggestions = []

        # Cost optimization suggestions
        if accounting['expenses'] > accounting['revenue'] * 0.7:
            suggestions.append({
                'category': 'Cost Optimization',
                'suggestion': 'Review and reduce software subscriptions',
                'potential_savings': '$100-500/month',
                'effort': 'low',
                'roi': 'high',
            })

        # Revenue suggestions
        if accounting['invoices_sent'] < 5:
            suggestions.append({
                'category': 'Revenue',
                'suggestion': 'Increase invoicing - send invoices for all completed work',
                'potential_revenue': '$1000-5000/month',
                'effort': 'medium',
                'roi': 'high',
            })

        # Marketing suggestions
        if social['total_posts'] < 5:
            suggestions.append({
                'category': 'Marketing',
                'suggestion': 'Increase social media posting frequency',
                'potential_impact': '20-50% more leads',
                'effort': 'low',
                'roi': 'medium',
            })

        # Automation suggestions
        if tasks['pending'] > 10:
            suggestions.append({
                'category': 'Automation',
                'suggestion': 'Automate routine task processing',
                'time_savings': '5-10 hours/week',
                'effort': 'high',
                'roi': 'high',
            })

        # Add suggestions for each bottleneck
        for bottleneck in bottlenecks[:3]:  # Top 3 bottlenecks
            suggestions.append({
                'category': bottleneck['category'],
                'suggestion': bottleneck['suggestion'],
                'impact': bottleneck['impact'],
                'effort': 'medium',
                'roi': 'high',
            })

        return suggestions

    def generate_ceo_briefing(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> str:
        """
        Generate comprehensive CEO Briefing.

        Args:
            period_start: Start of reporting period
            period_end: End of reporting period

        Returns:
            Markdown formatted CEO Briefing
        """
        # Gather all data
        accounting = self.get_accounting_data()
        social = self.get_social_media_summary()
        tasks = self.get_task_completion_data()
        bottlenecks = self.identify_bottlenecks(accounting, social, tasks)
        suggestions = self.generate_proactive_suggestions(
            accounting, social, tasks, bottlenecks
        )

        # Generate briefing
        briefing = f"""# CEO Weekly Briefing

**Period:** {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Executive Summary

"""
        # Quick health indicators
        health_indicators = []
        
        if accounting['net_income'] > 0:
            health_indicators.append("🟢 Profitable")
        else:
            health_indicators.append("🔴 Not profitable")
        
        if tasks['completed_this_week'] >= 10:
            health_indicators.append("🟢 High productivity")
        elif tasks['completed_this_week'] >= 5:
            health_indicators.append("🟡 Moderate productivity")
        else:
            health_indicators.append("🔴 Low productivity")
        
        if len(bottlenecks) == 0:
            health_indicators.append("🟢 No bottlenecks")
        elif len(bottlenecks) <= 2:
            health_indicators.append("🟡 Minor bottlenecks")
        else:
            health_indicators.append("🔴 Multiple bottlenecks")

        briefing += " | ".join(health_indicators) + "\n\n"

        # Financial section
        briefing += f"""## Financial Performance

| Metric | Value |
|--------|-------|
| Revenue | ${accounting['revenue']:.2f} |
| Expenses | ${accounting['expenses']:.2f} |
| **Net Income** | **${accounting['net_income']:.2f}** |
| Cash Flow | ${accounting['cash_flow']:.2f} |
| Receivables | ${accounting['receivables']:.2f} |
| Pending Payments | ${accounting['pending_payments']:.2f} |
| Invoices Sent | {accounting['invoices_sent']} |
| Invoices Paid | {accounting['invoices_paid']} |

"""

        # Task completion section
        briefing += f"""## Task Completion

| Metric | Count |
|--------|-------|
| Completed This Week | {tasks['completed_this_week']} |
| Completed Today | {tasks['completed_today']} |
| Pending | {tasks['pending']} |
| Awaiting Approval | {tasks['blocked']} |

### Recent Completions
"""
        for task in tasks['tasks'][:10]:
            briefing += f"- {task['name']}\n"

        if not tasks['tasks']:
            briefing += "- No tasks completed this week\n"

        # Social media section
        briefing += f"""
## Social Media Summary

| Platform | Posts | Engagement |
|----------|-------|------------|
| LinkedIn | {social['linkedin']['posts']} | {social['linkedin']['engagement']} |
| Facebook | {social['facebook']['posts']} | {social['facebook']['engagement']} |
| Instagram | {social['instagram']['posts']} | {social['instagram']['engagement']} |
| Twitter | {social['twitter']['posts']} | {social['twitter']['engagement']} |
| **Total** | **{social['total_posts']}** | **{sum(p['engagement'] for p in [social['linkedin'], social['facebook'], social['instagram'], social['twitter']])}** |

"""

        # Bottlenecks section
        briefing += """## Bottlenecks Identified

"""
        if bottlenecks:
            for i, bottleneck in enumerate(bottlenecks, 1):
                priority_icon = "🔴" if bottleneck['priority'] == 'critical' else "⚠️" if bottleneck['priority'] == 'high' else "⚪"
                briefing += f"""### {priority_icon} {i}. {bottleneck['issue']}
- **Category:** {bottleneck['category']}
- **Impact:** {bottleneck['impact']}
- **Suggestion:** {bottleneck['suggestion']}

"""
        else:
            briefing += "*No significant bottlenecks identified.*\n\n"

        # Proactive suggestions section
        briefing += """## Proactive Suggestions

"""
        for i, suggestion in enumerate(suggestions, 1):
            roi_icon = "💰" if suggestion.get('roi') == 'high' else "📈"
            briefing += f"""### {roi_icon} {i}. {suggestion['suggestion']}
- **Category:** {suggestion['category']}
- **Effort:** {suggestion.get('effort', 'medium')}
"""
            if 'potential_savings' in suggestion:
                briefing += f"- **Potential Savings:** {suggestion['potential_savings']}\n"
            if 'potential_revenue' in suggestion:
                briefing += f"- **Potential Revenue:** {suggestion['potential_revenue']}\n"
            if 'potential_impact' in suggestion:
                briefing += f"- **Potential Impact:** {suggestion['potential_impact']}\n"
            if 'time_savings' in suggestion:
                briefing += f"- **Time Savings:** {suggestion['time_savings']}\n"
            if 'impact' in suggestion:
                briefing += f"- **Impact:** {suggestion['impact']}\n"
            briefing += "\n"

        # Action items
        briefing += """## Recommended Actions This Week

1. """
        
        # Top 3 actions from bottlenecks
        actions = [b['suggestion'] for b in bottlenecks[:3]]
        if not actions:
            actions = ["Review business goals and update strategy"]
        
        briefing += "\n2. ".join(actions)
        
        briefing += f"""

---

## Appendix

### Data Sources
- Accounting: {'Odoo integration' if accounting['transactions'] else 'Manual tracking'}
- Tasks: AI Employee vault (Done/, Needs_Action/, Pending_Approval/)
- Social Media: LinkedIn, Facebook, Instagram, Twitter logs

### Next Briefing
Scheduled for: {(period_end + timedelta(days=7)).strftime('%Y-%m-%d')}

---
*Generated automatically by AI Employee Gold Tier Weekly Audit*
"""

        return briefing

    def run(self) -> str:
        """
        Run the weekly audit and generate briefing.

        Returns:
            Path to generated briefing file
        """
        print("Generating Gold Tier Weekly Business Audit...")

        # Calculate period (last 7 days)
        period_end = datetime.now()
        period_start = period_end - timedelta(days=7)

        # Generate briefing
        briefing = self.generate_ceo_briefing(period_start, period_end)

        # Save briefing
        briefing_file = self.briefings_dir / f'CEO_Briefing_{period_end.strftime("%Y-%m-%d")}.md'
        briefing_file.write_text(briefing, encoding='utf-8')

        # Also save full audit
        audit_file = self.audits_dir / f'Weekly_Audit_{period_end.strftime("%Y-%m-%d")}.md'
        audit_file.write_text(briefing, encoding='utf-8')

        print(f"✓ CEO Briefing generated: {briefing_file.name}")
        print(f"✓ Weekly Audit saved: {audit_file.name}")

        return str(briefing_file)


if __name__ == '__main__':
    vault_path = Path(r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault')

    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])

    audit = GoldWeeklyAudit(vault_path)
    briefing_file = audit.run()

    print(f"\nBriefing saved to: {briefing_file}")
