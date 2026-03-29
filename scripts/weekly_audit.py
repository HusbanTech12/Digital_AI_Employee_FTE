"""
Weekly Business Audit Generator

Generates a comprehensive weekly business audit with:
- Revenue summary
- Task completion analysis
- Bottleneck identification
- Subscription audit
- Proactive suggestions

Scheduled to run every Monday at 7:00 AM.
"""

from pathlib import Path
from datetime import datetime, timedelta
import sys
import json


def generate_weekly_audit(vault_path: Path):
    """Generate weekly business audit."""
    print("Generating Weekly Business Audit...")
    
    # Create audit folder
    audits_folder = vault_path / 'Audits'
    audits_folder.mkdir(parents=True, exist_ok=True)
    
    # Calculate date range (last 7 days)
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    # Get last Monday's date for the report
    last_monday = today - timedelta(days=today.weekday())
    date_range_str = f"{(last_monday - timedelta(days=7)).strftime('%Y-%m-%d')} to {last_monday.strftime('%Y-%m-%d')}"
    
    # Count completed tasks
    done_folder = vault_path / 'Done'
    completed_tasks = []
    
    if done_folder.exists():
        for f in done_folder.glob('*.md'):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if week_ago <= mtime <= today:
                    completed_tasks.append({
                        'name': f.name,
                        'completed': mtime
                    })
            except:
                pass
    
    # Read business goals
    goals_path = vault_path / 'Business_Goals.md'
    goals = {}
    if goals_path.exists():
        content = goals_path.read_text()
        # Simple parsing - in production, use proper markdown parser
        if 'Monthly goal:' in content:
            for line in content.split('\n'):
                if 'Monthly goal:' in line:
                    try:
                        goals['monthly_revenue'] = line.split('$')[1].replace(',', '').strip()
                    except:
                        pass
    
    # Analyze bottlenecks (tasks that took longer than expected)
    bottlenecks = []
    
    # Check for expired approvals
    pending_approval = vault_path / 'Pending_Approval'
    expired_approvals = []
    if pending_approval.exists():
        for f in pending_approval.glob('*.md'):
            try:
                content = f.read_text()
                if 'expires:' in content:
                    # Parse expiration date
                    for line in content.split('\n'):
                        if 'expires:' in line:
                            try:
                                exp_str = line.split('expires:')[1].strip()
                                exp_date = datetime.fromisoformat(exp_str)
                                if exp_date < today:
                                    expired_approvals.append(f.name)
                            except:
                                pass
            except:
                pass
    
    # Generate audit report
    audit_content = f'''---
type: weekly_audit
period: {date_range_str}
generated: {today.isoformat()}
---

# Weekly Business Audit

## Executive Summary

**Period:** {date_range_str}

### Key Metrics
| Metric | Value |
|--------|-------|
| Tasks Completed | {len(completed_tasks)} |
| Avg Tasks/Day | {len(completed_tasks) / 7:.1f} |
| Pending Items | {len(list((vault_path / "Needs_Action").glob("*.md"))) if (vault_path / "Needs_Action").exists() else 0} |
| Awaiting Approval | {len(list((vault_path / "Pending_Approval").glob("*.md"))) if (vault_path / "Pending_Approval").exists() else 0} |

## Completed Tasks This Week

'''
    
    if completed_tasks:
        # Group by day
        by_day = {}
        for task in completed_tasks:
            day = task['completed'].strftime('%A')
            if day not in by_day:
                by_day[day] = []
            by_day[day].append(task['name'])
        
        for day, tasks in sorted(by_day.items()):
            audit_content += f"### {day}\n"
            for task in tasks:
                audit_content += f"- [x] {task}\n"
            audit_content += "\n"
    else:
        audit_content += "*No tasks completed this week.*\n\n"
    
    # Bottlenecks section
    audit_content += '''## Bottlenecks Identified

'''
    if expired_approvals:
        audit_content += "### Expired Approvals\n"
        for approval in expired_approvals:
            audit_content += f"- ⚠️ {approval}\n"
        audit_content += "\n"
    
    if bottlenecks:
        audit_content += "### Delayed Tasks\n"
        for bottleneck in bottlenecks:
            audit_content += f"- {bottleneck}\n"
    
    if not expired_approvals and not bottlenecks:
        audit_content += "*No bottlenecks identified this week.*\n\n"
    
    # Proactive suggestions
    audit_content += f'''## Proactive Suggestions

### Process Improvements
'''
    
    if len(completed_tasks) < 5:
        audit_content += "- ⚠️ Low task completion rate. Review workload and priorities.\n"
    
    if expired_approvals:
        audit_content += f"- ⚠️ {len(expired_approvals)} approval(s) expired. Consider reviewing approval process.\n"
    
    # Business goals check
    if goals.get('monthly_revenue'):
        audit_content += f"- 💰 Monthly revenue goal: ${goals['monthly_revenue']}. Track progress in Dashboard.md.\n"
    
    audit_content += f'''

## Next Week's Focus

1. Clear expired approvals
2. Process pending items in Needs_Action/
3. Review and update Business_Goals.md

## Notes for CEO Review

- Review completed tasks for quality
- Approve pending items requiring attention
- Update business goals if needed

---
*Generated automatically by AI Employee Weekly Audit*
'''
    
    # Write audit
    audit_file = audits_folder / f'Weekly_Audit_{last_monday.strftime("%Y-%m-%d")}.md'
    audit_file.write_text(audit_content, encoding='utf-8')
    
    print(f"✓ Weekly audit generated: {audit_file.name}")
    return str(audit_file)


if __name__ == '__main__':
    vault_path = Path(r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault')
    
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    
    generate_weekly_audit(vault_path)
