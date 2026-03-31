# Social Media Automation Setup Guide

**Automate posting to LinkedIn, Facebook, and Instagram**

---

## Quick Start

### Step 1: Install Playwright

```bash
pip install playwright
playwright install chromium
```

### Step 2: Run Setup

```bash
# Windows
cd scripts
python social_media_manager.py ..\AI_Employee_Vault setup

# Or use batch file
setup-social-media.bat
```

### Step 3: Create Your First Post

```bash
python social_media_manager.py ..\AI_Employee_Vault post
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Social Media Manager                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   LinkedIn   │  │   Facebook   │  │  Instagram   │  │
│  │   Poster     │  │   Watcher    │  │   Watcher    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         AI Content Generator (Qwen Code)         │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
AI_Employee_Vault/
├── Needs_Action/
│   ├── LINKEDIN_*.md        # LinkedIn posts to create
│   ├── FACEBOOK_*.md        # Facebook posts to create
│   └── INSTAGRAM_*.md       # Instagram posts to create
├── Pending_Approval/
│   └── APPROVAL_*.md        # Awaiting human approval
├── Approved/
│   └── APPROVAL_*.md        # Ready to post
├── Done/
│   └── *.md                 # Posted content
└── Logs/
    ├── linkedin_posts.jsonl
    ├── facebook_posts.jsonl
    └── instagram_posts.jsonl
```

---

## How It Works

### 1. Create Post Content

**Option A: Manual Creation**

Create a markdown file in `Needs_Action/`:

```markdown
---
type: social_media_post
platform: linkedin
title: Product Launch
scheduled_time: 2026-04-01T09:00:00Z
---

# LinkedIn Post: Product Launch

## Content
🚀 Excited to announce our new AI Employee system!

After months of development, we're launching a revolutionary automation platform.

Key features:
✅ Automated task processing
✅ Multi-platform integration
✅ Human-in-the-loop approval

#AI #Automation #Innovation
```

**Option B: Use Social Media Manager**

```bash
python social_media_manager.py ..\AI_Employee_Vault post
```

**Option C: AI-Generated Content**

Drop a file in `Inbox/`:

```
Please create social media posts about our new AI Employee system.
Key points:
- Automates routine tasks
- Integrates with LinkedIn, Facebook, Instagram
- Uses Qwen Code CLI for reasoning
```

The AI will generate platform-specific posts automatically.

---

### 2. Approval Workflow

1. **Post created** in `Needs_Action/`
2. **Move to** `Pending_Approval/` for review
3. **Review content** and approve
4. **Move to** `Approved/` for posting
5. **Automatic posting** on next orchestrator run

---

### 3. Automatic Posting

The orchestrator processes approved posts:

```bash
python scripts/orchestrator.py --vault AI_Employee_Vault --qwen-code --continuous
```

Or run the social media manager directly:

```bash
python scripts/social_media_manager.py ..\AI_Employee_Vault process
```

---

## Platform-Specific Setup

### LinkedIn

**First Run:**
1. Script will open browser
2. Login to LinkedIn manually
3. Session saved for future runs

**Posting:**
- Professional tone
- Up to 3,000 characters
- Supports images and links
- Hashtags recommended (3-5)

**Best Times to Post:**
- Tuesday-Thursday: 9-11 AM
- Wednesday: Best day

---

### Facebook

**First Run:**
1. Script will open browser
2. Login to Facebook manually
3. Session saved for future runs

**Posting:**
- Casual tone
- Up to 63,206 characters
- Supports images, videos, links
- Hashtags optional

**Best Times to Post:**
- Wednesday-Friday: 1-4 PM
- Saturday-Sunday: 12-1 PM

---

### Instagram

**First Run:**
1. Script will open browser
2. Login to Instagram manually
3. Session saved for future runs

**Posting:**
- Visual-focused content
- Emojis encouraged
- Up to 2,200 characters
- Hashtags important (10-15)
- **Requires images**

**Best Times to Post:**
- Monday-Friday: 11 AM-1 PM
- Wednesday: Best day

**Note:** Instagram automation has limitations. For production use, consider Instagram Graph API.

---

## Usage Examples

### Example 1: Cross-Platform Post

**Create file:** `Inbox/announcement.txt`

```
Create social media posts for all platforms about:

Topic: AI Employee Hackathon Completion
Content: Successfully completed Gold Tier integration with Qwen Code CLI
Key points:
- 9/9 tests passed
- Full automation working
- Social media integration complete
```

**AI will create:**
- `LINKEDIN_AI_Employee_Hackathon_*.md`
- `FACEBOOK_AI_Employee_Hackathon_*.md`
- `INSTAGRAM_AI_Employee_Hackathon_*.md`

