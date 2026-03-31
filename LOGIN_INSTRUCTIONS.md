# 🔐 How to Login to Social Media (First Time)

**Follow these steps to login to LinkedIn, Facebook, and Instagram for automatic posting**

---

## Quick Start (2 Steps)

### Step 1: Run the Login Script

**Option A: Use Batch File (Easiest)**
```batch
login-social-media.bat
```

**Option B: Command Line**
```bash
# Login to all platforms
python scripts\login_social_media.py all

# Or login to specific platforms
python scripts\login_social_media.py linkedin
python scripts\login_social_media.py facebook
python scripts\login_social_media.py instagram
```

### Step 2: Login in Browser

1. **Browser opens automatically** (Chromium)
2. **Login page loads** (LinkedIn/Facebook/Instagram)
3. **Enter your credentials**
4. **Complete 2FA if enabled**
5. **Close browser window** when done
6. **Session is saved automatically!**

---

## Detailed Instructions

### LinkedIn Login

1. Run: `python scripts\login_social_media.py linkedin`
2. Browser opens to: `https://www.linkedin.com/login`
3. Enter your:
   - Email or phone number
   - Password
4. Click "Sign in"
5. Complete any verification (email/SMS code)
6. Once you see your LinkedIn feed, **close the browser**
7. Session saved to: `linkedin_session/`

**After Login:**
- ✅ You can now post to LinkedIn automatically
- ✅ No need to login again (session persists)
- ✅ Run: `publish-social-media.bat` to post

---

### Facebook Login

1. Run: `python scripts\login_social_media.py facebook`
2. Browser opens to: `https://www.facebook.com`
3. Enter your:
   - Email or phone number
   - Password
4. Click "Log In"
5. Complete any verification
6. Once you see your Facebook feed, **close the browser**
7. Session saved to: `facebook_session/`

**After Login:**
- ✅ You can now post to Facebook automatically
- ✅ No need to login again (session persists)
- ✅ Run: `python scripts\facebook_instagram_watcher.py AI_Employee_Vault`

---

### Instagram Login

1. Run: `python scripts\login_social_media.py instagram`
2. Browser opens to: `https://www.instagram.com`
3. Enter your:
   - Username, email, or phone
   - Password
4. Click "Log in"
5. Complete any verification
6. Once you see your Instagram feed, **close the browser**
7. Session saved to: `facebook_session/instagram/`

**After Login:**
- ⚠️ Instagram requires images for posts
- ✅ You can now post to Instagram (with images)
- ✅ No need to login again (session persists)

---

## Session Management

### Where Sessions Are Saved

```
D:\Quarter_4\Hackathon_0\Digital_AI_Employee_FTE\
├── linkedin_session/          # LinkedIn credentials
└── facebook_session/           # Facebook credentials
    └── instagram/              # Instagram credentials
```

### Session Persistence

- ✅ Sessions are **automatically saved** after login
- ✅ Sessions are **reused** for future posts
- ✅ No need to login every time
- ✅ Sessions persist across reboots

### When to Re-Login

You only need to login again if:
- You change your password
- You clear the session folder
- Platform logs you out (rare)
- Session expires (very rare)

---

## Troubleshooting

### "Browser doesn't open"

**Solution:**
```bash
# Check Playwright is installed
pip install playwright
playwright install chromium
```

### "Login page doesn't load"

**Solution:**
- Check your internet connection
- Try opening LinkedIn/Facebook manually in your browser
- If site is blocked, check firewall/antivirus

### "Session not saving"

**Solution:**
```bash
# Delete old session and re-login
rmdir /s linkedin_session
python scripts\login_social_media.py linkedin
```

### "Browser closes immediately"

**Cause:** Script error or crash

**Solution:**
Use the manual method:
```bash
# Open browser manually
python scripts\login_social_media.py linkedin
# Login quickly before timeout
# Close browser when done
```

---

## Security Notes

### Session Storage

- Sessions stored **locally** on your computer
- **Encrypted** by Chromium browser
- **Never committed** to git (in .gitignore)
- **Only accessible** by you

### Best Practices

✅ **DO:**
- Login from your personal computer
- Use strong passwords
- Enable 2FA on all accounts
- Keep sessions private

❌ **DON'T:**
- Share session folders
- Commit sessions to git
- Login on public computers
- Use weak passwords

---

## After Login - Next Steps

### 1. Verify Login Worked

```bash
# Test LinkedIn posting
python scripts\linkedin_poster.py AI_Employee_Vault
```

If you see "Post published successfully!" - you're good! ✅

### 2. Publish Your AI Employee Posts

```batch
publish-social-media.bat
```

This will:
1. Move posts to Approved folder
2. Open browser
3. Post to LinkedIn automatically
4. Save results in Logs/

### 3. Check Results

```bash
# View logs
type AI_Employee_Vault\Logs\linkedin_*.log

# Check published posts
dir AI_Employee_Vault\Done\
```

---

## Quick Reference

| Platform | Login Command | Session Location | Test Command |
|----------|--------------|------------------|--------------|
| **LinkedIn** | `python scripts\login_social_media.py linkedin` | `linkedin_session/` | `python scripts\linkedin_poster.py AI_Employee_Vault` |
| **Facebook** | `python scripts\login_social_media.py facebook` | `facebook_session/` | `python scripts\facebook_instagram_watcher.py AI_Employee_Vault` |
| **Instagram** | `python scripts\login_social_media.py instagram` | `facebook_session/instagram/` | `python scripts\facebook_instagram_watcher.py AI_Employee_Vault` |

---

## Full Workflow

```
1. Run login script
   ↓
2. Browser opens
   ↓
3. Login manually
   ↓
4. Close browser
   ↓
5. Session saved ✅
   ↓
6. Run publish script
   ↓
7. Posts published automatically! 🚀
```

---

## Need Help?

**Documentation:**
- `SOCIAL_MEDIA_AUTOMATION.md` - Full guide
- `SOCIAL_MEDIA_READY.md` - Quick start
- `POST_APPROVAL_INSTRUCTIONS.md` - Post approval

**Support:**
- Wednesday Meetings: 10:00 PM Zoom
- Meeting ID: 871 8870 7642
- Passcode: 744832

---

*AI Employee Social Media Automation v1.0*
*First-Time Login Guide - March 31, 2026*
