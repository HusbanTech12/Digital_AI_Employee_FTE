# Gold Tier Implementation Guide

**Personal AI Employee Hackathon 0**
**Tier:** Gold (Autonomous Employee)
**Estimated Setup Time:** 40+ hours

## Overview

This document provides step-by-step instructions for implementing the Gold Tier of the Personal AI Employee system. Gold Tier builds upon Silver Tier by adding full cross-domain integration, accounting systems, multiple social media platforms, comprehensive audit logging, error recovery, and autonomous task completion.

**Gold Tier AI Integration:**
- **Ollama (Default)**: Free, local AI using Qwen2.5 models
- **DashScope (Optional)**: Cloud-based AI with API key for production use
- **qwen-agent Library**: Unified agent framework for both providers

## Gold Tier Requirements

1. ✅ All Silver Tier requirements (with Ollama integration)
2. ✅ Full cross-domain integration (Personal + Business)
3. ✅ Odoo accounting integration via MCP server
4. ✅ Facebook and Instagram integration
5. ✅ Twitter (X) integration
6. ✅ Multiple MCP servers for different action types
7. ✅ Weekly Business and Accounting Audit with CEO Briefing
8. ✅ Error recovery and graceful degradation
9. ✅ Comprehensive audit logging
10. ✅ Ralph Wiggum loop for autonomous multi-step task completion
11. ✅ All AI functionality using qwen-agent with Ollama/DashScope

## Quick Start

### 1. Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
playwright install chromium
```

### 2. Setup Ollama (Required - Local AI)

**If not already done:**
```bash
# Install Ollama from: https://ollama.com/download

# Download Qwen model (recommended)
ollama pull qwen2.5:7b

# Or use the model you have
ollama pull qwen2.5:1.5b

# Test it works
ollama run qwen2.5:1.5b "Hello!"
```

### 3. Configure Environment (.env file)

Create `.env` file in project root:

```bash
# AI Provider Configuration
AI_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:1.5b

# Email Configuration (for email-mcp)
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# Odoo Configuration (optional)
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

### 4. Setup MCP Servers

```bash
# Email MCP (Silver Tier)
cd mcp-servers/email-mcp
npm install

# Odoo MCP (Gold Tier)
cd mcp-servers/odoo-mcp
npm install
```

### 5. Start Gold Tier

```bash
# Using batch file (Windows)
start-gold-tier.bat

# Or run orchestrator directly
cd scripts
python orchestrator.py --vault ..\AI_Employee_Vault --ollama --once
```

### 6. Run Tests

```bash
python scripts/test_gold_tier.py
python scripts/test_ollama_integration.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GOLD TIER                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Gmail   │ │ WhatsApp │ │   File   │ │ LinkedIn │ │   FB/IG  │  │
│  │  Watcher │ │  Watcher │ │  Watcher │ │  Poster  │ │  Watcher │  │
│  └─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘  │
│        │            │            │            │            │        │
│        └────────────┴────────────┴────────────┴────────────┘        │
│                             │                                        │
│                             ▼                                        │
│              ┌─────────────────────────┐                            │
│              │    Needs_Action/        │                            │
│              │    (Action Files)       │                            │
│              └───────────┬─────────────┘                            │
│                          │                                          │
│                          ▼                                          │
│  ┌───────────────────────────────────────────────────┐             │
│  │        Claude Code + Gold Skills                  │             │
│  │  - plan-generator v2.0                            │             │
│  │  - approval-handler v2.0                          │             │
│  │  - audit-logger                                   │             │
│  │  - error-recovery                                 │             │
│  └───────────────────┬───────────────────────────────┘             │
│                      │                                              │
│         ┌────────────┼────────────┬────────────┐                   │
│         │            │            │            │                   │
│         ▼            ▼            ▼            ▼                   │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐         │
│  │  email-   │ │  odoo-    │ │  social-  │ │  Ralph    │         │
│  │   mcp     │ │   mcp     │ │   mcp     │ │  Wiggum   │         │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘         │
│                                                                      │
│  ┌───────────────────────────────────────────────────┐             │
│  │         Gold Tier Systems                         │             │
│  │  - Comprehensive Audit Logging                    │             │
│  │  - Error Recovery & Circuit Breakers              │             │
│  │  - Weekly Business Audit + CEO Briefing           │             │
│  │  - Cross-domain Integration                       │             │
│  └───────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Odoo Accounting Integration (MCP Server)

**Location:** `mcp-servers/odoo-mcp/`

**Features:**
- Invoice creation and management
- Payment registration
- Financial summary reporting
- Partner (customer/supplier) management

**Tools:**
| Tool | Description |
|------|-------------|
| `create_invoice` | Create customer invoices |
| `get_invoices` | Fetch invoices with filtering |
| `validate_invoice` | Post/validate draft invoices |
| `register_payment` | Record payments against invoices |
| `get_financial_summary` | Get receivables, payables, net position |
| `get_partners` | Search customers/suppliers |

**Setup:**
```bash
cd mcp-servers/odoo-mcp
npm install
```

**Configuration:**
```bash
# In .env file
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=your_api_key
```

### 2. Facebook/Instagram Integration

**Script:** `scripts/facebook_instagram_watcher.py`

**Features:**
- Cross-platform posting
- Session persistence
- Engagement tracking
- Summary generation

**Usage:**
```python
from facebook_instagram_watcher import FacebookInstagramWatcher

