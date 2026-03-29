# Approval Handler Skill

**Name:** approval-handler
**Version:** 2.0
**Tier:** Silver

## Description

Handles human-in-the-loop (HITL) approval workflows. Creates approval request files for sensitive actions, processes approved items, and handles rejections with proper logging.

This skill implements the complete Silver Tier approval workflow with:
- Automatic approval categorization
- Time-sensitive escalation
- Multi-action approval support
- Comprehensive audit logging

## Capabilities

- Create approval request files with automatic categorization
- Track approval status and expiration
- Process approved actions via MCP servers
- Handle rejections gracefully
- Log all approval decisions with audit trail
- Escalate time-sensitive requests
- Auto-approve based on configured rules
- Batch approval support for related actions

## Usage

```bash
qwen --skill approval-handler "Process all approved items"
```

Or in prompts:
```
Use the approval-handler skill to request approval for this payment.
```

## Input Format

Creates requests in: `AI_Employee_Vault/Pending_Approval/`

### Approval Request Structure (Silver Tier)

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
category: finance
priority: normal
created: 2026-03-28T10:00:00Z
expires: 2026-03-29T10:00:00Z
status: pending
auto_approve_eligible: false
requires_mcp: email-mcp
---

## Action Details
- Action Type: Payment
- Amount: $500.00
- To: Client A
- Reference: Invoice #1234
- Reason: Monthly service payment

## Risk Assessment
- New Payee: No
- Amount Threshold: Within limits
- Recurring: Yes (monthly)

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.

## To Request Changes
Edit this file and add a "changes_requested" section.
```

## Output Format

Processes from:
- `AI_Employee_Vault/Approved/` - Execute actions via MCP
- `AI_Employee_Vault/Rejected/` - Log and archive
- `AI_Employee_Vault/Done/` - Completed actions

## Approval Categories & Rules

### Silver Tier Auto-Approval Rules

| Category | Auto-Approve Conditions | Require Approval |
|----------|------------------------|------------------|
| **Payments** | < $50 AND recurring payee | All new payees, > $100, one-time > $50 |
| **Emails** | Known contacts, non-bulk | New contacts, bulk sends (>10), contains attachments |
| **Social Media** | Scheduled posts, business updates | Replies to comments, DMs, controversial topics |
| **File Operations** | Create, read, copy | Delete, move outside vault, sensitive folders |
| **LinkedIn Posts** | Business updates from template | Personal opinions, political content |

### Priority Levels

| Priority | Response Time | Escalation |
|----------|--------------|------------|
| **Critical** | 15 minutes | Immediate notification |
| **High** | 1 hour | Dashboard alert |
| **Normal** | 24 hours | Daily summary |
| **Low** | 7 days | Weekly summary |

## Workflow

### Creating Approval Request

1. Identify action requiring approval
2. Categorize action (payment, email, social media, etc.)
3. Check auto-approval rules
4. If auto-approve eligible and conditions met → execute directly
5. Otherwise, create file in Pending_Approval
6. Include all relevant details and risk assessment
7. Set expiration if time-sensitive
8. Update Dashboard with pending item
9. Log the request

### Processing Approval

1. Check Approved folder for files
2. Read approval details
3. Validate approval is still valid (not expired)
4. Execute the approved action via MCP server
5. Log the execution with result
6. Move to Done folder
7. Update Dashboard
8. Send confirmation if configured

### Processing Rejection

1. Check Rejected folder for files
2. Read rejection details
3. Log the rejection with reason
4. Archive the file
5. Update Dashboard
6. Notify if follow-up needed
7. Move to Logs/Rejected/

### Auto-Approval Flow

1. Action identified
2. Check against auto-approval rules
3. If eligible:
   - Log auto-approval decision
   - Execute action
   - Create summary in Done folder
4. If not eligible:
   - Create standard approval request

## Examples

### Example 1: Payment Approval

**Request:**
```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
category: finance
priority: normal
created: 2026-03-28T10:00:00Z
---

## Payment Details
- Amount: $500.00
- To: Client A
- Reference: Invoice #1234
- Reason: Monthly service payment

## Risk Assessment
- New Payee: No (paid 2025-12, 2026-01, 2026-02)
- Amount Threshold: Within monthly limit
- Recurring: Yes (monthly)

## To Approve
Move this file to /Approved folder.
```

**After Approval:** Execute payment via MCP, log transaction, move to Done

### Example 2: Email Approval (New Contact)

**Request:**
```markdown
---
type: approval_request
action: send_email
to: newclient@example.com
subject: Proposal
category: communication
priority: high
created: 2026-03-28T11:00:00Z
---

