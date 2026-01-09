# ADR-006: React Aria Component Library

**Status:** ✅ Accepted (Phase 3)
**Date:** 2026-01-03
**Deciders:** Janna Spicer, Architecture Review

> **Update (2026-01-09):** This ADR references TailwindCSS which was later replaced with CSS Custom Properties (design tokens). React Aria remains the component library choice - it is unstyled and works well with any CSS approach.

---

## Context

The Weather App needs a component library for building the Web UI (Phase 3). The UI must support:
- WCAG 2.2 Level AA compliance (mandatory for inclusive design)
- Desktop and iPad browser usage (not native mobile apps)
- Keyboard navigation, screen reader support, touch interaction
- TailwindCSS integration (already in stack)
- TypeScript type safety (already in stack)
- Flexibility for future design evolution

The decision is being made **before building the frontend** to avoid migration costs.

### User Requirements

From user discussion (2026-01-03):
> "we're building an app for desktop or ipad use, both using a browser - not a native app store app. but, we really do want to provide for a great user experience for all users, with true inclusive design."

### Inclusive Design Standards

From [docs/design/inclusive-design.md](../design/inclusive-design.md):
- WCAG 2.2 Level AA compliance is required
- ADA Title II compliance mandatory by April 2026
- HCD × WCAG integration (POUR principles)
- Accessibility as "Definition of Done"

---

## Decision

We will use **React Aria** (Adobe) as the component library for the Web UI.

---

## Rationale

### Comparison with Alternatives

| Feature | React Aria | Radix UI | Chakra UI | Headless UI |
|---------|-----------|----------|-----------|-------------|
| **WCAG 2.2 AA** | ✅ Full support | ✅ Strong | ⚠️ WCAG 2.0 | ⚠️ Basic |
| **Accessibility Quality** | ✅ Industry gold standard | ✅ Excellent | ⚠️ Good | ⚠️ Basic |
| **TailwindCSS Integration** | ✅ Full control (unstyled) | ✅ Purpose-built | ❌ CSS-in-JS | ✅ Native |
| **TypeScript Support** | ✅ Excellent | ✅ Excellent | ✅ Good | ✅ Good |
| **Bundle Size** | ✅ Small (tree-shakeable) | ✅ Small | ❌ Large (~100KB+) | ✅ Very small |
| **Learning Curve** | ⚠️ Steeper (hooks) | ✅ Moderate | ✅ Easy | ✅ Very easy |
| **Component Coverage** | ✅ Comprehensive | ✅ Comprehensive | ✅ Very comprehensive | ❌ Limited |
| **iPad/Touch Support** | ✅ Excellent | ✅ Good | ✅ Good | ✅ Basic |
| **Future-Proofing** | ✅ React Native ready | ✅ Web-only | ❌ Web-only | ❌ Web-only |

### Key Benefits

1. **Industry Gold Standard Accessibility**
   - Developed by Adobe for Adobe products (Photoshop Web, Adobe Express)
   - Tested with real assistive technology users
   - Implements WCAG 2.2 Level AA including:
     - APCA (Advanced Perceptual Contrast Algorithm) for better color contrast
     - Focus visible (WCAG 2.2 new requirement)
     - Dragging movements (WCAG 2.2 new requirement)
     - Target size minimum (44×44px touch targets)

2. **Hooks-Based Architecture**
   ```typescript
   // React Aria provides hooks for maximum flexibility
   import { useButton } from '@react-aria/button';
   import { useTextField } from '@react-aria/textfield';

   function Button(props) {
     let ref = useRef();
     let { buttonProps } = useButton(props, ref);

     return (
       <button {...buttonProps} ref={ref} className="btn-primary">
         {props.children}
       </button>
     );
   }
   ```

3. **Complete ARIA Patterns**
   - All WAI-ARIA 1.2 design patterns implemented
   - Keyboard navigation (arrow keys, Enter, Escape, Tab)
   - Screen reader announcements (live regions, roles, labels)
   - Focus management (trap, restore, visible indicators)
   - Touch gesture support (swipe, drag, pinch)

4. **iPad Optimization**
   - Touch, mouse, keyboard, and pen input handled automatically
   - Adaptive behavior (e.g., hover states only for pointer devices)
   - Proper touch target sizing (44×44px minimum)
   - VoiceOver optimization for iOS screen reader

5. **TailwindCSS Integration**
   ```typescript
   // React Aria is unstyled - perfect for Tailwind
   function TextField(props) {
     let { label } = props;
     let ref = useRef();
     let { labelProps, inputProps } = useTextField(props, ref);

     return (
       <div className="flex flex-col gap-2">
         <label {...labelProps} className="text-sm font-medium text-gray-700">
           {label}
         </label>
         <input
           {...inputProps}
           ref={ref}
           className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
         />
       </div>
     );
   }
   ```

6. **Future-Proof for React Native**
   - Adobe is developing `@react-aria/native` for React Native
   - If mobile becomes native app later, component logic is reusable
   - Hooks work identically across platforms

### Alignment with Inclusive Design Standards

From [docs/design/inclusive-design.md](../design/inclusive-design.md):

| Requirement | React Aria Support |
|-------------|-------------------|
| **Keyboard Navigation** | ✅ All components support keyboard (arrow keys, Tab, Enter, Escape) |
| **Screen Reader** | ✅ NVDA, JAWS, VoiceOver, TalkBack tested and supported |
| **Color Contrast** | ✅ APCA algorithm for accurate contrast measurement |
| **Touch Targets** | ✅ 44×44px minimum enforced in component design |
| **Focus Management** | ✅ Focus trap, restore, visible indicators built-in |
| **ARIA Attributes** | ✅ All WAI-ARIA 1.2 patterns implemented correctly |