Each with platform-specific formatting!

---

### Example 2: Scheduled Post

```markdown
---
type: social_media_post
platform: linkedin
title: Weekly Update
scheduled_time: 2026-04-01T09:00:00Z
---

# LinkedIn Post: Weekly Update

## Content
This week's achievements:
✅ Integrated Qwen Code CLI
✅ Automated social media posting
✅ 100% test coverage

#Progress #AI #Automation
```

---

### Example 3: Generate Weekly Summary

```bash
python social_media_manager.py ..\AI_Employee_Vault summary
```

**Output:**
```
Weekly Social Media Summary
========================================
Total Posts: 12
LinkedIn: 5 posts
Facebook: 4 posts
Instagram: 3 posts
```

---

## Commands Reference

### Social Media Manager

```bash
# Setup all platforms
python social_media_manager.py [vault] setup

# Create test post
python social_media_manager.py [vault] post

# Generate weekly summary
python social_media_manager.py [vault] summary

# Check status
python social_media_manager.py [vault] status
```

### Orchestrator Integration

```bash
# Process all approved posts
python orchestrator.py --vault AI_Employee_Vault --qwen-code --once
```

### Direct Platform Scripts

```bash
# LinkedIn only
python linkedin_poster.py ..\AI_Employee_Vault

# Facebook/Instagram
python facebook_instagram_watcher.py ..\AI_Employee_Vault
```

---

## Troubleshooting

### "Playwright not installed"

```bash
pip install playwright
playwright install chromium
```

### "Not logged in"

First run requires manual login:
1. Script opens browser
2. Login to platform
3. Session saved automatically
4. Future runs use saved session

### "Instagram post failed"

Instagram requires images. Add image paths:

```markdown
---
images: path/to/image1.jpg, path/to/image2.jpg
---
```

Or use Instagram Graph API for production.

### "Session not saving"

Check session folder permissions:
- Windows: `%APPDATA%\..\Local\Programs\`
- Linux/macOS: `~/.qwen/`

---

## Best Practices

### Content Strategy

1. **LinkedIn:** Professional, industry insights, company news
2. **Facebook:** Casual, behind-the-scenes, community engagement
3. **Instagram:** Visual, stories, lifestyle content

### Posting Schedule

- **LinkedIn:** 2-3 times per week
- **Facebook:** 1-2 times per day
- **Instagram:** 1-2 times per day

### Approval Workflow

- Always review before posting
- Check for typos and formatting
- Verify links work
- Ensure images are appropriate

### Hashtag Strategy

- **LinkedIn:** 3-5 professional hashtags
- **Facebook:** 0-3 casual hashtags
- **Instagram:** 10-15 relevant hashtags

---

## Security & Privacy

### Session Management

- Sessions stored locally
- OAuth tokens encrypted
- Never commit session files to git

### Approval Requirements

All posts require human approval before publishing:
- Move file to `Approved/` to publish
- Move file to `Rejected/` to discard

### Rate Limiting

Avoid spam by limiting posts:
- LinkedIn: Max 5 posts/day
- Facebook: Max 10 posts/day
- Instagram: Max 10 posts/day

---

## Advanced: AI-Generated Content

### Auto-Generate from Business Updates

Drop a file in `Inbox/`:

```
Generate social media posts for this week's business updates:

1. Completed Qwen Code integration
2. Launched new website
3. Reached 1000 users
4. Partnership with TechCorp
```

AI will create platform-specific posts for each update!

### Content Templates

The system includes templates for:
- Business updates
- Thought leadership
- Project announcements
- Client success stories
- Event promotions

---

## Integration with AI Employee

### Automated Workflow

```
1. User drops update in Inbox/
   ↓
2. AI generates social media posts
   ↓
3. Posts created in Needs_Action/
   ↓
4. Approval requests generated
   ↓
5. Human reviews and approves
   ↓
6. Posts published automatically
   ↓
7. Results logged and tracked
```

### Weekly Briefing

The AI generates a weekly social media summary:
- Total posts per platform
- Engagement metrics
- Top performing content
- Recommendations for improvement

---

## Resources

- **Playwright Docs:** https://playwright.dev/python/
- **LinkedIn API:** https://docs.microsoft.com/en-us/linkedin/
- **Facebook Graph API:** https://developers.facebook.com/docs/graph-api
- **Instagram Graph API:** https://developers.facebook.com/docs/instagram-api

---

## Support

**Wednesday Meetings:**
- Time: 10:00 PM on Zoom
- Meeting ID: 871 8870 7642
- Passcode: 744832

---

*AI Employee Social Media Automation v1.0*
*Gold Tier Feature - Complete & Ready to Use*
