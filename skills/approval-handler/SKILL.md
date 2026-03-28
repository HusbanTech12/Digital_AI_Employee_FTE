# Approval Handler Skill

**Name:** approval-handler  
**Version:** 1.0  
**Tier:** Bronze  

## Description

Handles human-in-the-loop approval workflows. Creates approval request files for sensitive actions, processes approved items, and handles rejections with proper logging.

## Capabilities

- Create approval request files
- Track approval status
- Process approved actions
- Handle rejections gracefully
- Log all approval decisions
- Escalate time-sensitive requests

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

Approval request structure:
```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
created: 2026-03-28T10:00:00Z
expires: 2026-03-29T10:00:00Z
status: pending
---

## Action Details
- Action Type: Payment
- Amount: $500.00
- Recipient: Client A
- Reason: Invoice #1234

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

## Output Format

Processes from:
- `AI_Employee_Vault/Approved/` - Execute actions
- `AI_Employee_Vault/Rejected/` - Log and archive

## Approval Categories

| Category | Auto-Approve | Require Approval |
|----------|--------------|------------------|
| Payments | < $50 recurring | All new payees, > $100 |
| Emails | Known contacts | New contacts, bulk sends |
| Social Media | Scheduled posts | Replies, DMs |
| File Operations | Create, read | Delete, move outside vault |

## Workflow

### Creating Approval Request

1. Identify action requiring approval
2. Create file in Pending_Approval
3. Include all relevant details
4. Set expiration if time-sensitive
5. Update Dashboard with pending item

### Processing Approval

1. Check Approved folder for files
2. Read approval details
3. Execute the approved action
4. Log the execution
5. Move to Done folder
6. Update Dashboard

### Processing Rejection

1. Check Rejected folder for files
2. Read rejection details
3. Log the rejection
4. Archive the file
5. Update Dashboard
6. Notify if follow-up needed

## Examples

### Example 1: Payment Approval

**Request:**
```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
---

## Payment Details
- Amount: $500.00
- To: Client A
- Reference: Invoice #1234
```

**After Approval:** Execute payment, log transaction

### Example 2: Email Approval

**Request:**
```markdown
---
type: approval_request
action: send_email
to: newclient@example.com
subject: Proposal
---

## Email Details
- To: newclient@example.com
- Subject: Proposal
- Attachment: proposal.pdf
```

**After Approval:** Send email via MCP

### Example 3: Bulk Action Approval

**Request:**
```markdown
---
type: approval_request
action: bulk_email
count: 50
campaign: Newsletter
---

## Bulk Email Details
- Recipients: 50
- Campaign: Monthly Newsletter
```

**After Approval:** Send bulk emails

## Time-Sensitive Handling

For urgent approvals:
1. Set expires timestamp
2. Add URGENT flag to filename
3. Create Dashboard alert
4. If expired: escalate to human

## Logging Format

```json
{
  "timestamp": "2026-03-28T10:30:00Z",
  "action_type": "payment",
  "amount": 500.00,
  "approval_status": "approved",
  "approved_by": "human",
  "executed_at": "2026-03-28T10:35:00Z",
  "result": "success"
}
```

## Error Handling

- **Expired Approval:** Notify human, archive request
- **Failed Execution:** Log error, notify human, retry option
- **Invalid Request:** Reject with explanation

## Related Skills

- task-manager: For tasks requiring approval steps
- dashboard-updater: For pending approval display
- file-processor: For file-based approval requests

---

*AI Employee v0.1 - Bronze Tier*
