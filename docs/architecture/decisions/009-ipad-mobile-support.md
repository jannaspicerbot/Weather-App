# ADR-009: iPad/Mobile Support Options

**Status:** Proposed (Not Yet Decided)
**Date:** 2026-01-07
**Deciders:** TBD

---

## Context

The Weather App currently runs as:
- **Web dashboard** (React + TypeScript) - accessible on any device with a browser
- **Desktop apps** (Windows .exe, macOS .app) - standalone installers via PyInstaller

Users have expressed interest in a native iPad/iOS experience. This ADR documents the available options for future consideration.

---

## Options Under Consideration

### Option 1: Progressive Web App (PWA)

**Approach:** Enhance the existing React web app to be installable on iPad/iOS.

**Implementation:**
- Add a web manifest (`manifest.json`)
- Implement a service worker for offline caching
- Add iOS-specific meta tags for home screen icon
- Ensure responsive design works well on iPad

**Pros:**
| Benefit | Details |
|---------|---------|
| Minimal effort | Reuses existing React codebase |
| No Apple Developer account | Free, no $99/year fee |
| No App Store review | Deploy instantly via web |
| Single codebase | Web and "app" are the same |
| Automatic updates | Users always get latest version |

**Cons:**
| Limitation | Details |
|------------|---------|
| No App Store presence | Users can't discover via App Store |
| Limited native features | No push notifications, background refresh |
| Safari-only | Must use Safari to install |
| iOS restrictions | Some web APIs limited on iOS |

**Estimated Effort:** 1-2 days

**CI/CD Impact:** None - existing frontend build works as-is

---

### Option 2: React Native (Full Rewrite)

**Approach:** Rewrite the frontend using React Native for true native iOS/iPadOS app.

**Implementation:**
- Create new React Native project
- Port components from React to React Native
- Use native navigation (React Navigation)
- Implement native charts (Victory Native or similar)
- Set up Xcode project for iOS builds

**Pros:**
| Benefit | Details |
|---------|---------|
| True native experience | Native UI components, gestures |
| App Store distribution | Users can find/install via App Store |
| Push notifications | Full iOS notification support |
| Background refresh | Can fetch data when app is closed |
| Native performance | 60fps animations, native rendering |

**Cons:**
| Limitation | Details |
|------------|---------|
| Complete rewrite | Cannot reuse existing React components |
| Apple Developer account | $99/year required |
| App Store review | 1-7 day review process |
| Two codebases | Web and mobile diverge |
| Complex CI/CD | Xcode, code signing, provisioning |

**Estimated Effort:** 2-4 weeks

**CI/CD Impact:**
- Requires macOS runner with Xcode
- Code signing certificates in GitHub Secrets
- Fastlane for build automation
- App Store Connect API integration

---

### Option 3: Expo (Managed React Native)

**Approach:** Use Expo to simplify React Native development and builds.

**Implementation:**
- Create Expo project
- Port components to React Native
- Use EAS Build for cloud builds (no local Xcode needed)
- Use EAS Submit for App Store uploads

**Pros:**
| Benefit | Details |
|---------|---------|
| Simplified setup | No Xcode configuration required |
| Cloud builds | EAS Build handles iOS builds |
| OTA updates | Push updates without App Store review |
| Easier onboarding | Lower barrier to entry |
| Cross-platform | Android support included |

**Cons:**
| Limitation | Details |
|------------|---------|
| Still a rewrite | Cannot reuse React web components directly |
| Expo limitations | Some native modules not supported |
| EAS costs | Free tier limited, paid for more builds |
| Apple Developer account | Still required ($99/year) |
| Less control | Abstraction layer adds constraints |

**Estimated Effort:** 1-3 weeks

