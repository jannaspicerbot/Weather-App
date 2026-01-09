# ADR-010: Code Signing Strategy

**Status:** Accepted
**Date:** 2026-01-09
**Deciders:** Project Owner

---

## Context

Windows SmartScreen displays a warning when users run unsigned executables:

> "Windows protected your PC - Microsoft Defender SmartScreen prevented an unrecognized app from starting."

This creates friction for users downloading the Weather App installer from GitHub. Users must click "More info" → "Run anyway" to proceed, which may deter non-technical users or raise security concerns.

macOS has similar requirements: unsigned apps trigger Gatekeeper warnings, and apps distributed outside the Mac App Store must be notarized since macOS Catalina.

---

## Decision Drivers

- **User trust**: Reduce friction and security warnings for end users
- **Cost**: Minimize ongoing expenses for a personal/learning project
- **CI/CD integration**: Solution must work with GitHub Actions automated builds
- **Maintenance**: Low ongoing maintenance burden

---

## Options Considered

### Option 1: No Code Signing (Current State)

**Approach:** Accept SmartScreen/Gatekeeper warnings.

| Pros | Cons |
|------|------|
| No cost | Poor user experience |
| No setup required | May deter users |
| | Some enterprise environments block unsigned apps |

### Option 2: SignPath Foundation (Free for Open Source)

**Approach:** Apply for free code signing through SignPath's open source program.

| Pros | Cons |
|------|------|
| Completely free | Publisher shows "SignPath Foundation" |
| Full SmartScreen trust | Application/approval process |
| Excellent CI/CD integration | Requires MFA for all team members |
| Handles certificate management | Manual approval required per release |

**Requirements:**
- Public GitHub repository
- Fully automated build process
- MFA enabled on GitHub and SignPath accounts
- Binary artifacts built from source in verifiable way

### Option 3: Azure Trusted Signing

**Approach:** Use Microsoft's cloud signing service.

| Pros | Cons |
|------|------|
| $10/month (~$120/year) | Ongoing cost |
| Publisher shows your name | Limited availability (US/Canada) |
| Excellent GitHub Actions support | Azure account required |
| Full Microsoft trust | |

### Option 4: Commercial OV Certificate

**Approach:** Purchase a standard code signing certificate (e.g., Certum Cloud ~$108-150/year).

| Pros | Cons |
|------|------|
| Publisher shows your name | Annual cost |
| Works with any CI/CD | SmartScreen reputation builds over 2-8 weeks |
| No approval process | Certificate management responsibility |

### Option 5: Commercial EV Certificate

**Approach:** Purchase an Extended Validation certificate (~$250-300/year).

| Pros | Cons |
|------|------|
| Faster reputation building | Higher cost |
| Organization verification | Requires registered business |
| | EV no longer guarantees instant trust (as of March 2024) |

---

## Decision

**Accepted: Option 2 - SignPath Foundation** as primary strategy, with Option 1 as interim measure.

### Rationale

1. **Cost-effective**: Free for qualifying open source projects
2. **Full trust**: SignPath certificates are fully trusted by Windows SmartScreen
3. **CI/CD ready**: Designed for automated builds with GitHub Actions integration
4. **Low maintenance**: SignPath manages certificate lifecycle

### Trade-offs Accepted

- Publisher name shows "SignPath Foundation" instead of personal/project name
- Requires manual approval for each release (security feature)
- Application process takes 1-2 weeks

### Interim Measure

Until SignPath approval:
- Document SmartScreen bypass instructions for users
- Add installation guide explaining the warning
- Consider applying to Azure Trusted Signing as backup

---

## Implementation Plan

### Phase 1: Documentation (Immediate)

1. Add SmartScreen bypass instructions to README and installation docs
2. Create user-facing installation guide
3. Document the warning and explain why it appears

### Phase 2: SignPath Application

1. Ensure repository meets requirements:
   - Public GitHub repository ✓
   - Automated CI/CD builds ✓
   - MFA enabled on accounts
2. Submit application at https://signpath.org/
3. Configure SignPath integration once approved

### Phase 3: CI/CD Integration (Post-Approval)

1. Add SignPath configuration to repository
2. Update `platform-builds.yml` to submit builds for signing
3. Configure release workflow to wait for signed artifacts

---

## macOS Code Signing (Future)

For macOS distribution without Gatekeeper warnings:

- **Required**: Apple Developer Program ($99/year)
- **Process**: Code signing + notarization
- **Decision**: Defer until there's demand for macOS distribution

Currently, macOS users can bypass Gatekeeper via right-click → Open, which is acceptable for a personal project.

---

## Consequences

### Positive

- Users won't see SmartScreen warnings (after SignPath approval)
- Builds trust with potential users
- Professional appearance for the project

### Negative

- Publisher appears as "SignPath Foundation" not project name
- Adds complexity to release process (manual approval step)
- Dependency on third-party service

### Risks

- SignPath application may be rejected (mitigated by Option 3/4 as backup)
- SignPath service availability (mitigated by having documented manual bypass)

---

## References

- [SignPath Foundation](https://signpath.org/) - Free code signing for open source
- [SignPath Open Source Program Requirements](https://about.signpath.io/product/open-source)
- [Azure Trusted Signing](https://azure.microsoft.com/en-us/products/artifact-signing)
- [Microsoft SmartScreen Documentation](https://docs.microsoft.com/en-us/windows/security/threat-protection/microsoft-defender-smartscreen/microsoft-defender-smartscreen-overview)
- [Melatonin: Code Signing with GitHub Actions](https://melatonin.dev/blog/how-to-code-sign-windows-installers-with-an-ev-cert-on-github-actions/)
