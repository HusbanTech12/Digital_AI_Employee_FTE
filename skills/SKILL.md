# AI Employee Skills

**Version:** 1.0 (Bronze Tier)  
**Description:** Agent skills for the Personal AI Employee system using Qwen Code

This directory contains Agent Skill definitions for Qwen Code to use when processing tasks in the AI Employee system.

## Available Skills

### 1. File Processor Skill
**File:** `file-processor/SKILL.md`

Processes files dropped into the Inbox folder:
- Reads file content
- Identifies file type
- Extracts key information
- Creates action items

### 2. Task Manager Skill
**File:** `task-manager/SKILL.md`

Manages tasks in the Needs_Action folder:
- Reads action files
- Creates plans with checkboxes
- Tracks progress
- Moves completed tasks to Done

### 3. Dashboard Updater Skill
**File:** `dashboard-updater/SKILL.md`

Updates the Dashboard.md with:
- Recent activity
- Task statistics
- Pending approvals
- Alerts and notifications

### 4. Approval Handler Skill
**File:** `approval-handler/SKILL.md`

Handles human-in-the-loop approvals:
- Creates approval request files
- Processes approved items
- Handles rejections
- Logs decisions

## Usage

To use these skills with Qwen Code:

```bash
# In your vault directory
qwen --skill file-processor
qwen --skill task-manager
```

Or reference in prompts:
```
Use the task-manager skill to process pending items.
```

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md          # Skill definition and instructions
├── examples/         # Example inputs/outputs
└── scripts/          # Helper scripts (if needed)
```

## Creating Custom Skills

To create a new skill:

1. Create a folder in `skills/`
2. Add `SKILL.md` with:
   - Skill name and description
   - Capabilities
   - Usage examples
   - Input/output formats
3. Test with Claude Code
4. Document in this file

## Bronze Tier Skills

For Bronze Tier, implement these core skills:

### File Processing
- Detect file type
- Extract content
- Create metadata
- Generate action items

### Task Management
- Read action files
- Create plans
- Track completion
- Archive done items

### Dashboard Updates
- Update activity log
- Refresh statistics
- Show pending items
- Display alerts

---

*AI Employee v0.1 - Bronze Tier*
