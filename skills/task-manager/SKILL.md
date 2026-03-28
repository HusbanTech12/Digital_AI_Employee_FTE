# Task Manager Skill

**Name:** task-manager  
**Version:** 1.0  
**Tier:** Bronze  

## Description

Manages tasks in the AI Employee system. Reads action files from Needs_Action, creates execution plans, tracks progress, and moves completed tasks to Done.

## Capabilities

- Read and parse action files from Needs_Action folder
- Create structured Plan.md files with checkboxes
- Execute tasks step-by-step
- Track task completion status
- Move completed tasks to Done folder
- Update Dashboard with activity

## Usage

```bash
qwen --skill task-manager "Process all pending tasks"
```

Or in prompts:
```
Use the task-manager skill to process items in Needs_Action.
```

## Input Format

Reads from: `AI_Employee_Vault/Needs_Action/*.md`

Action file structure:
```markdown
---
type: file_drop
created: 2026-03-28T10:00:00Z
status: pending
---

## Content
[Content to process]

## Suggested Actions
- [ ] Action 1
- [ ] Action 2
```

## Output Format

Creates plans in: `AI_Employee_Vault/Plans/`

Plan file structure:
```markdown
---
created: 2026-03-28T10:00:00Z
action_file: FILE_task_20260328.md
status: in_progress
---

# Plan: Process Task

## Objective
[Clear objective statement]

## Steps
- [ ] Read and understand the action file
- [ ] Identify required actions
- [ ] Execute actions
- [ ] Verify completion
- [ ] Move to Done folder

## Notes
[Notes during execution]
```

## Task Workflow

1. **Read:** Load action file from Needs_Action
2. **Plan:** Create Plan.md with checkboxes
3. **Execute:** Work through each step
4. **Verify:** Confirm task completion
5. **Archive:** Move to Done folder
6. **Update:** Refresh Dashboard

## Task Types

| Type | Description | Auto-Process |
|------|-------------|-------------|
| file_drop | Files dropped for processing | Yes |
| email | Email messages | No (needs approval) |
| message | Chat/WhatsApp messages | Yes |
| approval_request | Awaiting human decision | No |
| scheduled | Scheduled tasks | Yes |

## Priority Rules

1. **Urgent:** Contains keywords: urgent, asap, deadline, emergency
2. **High:** From VIP contacts, payments, invoices
3. **Normal:** Regular business tasks
4. **Low:** Administrative, cleanup, organization

## Completion Criteria

A task is complete when:
- All checkboxes in Plan.md are checked
- Action file moved to Done folder
- Dashboard updated with activity
- Any output files created in appropriate folders

## Examples

### Example 1: Process File Drop

**Input:** Action file for text file review

**Process:**
1. Read file content
2. Summarize key points
3. Create follow-up tasks if needed
4. Move to Done

**Output:** Summary in Dashboard, original file archived

### Example 2: Create Plan for Complex Task

**Input:** Action file with multiple steps

**Process:**
1. Analyze requirements
2. Create detailed Plan.md
3. Execute each step
4. Document results

**Output:** Completed plan, results logged

## Error Handling

- If task fails: Log error, create alert in Dashboard
- If stuck: Create approval request for human review
- If incomplete: Leave in Needs_Action with notes

## Related Skills

- file-processor: For initial file handling
- dashboard-updater: For activity logging
- approval-handler: For tasks needing approval

---

*AI Employee v0.1 - Bronze Tier*
