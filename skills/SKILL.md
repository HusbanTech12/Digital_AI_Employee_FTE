# AI Employee Skills

**Version:** 2.0 (Silver Tier)
**Description:** Agent skills for the Personal AI Employee system using Qwen Code

This directory contains Agent Skill definitions for Qwen Code to use when processing tasks in the AI Employee system.

## Available Skills

### 1. File Processor Skill
**File:** `file-processor/SKILL.md`
**Tier:** Bronze

Processes files dropped into the Inbox folder:
- Reads file content
- Identifies file type
- Extracts key information
- Creates action items

### 2. Task Manager Skill
**File:** `task-manager/SKILL.md`
**Tier:** Bronze

Manages tasks in the Needs_Action folder:
- Reads action files
- Creates plans with checkboxes
- Tracks progress
- Moves completed tasks to Done

### 3. Dashboard Updater Skill
**File:** `dashboard-updater/SKILL.md`
**Tier:** Bronze

Updates the Dashboard.md with:
- Recent activity
- Task statistics
- Pending approvals
- Alerts and notifications

### 4. Approval Handler Skill
**File:** `approval-handler/SKILL.md`
**Tier:** Silver ⭐

Handles human-in-the-loop approvals:
- Create approval request files
- Auto-approval based on rules
- Process approved items via MCP
- Handle rejections gracefully
- Comprehensive audit logging
- Priority escalation

### 5. Plan Generator Skill
**File:** `plan-generator/SKILL.md`
**Tier:** Silver ⭐

Creates structured plans for Claude reasoning loop:
- Parse action files from Needs_Action
- Generate step-by-step plans
- Track progress via checkboxes
- Identify dependencies
- Define success criteria

## Usage

To use these skills with Qwen Code:

```bash
# In your vault directory
qwen --skill file-processor
qwen --skill task-manager
qwen --skill approval-handler
qwen --skill plan-generator
```

Or reference in prompts:
```
Use the plan-generator skill to create a plan for processing emails.
Use the approval-handler skill to request approval for this payment.
```

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md          # Skill definition and instructions
├── examples/         # Example inputs/outputs (optional)
└── scripts/          # Helper scripts (if needed)
```

## Tier Requirements

### Bronze Tier Skills
- ✅ File Processing
- ✅ Task Management
- ✅ Dashboard Updates
- ✅ Basic Approvals

### Silver Tier Skills (Additional)
- ✅ Advanced Approval Handler with auto-approval rules
- ✅ Plan Generator for Claude reasoning loop
- ✅ MCP server integration
- ✅ Priority escalation
- ✅ Audit logging

### Gold Tier Skills (Future)
- ⏳ Odoo Accounting Integration
- ⏳ Social Media Management (Facebook, Instagram, Twitter)
- ⏳ Weekly Business Audit Generator
- ⏳ Error Recovery Handler
- ⏳ Ralph Wiggum Loop Coordinator

## Creating Custom Skills

To create a new skill:

1. Create a folder in `skills/`
2. Add `SKILL.md` with:
   - Skill name and description
   - Tier level (Bronze/Silver/Gold)
   - Capabilities
   - Usage examples
   - Input/output formats
3. Test with Qwen Code
4. Document in this file
5. Update version number

## Skill Integration

Skills work together in the AI Employee workflow:

```
Watcher Scripts → Action Files → Plan Generator → Task Manager
                                           ↓
                                    Approval Handler
                                           ↓
                                      MCP Servers
                                           ↓
                                      Dashboard
```

## Watcher Integration

Skills integrate with watcher scripts:

| Watcher | Creates | Skills Used |
|---------|---------|-------------|
| Filesystem | FILE_*.md | file-processor |
| Gmail | EMAIL_*.md | approval-handler, task-manager |
| WhatsApp | WHATSAPP_*.md | approval-handler, task-manager |
| LinkedIn | LINKEDIN_*.md | approval-handler |

## MCP Server Integration

Silver Tier skills integrate with MCP servers:

| MCP Server | Skills | Actions |
|------------|--------|---------|
| email-mcp | approval-handler | send_email, draft_email |
| linkedin | approval-handler | create_post |
| filesystem | file-processor | read, write, move |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-28 | Bronze Tier initial release |
| 2.0 | 2026-03-29 | Silver Tier: approval-handler v2, plan-generator |

---

*AI Employee v0.2 - Silver Tier*
*Last Updated: 2026-03-29*
