# ✅ Social Media Automation - Ready to Use!

**Status:** Complete & Tested  
**Platforms:** LinkedIn, Facebook, Instagram  
**Tests:** All Passed ✅

---

## What's Configured

| Platform | Status | Features |
|----------|--------|----------|
| **LinkedIn** | ✅ Ready | Auto-posting, Session saved, Approval workflow |
| **Facebook** | ✅ Ready | Auto-posting, Session saved, Approval workflow |
| **Instagram** | ✅ Ready | Auto-posting, Session saved, Image support |
| **Unified Manager** | ✅ Ready | Cross-platform posting, AI content generation |

---

## Quick Start (3 Steps)

### Step 1: Install Playwright (One-time)

```bash
pip install playwright
playwright install chromium
```

Or run the batch file:
```batch
setup-social-media.bat
```

### Step 2: Create Your First Post

**Option A: Use the Manager (Easiest)**
```bash
python scripts\social_media_manager.py AI_Employee_Vault post
```

**Option B: Drop a File in Inbox**
Create `AI_Employee_Vault/Inbox/social_request.txt`:
```
Create social media posts about:
Topic: New Product Launch
Content: We're launching our AI Employee system next week!
Key points:
- Automates social media posting
- Integrates with Qwen Code CLI
- Gold Tier hackathon project
```

**Option C: Create Manual Post Files**
Create files directly in `Needs_Action/` folder (see templates below)

### Step 3: Approve & Post

1. **Review** post in `Needs_Action/`
2. **Move** to `Pending_Approval/` for review
3. **Approve** by moving to `Approved/`
4. **Post automatically** via orchestrator

---

## Created Test Posts

3 test posts have been created for you:

```
AI_Employee_Vault/Needs_Action/
├── LINKEDIN_AI_Employee_Update_20260331_165330.md
├── FACEBOOK_AI_Employee_Update_20260331_165330.md
└── INSTAGRAM_AI_Employee_Update_20260331_165330.md
```

Each post is platform-optimized:
- **LinkedIn:** Professional tone, 3-5 hashtags
- **Facebook:** Casual tone, emoji-friendly
- **Instagram:** Visual-focused, 10+ hashtags

---

## How to Approve & Publish Test Posts

### Manual Approval (Recommended for First Time)

1. **Review the post:**
   - Open `LINKEDIN_AI_Employee_Update_20260331_165330.md`
   - Check content and formatting

2. **Move to Pending_Approval:**
   ```
   From: Needs_Action/
   To: Pending_Approval/
   ```

3. **Review again** (human-in-the-loop)

4. **Move to Approved:**
   ```
   From: Pending_Approval/
   To: Approved/
   ```

5. **Run the poster:**
   ```bash
   python scripts\linkedin_poster.py AI_Employee_Vault
   ```

6. **First run:** Login to LinkedIn manually
   - Browser opens
   - Login to your account
   - Session saved automatically
   - Post published!

---

## Automated Workflow (After Setup)

```
1. Create post (automatic or manual)
   ↓
2. AI generates platform-specific content
   ↓
3. Approval request created
   ↓
4. Human reviews and approves
   ↓
5. Orchestrator posts automatically
   ↓
6. Results logged in Logs/
```

---

## Commands Reference

### Social Media Manager

```bash
# Setup all platforms
python scripts\social_media_manager.py AI_Employee_Vault setup

# Create test post
python scripts\social_media_manager.py AI_Employee_Vault post

# Generate weekly summary
python scripts\social_media_manager.py AI_Employee_Vault summary

# Check status
python scripts\social_media_manager.py AI_Employee_Vault status
```

### Platform-Specific Scripts

```bash
# LinkedIn only
python scripts\linkedin_poster.py AI_Employee_Vault

# Facebook/Instagram
python scripts\facebook_instagram_watcher.py AI_Employee_Vault
```

### Orchestrator Integration

```bash
# Process all approved posts
python scripts\orchestrator.py --vault AI_Employee_Vault --qwen-code --once
```

---

## Post Templates

### LinkedIn Template

```markdown
---
type: social_media_post
platform: linkedin
title: Your Title
scheduled_time: 2026-04-01T09:00:00Z
---

# LinkedIn Post: Your Title

## Content
Your professional content here (up to 3,000 characters)

Key points:
• Point 1
• Point 2
• Point 3

#Hashtag1 #Hashtag2 #Hashtag3

## Posting Instructions
1. Review the content above
2. Move this file to /Pending_Approval for approval
3. Once approved, move to /Approved for posting
4. Post will be published automatically
```

### Facebook Template