---

## Consequences

### Positive

- ✅ **Best-in-class accessibility** - Minimizes accessibility tech debt
- ✅ **WCAG 2.2 AA compliant** - Meets ADA Title II requirements (April 2026 deadline)
- ✅ **Future-proof** - React Native support in development
- ✅ **Maximum flexibility** - Unstyled hooks work with any design system
- ✅ **iPad optimized** - Touch, keyboard, and screen reader support
- ✅ **Type-safe** - Excellent TypeScript definitions
- ✅ **Tree-shakeable** - Small bundle size (only ship what you use)

### Negative

- ⚠️ **Steeper learning curve** - Hooks-based API requires understanding composition
- ⚠️ **More verbose code** - Wire up hooks manually (vs pre-built components)
- ⚠️ **Slower initial development** - ~20-30% more time vs Chakra UI
- ⚠️ **Smaller community** - Less Stack Overflow content vs Radix UI or Chakra

### Neutral

- React Aria is unstyled - requires TailwindCSS for styling (already in stack)
- Need to build design system - but provides maximum control

### Mitigation Strategies

**Learning Curve:**
- Create reusable component library in `src/components/ui/`
- Document component patterns in codebase
- Reference Adobe Spectrum for example implementations

**Development Velocity:**
- Build components once, reuse everywhere
- Use Adobe React Spectrum (pre-built components on React Aria) as reference
- Leverage ChatGPT/Claude for React Aria pattern generation

---

## Implementation

### Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                    # Reusable React Aria + Tailwind components
│   │   │   ├── Button.tsx
│   │   │   ├── TextField.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Dialog.tsx
│   │   │   └── Tabs.tsx
│   │   └── weather/               # Domain-specific components
│   │       ├── TemperatureChart.tsx
│   │       └── WeatherCard.tsx
```

### Sample Component (Accessible Button)

```typescript
// src/components/ui/Button.tsx
import { useButton } from '@react-aria/button';
import { useRef } from 'react';
import { AriaButtonProps } from '@react-types/button';

interface ButtonProps extends AriaButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({ variant = 'primary', size = 'md', ...props }: ButtonProps) {
  let ref = useRef();
  let { buttonProps } = useButton(props, ref);

  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-md focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus-visible:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500',
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm min-h-[44px] min-w-[44px]', // WCAG 2.2 touch target
    md: 'px-4 py-2 text-base min-h-[44px] min-w-[44px]',
    lg: 'px-6 py-3 text-lg min-h-[44px] min-w-[44px]',
  };

  return (
    <button
      {...buttonProps}
      ref={ref}
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]}`}
    >
      {props.children}
    </button>
  );
}
```

### Dependencies

```json
{
  "dependencies": {
    "@react-aria/button": "^3.9.0",
    "@react-aria/dialog": "^3.5.0",
    "@react-aria/focus": "^3.17.0",
    "@react-aria/textfield": "^3.14.0",
    "@react-aria/select": "^3.14.0",
    "@react-aria/tabs": "^3.9.0",
    "@react-aria/utils": "^3.24.0",
    "@react-types/button": "^3.9.0",
    "@react-types/shared": "^3.23.0"
  }
}
```

---

## Alternatives Considered

### 1. Radix UI
- **Pros:** Excellent accessibility, TailwindCSS integration, component-based (easier API)
- **Cons:** Not as comprehensive as React Aria for WCAG 2.2, web-only (no native mobile)
- **Verdict:** Great choice, but React Aria has better accessibility guarantees

### 2. Chakra UI
- **Pros:** Fastest development, pre-styled, good accessibility baseline
- **Cons:** WCAG 2.0 only (not 2.2), large bundle size, CSS-in-JS conflicts with Tailwind, vendor lock-in
- **Verdict:** Too opinionated, limits future flexibility

### 3. Headless UI
- **Pros:** Simple API, Tailwind native, small bundle
- **Cons:** Limited component set, basic accessibility (not WCAG 2.2 certified)
- **Verdict:** Too limited for a full application

### 4. Build from scratch
- **Pros:** Complete control
- **Cons:** Accessibility is extremely complex, high risk of WCAG violations, months of work
- **Verdict:** Unacceptable accessibility risk

---

## Validation

### Success Criteria
- [ ] All UI components pass axe-core accessibility tests
- [ ] Keyboard navigation works for all interactive elements
- [ ] Screen reader announces all content correctly (NVDA, VoiceOver)
- [ ] Touch targets meet 44×44px minimum on iPad
- [ ] Focus indicators visible and clear (WCAG 2.2 requirement)
- [ ] Color contrast meets WCAG 2.2 Level AA (4.5:1 for text)

### Testing Strategy
```bash
# Automated accessibility testing
npm run test:a11y  # axe-core + jest-axe

# Lighthouse CI (must pass accessibility score ≥95)
npm run lighthouse

# Manual testing
# 1. Keyboard-only navigation
# 2. NVDA screen reader on Windows
# 3. VoiceOver on iPad
# 4. Color contrast validation (APCA)
```

---

## References

- [React Aria Documentation](https://react-spectrum.adobe.com/react-aria/)
- [Adobe Spectrum (example implementations)](https://react-spectrum.adobe.com/react-spectrum/)
- [WAI-ARIA 1.2 Design Patterns](https://www.w3.org/WAI/ARIA/apg/)
- [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/)
- [Inclusive Design Standards](../design/inclusive-design.md)

---

## Document Changelog

- **2026-01-03:** Decision made during Phase 3 planning (Web UI architecture)
- **2026-01-03:** Formalized as ADR-006
