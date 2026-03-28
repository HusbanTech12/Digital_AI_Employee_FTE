# Personal AI Employee Hackathon 0: Building Autonomous FTEs in 2026

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

## Overview

This document provides a comprehensive architectural blueprint for building a "Digital FTE" (Full-Time Equivalent)—an AI agent powered by Claude Code and Obsidian that proactively manages personal and business affairs 24/7.

## Architecture & Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **The Brain** | Claude Code | Reasoning engine |
| **The Memory/GUI** | Obsidian | Dashboard & knowledge base |
| **The Senses (Watchers)** | Python scripts | Monitor Gmail, WhatsApp, filesystems |
| **The Hands (MCP)** | MCP Servers | External actions (email, payments, browser) |

## Key Concepts

### Digital FTE vs Human FTE

- **Availability:** 168 hours/week (24/7) vs 40 hours/week
- **Monthly Cost:** $500–$2,000 vs $4,000–$8,000+
- **Scaling:** Exponential (instant duplication) vs Linear
- **Cost per Task:** ~$0.25–$0.50 vs ~$3.00–$6.00

### Architecture Layers

1. **Perception (Watchers):** Lightweight Python scripts monitor external sources
2. **Reasoning (Claude Code):** Reads, thinks, plans, and writes to Obsidian vault
3. **Action (MCP Servers):** Execute external actions with human-in-the-loop approval
4. **Persistence (Ralph Wiggum Loop):** Keeps Claude working until tasks are complete

## Hackathon Tiers

### Bronze Tier (8-12 hours)
- Obsidian vault with Dashboard.md and Company_Handbook.md
- One working Watcher script
- Claude Code reading/writing to vault
- Basic folder structure: /Inbox, /Needs_Action, /Done

### Silver Tier (20-30 hours)
- All Bronze requirements plus:
- Two or more Watcher scripts
- Auto-posting to LinkedIn
- Plan.md creation by Claude
- One working MCP server
- Human-in-the-loop approval workflow
- Basic scheduling

### Gold Tier (40+ hours)
- All Silver requirements plus:
- Full cross-domain integration
- Odoo accounting integration via MCP
- Facebook, Instagram, Twitter integration
- Weekly Business Audit with CEO Briefing
- Error recovery and audit logging
- Ralph Wiggum loop for autonomous completion

### Platinum Tier (60+ hours)
- All Gold requirements plus:
- 24/7 cloud deployment
- Cloud/Local work-zone specialization
- Delegated agents via synced vault
- Odoo on cloud VM with HTTPS and backups

## Folder Structure

```
/Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── /Needs_Action/      # New items to process
├── /Plans/             # Claude's action plans
├── /Done/              # Completed tasks
├── /Pending_Approval/  # Awaiting human approval
├── /Approved/          # Approved actions
├── /Rejected/          # Rejected actions
├── /Logs/              # Audit logs
└── /Invoices/          # Generated invoices
```

## Watcher Pattern

All Watchers follow this base structure:

```python
class BaseWatcher(ABC):
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(check_interval)
```

## Human-in-the-Loop (HITL)

For sensitive actions, Claude writes an approval request file:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
created: 2026-01-07T10:30:00Z
status: pending
---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

## Ralph Wiggum Loop

A Stop hook pattern that keeps Claude working until tasks are complete:

1. Orchestrator creates state file with prompt
2. Claude works on task
3. Claude tries to exit
4. Stop hook checks: Is task file in /Done?
5. If NO → Block exit, re-inject prompt (loop continues)
6. Repeat until complete

## Security & Privacy

### Credential Management
- Never store credentials in plain text
- Use environment variables or secrets manager
- Create `.env` file (add to `.gitignore`)
- Rotate credentials monthly

### Audit Logging
Every action must be logged:

```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "approval_status": "approved",
  "result": "success"
}
```

### Permission Boundaries

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Email replies | Known contacts | New contacts, bulk |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |

## Process Management

Use PM2 to keep watchers running:

```bash
# Install PM2
npm install -g pm2

# Start watcher
pm2 start gmail_watcher.py --interpreter python3

# Save and setup startup
pm2 save
pm2 startup
```

## Example Flow: Invoice Request

1. **Detection:** WhatsApp Watcher detects "invoice" keyword
2. **Reasoning:** Claude creates Plan.md with steps
3. **Approval:** Claude creates approval request for email send
4. **Human Review:** User moves file to /Approved
5. **Action:** Email MCP sends invoice
6. **Completion:** Files moved to /Done, Dashboard updated

## Learning Resources

### Prerequisites
- [Claude Code Fundamentals](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [Obsidian Fundamentals](https://help.obsidian.md/Getting+started)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### Core Learning
- [Claude + Obsidian Integration](https://youtube.com/watch?v=sCIS05Qt79Y)
- [Building MCP Servers](https://modelcontextprotocol.io/quickstart)
- [Gmail API Setup](https://developers.google.com/gmail/api/quickstart)
- [Playwright Automation](https://playwright.dev/python/docs/intro)

## Meeting Information

**Research and Showcase Meeting Every Wednesday:**
- **Time:** 10:00 PM on Zoom
- **First Meeting:** Wednesday, Jan 7th, 2026
- **Meeting ID:** 871 8870 7642
- **Passcode:** 744832
- **Zoom Link:** https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube:** https://www.youtube.com/@panaversity

## Submission Requirements

- GitHub repository with code
- README.md with setup instructions
- Demo video (5-10 minutes)
- Security disclosure
- Tier declaration (Bronze/Silver/Gold/Platinum)
- Submit Form: https://forms.gle/JR9T1SJq5rmQyGkGA

## Judging Criteria

| Criterion | Weight |
|-----------|--------|
| Functionality | 30% |
| Innovation | 25% |
| Practicality | 20% |
| Security | 15% |
| Documentation | 10% |

## Ethics & Responsible Automation

### When AI Should NOT Act Autonomously
- Emotional contexts (condolences, conflicts)
- Legal matters (contracts, filings)
- Medical decisions
- Financial edge cases
- Irreversible actions

### Oversight Schedule
- **Daily:** 2-minute dashboard check
- **Weekly:** 15-minute action log review
- **Monthly:** 1-hour comprehensive audit
- **Quarterly:** Full security review

**Remember:** You are responsible for your AI Employee's actions. Regular oversight is essential.
