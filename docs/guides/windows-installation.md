# Windows Installation Guide

This guide covers installing the Weather Dashboard on Windows using the standalone installer.

---

## Download the Installer

1. Go to the [GitHub Actions](https://github.com/jannaspicerbot/Weather-App/actions/workflows/platform-builds.yml) page
2. Click on the most recent successful build
3. Scroll to **Artifacts** and download `windows-installer-...`
4. Extract the zip file

---

## Windows SmartScreen Warning

When running `WeatherApp.exe` for the first time, you may see this warning:

> **"Windows protected your PC"**
> Microsoft Defender SmartScreen prevented an unrecognized app from starting.

### Why This Happens

This warning appears because the executable is not yet code-signed with a trusted certificate. This is normal for open-source software distributed outside of official app stores.

**The app is safe to run** - you can verify this by:
- Reviewing the [source code on GitHub](https://github.com/jannaspicerbot/Weather-App)
- Checking that you downloaded from the official repository
- Verifying the build was created by GitHub Actions (not modified)

### How to Bypass the Warning

1. Click **"More info"** (blue link below the warning text)
2. Click **"Run anyway"** button that appears
3. The app will start normally

![SmartScreen Bypass](../design/screenshots/smartscreen-bypass.png)

> **Note:** You only need to do this once. Windows remembers your choice for this specific file.

### Future Improvement

We're working on getting the app code-signed through [SignPath Foundation](https://signpath.org/), which will eliminate this warning in future releases. See [ADR-010](../architecture/decisions/010-code-signing-strategy.md) for details.

---

## First-Time Setup

After the app launches:

1. **System Tray**: The app runs in the system tray (bottom-right of taskbar)
2. **Dashboard**: Your browser will open to `http://localhost:8000`
3. **Configure**: Add your Ambient Weather API credentials if not already set

### Setting Up API Credentials

If you haven't configured your credentials yet:

1. Get your API keys from [Ambient Weather](https://ambientweather.net/account)
2. Create a `.env` file in the app's data directory with:
   ```
   AMBIENT_API_KEY=your_api_key_here
   AMBIENT_APP_KEY=your_app_key_here
   ```
3. Restart the app

---

## Installing as a PWA (Alternative)

Instead of the desktop installer, you can install the Weather Dashboard as a Progressive Web App:

1. Start the backend server (via Docker or native installation)
2. Open `http://localhost:8000` in Chrome, Edge, or Firefox
3. Click the **"Install App"** button in the dashboard header
4. The app installs to your Start Menu with its own window

See [PWA Setup Guide](./pwa-setup.md) for detailed instructions.

---

## Troubleshooting

### App won't start

- Check Windows Event Viewer for errors
- Ensure no other app is using port 8000
- Try running as Administrator (right-click → Run as administrator)

### Dashboard doesn't load

- Wait a few seconds for the server to start
- Check that `http://localhost:8000` is accessible
- Look for firewall prompts blocking the connection

### No weather data

- Verify your API credentials in the `.env` file
- Check your internet connection
- Ensure your Ambient Weather station is online

---

## Uninstalling

1. Right-click the system tray icon and select **Exit**
2. Delete the `WeatherApp` folder
3. Optionally remove the data folder (contains your database)

---

## Related Documentation

- [PWA Setup Guide](./pwa-setup.md) - Install as a web app instead
- [CLI Reference](../technical/cli-reference.md) - Command-line options
- [Deployment Guide](../technical/deployment-guide.md) - Docker and server setup