**CI/CD Impact:**
- Can use EAS Build (Expo's cloud service) instead of GitHub Actions
- Still requires Apple Developer account
- Simpler than raw React Native CI/CD

---

### Option 4: Capacitor (Web-to-Native Wrapper)

**Approach:** Wrap the existing React web app in a native iOS container using Capacitor.

**Implementation:**
- Add Capacitor to existing React project
- Configure iOS platform
- Add native plugins as needed (status bar, splash screen)
- Build with Xcode or Capacitor CLI

**Pros:**
| Benefit | Details |
|---------|---------|
| Reuses existing code | Wrap current React app as-is |
| Single codebase | Web and mobile share 95%+ code |
| Native plugins | Access native features via plugins |
| Gradual adoption | Add native features incrementally |
| Ionic ecosystem | Large plugin library available |

**Cons:**
| Limitation | Details |
|------------|---------|
| WebView performance | Not truly native rendering |
| Apple Developer account | Required ($99/year) |
| App Store review | Still need approval |
| Web-like feel | May not feel fully native |
| Plugin limitations | Some features need custom native code |

**Estimated Effort:** 3-5 days

**CI/CD Impact:**
- Requires macOS runner with Xcode
- Code signing complexity
- Capacitor CLI in build pipeline

---

### Option 5: No Mobile App (Web Only)

**Approach:** Focus on responsive web design; users access via Safari.

**Implementation:**
- Ensure responsive design works on iPad
- Optimize touch interactions
- Add "Add to Home Screen" instructions

**Pros:**
| Benefit | Details |
|---------|---------|
| Zero additional effort | Current web app works now |
| No maintenance burden | One codebase, one deployment |
| No Apple fees | No developer account needed |
| Instant updates | Users always have latest version |

**Cons:**
| Limitation | Details |
|------------|---------|
| No home screen icon | Unless user knows to add manually |
| Browser chrome | Address bar takes screen space |
| No offline support | Requires internet connection |
| Less discoverable | No App Store presence |

**Estimated Effort:** None (already works)

---

## Comparison Matrix

| Factor | PWA | React Native | Expo | Capacitor | Web Only |
|--------|-----|--------------|------|-----------|----------|
| **Effort** | 1-2 days | 2-4 weeks | 1-3 weeks | 3-5 days | None |
| **Code Reuse** | 100% | 20-40% | 20-40% | 90-95% | 100% |
| **Apple Dev Account** | No | Yes ($99/yr) | Yes ($99/yr) | Yes ($99/yr) | No |
| **App Store** | No | Yes | Yes | Yes | No |
| **Native Feel** | Medium | High | High | Medium | Low |
| **Offline Support** | Yes | Yes | Yes | Yes | No |
| **Push Notifications** | Limited | Yes | Yes | Yes | No |
| **CI/CD Complexity** | None | High | Medium | High | None |
| **Maintenance** | Low | High | Medium | Medium | None |

---

## Recommendation

**For initial iPad support, we recommend Option 1 (PWA)** because:

1. **Minimal effort** - Can be implemented in 1-2 days
2. **No ongoing costs** - No Apple Developer account needed
3. **Validates demand** - Test if users actually want mobile access
4. **Reversible** - Can pursue native app later if needed
5. **No CI/CD changes** - Existing build pipeline works

If PWA adoption is high and users request native features (push notifications, background refresh), then consider **Option 4 (Capacitor)** as a next step since it maximizes code reuse.

---

## Implementation Notes (PWA)

If we proceed with PWA, the key files needed are:

```
web/
├── public/
│   ├── manifest.json      # Web app manifest
│   ├── sw.js              # Service worker
│   ├── icons/
│   │   ├── icon-192.png   # Android/Chrome icon
│   │   ├── icon-512.png   # Large icon
│   │   └── apple-touch-icon.png  # iOS icon
│   └── index.html         # Add iOS meta tags
```

**Key manifest.json fields:**
```json
{
  "name": "Weather App",
  "short_name": "Weather",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [...]
}
```

**iOS-specific meta tags:**
```html
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Weather App">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
```

---

## Decision

**Status: Proposed** - No decision made yet. This ADR documents options for future reference.

When ready to proceed:
1. Update status to "Accepted"
2. Document chosen option
3. Create implementation tasks

---

## References

- [MDN: Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [React Native Documentation](https://reactnative.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [Capacitor Documentation](https://capacitorjs.com/docs)
- [Apple Developer Program](https://developer.apple.com/programs/)
- [Vite PWA Plugin](https://vite-pwa-org.netlify.app/)
