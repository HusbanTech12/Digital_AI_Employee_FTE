# Plan Generator Skill

**Name:** plan-generator
**Version:** 1.0
**Tier:** Silver

## Description

Creates structured Plan.md files for Claude Code to execute multi-step tasks. This skill implements the Silver Tier reasoning loop that breaks down complex tasks into actionable, trackable steps.

## Purpose

When Claude Code receives a complex task, this skill creates a structured plan with:
- Clear objectives
- Step-by-step actions
- Dependencies between steps
- Progress tracking
- Success criteria

## Usage

```bash
qwen --skill plan-generator "Process all items in Needs_Action"
```

Or in prompts:
```
Use the plan-generator skill to create a plan for processing the email inbox.
```

## Plan Structure

### Standard Plan.md Template

```markdown
---
type: plan
title: Email Inbox Processing
created: 2026-03-28T10:00:00Z
created_by: claude_code
status: in_progress
priority: normal
estimated_steps: 5
completed_steps: 0
---

# Plan: Email Inbox Processing

## Objective
Process all unread emails in the inbox, categorize them, and take appropriate actions.

## Context
- Source: Gmail Watcher detected 5 new emails
- Priority keywords detected: 2 emails
- Known contacts: 3 emails
- New contacts: 2 emails (require approval)

## Steps

### Step 1: Read and Categorize Emails
- [ ] Read all action files in Needs_Action/EMAIL_*
- [ ] Categorize each email (payment, inquiry, meeting, other)
- [ ] Identify emails requiring approval
- [ ] Update Dashboard with summary

### Step 2: Process Known Contact Emails
- [ ] Draft replies to known contacts
- [ ] Create approval requests for new contacts
- [ ] Flag urgent emails for immediate attention

### Step 3: Create Approval Requests
- [ ] Create approval files for new contact emails
- [ ] Create approval files for bulk sends
- [ ] Move approval files to Pending_Approval/

### Step 4: Execute Approved Actions
- [ ] Check Approved/ folder for ready actions
- [ ] Execute approved email sends via MCP
- [ ] Log all actions taken

### Step 5: Archive and Update
- [ ] Move processed emails to Done/
- [ ] Update Dashboard with completion status
- [ ] Generate summary report

## Dependencies
- Step 2 depends on: Step 1 completion
- Step 3 depends on: Step 2 completion
- Step 4 depends on: Step 3 completion AND human approval
- Step 5 depends on: All previous steps

## Success Criteria
- [ ] All emails categorized
- [ ] Approval requests created for new contacts
- [ ] Known contact emails replied to
- [ ] All files moved to appropriate folders
- [ ] Dashboard updated

## Notes
- Escalate any emails containing "urgent" or "asap"
- Check Company_Handbook.md for known contact list
- Log all actions in Logs/email_processing.jsonl

## Blockers
None currently.

## Resources
- Gmail MCP server for sending
- Company_Handbook.md for contact verification
- approval-handler skill for approval workflow
```

## Capabilities

- Parse action files from Needs_Action folder
- Generate structured plans with dependencies
- Track progress via checkboxes
- Identify required approvals
- Create success criteria
- Log plan execution progress

## Plan Categories

### Email Processing Plan
For processing emails from Gmail Watcher.

### WhatsApp Response Plan
For responding to WhatsApp messages.

### LinkedIn Posting Plan
For creating and scheduling LinkedIn posts.

### File Processing Plan
For handling dropped files.

### Multi-Domain Plan
For complex tasks spanning multiple domains.

## Workflow

### 1. Analyze Input
- Read all files in Needs_Action/
- Identify patterns and common themes
- Group related items

### 2. Create Plan
- Define clear objective
- Break down into steps
- Add dependencies
- Set success criteria

### 3. Execute Plan
- Work through steps sequentially
- Check off completed steps
- Update progress in plan

### 4. Handle Approvals
- Identify steps requiring approval
- Create approval request files
- Wait for approval before proceeding

### 5. Complete and Archive
- Verify all success criteria met
- Move plan to Done/
- Update Dashboard

## Progress Tracking

### Status Values

| Status | Description |
|--------|-------------|
| `draft` | Plan being created |
| `in_progress` | Currently executing |
| `blocked` | Waiting on approval/dependency |
| `completed` | All steps done |
| `cancelled` | Plan abandoned |

### Progress Calculation

```
Progress % = (completed_steps / total_steps) * 100
```

