# Inclusive Design Standards

**Version:** 1.0
**Date:** 2026-01-03
**Status:** Active
**Target Compliance:** WCAG 2.2 Level AA

---

## Table of Contents

- [Introduction](#introduction)
- [Why Inclusive Design Matters](#why-inclusive-design-matters)
- [Strategic Approach: HCD × WCAG](#strategic-approach-hcd--wcag)
- [WCAG 2.2 Principles (POUR)](#wcag-22-principles-pour)
- [Implementation Standards](#implementation-standards)
- [Component-Level Guidelines](#component-level-guidelines)
- [Testing Strategy](#testing-strategy)
- [Tooling & Automation](#tooling--automation)
- [Development Workflow](#development-workflow)
- [Resources & References](#resources--references)

---

## Introduction

Combining Human-Centered Design (HCD) with accessibility (a11y) standards like WCAG transforms compliance from a "checkbox exercise" into a core part of a high-quality user experience. In 2026, the standard for excellence is **"Inclusive Design"**—creating products that are usable by the widest possible range of people, including those with permanent, temporary, or situational disabilities.

### Our Commitment

This Weather App is built for **everyone**:
- Users with visual impairments (screen readers, high contrast, zoom)
- Users with motor disabilities (keyboard-only navigation, voice control)
- Users with cognitive disabilities (plain language, clear structure)
- Users with temporary limitations (broken arm, bright sunlight, noisy environment)

### Compliance Target

- **WCAG 2.2 Level AA** - Industry standard for 2026
- **ADA Title II compliance** - Required by April 2026
- **Section 508** - U.S. federal accessibility standards

---

## Why Inclusive Design Matters

### Legal Requirements

New laws (like the ADA Title II update effective April 2026) make WCAG 2.1 Level AA mandatory for many entities. Non-compliance can result in:
- Legal liability and lawsuits
- Inability to serve government contracts
- Exclusion from public sector deployment

### Business Benefits

- **Wider user base**: 15% of the global population has some form of disability
- **Better UX for everyone**: Curb-cut effect - accessibility improvements help all users
- **SEO advantages**: Semantic HTML and alt text improve search rankings
- **Market differentiation**: Few open-source weather apps prioritize accessibility

### Ethical Responsibility

Building accessible software is about **dignity** and **independence**. Weather data shouldn't be a privilege—it's essential information that everyone deserves equal access to.

---

## Strategic Approach: HCD × WCAG

The most effective way to achieve inclusive design is to map Human-Centered Design phases to the WCAG POUR principles (Perceivable, Operable, Understandable, Robust).

| HCD Phase | WCAG Principle | Actionable Best Practice |
|-----------|----------------|--------------------------|
| **Empathize / Research** | **Perceivable** | Conduct research with users who use screen readers, high-contrast modes, or voice control. Don't just design for "eyes"; design for "ears" and "touch." |
| **Define / Requirements** | **Understandable** | Define accessibility as a "Definition of Done." Example: "All forms must have inline error validation that is announced by screen readers." |
| **Ideate / Prototype** | **Operable** | Ensure every interactive element has a clear Focus State. Test "Keyboard-Only" navigation during the wireframing stage. |
| **Test / Iterate** | **Robust** | Test code on real devices (iOS/Android) with TalkBack/VoiceOver enabled. Automation catches 30-40% of bugs; manual testing catches the rest. |

### Definition of Done

A feature is **not complete** until it meets these accessibility criteria:
- ✅ Passes automated axe-core tests (0 violations)
- ✅ Keyboard navigation works for all interactive elements
- ✅ Screen reader announces all content and state changes
- ✅ Color contrast meets WCAG AA standards (4.5:1 for text)
- ✅ Touch targets are at least 44×44px on mobile
- ✅ Manual testing completed with screen reader

---

## WCAG 2.2 Principles (POUR)

### 1. Perceivable

**Principle**: Information and UI components must be presentable to users in ways they can perceive.

#### Requirements

**1.1 Text Alternatives**
- All images must have alt text
- Decorative images must have `alt=""`
- Complex images (charts, graphs) need detailed descriptions

**1.2 Time-Based Media**
- N/A for this project (no video/audio content currently)

**1.3 Adaptable**
- Content must be presentable in different ways without losing information
- Use semantic HTML (`<button>`, `<nav>`, `<main>`, `<article>`)
- Ensure reading order makes sense when CSS is disabled

**1.4 Distinguishable**
- **Color contrast**: Minimum 4.5:1 for normal text, 3:1 for large text (18pt+)
- **Text resize**: Support up to 200% zoom without horizontal scrolling
- **Reflow**: Content reflows at 320px viewport (mobile)
- **Non-text contrast**: UI components and graphical objects have 3:1 contrast

#### WCAG 2.2 Additions
- **Focus Not Obscured (Minimum)**: When element receives focus, it's not entirely hidden
- **Dragging Movements**: Provide alternative for drag-and-drop (not critical for weather app)

---

### 2. Operable

**Principle**: UI components and navigation must be operable by all users.

#### Requirements

**2.1 Keyboard Accessible**
- All functionality available via keyboard
- No keyboard traps (user can always navigate away)
- Visible focus indicators on all interactive elements
- Tab order follows logical reading order

**2.2 Enough Time**
- No time limits on data viewing
- Auto-updating data (weather) doesn't disrupt user's context

**2.3 Seizures and Physical Reactions**
- Nothing flashes more than 3 times per second
- Respect `prefers-reduced-motion` for animations

**2.4 Navigable**
- Skip links to main content
- Descriptive page titles (`<title>`)
- Focus order is logical
- Link purpose is clear from link text alone

**2.5 Input Modalities**
- Touch targets at least 44×44px (WCAG 2.2: 24×24px minimum)
- Support pointer, keyboard, touch, and voice input

#### WCAG 2.2 Additions
- **Focus Appearance (Minimum)**: Focus indicator is clearly visible (2px minimum perimeter)
- **Target Size (Minimum)**: 24×24 CSS pixels for touch targets

---

### 3. Understandable

**Principle**: Information and operation of UI must be understandable.

#### Requirements

**3.1 Readable**
- Language of page is identified (`<html lang="en">`)
- Content written at 8th-grade reading level (plain language)
- Technical terms are defined on first use

**3.2 Predictable**
- Navigation is consistent across pages
- UI components behave consistently
- No unexpected context changes on focus
- Changes on input are announced to screen readers

**3.3 Input Assistance**
- Form fields have visible labels
- Error messages are specific and helpful
- Errors announced to screen readers
- Suggestions provided for corrections

#### WCAG 2.2 Additions
- **Redundant Entry**: Don't make users re-enter information already provided
- **Accessible Authentication**: Cognitive function test is not required (e.g., no CAPTCHA)

---

### 4. Robust

**Principle**: Content must be robust enough to work with current and future technologies.

#### Requirements

**4.1 Compatible**
- Valid HTML (passes W3C validator)
- Proper ARIA usage (only when semantic HTML insufficient)
- Status messages announced to assistive technologies
- All interactive elements have accessible names

#### WCAG 2.2 Focus
- All custom components have proper ARIA roles, states, and properties
- Live regions (`aria-live`) for dynamic content updates
- Progressive enhancement (works without JavaScript where possible)

---

## Implementation Standards

### HTML Semantics

Use semantic HTML elements to provide meaning and structure:

```html
<!-- ✅ GOOD - Semantic HTML -->
<header>
  <nav>
    <ul>
      <li><a href="/">Dashboard</a></li>
      <li><a href="/settings">Settings</a></li>
    </ul>
  </nav>
</header>

<main>
  <h1>Current Weather</h1>
  <article>
    <h2>Temperature Trends</h2>
    <!-- Chart component -->
  </article>
</main>

<!-- ❌ BAD - Div soup -->
<div class="header">
  <div class="nav">
    <div class="link">Dashboard</div>
    <div class="link">Settings</div>
  </div>
</div>
```

### ARIA Best Practices

**When to use ARIA:**
- Only when semantic HTML is insufficient
- For dynamic content and custom widgets
- To announce state changes to screen readers

**When NOT to use ARIA:**
- Don't override semantic HTML (`<button>` doesn't need `role="button"`)
- Don't use ARIA to fix invalid HTML
- Don't add ARIA if semantic HTML works

```typescript
// ✅ GOOD - Semantic button
<button onClick={handleSubmit}>
  Submit
</button>

// ❌ BAD - ARIA on div (use <button> instead)
<div
  role="button"
  tabIndex={0}
  onClick={handleSubmit}
  onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
>
  Submit
</div>

// ✅ GOOD - ARIA for status announcement
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  {statusMessage}
</div>
```

### Focus Management

```typescript
// ✅ GOOD - Visible focus indicator
button {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

button:focus-visible {
  outline: 3px solid var(--color-focus);
  outline-offset: 3px;
}

// ❌ BAD - Never do this!
* {
  outline: none;
}
```

### Color Contrast

**Minimum ratios (WCAG AA):**
- Normal text (< 18pt): **4.5:1**
- Large text (≥ 18pt or bold ≥ 14pt): **3:1**
- UI components and graphics: **3:1**

**Tools for checking:**
- Chrome DevTools Accessibility Panel
- Figma contrast plugins
- WebAIM Contrast Checker
- ColorSlurp (macOS/iOS)

```css
/* ✅ GOOD - High contrast */
.text-primary {
  color: #1a1a1a; /* Dark gray on white = 12.6:1 */
}

.button-primary {
  background: #0066cc; /* Blue with 4.5:1 on white */
  color: #ffffff;
}

/* ❌ BAD - Low contrast */
.text-muted {
  color: #cccccc; /* Light gray on white = 1.6:1 ❌ */
}
```

---

## Component-Level Guidelines

### Buttons

```typescript
// ✅ GOOD - Accessible button
<button
  type="button"
  aria-label="Refresh weather data"
  onClick={handleRefresh}
  disabled={isLoading}
  aria-busy={isLoading}
>
  {isLoading ? 'Loading...' : 'Refresh'}
</button>

// Touch target: 44×44px minimum
button {
  min-width: 44px;
  min-height: 44px;
  padding: 12px 24px;
}
```

### Form Fields

```typescript
// ✅ GOOD - Accessible form
<div>
  <label htmlFor="api-key">
    Ambient Weather API Key
    <span aria-label="required">*</span>
  </label>
  <input
    id="api-key"
    type="text"
    required
    aria-required="true"
    aria-invalid={hasError}
    aria-describedby={hasError ? "api-key-error" : undefined}
  />
  {hasError && (
    <div id="api-key-error" role="alert">
      API key is required and must be 32 characters
    </div>
  )}
</div>
```

### Navigation

```typescript
// ✅ GOOD - Skip to main content
<a href="#main-content" className="skip-link">
  Skip to main content
</a>

<nav aria-label="Main navigation">
  <ul>
    <li>
      <a href="/" aria-current={pathname === '/' ? 'page' : undefined}>
        Dashboard
      </a>
    </li>
  </ul>
</nav>

<main id="main-content">
  {/* Page content */}
</main>

// CSS for skip link
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

### Charts & Data Visualization

Weather charts need special attention for accessibility.

**This project uses Victory Charts** as the official charting library (see [ADR-007](../architecture/decisions/007-victory-charts.md)).

**Why Victory Charts?**
- Built-in ARIA support via `VictoryAccessibleSVG`
- Keyboard navigation via `VictoryVoronoiContainer` (Tab to enter, arrow keys to navigate data points)
- Screen reader announcements for data points automatically
- Touch-optimized for iPad (larger hit areas, smooth interactions)
- Cross-platform (works on web and React Native if needed later)

**Key accessibility features:**
- `VictoryVoronoiContainer` - Provides keyboard navigation and tooltips
- Automatic ARIA labels for chart elements
- Customizable color palettes (support color-blind friendly schemes)

```typescript
// ✅ GOOD - Accessible Victory Chart with keyboard navigation
import {
  VictoryChart,
  VictoryLine,
  VictoryAxis,
  VictoryVoronoiContainer,
  VictoryTooltip
} from 'victory';

<figure>
  <figcaption>
    <h2 id="temp-chart-title">Temperature Trends - Last 24 Hours</h2>
    <p id="temp-chart-desc">
      Line chart showing temperature ranging from 45°F to 68°F
      with peak at 3:00 PM today.
    </p>
  </figcaption>

  <div
    role="img"
    aria-labelledby="temp-chart-title"
    aria-describedby="temp-chart-desc"
  >
    <VictoryChart
      width={600}
      height={400}
      containerComponent={
        <VictoryVoronoiContainer
          voronoiDimension="x"
          labels={({ datum }) => `${datum.time}: ${datum.temperature}°F`}
          labelComponent={
            <VictoryTooltip
              flyoutStyle={{ fill: "white", stroke: "#64748b" }}
              style={{ fill: "#1e293b", fontSize: 14 }}
            />
          }
        />
      }
    >
      <VictoryAxis
        tickFormat={(t) => new Date(t).toLocaleTimeString()}
      />
      <VictoryAxis dependentAxis tickFormat={(t) => `${t}°F`} />
      <VictoryLine
        data={data}
        x="time"
        y="temperature"
        style={{ data: { stroke: "#3b82f6", strokeWidth: 2 } }}
      />
    </VictoryChart>
  </div>

  {/* REQUIRED: Provide data table alternative for screen readers */}
  <details className="mt-4">
    <summary className="cursor-pointer text-blue-600">
      View data as table
    </summary>
    <table className="mt-2 min-w-full divide-y divide-gray-200">
      <caption className="sr-only">Temperature readings by hour</caption>
      <thead>
        <tr>
          <th scope="col" className="px-4 py-2 text-left">Time</th>
          <th scope="col" className="px-4 py-2 text-left">Temperature (°F)</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-200">
        {data.map(point => (
          <tr key={point.time}>
            <th scope="row" className="px-4 py-2">{point.time}</th>
            <td className="px-4 py-2">{point.temperature}°F</td>
          </tr>
        ))}
      </tbody>
    </table>
  </details>
</figure>
```

**Chart Accessibility Checklist:**
- ✅ Victory chart wrapped in `<figure>` with `<figcaption>`
- ✅ `VictoryVoronoiContainer` enables keyboard navigation
- ✅ ARIA labels (`aria-labelledby`, `aria-describedby`)
- ✅ Data table alternative in `<details>` for screen reader users
- ✅ Color contrast meets WCAG AA (4.5:1 minimum)
- ✅ Color-blind friendly palette (don't rely on color alone)

**Color as Secondary Indicator (WCAG 1.4.1):**

Per WCAG 2.2 standards, color must never be the **only** way to convey information. When multiple data series appear in one chart:

- Use different `strokeDasharray` patterns (solid vs. dashed)
- Include distinct symbols or markers in legends
- Provide text labels where feasible

```typescript
// ✅ GOOD - Color + pattern differentiation
// Primary metric: solid line
<VictoryLine style={{ data: { stroke: 'var(--color-water)', strokeWidth: 2 } }} />

// Secondary metric: dashed line (visually distinct without relying on color)
<VictoryLine style={{ data: { stroke: 'var(--color-growth)', strokeWidth: 2, strokeDasharray: '6,3' } }} />
```

For detailed chart styling guidelines, see [Design Tokens - Chart Implementation Guide](./design-tokens.md#chart-implementation-guide).

---

## Testing Strategy

### Automated Testing (30-40% coverage)

**Tools to integrate:**
- `@axe-core/react` - Runtime accessibility testing
- `eslint-plugin-jsx-a11y` - Static analysis
- `@testing-library/jest-dom` - Accessibility assertions
- `lighthouse-ci` - CI/CD accessibility audits

```typescript
// Example: Component test with accessibility checks
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('Dashboard has no accessibility violations', async () => {
  const { container } = render(<Dashboard />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

test('Button is keyboard accessible', () => {
  const { getByRole } = render(<RefreshButton />);
  const button = getByRole('button', { name: /refresh/i });

  expect(button).toBeInTheDocument();
  expect(button).not.toHaveAttribute('tabindex', '-1');
});
```

### Manual Testing Checklist (60-70% coverage)

Automation misses many issues. **Every feature must be manually tested:**

#### Keyboard Navigation
- [ ] Tab through all interactive elements in logical order
- [ ] Shift+Tab works in reverse
- [ ] Enter activates buttons and links
- [ ] Space activates buttons and checkboxes
- [ ] Arrow keys work for custom components (tabs, sliders)
- [ ] Esc closes modals and dialogs
- [ ] No keyboard traps (can always escape)

#### Screen Reader Testing
- [ ] Test with NVDA (Windows, free)
- [ ] Test with VoiceOver (Mac/iOS, built-in)
- [ ] Test with TalkBack (Android, built-in)
- [ ] All images have meaningful alt text or alt=""
- [ ] Form labels are announced
- [ ] Error messages are announced
- [ ] Dynamic content changes are announced
- [ ] Heading structure is logical (H1 → H2 → H3)

#### Visual & Zoom Testing
- [ ] Zoom to 200% - no horizontal scrolling, all content visible
- [ ] High contrast mode (Windows) - all content visible
- [ ] Dark mode - contrast ratios still meet WCAG AA
- [ ] Reduced motion respected (`prefers-reduced-motion`)
- [ ] Text spacing increased (150% line height) - content doesn't overlap

#### Touch/Mobile Testing
- [ ] All touch targets at least 44×44px
- [ ] No hover-dependent interactions
- [ ] Portrait and landscape orientation work
- [ ] Pinch-to-zoom enabled

### Testing Schedule

**Every PR:**
- Automated axe-core tests must pass
- ESLint accessibility checks (warnings reviewed)

**Before release:**
- Full keyboard navigation test
- Screen reader test (NVDA or VoiceOver)
- Zoom and high contrast test
- Mobile touch target verification

**Quarterly:**
- Full WCAG 2.2 audit
- Real user testing with assistive technology users

---

## Tooling & Automation

### Recommended Libraries

#### For Web (React/TypeScript)

**Component Libraries:**

This project uses **React Aria (Adobe)** as the official component library (see [ADR-006](../architecture/decisions/006-react-aria-components.md)).

**Why React Aria?**
- Industry gold standard for accessibility (WCAG 2.2 Level AA compliant)
- Headless hooks-based architecture - maximum flexibility with TailwindCSS
- All WAI-ARIA 1.2 design patterns implemented correctly
- Focus management, keyboard navigation, and screen reader support built-in
- Touch, mouse, keyboard, and pen input handled automatically (iPad optimized)
- Future-proof: React Native support in development

**Alternatives considered:**
- **Radix UI** - Excellent accessibility, component-based (easier API)
- **Headless UI** - Tailwind-focused, limited component set
- **Chakra UI** - Pre-styled components, WCAG 2.0 baseline

**Why use accessible component libraries?**
Focus management, keyboard navigation, and ARIA attributes are **hard to get right**. React Aria solves 80%+ of accessibility problems with battle-tested patterns from Adobe products.

```typescript
// ✅ GOOD - Using React Aria for accessible dialog
import { useDialog } from '@react-aria/dialog';
import { useOverlay, useModal } from '@react-aria/overlays';

function Dialog({ title, children, isOpen, onClose }) {
  let ref = React.useRef();
  let { overlayProps } = useOverlay({ isOpen, onClose }, ref);
  let { modalProps } = useModal();
  let { dialogProps, titleProps } = useDialog({}, ref);

  return (
    <div {...overlayProps} {...modalProps}>
      <div {...dialogProps} ref={ref}>
        <h2 {...titleProps}>{title}</h2>
        {children}
      </div>
    </div>
  );
}
```

### Development Tools

**Browser Extensions:**
- **axe DevTools** - Real-time accessibility scanning
- **WAVE** - Visual feedback for accessibility issues
- **Accessibility Insights for Web** - Microsoft's guided testing tool

**Command-line Tools:**
- **axe-core/cli** - Automated testing in CI/CD
- **pa11y-ci** - Configurable accessibility testing
- **lighthouse-ci** - Performance + accessibility audits

### CI/CD Integration

```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests

on: [pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run accessibility tests
        run: npm run test:a11y

      - name: Run axe-core scans
        run: npm run test:axe

      - name: Lighthouse CI
        run: npm run lighthouse:ci
        env:
          LHCI_MIN_SCORE_ACCESSIBILITY: 90
```

**Block PRs if:**
- axe-core violations found
- Lighthouse accessibility score < 90
- ESLint jsx-a11y errors (warnings are OK to merge with issue created)

---

## Development Workflow

### Step 1: Design Phase

- [ ] Create mockups with focus states visible
- [ ] Document keyboard shortcuts
- [ ] Choose color palette with WCAG AA contrast
- [ ] Plan heading hierarchy (H1 → H2 → H3)
- [ ] Identify complex interactions (modals, dropdowns) - use accessible library

### Step 2: Implementation

- [ ] Use semantic HTML first
- [ ] Add ARIA only when necessary
- [ ] Implement keyboard navigation
- [ ] Add visible focus indicators
- [ ] Write alt text for images
- [ ] Test with keyboard only
- [ ] Run axe-core during development

### Step 3: Testing

- [ ] Run automated tests (axe-core, ESLint)
- [ ] Keyboard navigation test
- [ ] Screen reader test (quick pass with VoiceOver/NVDA)
- [ ] Zoom to 200% test
- [ ] Color contrast check
- [ ] Touch target verification (mobile)

### Step 4: Code Review

Reviewers must verify:
- [ ] Automated tests pass
- [ ] Manual testing checklist completed
- [ ] Documentation updated (if new patterns introduced)

---

## Resources & References

### Official Standards

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) - Official W3C recommendation
- [ARIA Authoring Practices Guide (APG)](https://www.w3.org/WAI/ARIA/apg/) - Design patterns for common widgets
- [Section 508](https://www.section508.gov/) - U.S. federal accessibility standards

### Learning Resources

- [The A11y Project](https://www.a11yproject.com/) - Community-driven accessibility checklist
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility) - Comprehensive guides
- [WebAIM](https://webaim.org/) - Articles, tools, and training
- [Deque University](https://dequeuniversity.com/) - In-depth courses (paid)

### Tools & Testing

- [axe DevTools](https://www.deque.com/axe/devtools/) - Browser extension for accessibility scanning
- [WAVE](https://wave.webaim.org/) - Visual accessibility evaluation tool
- [Accessibility Insights](https://accessibilityinsights.io/) - Microsoft's automated and manual testing tool
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) - Color contrast ratio calculator
- [Who Can Use](https://whocanuse.com/) - Color contrast simulator for different vision types

### Component Libraries

- [React Aria (Adobe)](https://react-spectrum.adobe.com/react-aria/) - Accessible React hooks
- [Radix UI](https://www.radix-ui.com/) - Unstyled accessible components
- [Headless UI](https://headlessui.com/) - Tailwind's accessible components
- [Chakra UI](https://chakra-ui.com/) - Full component library with accessibility

### Screen Readers

- [NVDA](https://www.nvaccess.org/) - Free, open-source screen reader (Windows)
- [VoiceOver](https://www.apple.com/accessibility/voiceover/) - Built into macOS and iOS
- [TalkBack](https://support.google.com/accessibility/android/answer/6283677) - Built into Android
- [JAWS](https://www.freedomscientific.com/products/software/jaws/) - Commercial screen reader (Windows)

### Plain Language

- [PlainLanguage.gov](https://www.plainlanguage.gov/) - U.S. government plain language guidelines
- [Hemingway Editor](https://hemingwayapp.com/) - Readability checker
- [Readable](https://readable.com/) - Content readability analysis

---

## Document Changelog

- **2026-01-03:** Updated with official library decisions (React Aria, Victory Charts)
  - Added links to ADR-006 (React Aria) and ADR-007 (Victory Charts)
  - Updated component library section with React Aria as official choice
  - Updated charts section with Victory Charts implementation examples
- **2026-01-03:** Initial inclusive design standards document created
  - Integrated HCD × WCAG strategic approach
  - Defined WCAG 2.2 Level AA compliance target
  - Established testing strategy and tooling recommendations

---

## Related Documents

- [docs/CONTRIBUTING.md](../CONTRIBUTING.md) - General contribution guidelines
- [Architecture Decision Records](../architecture/decisions/) - Technical decisions
- Product Requirements - User personas and accessibility needs

---

**Questions or suggestions?** Open an issue or submit a PR to improve these standards.
