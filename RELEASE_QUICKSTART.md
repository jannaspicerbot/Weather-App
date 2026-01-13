# Release Quickstart Guide

> **TL;DR:** Push a version tag to automatically create a release with Windows, macOS, and Docker builds.

## Creating a Release (3 Steps)

### 1. Commit and Push Your Code
```bash
git checkout main
git pull origin main
```

### 2. Create a Version Tag
```bash
# Create tag (use semantic versioning)
git tag -a v1.0.0 -m "Release v1.0.0: Your release notes here"

# Push tag to GitHub (triggers automatic release)
git push origin v1.0.0
```

### 3. Wait for Automation
- GitHub Actions builds everything (~10-15 minutes)
- Release appears automatically at: `github.com/YOUR-USERNAME/Weather-App/releases`

## What Gets Built Automatically

When you push a tag, GitHub Actions automatically:

✅ **Windows Installer** - `.exe` packaged as `.zip`
✅ **macOS App Bundle** - `.app` packaged as `.zip`
✅ **Docker Image** - Pushed to GitHub Container Registry
✅ **GitHub Release** - Created with all downloads and instructions

## Finding Your Releases

### Desktop Installers
**Location:** `github.com/YOUR-USERNAME/Weather-App/releases`

Users download and run:
- Windows: `WeatherApp-Windows-v1.0.0.zip`
- macOS: `WeatherApp-macOS-v1.0.0.zip`

### Docker Images
**Location:** `github.com/YOUR-USERNAME/weather-app/pkgs/container/weather-app`

Users run:
```bash
docker pull ghcr.io/YOUR-USERNAME/weather-app:1.0.0
docker pull ghcr.io/YOUR-USERNAME/weather-app:latest  # Always latest
```

## Version Numbering (Semantic Versioning)

Use `vMAJOR.MINOR.PATCH` format:

- `v1.0.0` → `v2.0.0` - Major release (breaking changes)
- `v1.0.0` → `v1.1.0` - Minor release (new features)
- `v1.0.0` → `v1.0.1` - Patch release (bug fixes)

## Troubleshooting

**Release failed?**
1. Check Actions tab: `github.com/YOUR-USERNAME/Weather-App/actions`
2. Delete tag and try again:
   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   ```

**Need more details?** See [docs/technical/releases.md](docs/technical/releases.md)

---

**That's it!** Creating releases is now as simple as pushing a tag. 🎉