## Examples

### Example 1: Simple Email Response Plan

```markdown
---
type: plan
title: Respond to Client Inquiry
created: 2026-03-28T11:00:00Z
status: in_progress
---

# Plan: Respond to Client Inquiry

## Objective
Reply to client@example.com regarding their pricing inquiry.

## Steps
- [ ] Read email content
- [ ] Draft response
- [ ] Create approval request (new contact)
- [ ] Wait for approval
- [ ] Send email via MCP
- [ ] Archive to Done/

## Success Criteria
- [ ] Response sent
- [ ] Email archived
```

### Example 2: Complex Multi-Step Business Plan

```markdown
---
type: plan
title: Weekly Business Audit
created: 2026-03-28T08:00:00Z
status: in_progress
estimated_steps: 10
---

# Plan: Weekly Business Audit

## Objective
Generate weekly CEO briefing with revenue, bottlenecks, and suggestions.

## Steps
### Phase 1: Data Collection
- [ ] Read Business_Goals.md
- [ ] Scan Transactions from bank integration
- [ ] Review completed tasks in Done/
- [ ] Check pending items in Needs_Action/

### Phase 2: Analysis
- [ ] Calculate weekly revenue
- [ ] Identify delayed tasks
- [ ] Analyze subscription costs
- [ ] Compare against goals

### Phase 3: Report Generation
- [ ] Write Executive Summary
- [ ] Document Revenue section
- [ ] List Completed Tasks
- [ ] Identify Bottlenecks
- [ ] Generate Proactive Suggestions

### Phase 4: Review and Distribute
- [ ] Create approval request for report
- [ ] After approval, save to Briefings/
- [ ] Update Dashboard
- [ ] Notify via WhatsApp

## Dependencies
- Phase 2 depends on: Phase 1
- Phase 3 depends on: Phase 2
- Phase 4 depends on: Phase 3 + approval

## Success Criteria
- [ ] All data collected
- [ ] Analysis complete
- [ ] Report generated
- [ ] Report approved
- [ ] Dashboard updated
- [ ] CEO notified
```

## Integration with Other Skills

### task-manager
- Plans create tasks that task-manager tracks
- Task completion updates plan progress

### approval-handler
- Plans identify steps requiring approval
- Approval results unblock plan steps

### dashboard-updater
- Plans update Dashboard with progress
- Completed plans update statistics

## Plan Templates

### Template: Email Processing
```markdown
---
type: plan
title: Email Processing
created: {{timestamp}}
status: in_progress
---

# Plan: Email Processing

## Objective
Process all pending emails.

## Steps
- [ ] Read emails in Needs_Action/
- [ ] Categorize by type
- [ ] Create approval requests
- [ ] Execute approved actions
- [ ] Archive processed emails

## Success Criteria
- [ ] All emails processed
- [ ] Approvals requested where needed
- [ ] Dashboard updated
```

### Template: Social Media Posting
```markdown
---
type: plan
title: Social Media Posting
created: {{timestamp}}
status: in_progress
---

# Plan: Social Media Posting

## Objective
Create and schedule posts for the week.

## Steps
- [ ] Review Business_Goals.md for messaging
- [ ] Create post drafts
- [ ] Create approval requests
- [ ] Schedule approved posts
- [ ] Log scheduled posts

## Success Criteria
- [ ] Posts created for all platforms
- [ ] Posts approved
- [ ] Posts scheduled
```

## Error Handling

### Plan Execution Errors

| Error | Handling |
|-------|----------|
| Step fails | Log error, try alternative, or mark blocked |
| Approval denied | Update plan, skip step, or cancel plan |
| Dependency not met | Wait or find workaround |
| Resource unavailable | Log blocker, notify human |

### Plan Recovery

1. Identify failed step
2. Determine root cause
3. Create recovery step
4. Update plan
5. Continue or escalate

## Best Practices

1. **Clear Objectives:** Each plan should have a single, clear objective
2. **Atomic Steps:** Each step should be independently actionable
3. **Explicit Dependencies:** Document what each step depends on
4. **Measurable Criteria:** Success criteria should be verifiable
5. **Progress Updates:** Update plan as steps complete
6. **Blocker Documentation:** Note anything blocking progress

## Related Files

- `Plans/` - Folder for all plan files
- `Dashboard.md` - Progress display
- `Logs/plans.jsonl` - Plan execution logs

---

*AI Employee v0.2 - Silver Tier*
