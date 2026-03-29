"""
Daily Briefing Generator

Generates a daily CEO briefing with:
- Today's agenda
- Pending items overview
- Recent completions
- Key metrics snapshot

Scheduled to run daily at 8:00 AM.
"""

from pathlib import Path
from datetime import datetime
import sys


def generate_daily_briefing(vault_path: Path):
    """Generate daily CEO briefing."""
    print("Generating Daily CEO Briefing...")
    
    # Create briefings folder
    briefings_folder = vault_path / 'Briefings'
    briefings_folder.mkdir(parents=True, exist_ok=True)
    
    # Get today's date
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    day_name = today.strftime('%A')
    
    # Count items in different folders
    needs_action = vault_path / 'Needs_Action'
    pending_approval = vault_path / 'Pending_Approval'
    done = vault_path / 'Done'
    
    pending_count = len(list(needs_action.glob('*.md'))) if needs_action.exists() else 0
    approval_count = len(list(pending_approval.glob('*.md'))) if pending_approval.exists() else 0
    
    # Get recent completions (last 7 days)
    recent_done = []
    if done.exists():
        for f in done.glob('*.md'):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if (today - mtime).days <= 7:
                    recent_done.append(f.name)
            except:
                pass
    
    # Read business goals
    goals_path = vault_path / 'Business_Goals.md'
    goals_content = ""
    if goals_path.exists():
        goals_content = goals_path.read_text()[:500]  # First 500 chars
    
    # Create briefing
    briefing_content = f'''---
type: daily_briefing
date: {date_str}
day: {day_name}
generated: {datetime.now().isoformat()}
---

# Daily CEO Briefing - {day_name}, {date_str}

## Quick Summary
- **Pending Items:** {pending_count}
- **Awaiting Approval:** {approval_count}
- **Completed (7 days):** {len(recent_done)}

## Priority Items Requiring Attention
'''
    
    # List high-priority pending items
    if needs_action.exists() and pending_count > 0:
        briefing_content += "\n### Needs Action\n"
        for f in list(needs_action.glob('*.md'))[:5]:  # Top 5 items
            briefing_content += f"- {f.name}\n"
    
    if pending_approval.exists() and approval_count > 0:
        briefing_content += "\n### Awaiting Your Approval\n"
        for f in list(pending_approval.glob('*.md'))[:5]:  # Top 5 items
            briefing_content += f"- {f.name}\n"
    
    # Recent completions
    briefing_content += f'''

## Recent Completions (Last 7 Days)
'''
    if recent_done:
        for item in recent_done[:10]:  # Show up to 10
            briefing_content += f"- [x] {item}\n"
    else:
        briefing_content += "- No recent completions\n"
    
    # Business goals reminder
    briefing_content += f'''

## Business Goals Reminder
{goals_content if goals_content else "No business goals defined yet."}

## Suggested Focus for Today
1. Review and approve pending items in Pending_Approval/
2. Process high-priority items in Needs_Action/
3. Check Dashboard.md for overall status

---
*Generated automatically by AI Employee Daily Briefing*
'''
    
    # Write briefing
    briefing_file = briefings_folder / f'{date_str}_{day_name}_Briefing.md'
    briefing_file.write_text(briefing_content, encoding='utf-8')
    
    print(f"✓ Daily briefing generated: {briefing_file.name}")
    return str(briefing_file)


if __name__ == '__main__':
    vault_path = Path(r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault')
    
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    
    generate_daily_briefing(vault_path)
