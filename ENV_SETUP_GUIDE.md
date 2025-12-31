# Setting Up Environment Variables for Weather App

## Overview

This guide shows you how to securely store your Ambient Weather API credentials using environment variables instead of hardcoding them in your script.

## Why Environment Variables?

✅ **More Secure** - Keys never appear in your code
✅ **Safe to Share** - You can share your GitHub repo without exposing credentials
✅ **Easy to Update** - Change keys without editing code

---

## Quick Setup (PowerShell - Temporary)

These environment variables will last **only for your current PowerShell session**.

### Step 1: Open PowerShell in your weather-app folder

```powershell
cd "C:\GitHub Repos\Weather-App"
```

### Step 2: Set your environment variables

Replace `your_actual_api_key` and `your_actual_application_key` with your real keys:

```powershell
$env:AMBIENT_API_KEY="your_actual_api_key"
$env:AMBIENT_APP_KEY="your_actual_application_key"
```

**Example:**
```powershell
$env:AMBIENT_API_KEY="abc123def456ghi789"
$env:AMBIENT_APP_KEY="xyz987uvw654rst321"
```

### Step 3: Verify they're set (optional)

```powershell
echo $env:AMBIENT_API_KEY
echo $env:AMBIENT_APP_KEY
```

### Step 4: Run the script

```powershell
python ambient_weather_fetch.py
```

---

## Permanent Setup (Windows System Environment Variables)

If you want to set these permanently so you don't have to enter them every time:

### Option A: Using PowerShell (Permanent for your user)

```powershell
[System.Environment]::SetEnvironmentVariable('AMBIENT_API_KEY', 'your_actual_api_key', 'User')
[System.Environment]::SetEnvironmentVariable('AMBIENT_APP_KEY', 'your_actual_application_key', 'User')
```

**After setting, close and reopen PowerShell**, then you can run the script without setting them again.

### Option B: Using Windows GUI

1. Press `Windows Key + R`
2. Type: `sysdm.cpl` and press Enter
3. Click **"Advanced"** tab
4. Click **"Environment Variables"** button
5. Under **"User variables"**, click **"New"**
6. Add first variable:
   - Variable name: `AMBIENT_API_KEY`
   - Variable value: `your_actual_api_key`
   - Click OK
7. Click **"New"** again for second variable:
   - Variable name: `AMBIENT_APP_KEY`
   - Variable value: `your_actual_application_key`
   - Click OK
8. Click OK on all windows
9. **Close and reopen PowerShell**

---

## Creating a Helper Script (Optional)

You can create a PowerShell script to set the variables quickly each time.

### Create `set_env.ps1` in your weather-app folder:

```powershell
# set_env.ps1
# Replace with your actual keys
$env:AMBIENT_API_KEY="your_actual_api_key"
$env:AMBIENT_APP_KEY="your_actual_application_key"

Write-Host "Environment variables set!" -ForegroundColor Green
Write-Host "You can now run: python ambient_weather_fetch.py"
```

### Usage:

```powershell
# Run the helper script first
.\set_env.ps1

# Then run your weather app
python ambient_weather_fetch.py
```

**Note:** Don't commit `set_env.ps1` to GitHub! The .gitignore already excludes `.env` files, but be careful.

---

## Troubleshooting

### "ERROR: API credentials not found!"

This means the environment variables aren't set. Make sure you:
1. Set them in the same PowerShell window where you run the script
2. Didn't close PowerShell after setting them (for temporary setup)
3. Reopened PowerShell after setting permanent variables

### Check if variables are set:

```powershell
echo $env:AMBIENT_API_KEY
echo $env:AMBIENT_APP_KEY
```

If these return nothing, the variables aren't set.

### Variables disappear after closing PowerShell

This is normal for temporary variables. Either:
- Set them again each session, OR
- Use the permanent setup method above

---

## Security Best Practices

✅ **DO:**
- Use environment variables for all sensitive data
- Keep your keys private
- Use different keys for different projects if possible

❌ **DON'T:**
- Hardcode keys in your scripts
- Commit files containing keys to GitHub
- Share your keys with others
- Post screenshots containing your keys

---

## Summary

**Quick start (temporary - for each session):**
```powershell
$env:AMBIENT_API_KEY="your_api_key"
$env:AMBIENT_APP_KEY="your_application_key"
python ambient_weather_fetch.py
```

**Permanent setup:**
- Use Windows System Environment Variables (GUI method)
- Or use PowerShell permanent method
- Close and reopen PowerShell after setting

---

**You're all set!** Your keys are now secure and your code is safe to share on GitHub. 🔒
