# SignPath Foundation Application Guide

This document outlines the requirements and steps for applying to [SignPath Foundation](https://signpath.org/) for free code signing.

---

## Overview

SignPath Foundation provides **free code signing certificates** for qualifying open source projects. Once approved:
- Windows SmartScreen warnings are eliminated
- The publisher shows as "SignPath Foundation"
- Signing is integrated into GitHub Actions CI/CD

---

## Requirements Checklist

### Repository Requirements

- [x] **Public GitHub repository** - https://github.com/jannaspicerbot/Weather-App
- [x] **Open source license** - Repository is public
- [x] **Automated CI/CD builds** - GitHub Actions workflows in place
- [x] **Build from source** - PyInstaller builds from source code

### Account Requirements

- [ ] **MFA enabled on GitHub** - Required for all team members
- [ ] **MFA enabled on SignPath** - Required after account creation

### Build Process Requirements

- [x] **Deterministic builds** - Same source produces same output
- [x] **No external dependencies at build time** - All dependencies in `requirements.txt`
- [x] **Artifacts built by CI** - GitHub Actions produces the executables

---

## Application Process

### Step 1: Enable MFA on GitHub

1. Go to GitHub → Settings → Password and authentication
2. Enable two-factor authentication (2FA)
3. Use authenticator app (recommended) or SMS

### Step 2: Create SignPath Account

1. Go to https://signpath.io/
2. Sign up with your GitHub account
3. Enable MFA on your SignPath account

### Step 3: Submit Application

1. Go to https://signpath.org/ (Foundation site)
2. Click "Apply for free signing"
3. Provide repository URL: `https://github.com/jannaspicerbot/Weather-App`
4. Describe the project and its open source nature
5. Submit application

### Step 4: Wait for Approval

- Typical turnaround: 1-2 weeks
- SignPath may request additional information
- They verify the project meets open source criteria

### Step 5: Configure Integration

After approval, SignPath provides:
- Organization slug
- Project configuration
- Signing policy

---

## CI/CD Integration (Post-Approval)

### Add SignPath Configuration

Create `.signpath/config.yml` in repository root:

```yaml
# SignPath configuration for Weather App
# See: https://about.signpath.io/documentation/configuration

artifact-configuration:
  - name: weather-app-windows
    path: installer/windows/dist/WeatherApp.exe
    signing-policy: release-signing
```

### Update GitHub Actions Workflow

Add to `platform-builds.yml` after build step:

```yaml
- name: Submit for Signing
  if: github.ref == 'refs/heads/main'
  uses: signpath/github-action-submit-signing-request@v0.4
  with:
    api-token: ${{ secrets.SIGNPATH_API_TOKEN }}
    organization-id: ${{ secrets.SIGNPATH_ORG_ID }}
    project-slug: weather-app
    signing-policy-slug: release-signing
    artifact-configuration-slug: weather-app-windows
    github-artifact-name: windows-installer-${{ github.sha }}
    wait-for-completion: true
```

### Add GitHub Secrets

After SignPath approval, add these secrets to the repository:
- `SIGNPATH_API_TOKEN` - API token from SignPath dashboard
- `SIGNPATH_ORG_ID` - Organization ID from SignPath

---

## Release Process (Post-Approval)

1. **Merge to main** - Triggers platform-builds workflow
2. **Build completes** - Unsigned artifacts created
3. **Submit to SignPath** - Workflow submits for signing
4. **Manual approval** - Approve signing in SignPath dashboard
5. **Signed artifacts** - Download from SignPath or GitHub

---

## Alternative: Azure Trusted Signing

If SignPath application is rejected or takes too long, consider:

**Azure Trusted Signing** ($10/month)
- Microsoft's official signing service
- Immediate availability (no application process)
- Publisher shows your name (not "SignPath Foundation")

See [ADR-010](../architecture/decisions/010-code-signing-strategy.md) for comparison.

---

## References

- [SignPath Foundation](https://signpath.org/)
- [SignPath Documentation](https://about.signpath.io/documentation/)
- [SignPath GitHub Action](https://github.com/SignPath/github-action-submit-signing-request)
- [Open Source Program Requirements](https://about.signpath.io/product/open-source)
