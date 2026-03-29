# Silver Tier Implementation Guide

**Personal AI Employee Hackathon 0**
**Tier:** Silver (Functional Assistant)
**Estimated Setup Time:** 20-30 hours

## Overview

This document provides step-by-step instructions for implementing the Silver Tier of the Personal AI Employee system. Silver Tier builds upon the Bronze Tier foundation by adding multiple watchers, MCP server integration, human-in-the-loop approvals, and scheduling.

## Silver Tier Requirements

1. ✅ All Bronze Tier requirements
2. ✅ Two or more Watcher scripts (Gmail + WhatsApp + LinkedIn)
3. ✅ Auto-posting to LinkedIn for business promotion
4. ✅ Claude reasoning loop that creates Plan.md files
5. ✅ One working MCP server for external action (email-mcp)
6. ✅ Human-in-the-loop approval workflow
7. ✅ Basic scheduling via Windows Task Scheduler
8. ✅ All AI functionality implemented as Agent Skills

## Quick Start

### 1. Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
playwright install chromium
```

### 2. Setup Gmail API (Optional but Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to project root
6. First run will open browser for authorization

### 3. Setup WhatsApp (Optional)

WhatsApp watcher uses WhatsApp Web. First run requires QR code scan:

1. Run: `python scripts/whatsapp_watcher.py`
2. Open WhatsApp on phone
3. Go to Settings > Linked Devices
4. Scan QR code when prompted
5. Session saved for future runs

### 4. Start Silver Tier

```bash
start-silver-tier.bat
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SILVER TIER                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Gmail     │  │  WhatsApp   │  │  Filesystem │         │
│  │   Watcher   │  │   Watcher   │  │   Watcher   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│                          ▼                                  │
│              ┌─────────────────────┐                        │
│              │   Needs_Action/     │                        │
│              │   (Action Files)    │                        │
│              └──────────┬──────────┘                        │
│                         │                                   │
│                         ▼                                   │
│  ┌───────────────────────────────────────────┐             │
│  │        Claude Code + Skills               │             │
│  │  - plan-generator                         │             │
│  │  - approval-handler                       │             │
│  │  - task-manager                           │             │
│  └───────────────────┬───────────────────────┘             │
│                      │                                      │
│         ┌────────────┼────────────┐                        │
│         │            │            │                        │
│         ▼            ▼            ▼                        │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐                │
│  │ Pending/  │ │ Approved/ │ │   Done/   │                │
│  │ Approval  │ │  (MCP)    │ │           │                │
│  └───────────┘ └───────────┘ └───────────┘                │
│                      │                                      │
│                      ▼                                      │
│              ┌───────────────┐                              │
│              │  email-mcp    │                              │
│              │  linkedin-    │                              │
│              │  poster       │                              │
│              └───────────────┘                              │
│                                                              │
│  ┌───────────────────────────────────────────┐             │
│  │         Scheduling (Task Scheduler)       │             │
│  │  - Daily Briefing (8:00 AM)               │             │
│  │  - Weekly Audit (Monday 7:00 AM)          │             │
│  └───────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Watcher Scripts

#### Gmail Watcher (`scripts/gmail_watcher.py`)

Monitors Gmail for new unread messages.

**Features:**
- OAuth 2.0 authentication
- Keyword-based prioritization
- Attachment detection
- Known contact identification

**Setup:**
```bash
# Download credentials.json from Google Cloud Console
# Place in project root
python scripts/gmail_watcher.py
```

**Configuration:**
- Check interval: 120 seconds
- Priority keywords: urgent, asap, invoice, payment, important, deadline

#### WhatsApp Watcher (`scripts/whatsapp_watcher.py`)

Monitors WhatsApp Web for new messages.

**Features:**
- Session persistence
- Keyword detection
- Group chat support
- Priority flagging

**Setup:**
```bash
python scripts/whatsapp_watcher.py
# Scan QR code on first run
```

**Configuration:**
- Check interval: 30 seconds
- Priority keywords: urgent, asap, invoice, payment, help

#### LinkedIn Poster (`scripts/linkedin_poster.py`)

Automates posting to LinkedIn for business promotion.

**Features:**
- Approval workflow
- Template-based posts
- Session persistence
- Post tracking

**Usage:**
1. Create post in `Needs_Action/LINKEDIN_*.md`
2. Approval request created automatically
3. Move approval to `Approved/` to publish
4. Post tracked in `Logs/linkedin_posts.jsonl`

### 2. MCP Server (email-mcp)

Model Context Protocol server for sending emails.

**Location:** `mcp-servers/email-mcp/`

**Installation:**
```bash
cd mcp-servers/email-mcp
npm install
```

**Configuration:**
Create `.env` file:
```
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```

**Tools:**
- `send_email` - Send email immediately
- `draft_email` - Create draft for review
- `search_emails` - Search Gmail (Gmail provider only)

### 3. Approval Handler Skill

**Location:** `skills/approval-handler/SKILL.md`

**Silver Tier Features:**
- Auto-approval rules
- Priority levels (Critical, High, Normal, Low)
- Expiration handling
- Audit logging
- MCP integration