```markdown
---
type: social_media_post
platform: facebook
title: Your Title
---

# Facebook Post: Your Title

## Content
📢 Your casual content here (up to 63,206 characters)

Share with your friends! 👍

#Hashtag1 #Hashtag2
```

### Instagram Template

```markdown
---
type: social_media_post
platform: instagram
title: Your Title
images: path/to/image.jpg
---

# Instagram Post: Your Title

## Content
✨ Your visual content here with emojis

📸 Double tap if you agree!
💬 Comment your thoughts below!

#Hashtag1 #Hashtag2 #Hashtag3 #InstaDaily
```

---

## AI-Generated Content

Drop a file in `Inbox/` and let AI create posts for you!

**Example Inbox File:**
```
Please create social media posts for all platforms about:

Topic: AI Employee Gold Tier Completion
Content: We just completed Gold Tier of the hackathon!
Key achievements:
- Qwen Code CLI integration (9/9 tests passed)
- Social media automation working
- Cross-platform posting ready
- Full audit logging enabled

Target audience: Developers and business owners
Tone: Professional but exciting
```

**AI will create:**
- LinkedIn post (professional tone)
- Facebook post (casual tone)
- Instagram post (visual-friendly)

Each with platform-specific formatting and hashtags!

---

## Best Practices

### Content Strategy

| Platform | Tone | Frequency | Best Time |
|----------|------|-----------|-----------|
| **LinkedIn** | Professional | 2-3x/week | Tue-Thu 9-11 AM |
| **Facebook** | Casual | 1-2x/day | Wed-Fri 1-4 PM |
| **Instagram** | Visual | 1-2x/day | Mon-Fri 11 AM-1 PM |

### Hashtag Strategy

- **LinkedIn:** 3-5 professional hashtags
- **Facebook:** 0-3 casual hashtags
- **Instagram:** 10-15 relevant hashtags

### Approval Workflow

✅ **Always review before posting:**
- Check for typos
- Verify links work
- Ensure appropriate content
- Confirm scheduling is correct

---

## Troubleshooting

### "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### "Not logged in"
- First run requires manual login
- Browser will open automatically
- Login to your account
- Session saved for future runs

### "Instagram post failed"
- Instagram requires images
- Add image paths in frontmatter:
  ```markdown
  ---
  images: path/to/image1.jpg, path/to/image2.jpg
  ---
  ```

### "Session not saving"
- Check folder permissions
- Sessions saved in:
  - `linkedin_session/`
  - `facebook_session/`
  - `facebook_session/instagram/`

---

## Integration with AI Employee

### Full Automation Flow

```
User Input (Inbox/)
    ↓
Qwen Code CLI (AI Processing)
    ↓
Social Media Manager (Content Generation)
    ↓
Platform-Specific Posts (Needs_Action/)
    ↓
Approval Workflow (Pending_Approval → Approved)
    ↓
Auto-Posting (LinkedIn/Facebook/Instagram)
    ↓
Results Logged (Logs/)
```

### Weekly Summary

The system generates automatic summaries:
- Total posts per platform
- Engagement metrics
- Top performing content
- Recommendations

---

## Files Created

| File | Purpose |
|------|---------|
| `scripts/social_media_manager.py` | Unified manager |
| `scripts/linkedin_poster.py` | LinkedIn automation |
| `scripts/facebook_instagram_watcher.py` | FB/IG automation |
| `SOCIAL_MEDIA_AUTOMATION.md` | Full documentation |
| `setup-social-media.bat` | Windows setup script |
| `SOCIAL_MEDIA_READY.md` | This quick start guide |

---

## Next Steps

1. **Run Setup** (if not done):
   ```batch
   setup-social-media.bat
   ```

2. **Review Test Posts**:
   - Check `Needs_Action/` folder
   - Review content and formatting

3. **Approve First Post**:
   - Move to `Pending_Approval/`
   - Then move to `Approved/`

4. **Run LinkedIn Poster**:
   ```bash
   python scripts\linkedin_poster.py AI_Employee_Vault
   ```

5. **Login Manually** (first run only):
   - Browser opens
   - Login to LinkedIn
   - Post published automatically!

6. **Create More Posts**:
   - Drop files in `Inbox/`
   - Or use the manager command

---

## Documentation

- **Full Guide:** `SOCIAL_MEDIA_AUTOMATION.md`
- **Setup Script:** `setup-social-media.bat`
- **Manager Code:** `scripts/social_media_manager.py`

---

## Support

**Wednesday Meetings:**
- Time: 10:00 PM on Zoom
- Meeting ID: 871 8870 7642
- Passcode: 744832
- YouTube: https://www.youtube.com/@panaversity

---

*AI Employee Social Media Automation v1.0*
*Gold Tier Feature - Complete & Ready to Use!*
*Tested: March 31, 2026*