## Email Details
- To: newclient@example.com (NEW CONTACT)
- Subject: Proposal
- Body: Please find attached our proposal...
- Attachment: proposal.pdf

## Risk Assessment
- New Contact: Yes
- Contains Attachment: Yes
- Bulk Send: No

## To Approve
Move this file to /Approved folder.
```

**After Approval:** Send email via email-mcp, log send result

### Example 3: LinkedIn Post Approval

**Request:**
```markdown
---
type: approval_request
action: linkedin_post
title: Business_Update_March
category: social_media
priority: low
created: 2026-03-28T12:00:00Z
---

## Post Content
🚀 Exciting business update!

We've achieved great progress this month...

#Business #Growth

## Risk Assessment
- Content Type: Business update
- Template Used: Yes
- Controversial: No

## To Approve
Move this file to /Approved folder.
```

**After Approval:** Post to LinkedIn via linkedin_poster.py

### Example 4: Auto-Approved Payment (Recurring, Under Threshold)

**Action:** $30/month software subscription

**Auto-Approval Log:**
```json
{
  "timestamp": "2026-03-28T08:00:00Z",
  "action_type": "payment",
  "amount": 30.00,
  "recipient": "Software Company",
  "approval_status": "auto_approved",
  "reason": "Recurring payment under $50 threshold",
  "executed_at": "2026-03-28T08:00:01Z"
}
```

## Time-Sensitive Handling

For urgent approvals:

1. Set `priority: critical` or `priority: high`
2. Set `expires` timestamp
3. Add `URGENT_` prefix to filename
4. Create Dashboard alert immediately
5. If expired:
   - Log expiration
   - Move to Rejected/Expired
   - Escalate to human via notification

### Expiration Handling

```markdown
---
type: approval_request
action: time_sensitive_action
priority: critical
created: 2026-03-28T10:00:00Z
expires: 2026-03-28T11:00:00Z
---

## URGENT: Action Required Within 1 Hour

[Details]

**EXPIRATION:** This request expires at 2026-03-28T11:00:00Z
```

## Logging Format

All approval decisions are logged in `Logs/approvals.jsonl`:

```json
{
  "timestamp": "2026-03-28T10:30:00Z",
  "action_type": "payment",
  "amount": 500.00,
  "recipient": "Client A",
  "approval_status": "approved",
  "approved_by": "human",
  "approved_at": "2026-03-28T10:25:00Z",
  "executed_at": "2026-03-28T10:30:00Z",
  "result": "success",
  "execution_time_ms": 1250
}
```

### Log Categories

- `approvals.jsonl` - All approval decisions
- `auto_approvals.jsonl` - Auto-approved actions
- `rejections.jsonl` - Rejected actions
- `expired.jsonl` - Expired approvals
- `errors.jsonl` - Execution errors

## Error Handling

### Expired Approval
- **Action:** Notify human, archive request
- **Log:** Entry in expired.jsonl
- **File:** Move to Rejected/Expired/

### Failed Execution
- **Action:** Log error, notify human, offer retry
- **Log:** Entry in errors.jsonl
- **File:** Keep in Approved for retry or move to Done with error note

### Invalid Request
- **Action:** Reject with explanation
- **Log:** Entry in rejections.jsonl
- **File:** Move to Rejected/Invalid/

### MCP Server Unavailable
- **Action:** Retry up to 3 times, then notify
- **Log:** Entry in errors.jsonl
- **File:** Keep in Approved with retry count

## Configuration

Create `approval_rules.json` in vault root:

```json
{
  "auto_approve": {
    "payments": {
      "max_amount": 50,
      "recurring_only": true,
      "known_payees_only": true
    },
    "emails": {
      "known_contacts_only": true,
      "max_recipients": 10,
      "allow_attachments": false
    },
    "social_media": {
      "allow_scheduled": true,
      "require_template": true
    }
  },
  "thresholds": {
    "payment_requiring_approval": 100,
    "bulk_email_count": 10
  },
  "escalation": {
    "critical_timeout_minutes": 15,
    "high_timeout_minutes": 60,
    "normal_timeout_hours": 24
  }
}
```

## Related Skills

- **task-manager:** For tasks requiring approval steps
- **dashboard-updater:** For pending approval display
- **file-processor:** For file-based approval requests
- **email-mcp:** For email sending approvals

## MCP Integration

This skill integrates with MCP servers for action execution:

| MCP Server | Actions |
|------------|---------|
| email-mcp | send_email, draft_email |
| linkedin-mcp | create_post, schedule_post |
| payment-mcp | initiate_payment, schedule_payment |
| file-mcp | move_file, delete_file |

---

*AI Employee v0.2 - Silver Tier*
