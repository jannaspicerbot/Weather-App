# PWA Installation Guide

The Weather Dashboard is a Progressive Web App (PWA) that can be installed on Windows, macOS, and iPad for a native app-like experience without browser chrome.

## Benefits of Installing as a PWA

- **Standalone Window**: No address bar or browser toolbar
- **Desktop/Dock Icon**: Quick access from your taskbar, dock, or home screen
- **Offline Support**: Cached data remains accessible when offline
- **Auto-Updates**: Always get the latest version automatically

---

## Windows Installation

### Chrome

1. Navigate to your Weather Dashboard URL
2. Look for the **Install** icon (computer with arrow) in the address bar
3. Click **Install** in the popup
4. The app will appear in your Start Menu

### Edge

1. Navigate to your Weather Dashboard URL
2. Click the **three dots menu** (⋯) in the top-right
3. Select **Apps** → **Install Weather Dashboard**
4. The app will appear in your Start Menu and can be pinned to the taskbar

### Firefox

1. Navigate to your Weather Dashboard URL
2. If the app is installable, look for the **Install App** button in the dashboard header
3. Click to trigger the installation prompt
4. Follow the browser prompts to complete installation

---

## macOS Installation

### Chrome

1. Navigate to your Weather Dashboard URL
2. Click the **Install** icon in the address bar (right side)
3. Click **Install** in the popup
4. The app will appear in your Applications folder and Launchpad

### Safari

1. Navigate to your Weather Dashboard URL
2. Click **File** → **Add to Dock**
3. The app will appear in your Dock

---

## iPad Installation (Safari)

> **Important**: iPad requires HTTPS for PWA features. See [Local HTTPS Setup](./local-https-setup.md) if accessing a local server.

1. Open **Safari** and navigate to your Weather Dashboard URL
2. Tap the **Share** button (square with upward arrow)
3. Scroll down and tap **Add to Home Screen**
4. Edit the name if desired, then tap **Add**
5. The Weather Dashboard will now appear as an icon on your home screen

### iPad-Specific Features

- **Full-Screen Mode**: Launches without Safari's address bar
- **Splash Screen**: Shows app icon during load
- **Status Bar**: Displays time and battery in translucent style

---

## Verifying Installation

After installation, the app should:

1. Open in its own window (no browser chrome)
2. Show the Weather Dashboard icon in your taskbar/dock/home screen
3. Continue working if you lose network briefly (cached data)

### Checking Display Mode

You can verify PWA mode by checking:

- **Desktop**: Window has no address bar
- **iPad**: No Safari UI, status bar is translucent

---

## Troubleshooting

### "Install" button not appearing

- Ensure you're using a supported browser (Chrome, Edge, Firefox on Windows; Chrome, Safari on macOS)
- Clear browser cache and reload
- Check that the site is served over HTTPS

### iPad won't add to home screen

- Ensure the site is served over HTTPS (required for PWA on iOS)
- Try using Safari (other browsers on iOS don't support home screen installation)
- See [Local HTTPS Setup](./local-https-setup.md) for local network access

### App not updating

- Close and reopen the app
- The service worker should automatically fetch updates
- If stuck, uninstall and reinstall the PWA

---

## Uninstalling

### Windows/macOS

- Right-click the app in Start Menu/Applications and select **Uninstall**
- Or open the PWA, click the three dots menu, and select **Uninstall**

### iPad

- Long-press the app icon until it jiggles
- Tap the **X** or **Remove App** option
- Confirm removal

---

## Related Documentation

- [Local HTTPS Setup](./local-https-setup.md) - Required for iPad local network access
- [ADR-009: iPad/Mobile Support](../architecture/decisions/009-ipad-mobile-support.md) - Architecture decision record
