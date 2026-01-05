# Dashboard Drag-and-Drop Accessibility Testing Guide

**Feature:** Drag-and-drop widget reordering with full WCAG 2.2 AA compliance
**Implementation:** ADR-008
**Last Updated:** 2026-01-05

---

## Overview

The Weather Dashboard implements drag-and-drop widget reordering using dnd-kit with full accessibility support. This document provides comprehensive testing procedures to validate WCAG 2.2 Level AA compliance.

---

## Automated Testing

### 1. Install Testing Dependencies

```bash
cd web
npm install -D @axe-core/react jest-axe @testing-library/react @testing-library/user-event
```

### 2. Configure axe-core Runtime Testing

Add to your main entry point for development:

```typescript
// src/main.tsx (development only)
if (process.env.NODE_ENV !== 'production') {
  import('@axe-core/react').then((axe) => {
    axe.default(React, ReactDOM, 1000);
  });
}
```

### 3. Run Lighthouse CI

```bash
npm install -D @lhci/cli

# Run Lighthouse audit
npx lhci autorun --collect.url=http://localhost:5173

# Accessibility score MUST be ≥95
```

### 4. ESLint Accessibility Linting

```bash
npm install -D eslint-plugin-jsx-a11y

# Add to .eslintrc
{
  "extends": ["plugin:jsx-a11y/recommended"]
}
```

---

## Manual Testing Procedures

### Test 1: Keyboard Navigation (WCAG 2.1.1)

**Objective:** Verify all drag-and-drop functionality works with keyboard only.

**Steps:**
1. Start browser and navigate to dashboard
2. **DO NOT use mouse** - keyboard only
3. Press `Tab` to navigate to first chart card
4. Verify focus indicator is visible (blue ring, 2px minimum)
5. Press `Enter` to activate drag mode
6. Verify screen reader announces: "Picked up [chart name] chart. Use arrow keys to move..."
7. Press `Arrow Down` to move chart down
8. Press `Arrow Right` to move chart right
9. Verify chart position updates
10. Press `Enter` to drop chart at new position
11. Verify screen reader announces: "[chart name] chart was dropped at position X"
12. Press `Escape` while dragging to cancel
13. Verify chart returns to original position
14. Verify screen reader announces: "Dragging [chart name] chart was cancelled"

**Pass Criteria:**
- [ ] Focus indicator visible on all interactive elements
- [ ] Enter key activates drag mode
- [ ] Arrow keys move chart (all 4 directions)
- [ ] Enter key drops chart at new position
- [ ] Escape key cancels drag operation
- [ ] No keyboard traps (can Tab through all elements)

---

### Test 2: Screen Reader Testing - NVDA (Windows)

**Objective:** Verify screen reader users can understand and use drag-and-drop.

**Prerequisites:**
- Install NVDA screen reader (free): https://www.nvaccess.org/download/
- Close other applications to reduce background noise

**Steps:**
1. Start NVDA (Insert + N to open menu, then select "Start NVDA")
2. Navigate to Weather Dashboard in browser
3. Press `H` to jump to headings, verify "Weather Dashboard" is announced
4. Press `Tab` to navigate to first chart
5. Listen for announcement: "[Chart name] chart - draggable, article"
6. Press `Enter` to activate drag
7. **Listen carefully** for announcement: "Picked up [chart name] chart. Use arrow keys to move, Enter to drop, Escape to cancel."
8. Press `Arrow Down`
9. Listen for announcement: "[Chart name] chart is over [other chart] chart"
10. Press `Enter` to drop
11. Listen for announcement: "[Chart name] chart was dropped at position X of 4"
12. Press `R` to navigate by region, verify "Weather charts - drag to reorder" is announced
13. Navigate to "Reset Layout" button, verify it's announced
14. Press `Space` to activate button
15. Verify chart order resets to default