watcher = FacebookInstagramWatcher(vault_path)
posts = watcher.check_for_posts()
for post in posts:
    if post.platform == 'facebook':
        watcher.post_to_facebook(post)
```

**Note:** Instagram requires image uploads. For production, use Instagram Graph API.

### 3. Twitter (X) Integration

**Script:** `scripts/twitter_watcher.py`

**Features:**
- Tweet posting with thread support
- Automatic thread splitting for long content
- Session persistence
- Engagement tracking

**Thread Support:**
Content longer than 280 characters is automatically split into threads.

**Warning:** Twitter has strict automation policies. Use responsibly and consider official API.

### 4. Comprehensive Audit Logging

**Script:** `scripts/audit_logger.py`

**Features:**
- Centralized logging for all actions
- Daily log rotation
- Search and filter capabilities
- Statistics and reporting
- Compliance report generation

**Usage:**
```python
from audit_logger import AuditLogger

logger = AuditLogger(vault_path)

# Log an action
logger.log_action(
    action_type='email_send',
    details={'to': 'client@example.com'},
    result='success',
    category='email',
    duration_ms=1250
)

# Search logs
entries = logger.search(
    action_type='email_send',
    result='success',
    limit=100
)

# Get statistics
stats = logger.get_statistics(days=7)
```

**Log Structure:**
```
Logs/
├── Audit/
│   ├── audit_2026-03-29.jsonl    # Daily log
│   ├── audit_index.json          # Search index
│   └── compliance_report.md      # Generated reports
```

### 5. Error Recovery System

**Script:** `scripts/error_recovery.py`

**Features:**
- Retry with exponential backoff
- Circuit breaker pattern
- Fallback functions
- Error categorization
- Recovery statistics

**Usage:**
```python
from error_recovery import ErrorRecovery, RecoveryStrategy

recovery = ErrorRecovery(vault_path)

@recovery.retry(
    max_attempts=3,
    strategy=RecoveryStrategy.EXPONENTIAL_BACKOFF,
    fallback=lambda: "Fallback result"
)
def send_email():
    # Email sending code
    pass
```

**Circuit Breaker:**
```python
cb = recovery.get_circuit_breaker('email_service')
status = cb.get_status()
# {'state': 'closed', 'failure_count': 0, ...}
```

### 6. Ralph Wiggum Loop

**Script:** `scripts/ralph_wiggum_loop.py`

**Features:**
- Autonomous multi-step task completion
- Stop hook pattern
- Iteration tracking
- Completion verification

**Usage:**
```python
from ralph_wiggum_loop import RalphWiggumLoop

loop = RalphWiggumLoop(vault_path)

# Register completion checker
def email_completion_checker(task):
    emails = list(loop.needs_action_dir.glob('EMAIL_*.md'))
    return len(emails) == 0

loop.register_completion_checker('email', email_completion_checker)

# Run autonomous task
task = loop.run(
    prompt="Process all emails in Needs_Action folder",
    completion_criteria="Move all processed emails to Done/",
    max_iterations=10
)
```

**Stop Hook Pattern:**
1. Claude works on task
2. Claude tries to exit
3. Stop hook checks: Is task complete?
4. If NO → Block exit, re-inject prompt
5. Repeat until complete

### 7. Weekly Business Audit & CEO Briefing

**Script:** `scripts/gold_weekly_audit.py`

**Features:**
- Accounting data integration
- Multi-platform social media summary
- Bottleneck identification
- Proactive suggestions with ROI
- Comprehensive CEO Briefing

**Usage:**
```bash
python scripts/gold_weekly_audit.py
```

**CEO Briefing Sections:**
- Executive Summary with health indicators
- Financial Performance (revenue, expenses, net income)
- Task Completion metrics
- Social Media Summary (all platforms)
- Bottlenecks Identified
- Proactive Suggestions
- Recommended Actions

## Vault Structure (Gold Tier)

```
AI_Employee_Vault/
├── Dashboard.md                    # Main dashboard
├── Company_Handbook.md             # Rules and contacts
├── Business_Goals.md               # Business objectives
├── Accounting/
│   └── transactions.json           # Transaction data
├── Needs_Action/                   # Pending items
├── Plans/                          # Claude action plans
├── Done/                           # Completed tasks
├── Pending_Approval/               # Awaiting approval
├── Approved/                       # Approved actions
├── Rejected/                       # Rejected actions
├── Logs/
│   ├── Audit/                      # Audit logs
│   ├── Recovery/                   # Error recovery logs
│   └── Ralph_Loop/                 # Ralph loop logs
├── Briefings/                      # CEO briefings
├── Audits/                         # Business audits
└── Files/                          # Processed files
```

## Gold Tier Skills

### Updated Skills

| Skill | Version | Tier | New Features |
|-------|---------|------|--------------|
| approval-handler | v2.0 | Silver→Gold | Auto-approval rules, audit integration |
| plan-generator | v2.0 | Silver→Gold | Ralph Wiggum integration |
| audit-logger | v1.0 | Gold | New skill |
| error-recovery | v1.0 | Gold | New skill |

### Creating Gold Tier Skills

```markdown
# Skill Name

