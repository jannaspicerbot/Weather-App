# ADR-006: Accessible UI Component Strategy

**Status:** Superseded (Implementation Diverged)
**Date:** 2026-01-03
**Updated:** 2026-01-09
**Deciders:** Janna Spicer, Architecture Review

---

## Update Notice (2026-01-09)

**This ADR has been superseded by actual implementation choices.**

The original decision was to use React Aria for all UI components. During implementation, a more pragmatic approach was adopted:

| Component Type | Original Plan | Actual Implementation |
|----------------|---------------|----------------------|
| **Drag-and-Drop** | React Aria (unspecified) | **@dnd-kit** (better accessibility for D&D) |
| **Forms/Inputs** | React Aria hooks | **Semantic HTML + manual ARIA** |
| **Buttons** | React Aria useButton | **Native `<button>` elements** |
| **Dialogs/Modals** | React Aria useDialog | Not yet needed |

**Rationale for Divergence:**

1. **@dnd-kit provides superior accessibility for drag-and-drop:**
   - Built-in screen reader announcements with customizable messages
   - Keyboard navigation (Tab → Enter → Arrow keys → Enter/Escape)
   - Touch sensor support optimized for iPad
   - Well-documented accessibility patterns

2. **Semantic HTML is sufficient for most components:**
   - Native `<button>`, `<input>`, `<label>` elements are inherently accessible
   - Manual ARIA attributes (e.g., `aria-label`, `role`, `aria-live`) added where needed
   - Simpler codebase without hook composition overhead

3. **CSS Custom Properties replaced Tailwind:**
   - Original ADR referenced Tailwind integration
   - Actual implementation uses semantic CSS classes with design tokens
   - Better maintainability and dark mode support

**Current Accessibility Stack:**
- **@dnd-kit/core** + **@dnd-kit/sortable** - Drag-and-drop
- **Semantic HTML** - Buttons, forms, navigation
- **Manual ARIA** - Announcements, roles, labels
- **CSS Custom Properties** - Styling with design tokens
- **vitest-axe** - Automated accessibility testing

---

## Original Context (2026-01-03)

The Weather App needs a component library for building the Web UI (Phase 3). The UI must support:
- WCAG 2.2 Level AA compliance (mandatory for inclusive design)
- Desktop and iPad browser usage (not native mobile apps)
- Keyboard navigation, screen reader support, touch interaction
- TypeScript type safety (already in stack)
- Flexibility for future design evolution

### User Requirements

From user discussion (2026-01-03):
> "we're building an app for desktop or ipad use, both using a browser - not a native app store app. but, we really do want to provide for a great user experience for all users, with true inclusive design."

---

## Original Decision

We will use **React Aria** (Adobe) as the component library for the Web UI.

---

## Actual Implementation

### What Was Used

**@dnd-kit for Drag-and-Drop (Charts and Metrics Reordering)**

```typescript
// DashboardGrid.tsx
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy,
} from '@dnd-kit/sortable';

// Accessibility announcements for screen readers
accessibility={{
  announcements: {
    onDragStart({ active }) {
      return `Picked up ${chartName}. Use arrow keys to move.`;
    },
    onDragEnd({ active, over }) {
      return `${chartName} was dropped at position ${position}.`;
    }
  }
}}
```

**Semantic HTML with Manual ARIA**

```typescript
// MetricCard.tsx
<article
  className="metric-card"
  role="region"
  aria-label={`${label}: ${value}`}
>
  <div className="metric-card__icon" aria-hidden="true">
    {icon}
  </div>
  ...
</article>

// App.tsx - Skip link
<a href="#main-content" className="skip-link">
  Skip to main content
</a>
```

**CSS Custom Properties (Design Tokens)**

```css
/* index.css */
:root {
  --color-water: var(--palette-primary);
  --color-growth: var(--palette-secondary);
  --color-interactive: var(--palette-accent);
  --spacing-4: 1rem;
}

.dashboard__button--primary {
  background-color: var(--color-interactive);
  color: var(--color-text-on-primary);
}
```

### Dependencies

```json
{
  "dependencies": {
    "@dnd-kit/core": "^6.3.1",
    "@dnd-kit/sortable": "^10.0.0",
    "@dnd-kit/utilities": "^3.2.2",
    "victory": "^37.3.6"
  },
  "devDependencies": {
    "vitest-axe": "^0.1.0"
  }
}
```

---

## Consequences of Actual Approach

### Positive

- ✅ **Excellent drag-and-drop accessibility** - @dnd-kit is purpose-built for this
- ✅ **Simpler codebase** - No hook composition, direct HTML elements
- ✅ **Smaller bundle size** - @dnd-kit is lighter than full React Aria
- ✅ **WCAG 2.2 AA compliance achieved** - vitest-axe tests pass
- ✅ **Touch/iPad optimized** - @dnd-kit sensors handle touch input well

### Neutral

- React Aria remains a valid choice for future complex components
- If dialogs, comboboxes, or complex widgets are needed, React Aria could be added

### Lessons Learned

- **Match the tool to the problem** - @dnd-kit is better for D&D than React Aria
- **Semantic HTML first** - Only add libraries when native elements are insufficient
- **Start simple** - Manual ARIA is often clearer than hook abstractions

---

## Validation

### Success Criteria (All Met)

- [x] All UI components pass axe-core accessibility tests
- [x] Keyboard navigation works for all interactive elements
- [x] Screen reader announces all content correctly
- [x] Touch targets meet 44×44px minimum on iPad
- [x] Focus indicators visible and clear
- [x] Color contrast meets WCAG 2.2 Level AA

### Testing Strategy

```bash
# Automated accessibility testing
npm run test          # Includes vitest-axe tests

# Manual testing completed
# 1. Keyboard-only navigation ✓
# 2. VoiceOver on macOS ✓
# 3. 200% zoom test ✓
# 4. Touch target verification ✓
```

---

## References

- [@dnd-kit Documentation](https://docs.dndkit.com/)
- [@dnd-kit Accessibility Guide](https://docs.dndkit.com/guides/accessibility)
- [React Aria Documentation](https://react-spectrum.adobe.com/react-aria/) (for future reference)
- [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/)
- [Accessibility Standards](../../standards/ACCESSIBILITY.md)

---

## Document Changelog

- **2026-01-09:** ADR superseded - documented actual implementation (@dnd-kit + semantic HTML)
- **2026-01-03:** Original decision (React Aria)
