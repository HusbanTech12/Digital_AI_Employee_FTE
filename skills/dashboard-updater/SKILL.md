# Dashboard Updater Skill

**Name:** dashboard-updater  
**Version:** 1.0  
**Tier:** Bronze  

## Description

Updates the Dashboard.md with real-time activity, statistics, pending items, and alerts. Serves as the central status display for the AI Employee system.

## Capabilities

- Update Recent Activity section
- Refresh task statistics
- List pending approvals
- Display alerts and notifications
- Track daily/weekly metrics
- Generate summary reports

## Usage

```bash
qwen --skill dashboard-updater "Update dashboard with today's activity"
```

Or in prompts:
```
Use the dashboard-updater skill to refresh the Dashboard.
```

## Input Format

Reads activity from:
- `AI_Employee_Vault/Logs/` - Activity logs
- `AI_Employee_Vault/Needs_Action/` - Pending items
- `AI_Employee_Vault/Done/` - Completed items
- `AI_Employee_Vault/Pending_Approval/` - Awaiting approval

## Output Format

Updates: `AI_Employee_Vault/Dashboard.md`

Dashboard sections:
```markdown
# AI Employee Dashboard

## Quick Stats
| Metric | Value |
|--------|-------|
| Pending Tasks | X |
| Awaiting Approval | X |
| Completed Today | X |

## Today's Priorities
- [ ] Priority items

## Recent Activity
- [timestamp] Activity description

## Active Projects
| Project | Status | Next Action |
|---------|--------|-------------|

## Pending Approvals
List of items awaiting human review

## Alerts
Important notifications
```

## Update Triggers

1. **Task Completed:** Add to Recent Activity
2. **New Pending:** Update Pending Tasks count
3. **Approval Needed:** Add to Pending Approvals
4. **Alert Condition:** Add to Alerts section
5. **Scheduled:** Daily summary update

## Statistics Tracked

| Metric | Calculation |
|--------|-------------|
| Pending Tasks | Count of files in Needs_Action |
| Awaiting Approval | Count of files in Pending_Approval |
| Completed Today | Count of files in Done (today) |
| Last Activity | Timestamp of last update |

## Alert Conditions

Generate alerts for:
- More than 10 pending items
- Approval waiting > 24 hours
- High-priority tasks detected
- Error conditions in logs

## Examples

### Example 1: Update After Task Completion

**Trigger:** Task moved to Done

**Update:**
```markdown
## Recent Activity
- [2026-03-28 10:30] Processed: FILE_task_20260328
```

### Example 2: Add Pending Approval

**Trigger:** New file in Pending_Approval

**Update:**
```markdown
## Pending Approvals
- PAYMENT_Client_A: $500 invoice payment
```

### Example 3: Daily Summary

**Trigger:** Scheduled daily update

**Update:**
```markdown
## Quick Stats
| Metric | Value |
|--------|-------|
| Pending Tasks | 3 |
| Awaiting Approval | 1 |
| Completed Today | 5 |
```

## Formatting Rules

1. **Timestamps:** Use format `[YYYY-MM-DD HH:MM]`
2. **Activity:** Start with verb (Processed, Created, Updated)
3. **Stats:** Update all metrics on each run
4. **Priorities:** Show max 5 items
5. **Alerts:** Show only active/unresolved

## Related Skills

- task-manager: Provides completion data
- file-processor: Provides processing activity
- approval-handler: Provides approval status

---

*AI Employee v0.1 - Bronze Tier*