**Version:** 1.0 (Gold Tier)

## Description
Gold Tier skill with audit logging and error recovery.

## Integration
- Logs all actions via audit_logger
- Uses error_recovery for graceful degradation
- Supports Ralph Wiggum loop
```

## Testing

Run the Gold Tier test suite:

```bash
python scripts/test_gold_tier.py
```

**Tests:**
1. Silver Tier requirements (prerequisite)
2. Odoo accounting integration
3. Facebook/Instagram integration
4. Twitter (X) integration
5. Multiple MCP servers
6. Weekly audit & CEO briefing
7. Error recovery system
8. Audit logging
9. Ralph Wiggum loop
10. Vault structure

## Workflow Examples

### Example 1: Invoice Creation and Sending

1. **Detection:** Gmail Watcher finds invoice request
2. **Plan:** Claude creates `Plans/Invoice_Plan_*.md`
3. **Odoo:** `odoo-mcp` creates invoice
4. **Email:** `email-mcp` sends invoice
5. **Audit:** All actions logged via `audit_logger`
6. **Approval:** Required for new clients
7. **Complete:** Move to `Done/`, update Dashboard

### Example 2: Multi-Platform Social Media Campaign

1. **Create:** Claude drafts campaign content
2. **Approval:** Create approval requests for each platform
3. **Human Review:** Move approvals to `Approved/`
4. **Post:**
   - LinkedIn via `linkedin_poster.py`
   - Facebook via `facebook_instagram_watcher.py`
   - Twitter via `twitter_watcher.py`
5. **Track:** Engagement logged to `Logs/`
6. **Summary:** Weekly summary in CEO Briefing

### Example 3: Autonomous Email Processing (Ralph Wiggum)

1. **Task:** "Process all emails in Needs_Action"
2. **Loop Start:** Ralph Wiggum Loop creates task
3. **Iteration 1:** Claude reads emails, categorizes
4. **Iteration 2:** Claude creates approval requests
5. **Iteration 3:** Claude sends approved emails
6. **Completion Check:** Needs_Action empty?
7. **Loop End:** Task complete, move to Done

## Error Handling

### Graceful Degradation

| Error Type | Handling |
|------------|----------|
| Network timeout | Retry with backoff |
| API rate limit | Circuit breaker, wait |
| Authentication | Alert human, skip |
| Invalid data | Log error, continue |

### Circuit Breaker States

- **Closed:** Normal operation
- **Open:** Service failing, stop requests
- **Half-Open:** Testing if service recovered

## Security Considerations

### Credential Management

- Never commit credentials
- Use `.env` file (in `.gitignore`)
- Rotate passwords monthly
- Use app-specific passwords

### Audit Trail

All actions logged with:
- Timestamp
- Actor (AI/human)
- Action type
- Result
- Duration

### Approval Boundaries (Gold Tier)

| Action | Auto | Approval Required |
|--------|------|-------------------|
| Payments | < $50 recurring | > $100, new payees |
| Invoices | Standard templates | Custom terms |
| Social Media | Business updates | Personal opinions |
| Email | Known contacts | New contacts, bulk |

## Troubleshooting

### Odoo MCP Issues

**Problem:** "Connection refused"
**Solution:** Check Odoo server is running, URL correct

**Problem:** "Authentication failed"
**Solution:** Verify username/password, check API key

### Social Media Issues

**Problem:** "Not logged in"
**Solution:** Run script manually, login, session saved

**Problem:** "Post failed"
**Solution:** Check content length, image requirements

### Ralph Wiggum Loop Issues

**Problem:** "Infinite loop"
**Solution:** Set appropriate max_iterations, verify completion criteria

**Problem:** "Task never completes"
**Solution:** Review completion checker logic

## Next Steps: Platinum Tier

To advance to Platinum Tier, add:

1. **24/7 Cloud Deployment**
   - Deploy to Oracle Cloud Free VM
   - Always-on watchers and orchestrator
   - Health monitoring

2. **Work-Zone Specialization**
   - Cloud: Email triage, draft replies, social drafts
   - Local: Approvals, WhatsApp, payments

3. **Synced Vault**
   - Git-based vault sync
   - Claim-by-move rule for agents
   - Single-writer Dashboard.md

4. **Odoo on Cloud VM**
   - HTTPS with Let's Encrypt
   - Automated backups
   - Health monitoring

## Support Resources

- **Main Documentation:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Silver Tier Guide:** `SILVER_TIER.md`
- **Wednesday Meetings:** 10:00 PM Zoom (ID: 871 8870 7642)
- **YouTube:** https://www.youtube.com/@panaversity

---

*AI Employee v0.3 - Gold Tier*
*Last Updated: 2026-03-29*
