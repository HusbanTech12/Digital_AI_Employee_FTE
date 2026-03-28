# File Processor Skill

**Name:** file-processor  
**Version:** 1.0  
**Tier:** Bronze  

## Description

Processes files dropped into the AI Employee Inbox folder. Automatically detects file types, extracts content, and creates actionable items for further processing.

## Capabilities

- Detect and identify file types (txt, md, pdf, doc, csv, json, images)
- Extract text content from supported formats
- Generate file metadata (size, created date, hash)
- Create structured action files in Needs_Action folder
- Handle multiple files in batch

## Usage

```bash
qwen --skill file-processor "Process all files in Inbox"
```

Or in prompts:
```
Use the file-processor skill to handle the new file drop.
```

## Input Format

Files placed in: `AI_Employee_Vault/Inbox/`

## Output Format

Creates action files in: `AI_Employee_Vault/Needs_Action/`

Action file structure:
```markdown
---
type: file_drop
original_name: filename.ext
size: 1234
created: 2026-03-28T10:00:00Z
status: pending
---

## Content
[File content or summary]

## Suggested Actions
- [ ] Review file content
- [ ] Extract key information
- [ ] Take necessary action
- [ ] Archive after processing
```

## Processing Rules

1. **Text files (.txt, .md):** Read and display full content
2. **PDF files:** Note that manual review is needed
3. **Documents (.doc, .docx):** Note that manual review is needed
4. **Spreadsheets (.csv, .xlsx):** Show preview of data
5. **Images:** Note that vision analysis is needed
6. **JSON:** Parse and display structured content

## Examples

### Example 1: Process Text File

**Input:** `task.txt`
```
Meeting notes from today:
1. Discuss Q1 goals
2. Review budget
3. Plan next sprint
```

**Output:** Action file with content and suggested actions to summarize and create follow-up tasks.

### Example 2: Process CSV File

**Input:** `sales.csv`
```
Date,Product,Amount
2026-01-01,Widget A,100
2026-01-02,Widget B,200
```

**Output:** Action file with data preview and suggested actions to analyze trends.

## Error Handling

- If file cannot be read: Create action file noting the error
- If file is corrupted: Quarantine and alert user
- If file type unknown: Create generic action file for manual review

## Related Skills

- task-manager: For processing created action files
- dashboard-updater: For logging file processing activity

---

*AI Employee v0.1 - Bronze Tier*
