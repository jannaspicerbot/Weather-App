# iPad Setup Guide

This guide explains how to add the Weather Dashboard to your iPad home screen for a native app-like experience.

---

## Prerequisites

1. **Weather App running on your computer** - The backend must be running
2. **iPad on the same WiFi network** as your computer
3. **Safari browser** on iPad (required for "Add to Home Screen")

---

## Step 1: Find Your Computer's IP Address

On the computer running the Weather App:

**Windows:**
1. Open Command Prompt
2. Type `ipconfig` and press Enter
3. Find "IPv4 Address" (usually looks like `192.168.1.xxx`)

**Mac:**
1. Open System Preferences → Network
2. Select your WiFi connection
3. Your IP address is shown (usually looks like `192.168.1.xxx`)

**Example:** `192.168.1.100`

---

## Step 2: Start the Weather App

Make sure the Weather App is running on your computer:

```bash
# If using the desktop app
# Just launch WeatherApp.exe (Windows) or WeatherApp.app (Mac)

# If running from command line
uvicorn weather_app.web.app:create_app --factory --host 0.0.0.0 --port 8000
```

The `--host 0.0.0.0` is important - it allows connections from other devices on your network.

---

## Step 3: Open Safari on iPad

1. Open **Safari** (not Chrome or other browsers - only Safari supports "Add to Home Screen")
2. In the address bar, type: `http://YOUR_IP_ADDRESS:8000`
   - Example: `http://192.168.1.100:8000`
3. The Weather Dashboard should load

---

## Step 4: Add to Home Screen

1. Tap the **Share button** (square with arrow pointing up) at the bottom of Safari
2. Scroll down and tap **"Add to Home Screen"**
3. Edit the name if desired (default: "Weather")
4. Tap **"Add"** in the top right

---

## Step 5: Launch the App

1. Go to your iPad home screen
2. Find the **Weather** app icon
3. Tap to launch - it opens full-screen like a native app!

---

## Features

Once installed, the app:

- **Launches full-screen** (no browser chrome)
- **Has its own app icon** on your home screen
- **Works offline** for recently viewed data (cached for a few minutes)
- **Auto-updates** when new versions are deployed

---

## Troubleshooting

### "Can't connect" or page won't load

1. **Check your computer's IP address** - it may have changed
2. **Make sure the Weather App is running** on your computer
3. **Verify both devices are on the same WiFi network**
4. **Check firewall settings** - port 8000 must be allowed

### App shows old data

The app caches data for offline use. Pull down to refresh, or wait a few minutes for the cache to expire.

### "Add to Home Screen" option not showing

- You must use **Safari** - this feature is not available in Chrome or other browsers
- Make sure the page has fully loaded before trying

### App icon looks wrong

Delete the app from your home screen and re-add it. The icons should be properly sized for iPad.

---

## Network Notes

- The iPad must be on the **same local network** as your computer
- This works over **WiFi only** - the iPad cannot access your computer over cellular data
- If you want to access from anywhere, you'd need to set up port forwarding or a VPN (advanced)

---

## Updating the App

The PWA will automatically update when you visit the app and a new version is available. You don't need to re-add it to your home screen.

If you want to force an update:
1. Open the app
2. Close it completely (swipe up from the bottom)
3. Re-open the app

---

**Last Updated:** January 2026