**Pass Criteria:**
- [ ] All chart titles are announced
- [ ] Draggable state is announced ("draggable, article")
- [ ] Drag start is announced with instructions
- [ ] Drag over events are announced
- [ ] Drop event is announced with new position
- [ ] Cancel event is announced
- [ ] Reset button is announced and functional
- [ ] No silent regions (all content is accessible)

---

### Test 3: Screen Reader Testing - VoiceOver (macOS/iPad)

**Objective:** Verify VoiceOver users can use drag-and-drop on desktop and iPad.

**Desktop (macOS) Steps:**
1. Enable VoiceOver: `Cmd + F5`
2. Navigate to Weather Dashboard
3. Press `VO + Right Arrow` to move to next item
4. When on chart card, verify announcement includes "article, draggable"
5. Press `Enter` to activate drag
6. Press `VO + Arrow keys` to move
7. Press `Enter` to drop
8. Press `Cmd + F5` to disable VoiceOver

**iPad Steps:**
1. Enable VoiceOver: Settings > Accessibility > VoiceOver > On
2. Navigate to Weather Dashboard in Safari
3. Swipe right to navigate to chart
4. Verify VoiceOver announces chart name and "draggable"
5. Use VoiceOver rotor (two-finger rotate) to navigate by landmarks
6. Verify "region, Weather charts - drag to reorder" is announced
7. Double-tap to activate drag (VoiceOver gesture)
8. Swipe to move chart
9. Double-tap to drop

**Pass Criteria:**
- [ ] All charts are announced with names
- [ ] Draggable state is communicated
- [ ] VoiceOver rotor shows chart region
- [ ] Drag and drop works with VoiceOver gestures on iPad
- [ ] Instructions are announced

---

### Test 4: Touch Interaction (iPad)

**Objective:** Verify touch targets meet 44×44px minimum and drag-and-drop works smoothly.

**Steps:**
1. Open Weather Dashboard on iPad (or responsive mode in browser)
2. Verify each chart card has sufficient tap target size
3. Long-press on a chart card (200ms delay before drag activates)
4. Drag chart to new position
5. Release to drop
6. Verify smooth animation during drag
7. Verify visual feedback (opacity change, cursor change)
8. Tap "Reset Layout" button
9. Verify button is easy to tap (44×44px minimum)

**Pass Criteria:**
- [ ] All touch targets ≥ 44×44px (WCAG 2.2.7)
- [ ] Long-press activates drag after 200ms
- [ ] Drag is smooth with visual feedback
- [ ] Drop animation is clear
- [ ] No accidental drags during scrolling
- [ ] Reset button is easy to tap

---

### Test 5: Color Contrast (WCAG 1.4.3)

**Objective:** Verify all text and UI elements meet WCAG AA contrast ratios.

**Tools:**
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Browser DevTools contrast checker

**Elements to Check:**
1. Chart card text on white background
2. "Reset Layout" button text on gray-100 background
3. Focus indicator (blue-500 ring) against gray-50 background
4. Drag instructions text (blue-800 on blue-50)
5. Header text (gray-900 on white)

**Pass Criteria:**
- [ ] Normal text: Minimum 4.5:1 contrast
- [ ] Large text (18pt+): Minimum 3:1 contrast
- [ ] UI components: Minimum 3:1 contrast
- [ ] Focus indicators: Minimum 3:1 contrast against both foreground and background

**Expected Results:**
- gray-900 on white: ~21:1 ✅
- blue-800 on blue-50: ~8:1 ✅
- blue-500 ring on gray-50: ~3.5:1 ⚠️ (may need adjustment)

---

### Test 6: Zoom and Responsive Design (WCAG 1.4.10)

**Objective:** Verify dashboard remains usable at 200% zoom without horizontal scrolling.

**Steps:**
1. Navigate to Weather Dashboard
2. Press `Ctrl + +` (Windows) or `Cmd + +` (macOS) to zoom to 200%
3. Verify no horizontal scrolling is required
4. Verify all charts are visible
5. Verify "Reset Layout" button is visible
6. Verify drag-and-drop still works at 200% zoom
7. Test responsive breakpoints:
   - Mobile (<768px): 1-column layout
   - Tablet (768-1023px): 2-column layout
   - Desktop (1024px+): 2-column layout

