# Local HTTPS Setup for iPad PWA

iPad Safari requires HTTPS to enable PWA features like "Add to Home Screen" with standalone display mode. This guide explains how to set up local HTTPS using **mkcert** for development and local network access.

---

## Why HTTPS is Required

iOS/iPadOS enforces security restrictions:

- Service workers only work over HTTPS (or localhost)
- "Add to Home Screen" with `display: standalone` requires HTTPS
- Mixed content (HTTP resources on HTTPS page) is blocked

For local network access from your iPad to your PC/Mac server, you need a trusted HTTPS certificate.

---

## Prerequisites

- **Windows**: Windows 10/11 with PowerShell or WSL
- **macOS**: macOS 10.13+
- **Your PC/Mac's local IP**: e.g., `192.168.1.100`
- **iPad on the same network**

---

## Step 1: Install mkcert

### Windows (Chocolatey)

```powershell
choco install mkcert
```

### Windows (Scoop)

```powershell
scoop bucket add extras
scoop install mkcert
```

### macOS (Homebrew)

```bash
brew install mkcert
```

---

## Step 2: Install the Local CA

This creates a local Certificate Authority that your devices will trust.

```bash
mkcert -install
```

> This adds mkcert's CA to your system's trust store. You'll need to do this once per machine.

---

## Step 3: Generate Certificates

Generate a certificate for localhost AND your local IP address:

```bash
# Replace 192.168.1.100 with your actual local IP
mkcert localhost 127.0.0.1 192.168.1.100
```

This creates two files:

- `localhost+2.pem` (certificate)
- `localhost+2-key.pem` (private key)

### Finding Your Local IP

**Windows:**
```powershell
ipconfig | findstr "IPv4"
```

**macOS:**
```bash
ipconfig getifaddr en0
```

---

## Step 4: Configure the Backend for HTTPS

### Option A: Uvicorn with SSL

Move the certificate files to your project and update the server command:

```bash
# Move certificates to a certs folder
mkdir certs
mv localhost+2.pem certs/cert.pem
mv localhost+2-key.pem certs/key.pem

# Run uvicorn with SSL
uvicorn weather_app.web.app:create_app --factory --host 0.0.0.0 --port 8000 \
  --ssl-certfile certs/cert.pem --ssl-keyfile certs/key.pem
```

### Option B: Create a Run Script

Create `run-https.sh` (or `.ps1` for Windows):

```bash
#!/bin/bash
uvicorn weather_app.web.app:create_app --factory \
  --host 0.0.0.0 \
  --port 8000 \
  --ssl-certfile certs/cert.pem \
  --ssl-keyfile certs/key.pem \
  --reload
```

---

## Step 5: Trust the CA on iPad

To make your iPad trust the local CA:

### 5a: Export the CA Certificate

Find the CA certificate location:

```bash
mkcert -CAROOT
```

This shows the folder containing `rootCA.pem`.

### 5b: Transfer to iPad

Options to transfer `rootCA.pem` to your iPad:

- **AirDrop** (macOS only)
- **Email** the file to yourself
- **iCloud Drive** or other cloud storage
- **Web server**: Temporarily serve it from your local server

### 5c: Install the CA Profile

1. Open `rootCA.pem` on your iPad
2. Safari will prompt: "This website is trying to download a configuration profile"
3. Tap **Allow**
4. Go to **Settings** → **General** → **VPN & Device Management**
5. Tap the downloaded profile (mkcert)
6. Tap **Install** and enter your passcode

### 5d: Enable Full Trust

1. Go to **Settings** → **General** → **About** → **Certificate Trust Settings**
2. Under "Enable full trust for root certificates", toggle ON for **mkcert**
3. Tap **Continue** in the warning dialog

---

## Step 6: Test the Connection

### From iPad Safari

1. Open Safari on your iPad
2. Navigate to `https://192.168.1.100:8000` (your PC's IP)
3. You should see the Weather Dashboard without certificate warnings
4. Tap **Share** → **Add to Home Screen**

### Verify PWA Features

After adding to home screen:

- App should open in standalone mode (no Safari UI)
- Splash screen should display briefly
- Status bar should be translucent

---

## Troubleshooting

### "Not Secure" Warning on iPad

- Verify the CA is installed: **Settings** → **General** → **VPN & Device Management**
- Verify trust is enabled: **Settings** → **General** → **About** → **Certificate Trust Settings**
- Ensure you're accessing the correct IP with HTTPS

### Certificate Expired

mkcert certificates are valid for ~2 years. To regenerate:

```bash
mkcert localhost 127.0.0.1 YOUR_LOCAL_IP
```

Then repeat the trust steps on iPad.

### iPad Can't Connect

- Verify both devices are on the same network
- Check Windows Firewall / macOS Firewall allows port 8000
- Ping your PC from iPad (use a network utility app)

### Frontend Proxy Issues

If running the Vite dev server separately, you'll need to configure its proxy to use HTTPS or access the backend directly:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'https://localhost:8000',
      secure: false, // Accept self-signed certs in dev
      changeOrigin: true,
    },
  },
},
```

---

## Security Notes

- **Never commit** certificate files to git (add to `.gitignore`)
- The mkcert CA is only trusted on devices where you explicitly install it
- For production, use proper certificates from Let's Encrypt or similar

### Add to .gitignore

```
# Local HTTPS certificates
certs/
*.pem
```

---

## Quick Reference

| Step | Command/Action |
|------|----------------|
| Install mkcert | `brew install mkcert` or `choco install mkcert` |
| Install CA | `mkcert -install` |
| Generate cert | `mkcert localhost 127.0.0.1 YOUR_IP` |
| Find CA | `mkcert -CAROOT` |
| Run with SSL | `uvicorn ... --ssl-certfile cert.pem --ssl-keyfile key.pem` |

---

## Related Documentation

- [PWA Setup Guide](./pwa-setup.md) - Installation instructions for all platforms
- [mkcert GitHub](https://github.com/FiloSottile/mkcert) - Official documentation
