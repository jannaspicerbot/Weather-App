# Release Management Guide

This guide explains how to create and manage releases for the Weather App.

## 📋 Table of Contents

- [Overview](#overview)
- [Creating a Release](#creating-a-release)
- [Release Workflow](#release-workflow)
- [Finding Releases](#finding-releases)
- [Docker Images](#docker-images)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Weather App uses **GitHub Releases** to distribute platform-specific builds and Docker images. When you push a version tag (e.g., `v1.0.0`), GitHub Actions automatically:

1. Builds Windows and macOS installers
2. Builds and pushes a Docker image to GitHub Container Registry
3. Creates a GitHub Release with all assets attached

---

## Creating a Release

### Step 1: Prepare Your Code

Ensure all changes are committed and pushed to the `main` branch:

```bash
# Make sure you're on main and up to date
git checkout main
git pull origin main

# Verify everything is working
pytest tests/ -m "not requires_api_key"
npm --prefix web run build
```

### Step 2: Create a Version Tag

Use [semantic versioning](https://semver.org/) for version numbers: `vMAJOR.MINOR.PATCH`

```bash
# Create an annotated tag with release notes
git tag -a v1.0.0 -m "Release v1.0.0: Initial stable release"

# Push the tag to GitHub (this triggers the release workflow)
git push origin v1.0.0
```

**Tag Naming Convention:**
- `v1.0.0` - Major release (breaking changes)
- `v1.1.0` - Minor release (new features, backward compatible)
- `v1.0.1` - Patch release (bug fixes only)

### Step 3: Monitor the Workflow

The release workflow will automatically start:

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Look for the **"Release Build & Publish"** workflow
4. Monitor progress (takes ~10-15 minutes)

### Step 4: Verify the Release

Once the workflow completes:

1. Go to your repository's main page
2. Click **Releases** in the right sidebar (or visit `https://github.com/USERNAME/Weather-App/releases`)
3. Verify all assets are present:
   - `WeatherApp-Windows-v1.0.0.zip`
   - `WeatherApp-macOS-v1.0.0.zip`
   - Docker image links in the release notes

---

## Release Workflow

The release workflow ([.github/workflows/release.yml](../../.github/workflows/release.yml)) performs these steps:

### 1. Platform Builds (Parallel)

**Windows Installer:**
- Builds production and debug executables using PyInstaller
- Packages frontend assets
- Uploads as artifact

**macOS App Bundle:**
- Builds production and debug `.app` bundles using PyInstaller
- Generates `.icns` icon
- Uploads as artifact

### 2. Docker Image Build

- Builds multi-stage Docker image (frontend + backend)
- Pushes to GitHub Container Registry with two tags:
  - `ghcr.io/USERNAME/weather-app:1.0.0` (version-specific)
  - `ghcr.io/USERNAME/weather-app:latest` (always points to latest release)

### 3. Release Creation

- Downloads all build artifacts
- Packages installers as `.zip` files
- Creates GitHub Release with:
  - Auto-generated release notes
  - Installation instructions
  - Docker usage examples
  - Download links

---

## Finding Releases

### GitHub Releases Page

The **easiest way** to find releases:

1. **From Repository Main Page:**
   - Look at the right sidebar under "Releases"
   - Click "Releases" or the latest version number

2. **Direct URL:**
   ```
   https://github.com/USERNAME/Weather-App/releases
   ```

3. **Latest Release Direct Link:**
   ```
   https://github.com/USERNAME/Weather-App/releases/latest
   ```

### What You'll See

Each release includes:

- **Version number** (e.g., v1.0.0)
- **Release date** and author
- **Release notes** (auto-generated changelog)
- **Assets** (downloadable files):
  - Windows installer (`.zip`)
  - macOS app bundle (`.zip`)
  - Source code (auto-generated)
- **Docker image links** in the description

---

## Docker Images

### Finding Docker Images

**GitHub Container Registry:**

1. Go to your repository
2. Click **Packages** (right sidebar, below "Releases")
3. Click `weather-app`
4. See all versions and tags

**Or visit directly:**
```
https://github.com/USERNAME/weather-app/pkgs/container/weather-app
```

### Pulling Docker Images

**Pull latest version:**
```bash
docker pull ghcr.io/USERNAME/weather-app:latest
```

**Pull specific version:**
```bash
docker pull ghcr.io/USERNAME/weather-app:1.0.0
```

### Running Docker Image

**Basic usage:**
```bash
docker run -d \
  -p 8000:8000 \
  -v weather-data:/data \
  -e AMBIENT_API_KEY=your_api_key \
  -e AMBIENT_APP_KEY=your_app_key \
  ghcr.io/USERNAME/weather-app:latest
```

**Access the app:**
- Frontend: http://localhost:8000
- API docs: http://localhost:8000/docs

**Environment Variables:**
- `AMBIENT_API_KEY` - Your Ambient Weather API key (required)
- `AMBIENT_APP_KEY` - Your Ambient Weather Application key (required)
- `DB_PATH` - Database path (default: `/data/ambient_weather.duckdb`)

**Volumes:**
- Mount `/data` to persist the database between container restarts

---

## Troubleshooting

### Release Workflow Fails

**Check the Actions Tab:**
1. Go to **Actions** → **Release Build & Publish**
2. Click on the failed workflow run
3. Expand failed steps to see error messages

**Common Issues:**

**1. Platform Builds Fail**
- Check [platform-builds.yml](../../.github/workflows/platform-builds.yml) workflow
- Verify frontend builds successfully: `npm --prefix web run build`
- Verify PyInstaller spec files are present in `installer/windows/` and `installer/macos/`

**2. Docker Build Fails**
- Test locally: `docker build -t weather-app .`
- Check Dockerfile syntax
- Ensure frontend and backend build successfully

**3. Artifacts Not Found**
- Verify artifacts were uploaded in platform-builds job
- Check artifact names match in release workflow
- Ensure `github.sha` is correctly referenced

### Delete a Failed Release

```bash
# Delete the tag locally
git tag -d v1.0.0

# Delete the tag remotely
git push origin :refs/tags/v1.0.0

# Delete the release on GitHub (use the web UI or gh CLI)
gh release delete v1.0.0
```

Then fix the issue and create the tag again.

### Docker Image Not Public

By default, GitHub Container Registry images are private. To make them public:

1. Go to **Packages** → `weather-app`
2. Click **Package settings**
3. Scroll to **Danger Zone**
4. Click **Change visibility** → **Public**

---

## Best Practices

### Before Releasing

- [ ] All tests pass locally
- [ ] Frontend builds successfully
- [ ] Backend runs without errors
- [ ] Update version in relevant files (if applicable)
- [ ] Update CHANGELOG.md (optional but recommended)
- [ ] Merge all feature branches to `main`

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (v2.0.0): Breaking changes, incompatible API changes
- **MINOR** (v1.1.0): New features, backward compatible
- **PATCH** (v1.0.1): Bug fixes, backward compatible

### Release Frequency

- **Stable releases** (v1.x.x): When significant features are complete and tested
- **Patch releases** (v1.0.x): For critical bug fixes
- **Pre-releases** (v1.0.0-beta.1): Use `-beta`, `-rc` suffix for testing

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Semantic Versioning](https://semver.org/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

**Last Updated:** January 12, 2026