**Pass Criteria:**
- [ ] No horizontal scrolling at 200% zoom
- [ ] All content remains accessible
- [ ] Drag-and-drop functions at 200% zoom
- [ ] Responsive breakpoints work correctly
- [ ] Touch targets remain ≥44×44px at all zoom levels

---

### Test 7: Focus Management (WCAG 2.4.7)

**Objective:** Verify focus indicators are always visible and meet size requirements.

**Steps:**
1. Tab through all interactive elements
2. Verify focus indicator on each element:
   - Chart cards: Blue ring (2px, ring-2)
   - Reset button: Blue ring (2px, ring-2)
   - Date range controls: Blue ring
3. Verify focus indicator has minimum 2px perimeter (WCAG 2.2)
4. Verify focus indicator color contrast ≥3:1 against background
5. Drag a chart and verify focus remains visible during drag

**Pass Criteria:**
- [ ] Focus indicator visible on all interactive elements
- [ ] Focus indicator minimum 2px perimeter
- [ ] Focus indicator contrast ≥3:1
- [ ] Focus indicator not obscured during drag
- [ ] Focus order is logical (left-to-right, top-to-bottom)

---

### Test 8: Motion and Animation (WCAG 2.3.3)

**Objective:** Verify animations respect prefers-reduced-motion.

**Steps:**
1. Enable reduced motion in OS:
   - Windows: Settings > Ease of Access > Display > Show animations
   - macOS: System Preferences > Accessibility > Display > Reduce motion
2. Refresh Weather Dashboard
3. Drag a chart
4. Verify animations are reduced or disabled
5. Verify functionality still works without animations

**Pass Criteria:**
- [ ] Drag animation respects prefers-reduced-motion
- [ ] Drop animation respects prefers-reduced-motion
- [ ] Functionality works without animations
- [ ] No flashing content (WCAG 2.3.1)

---

## Testing Checklist Summary

**Before Release:**
- [ ] Automated: axe-core shows 0 violations
- [ ] Automated: Lighthouse accessibility score ≥95
- [ ] Automated: ESLint jsx-a11y shows 0 errors
- [ ] Manual: Keyboard navigation works (Tab, Enter, Arrow keys, Escape)
- [ ] Manual: NVDA screen reader testing passed
- [ ] Manual: VoiceOver screen reader testing passed (macOS/iPad)
- [ ] Manual: Touch interaction works on iPad (44×44px targets)
- [ ] Manual: Color contrast meets WCAG AA (4.5:1)
- [ ] Manual: 200% zoom works without horizontal scroll
- [ ] Manual: Focus indicators visible (2px minimum, 3:1 contrast)
- [ ] Manual: prefers-reduced-motion respected

---

## Known Issues and Workarounds

**Issue:** Focus indicator color (blue-500) on gray-50 background is ~3.5:1 contrast, slightly below 3:1 minimum for some monitors.

**Workaround:** Consider using blue-600 or blue-700 for focus ring to ensure consistent 3:1 contrast across all displays.

**Issue:** CSS Grid maintains column-based layout, so visual order matches DOM order. True masonry layout (CSS Columns) would break tab order.

**Status:** Documented in ADR-008. Will migrate to CSS Columns only when variable-height widgets are needed, with keyboard shortcuts to navigate columns.

---

## Resources

- [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/)
- [dnd-kit Accessibility Documentation](https://docs.dndkit.com/guides/accessibility)
- [NVDA Screen Reader](https://www.nvaccess.org/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Lighthouse CI Documentation](https://github.com/GoogleChrome/lighthouse-ci)
- [Project Inclusive Design Standards](../design/inclusive-design.md)

---

## Document Changelog

- **2026-01-05:** Created comprehensive testing guide for ADR-008 implementation
