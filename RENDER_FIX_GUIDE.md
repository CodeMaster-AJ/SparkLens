# Fix Render DisallowedHost Error - SparkLens

## Problem
Render is showing: `ALLOWED_HOSTS: ['localhost', '127.0.0.1']` even after code fixes.

**Root Cause**: Render is running cached/old code.

---

## Step 1: Verify Latest Code (Local)

Check that your `idea_validator/config/settings.py` line 10 has:
```python
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'sparklens.onrender.com,localhost,127.0.0.1').split(',')
```

If not, update it and push:
```bash
cd "/Users/aj/Documents/AJ/B.tech Semesters/B.Tech SEM_4/CWH (Django)/Idea"
git add idea_validator/config/settings.py
git commit -m "Fix ALLOWED_HOSTS for Render"
git push origin main
```

---

## Step 2: Clear Render Cache & Redeploy

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on **sparklens** service
3. Click **"Manual Deploy"** button (top right)
4. Select **"Clear build cache & deploy latest commit"**
5. Wait 3-5 minutes for deployment

---

## Step 3: Check Environment Variables in Render

1. In Render Dashboard → sparklens service
2. Go to **Settings** → **Environment**
3. Check if `ALLOWED_HOSTS` exists:
   - **If it exists**: Delete it (so code defaults are used)
   - **Or update it to**: `sparklens.onrender.com,localhost,127.0.0.1`

4. Also set these if not present:
   - `DJANGO_DEBUG` = `False`
   - `PYTHON_VERSION` = `3.11`

5. Click **Save Changes**
6. **Redeploy** again after saving environment variables

---

## Step 4: Verify the Fix

After redeployment, visit: https://sparklens.onrender.com/

**If still failing**, check the error page:
- Look for `ALLOWED_HOSTS` in the settings table
- It should show: `['sparklens.onrender.com', 'localhost', '127.0.0.1']`
- If it still shows `['localhost', '127.0.0.1']`, the old code is still running

---

## Step 5: Nuclear Option - Recreate Service

If cache clear doesn't work:

1. In Render Dashboard, delete the **sparklens** service
2. Create new Web Service pointing to `https://github.com/CodeMaster-AJ/SparkLens`
3. Configure:
   - **Build Command**: `cd idea_validator && pip install -r requirements.txt`
   - **Start Command**: `cd idea_validator && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
   - **Environment Variables**:
     - `DJANGO_DEBUG` = `False`
     - `ALLOWED_HOSTS` = `sparklens.onrender.com,localhost,127.0.0.1`
     - `OPENROUTER_API_KEY` = `your_api_key_here`

---

## Quick Diagnosis Commands

Check what commit Render is running:
```bash
# After deployment, check Render logs for the git commit
# Or check the deployment timeline in Render dashboard
```

Verify your repo is up to date:
```bash
cd "/Users/aj/Documents/AJ/B.tech Semesters/B.Tech SEM_4/CWH (Django)/Idea"
git log --oneline -5
git push origin main
```

---

## Common Mistakes

❌ **Not clearing build cache** - Render caches old code  
❌ **Environment variable overrides code** - `ALLOWED_HOSTS` env var overrides settings.py  
❌ **Wrong start command** - Must match your project structure  
❌ **Not waiting for deployment** - Takes 3-5 minutes after clicking deploy  

---

## File Structure Reference

Your repo should have:
```
SparkLens/
├── idea_validator/
│   ├── config/
│   │   ├── settings.py  (ALLOWED_HOSTS here)
│   │   └── wsgi.py
│   ├── validator/
│   ├── requirements.txt
│   └── Procfile (optional)
├── Procfile (optional, at root)
└── render.yaml (optional)
```

If your code is inside `idea_validator/` folder, your start command must include that path.

---

**Last Resort**: If nothing works, the issue might be that Render is looking at the wrong branch or the wrong start command. Double-check the service configuration in Render.