**Approval Categories:**

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Payments | < $50 recurring | New payees, > $100 |
| Emails | Known contacts | New contacts, bulk |
| LinkedIn | Business templates | Personal opinions |

### 4. Plan Generator Skill

**Location:** `skills/plan-generator/SKILL.md`

Creates structured Plan.md files for Claude reasoning loop.

**Plan Structure:**
```markdown
---
type: plan
title: Email Processing
created: 2026-03-28T10:00:00Z
status: in_progress
---

# Plan: Title

## Objective
Clear statement of what this plan achieves.

## Steps
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Dependencies
Step 2 depends on: Step 1

## Success Criteria
- [ ] All criteria met
```

### 5. Scheduling

**Script:** `scripts/scheduler.py`

**Commands:**
```bash
# Install scheduled tasks
python scripts/scheduler.py install

# Check status
python scripts/scheduler.py status

# Remove tasks
python scripts/scheduler.py remove

# Run specific task
python scripts/scheduler.py run AI_Employee_Daily_Briefing
```

**Default Tasks:**
- `AI_Employee_Daily_Briefing` - Daily at 8:00 AM
- `AI_Employee_Weekly_Audit` - Monday at 7:00 AM
- `AI_Employee_Email_Processor` - Every 15 minutes
- `AI_Employee_Watcher_Health` - Every hour

## Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── Needs_Action/          # New items to process
├── Plans/                 # Claude action plans
├── Done/                  # Completed tasks
├── Pending_Approval/      # Awaiting approval
├── Approved/              # Approved actions
├── Rejected/              # Rejected actions
├── Logs/                  # Audit logs
├── Briefings/             # Daily/Weekly briefings
├── Audits/                # Business audits
└── Files/                 # Processed files
```

## Testing

Run the Silver Tier test suite:

```bash
python scripts/test_silver_tier.py
```

**Tests:**
1. Watcher scripts (2+ required)
2. MCP server setup
3. Approval workflow
4. Plan generator skill
5. Scheduling setup
6. Vault structure
7. Dependencies

## Workflow Examples

### Example 1: Email Processing

1. **Detection:** Gmail Watcher finds new email from client
2. **Action File:** Creates `Needs_Action/EMAIL_*.md`
3. **Plan:** Claude creates `Plans/Email_Processing_*.md`
4. **Approval:** If new contact, creates approval request
5. **Human Review:** Move approval to `Approved/`
6. **Action:** email-mcp sends reply
7. **Complete:** Move to `Done/`, update Dashboard

### Example 2: LinkedIn Post

1. **Create:** Claude drafts post in `Needs_Action/LINKEDIN_*.md`
2. **Approval:** Creates `Pending_Approval/APPROVAL_LINKEDIN_*.md`
3. **Human Review:** Move to `Approved/`
4. **Post:** linkedin_poster.py publishes
5. **Log:** Entry in `Logs/linkedin_posts.jsonl`

### Example 3: WhatsApp Response

1. **Detection:** WhatsApp Watcher finds "urgent invoice" message
2. **Priority:** Flagged as high priority
3. **Action File:** Created in `Needs_Action/`
4. **Plan:** Claude creates response plan
5. **Approval:** Required for external response
6. **Execute:** Send WhatsApp reply
7. **Archive:** Move to `Done/`

## Security Considerations

### Credential Management

- Never commit credentials to git
- Use `.env` file (add to `.gitignore`)
- Rotate passwords monthly
- Use app-specific passwords for Gmail

### Approval Boundaries

| Action | Auto | Approval |
|--------|------|----------|
| Email reply | Known contacts | New contacts |
| Payment | < $50 recurring | All new payees |
| LinkedIn | Business templates | Personal content |

### Audit Logging

All actions logged to:
- `Logs/approvals.jsonl` - Approval decisions
- `Logs/actions.jsonl` - Executed actions
- `Logs/errors.jsonl` - Error tracking

## Troubleshooting

### Gmail Watcher Issues

**Problem:** "Credentials not found"
**Solution:** Download credentials.json from Google Cloud Console

**Problem:** "Token expired"
**Solution:** Delete token.json, re-authenticate

### WhatsApp Watcher Issues

**Problem:** "Not authenticated"
**Solution:** Run watcher, scan QR code

**Problem:** "No messages detected"
**Solution:** Check WhatsApp Web is accessible, session folder exists

### LinkedIn Poster Issues

**Problem:** "Not logged in"
**Solution:** Run manually, login in browser, session saved

### MCP Server Issues

**Problem:** "Module not found"
**Solution:** Run `npm install` in email-mcp folder

**Problem:** "SMTP authentication failed"
**Solution:** Use app-specific password for Gmail

## Next Steps: Gold Tier

To advance to Gold Tier, add:
1. Odoo accounting integration
2. Facebook/Instagram integration
3. Twitter (X) integration
4. Weekly Business Audit with CEO Briefing
5. Error recovery and audit logging
6. Ralph Wiggum loop for autonomous completion

## Support

- Documentation: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- Wednesday Meetings: 10:00 PM Zoom (ID: 871 8870 7642)
- Recordings: https://www.youtube.com/@panaversity

---

*AI Employee v0.2 - Silver Tier*
*Generated: 2026-03-29*
