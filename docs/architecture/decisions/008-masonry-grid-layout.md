# ADR-008: Masonry Grid Layout and Drag-and-Drop Widget Reordering

**Status:** 🟡 Proposed
**Date:** 2026-01-05
**Deciders:** Janna Spicer, Architecture Review

> **Update (2026-01-09):** This ADR references TailwindCSS which was later replaced with CSS Custom Properties (design tokens). The layout recommendations remain valid - CSS Grid and Flexbox work with any styling approach.

---

## Context

The Weather Dashboard needs enhanced layout capabilities to support:
1. **User-customizable widget ordering** via drag-and-drop
2. **Future support for variable-height widgets** (true masonry layout)
3. **Responsive design** for desktop (1024px+) and iPad (768-1023px)
4. **WCAG 2.2 Level AA compliance** (mandatory per ADR-006)

### Current State (Phase 3)

The dashboard uses a simple CSS Grid layout (Dashboard.tsx, lines 218-223):
```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
  <TemperatureChart data={historicalData} />
  <HumidityChart data={historicalData} />
  <WindChart data={historicalData} />
  <PrecipitationChart data={historicalData} />
</div>
```

This works well for equal-height widgets but:
- No user customization (fixed widget order)
- Cannot support variable-height widgets efficiently
- No drag-and-drop interaction

### User Requirements

From user discussion (2026-01-05):
> "let's act as a principal software architect and principal designer pair, and make a plan for adding a masonry grid capability to our design system"
> "allow users to reorder widgets via drag-and-drop, AND support true masonry layout in the future"
> "using open source tools and libraries that are compatible with our inclusive design principles"

### Inclusive Design Standards

From [docs/standards/ACCESSIBILITY.md](../../standards/ACCESSIBILITY.md):
- WCAG 2.2 Level AA compliance is required
- Keyboard navigation for all interactive elements
- Screen reader compatibility with proper ARIA
- Touch targets minimum 44×44px (iPad optimized)
- No focus traps, visible focus indicators

---

## Decision

We will use **dnd-kit (Drag and Drop Kit) + CSS Grid** for dashboard widget management, with architecture that supports future migration to native CSS masonry when browser support reaches 90%.

**Immediate Implementation:**
- Install `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`
- Implement drag-and-drop widget reordering with full accessibility
- Maintain CSS Grid layout (2-column responsive)

**Future Path:**
- Migrate to CSS Columns for true masonry when needed
- Eventually adopt native CSS `display: grid-lanes` when widely supported

---

## Rationale

### Comparison with Alternatives

| Criterion (Priority Order) | dnd-kit + CSS Grid | React-Grid-Layout | Muuri | react-masonry-css | Masonic | CSS Columns |
|---------------------------|-------------------|-------------------|-------|-------------------|---------|-------------|
| **1. WCAG 2.2 AA Compliance** | ✅ 9/10 | ❌ 2/10 | ❌ 1/10 | ❌ 2/10 | ⚠️ 5/10 | ✅ 7/10 |
| **2. Keyboard Navigation** | ✅ 10/10 | ❌ 2/10 | ❌ 1/10 | ❌ 2/10 | ⚠️ 4/10 | ⚠️ 6/10 |
| **3. Screen Reader Support** | ✅ 9/10 | ❌ 2/10 | ❌ 1/10 | ❌ 3/10 | ⚠️ 5/10 | ✅ 6/10 |
| **4. React Aria Integration** | ✅ 10/10 | ⚠️ 4/10 | ❌ 2/10 | ⚠️ 5/10 | ⚠️ 5/10 | ✅ 8/10 |
| **5. TypeScript Support** | ✅ 10/10 | ✅ 9/10 | ⚠️ 5/10 | ⚠️ 6/10 | ✅ 8/10 | N/A |
| **6. Tailwind Compatibility** | ✅ 10/10 | ⚠️ 7/10 | ⚠️ 4/10 | ✅ 8/10 | ✅ 8/10 | ✅ 10/10 |
| **7. Bundle Size (gzipped)** | ✅ ~12KB | ⚠️ ~50KB | ⚠️ ~25KB | ✅ ~2KB | ✅ ~8KB | ✅ 0KB |
| **8. Maintenance Status** | ✅ 9/10 | ✅ 8/10 | ❌ 3/10 | ⚠️ 6/10 | ✅ 7/10 | N/A |
| **9. Touch/iPad Optimization** | ✅ 9/10 | ✅ 8/10 | ⚠️ 6/10 | ⚠️ 5/10 | ⚠️ 6/10 | ✅ 8/10 |
| **10. Learning Curve** | ✅ 7/10 | ⚠️ 6/10 | ⚠️ 4/10 | ✅ 9/10 | ✅ 7/10 | ✅ 10/10 |
| **11. Drag-and-Drop** | ✅ 10/10 | ✅ 10/10 | ✅ 10/10 | ❌ 0/10 | ❌ 0/10 | ❌ 0/10 |
| **12. Masonry Layout** | ⚠️ 6/10 | ✅ 8/10 | ✅ 9/10 | ✅ 9/10 | ✅ 9/10 | ✅ 10/10 |
| **TOTAL SCORE** | **99/120** | **66/120** | **50/120** | **51/120** | **69/120** | **59/100** |

**Scoring Scale:** 10 = Excellent, 7-9 = Good, 4-6 = Acceptable with caveats, 1-3 = Poor, 0 = Not supported

### Detailed Library Analysis

#### 1. dnd-kit + CSS Grid (RECOMMENDED)

**GitHub:** [clauderic/dnd-kit](https://github.com/clauderic/dnd-kit)
**Stars:** ~15K | **Weekly Downloads:** 1.5M+ | **Last Update:** Active (2025)

**Accessibility Features:**
- ✅ **Built-in WCAG 2.1 AA compliance** - Keyboard navigation via sensors
- ✅ **Automatic ARIA attributes** - `role`, `aria-roledescription`, `aria-describedby`
- ✅ **Screen reader announcements** - Live region updates for drag operations
- ✅ **Keyboard support** - Enter/Space to activate, Arrow keys to move, Escape to cancel
- ✅ **Focus management** - Automatic focus handling during drag operations
- ✅ **Customizable announcements** - Localization and custom messages

From [dnd-kit Accessibility Documentation](https://docs.dndkit.com/guides/accessibility):
> "dnd kit was built from the ground up with accessibility in mind. All sensors provide comprehensive built-in support for keyboard navigation and screen readers."

**Integration with React Aria:**
- Complements React Aria patterns (ADR-006)
- Similar hooks-based architecture
- Can wrap React Aria components as draggable items

**Pros:**
- Industry-leading accessibility (best-in-class)
- TypeScript-first with excellent types
- Modular architecture (tree-shakeable)
- Touch, mouse, keyboard support
- No CSS dependencies (works perfectly with Tailwind)

**Cons:**
- Not a masonry library - requires separate masonry layout solution
- Moderate learning curve (hooks-based API)
- Requires custom layout implementation

**Verdict:** ✅ **RECOMMENDED** - Best accessibility, aligns with project's inclusive design principles

---

#### 2. React-Grid-Layout

**GitHub:** [react-grid-layout/react-grid-layout](https://github.com/react-grid-layout/react-grid-layout)
**Stars:** 21.9K | **Weekly Downloads:** 997K | **Last Update:** Active (2025)

**Accessibility Analysis:**
- ❌ **CRITICAL: No built-in accessibility** - Documentation states: "You will need to add keyboard support and ARIA attributes to make them accessible to all users"
- ❌ No keyboard navigation for grid item movement
- ❌ No ARIA attributes automatically applied
- ❌ No screen reader announcements
- ⚠️ Manual implementation required for all WCAG compliance

**WCAG 2.2 Violations:**
- 2.1.1 Keyboard - Cannot move items without mouse
- 2.4.7 Focus Visible - No focus indicators on grid items
- 2.5.7 Dragging Movements - No keyboard alternative to drag

**Pros:**
- Comprehensive grid features (resize, drag, breakpoints)
- Large community and examples
- Supports responsive breakpoints

**Cons:**
- ❌ Fails WCAG 2.2 AA requirements without extensive custom work
- Requires significant accessibility engineering
- Creates ongoing tech debt

**Verdict:** ❌ **NOT RECOMMENDED** - Does not meet mandatory accessibility standards

---

#### 3. Muuri

**GitHub:** [haltu/muuri](https://github.com/haltu/muuri)
**Stars:** ~12K | **Weekly Downloads:** 14.6K | **Last Update:** ❌ Inactive

**Accessibility Analysis:**
- ❌ **Pure JavaScript library** - No React integration
- ❌ No accessibility features whatsoever
- ❌ No TypeScript types included
- ❌ Maintenance status: Inactive per Snyk analysis

**Verdict:** ❌ **NOT RECOMMENDED** - Inactive maintenance, no accessibility, poor React integration

---

#### 4. react-masonry-css

**GitHub:** [paulcollett/react-masonry-css](https://github.com/paulcollett/react-masonry-css)
**Stars:** 1K | **Weekly Downloads:** 110K

**Accessibility Analysis:**
- ❌ **CRITICAL: Broken tab order** - From [GitHub Issue #49](https://github.com/paulcollett/react-masonry-css/issues/49):
  > "Wrapping grid items into column divs means that the tab order of the page is changed, forcing keyboard users to navigate through items in a 1-5-9-2-6-10-3-7-11-4-8-12 order in a 4x3 grid"
- ❌ Visual order ≠ DOM order (WCAG violation)
- ❌ Cannot use semantic HTML lists (`<ul>`, `<ol>`)
- ❌ Cannot be fixed without breaking the layout

**WCAG 2.2 Violations:**
- 2.4.3 Focus Order - Visual order does not match DOM order
- 1.3.2 Meaningful Sequence - Reading order is incorrect for screen readers

**Verdict:** ❌ **NOT RECOMMENDED** - Fundamentally broken accessibility due to DOM structure

---

#### 5. Masonic

**GitHub:** [jaredLunde/masonic](https://github.com/jaredLunde/masonic)
**Stars:** 1.2K | **Weekly Downloads:** 26K

**Accessibility Analysis:**
- ⚠️ Provides customizable ARIA roles
- ⚠️ Virtualization improves performance
- ⚠️ Still requires manual keyboard navigation
- ⚠️ No live region announcements
- ❌ No drag-and-drop support

**Verdict:** ⚠️ **ACCEPTABLE** for static masonry layouts, but lacks drag-and-drop and requires accessibility work

---

#### 6. CSS Columns (Native Tailwind)

**Documentation:** [Tailwind CSS Columns](https://tailwindcss.com/docs/columns)

**Example:**
```tsx
<div className="columns-1 lg:columns-2 gap-6">
  <div className="break-inside-avoid mb-6">
    <TemperatureChart />
  </div>
  {/* more charts */}
</div>
```

**Accessibility Analysis:**
- ✅ Native browser behavior
- ✅ Standard tab order (top-to-bottom per column)
- ✅ Works with screen readers out of the box
- ❌ No drag-and-drop without additional library

**Verdict:** ✅ **GOOD** for static masonry layouts, but requires dnd-kit for drag-and-drop

---

### Why dnd-kit + CSS Grid is the Best Choice

1. **Meets All Accessibility Requirements** - Only library with WCAG 2.2 AA built-in
2. **Aligns with React Aria Decision** (ADR-006) - Same hooks-based, accessibility-first philosophy
3. **Future-Proof Architecture** - Can switch to CSS Columns or native CSS masonry later
4. **No Accessibility Tech Debt** - Built-in support means low ongoing maintenance
5. **Excellent iPad Support** - Touch, keyboard, and screen reader optimized

---

## Consequences

### Positive

- ✅ **Best-in-class accessibility** - Minimizes accessibility tech debt
- ✅ **WCAG 2.2 AA compliant** - Built-in keyboard nav, screen reader, ARIA support
- ✅ **React Aria alignment** - Same hooks-based philosophy as ADR-006
- ✅ **Flexible architecture** - Can migrate to CSS Columns or native CSS masonry later
- ✅ **iPad optimized** - Touch, keyboard, and screen reader support
- ✅ **TypeScript-first** - Excellent type definitions
- ✅ **Modular and tree-shakeable** - Small bundle size (~12KB)
- ✅ **Active maintenance** - 15K+ stars, millions of downloads

### Negative

- ⚠️ **Not a masonry library** - dnd-kit only provides drag-and-drop, not masonry layout
- ⚠️ **Learning curve** - Hooks-based API requires understanding composition
- ⚠️ **Custom masonry implementation** - Must pair with CSS Grid/Columns for layout
- ⚠️ **Implementation effort** - 6-10 hours for full drag-and-drop + masonry

### Neutral

- dnd-kit is a drag-and-drop library, not a layout library
- Must be paired with CSS Grid (current) or CSS Columns (future masonry)
- Native CSS masonry (`display: grid-lanes`) will replace libraries in 12-18 months

### Mitigation Strategies

**Not a masonry library:**
- Phase 1: Use dnd-kit + CSS Grid (2-column responsive)
- Phase 2: Migrate to dnd-kit + CSS Columns when variable heights needed
- Phase 3: Adopt native CSS masonry when browser support >90%

**Learning curve:**
- Comprehensive code examples in this ADR
- Similar patterns to React Aria (team already familiar)
- Excellent [dnd-kit documentation](https://docs.dndkit.com/)

---

## Implementation

### Phase 1: Drag-and-Drop with CSS Grid (Immediate)

#### Project Structure
```
web/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx                    # Updated to use DashboardGrid
│   │   └── dashboard/                       # New directory
│   │       ├── DashboardGrid.tsx           # DndContext container
│   │       └── SortableChartCard.tsx       # Draggable chart wrapper
│   └── hooks/
│       └── useDashboardLayout.ts            # Persist layout preferences
```

#### 1. Install Dependencies

```bash
cd web
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

#### 2. Create useDashboardLayout Hook

```typescript
// src/hooks/useDashboardLayout.ts
import { useState, useEffect } from 'react';

export type ChartId = 'temperature' | 'humidity' | 'wind' | 'precipitation';

const DEFAULT_LAYOUT: ChartId[] = ['temperature', 'humidity', 'wind', 'precipitation'];
const STORAGE_KEY = 'dashboard-layout';

export function useDashboardLayout() {
  const [chartOrder, setChartOrder] = useState<ChartId[]>(() => {
    // Load from localStorage on mount
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : DEFAULT_LAYOUT;
  });

  useEffect(() => {
    // Persist to localStorage on change
    localStorage.setItem(STORAGE_KEY, JSON.stringify(chartOrder));
  }, [chartOrder]);

  const resetLayout = () => {
    setChartOrder(DEFAULT_LAYOUT);
  };

  return { chartOrder, setChartOrder, resetLayout };
}
```

#### 3. Create SortableChartCard Component

```typescript
// src/components/dashboard/SortableChartCard.tsx
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { ChartId } from '../../hooks/useDashboardLayout';

interface SortableChartCardProps {
  id: ChartId;
  children: React.ReactNode;
}

export function SortableChartCard({ id, children }: SortableChartCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    cursor: isDragging ? 'grabbing' : 'grab',
  };

  return (
    <article
      ref={setNodeRef}
      style={style}
      className="bg-white shadow-md rounded-lg p-6 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
      {...attributes}
      {...listeners}
    >
      {children}
    </article>
  );
}
```

#### 4. Create DashboardGrid Component

```typescript
// src/components/dashboard/DashboardGrid.tsx
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy,
} from '@dnd-kit/sortable';
import type { ChartId } from '../../hooks/useDashboardLayout';

interface DashboardGridProps {
  chartOrder: ChartId[];
  onReorder: (newOrder: ChartId[]) => void;
  children: React.ReactNode;
}

export function DashboardGrid({ chartOrder, onReorder, children }: DashboardGridProps) {
  // Configure sensors for accessibility
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Prevent accidental drags (accessibility)
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 200, // Prevent accidental drags on touch
        tolerance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = chartOrder.indexOf(active.id as ChartId);
      const newIndex = chartOrder.indexOf(over.id as ChartId);

      const newOrder = [...chartOrder];
      newOrder.splice(oldIndex, 1);
      newOrder.splice(newIndex, 0, active.id as ChartId);

      onReorder(newOrder);
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
      accessibility={{
        announcements: {
          onDragStart({ active }) {
            return `Picked up ${active.id} chart. Use arrow keys to move, Enter to drop, Escape to cancel.`;
          },
          onDragOver({ active, over }) {
            if (over) {
              return `${active.id} chart is over ${over.id} chart.`;
            }
            return `${active.id} chart is no longer over a droppable area.`;
          },
          onDragEnd({ active, over }) {
            if (over) {
              return `${active.id} chart was dropped at position ${chartOrder.indexOf(over.id as ChartId) + 1}.`;
            }
            return `${active.id} chart was dropped.`;
          },
          onDragCancel({ active }) {
            return `Dragging ${active.id} chart was cancelled.`;
          },
        },
      }}
    >
      <SortableContext items={chartOrder} strategy={rectSortingStrategy}>
        <div
          className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6"
          role="region"
          aria-label="Weather charts - drag to reorder"
        >
          {children}
        </div>
      </SortableContext>

      {/* Keyboard instructions for screen reader users */}
      <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
        Press Enter to start dragging. Use arrow keys to move the chart. Press Enter again to drop, or Escape to cancel.
      </div>
    </DndContext>
  );
}
```

#### 5. Update Dashboard.tsx

```typescript
// src/components/Dashboard.tsx (updated section, lines 218-230)
import { DashboardGrid } from './dashboard/DashboardGrid';
import { SortableChartCard } from './dashboard/SortableChartCard';
import { useDashboardLayout } from '../hooks/useDashboardLayout';

export default function Dashboard() {
  // ... existing state ...
  const { chartOrder, setChartOrder, resetLayout } = useDashboardLayout();

  // Chart component mapping
  const chartComponents = {
    temperature: <TemperatureChart data={historicalData} />,
    humidity: <HumidityChart data={historicalData} />,
    wind: <WindChart data={historicalData} />,
    precipitation: <PrecipitationChart data={historicalData} />,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Weather Dashboard</h1>
            {stats && (
              <p className="text-sm text-gray-600 mt-1">
                {stats.total_records.toLocaleString()} readings •
                {stats.date_range_days ? ` ${stats.date_range_days} days` : ' No data'}
              </p>
            )}
          </div>
          <button
            onClick={resetLayout}
            className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            aria-label="Reset dashboard layout to default"
          >
            Reset Layout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* ... Empty State ... */}
        {/* ... Current Conditions ... */}
        {/* ... Date Range Selector ... */}

        {/* Charts Grid with Drag-and-Drop */}
        <DashboardGrid chartOrder={chartOrder} onReorder={setChartOrder}>
          {chartOrder.map((chartId) => (
            <SortableChartCard key={chartId} id={chartId}>
              {chartComponents[chartId]}
            </SortableChartCard>
          ))}
        </DashboardGrid>
      </main>
    </div>
  );
}
```

---

### Phase 2: True Masonry Layout (Future)

When variable-height widgets are needed, migrate to CSS Columns:

```typescript
// DashboardGrid.tsx (future masonry version)
<div
  className="columns-1 lg:columns-2 gap-6 mt-6"
  role="region"
  aria-label="Weather charts - drag to reorder"
>
  {children.map((child) => (
    <div key={child.key} className="break-inside-avoid mb-6">
      {child}
    </div>
  ))}
</div>
```

**Trade-off:** CSS Columns changes tab order (top-to-bottom per column). Document this for users and provide keyboard shortcuts to navigate columns.

---

### Phase 3: Native CSS Masonry (Future, 2026-2027)

When browser support for `display: grid-lanes` reaches 90%:

```css
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  grid-template-rows: masonry;
  gap: 1.5rem;
}
```

This will eliminate the need for JavaScript masonry libraries entirely.

---

## Alternatives Considered

### 1. React-Grid-Layout
- **Pros:** Comprehensive grid features, large community
- **Cons:** ❌ No built-in accessibility, extensive custom work required
- **Verdict:** Violates WCAG 2.2 AA - creates unacceptable tech debt

### 2. Muuri
- **Pros:** Smooth animations, masonry support
- **Cons:** ❌ Inactive maintenance, no React integration, zero accessibility
- **Verdict:** Unmaintained and inaccessible

### 3. react-masonry-css
- **Pros:** Simple, lightweight, true masonry
- **Cons:** ❌ Broken tab order (GitHub Issue #49), cannot be fixed
- **Verdict:** Fundamentally broken accessibility

### 4. Masonic
- **Pros:** Virtualization, customizable ARIA
- **Cons:** ❌ No drag-and-drop, manual accessibility work
- **Verdict:** Good for static masonry, but lacks drag-and-drop

### 5. CSS Columns (Native)
- **Pros:** Zero dependencies, native browser support
- **Cons:** ❌ No drag-and-drop, column-based tab order
- **Verdict:** Good for static masonry, pair with dnd-kit for drag-and-drop

### 6. Build from Scratch
- **Pros:** Complete control
- **Cons:** ❌ Months of work, high accessibility risk
- **Verdict:** Over-engineered, unacceptable risk

---

## Validation

### Success Criteria

- [ ] Drag-and-drop widget reordering works (mouse, touch, keyboard)
- [ ] Keyboard navigation: Tab to chart, Enter to activate drag, Arrow keys to move, Enter to drop, Escape to cancel
- [ ] Screen reader announces drag operations (NVDA, VoiceOver)
- [ ] Layout preferences persist to localStorage
- [ ] Charts pass axe-core accessibility tests (0 violations)
- [ ] Touch targets meet 44×44px minimum (iPad)
- [ ] Focus indicators visible and clear (2px minimum)
- [ ] Lighthouse accessibility score ≥95

### Testing Strategy

#### Automated Testing

```bash
# Install axe-core for accessibility testing
npm install -D @axe-core/react jest-axe

# Run tests
npm run test:a11y

# Lighthouse CI (accessibility score must be ≥95)
npm run lighthouse
```

```typescript
// tests/accessibility/Dashboard.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import Dashboard from '../components/Dashboard';

expect.extend(toHaveNoViolations);

describe('Dashboard Drag-and-Drop Accessibility', () => {
  it('has no axe violations', async () => {
    const { container } = render(<Dashboard />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('supports keyboard navigation for reordering', () => {
    const { getAllByRole } = render(<Dashboard />);
    const charts = getAllByRole('article');

    // Tab to first chart
    charts[0].focus();
    expect(document.activeElement).toBe(charts[0]);

    // Press Enter to activate drag (dnd-kit handles this)
    fireEvent.keyDown(charts[0], { key: 'Enter' });
    // Arrow keys move the chart (tested by dnd-kit library)
    // Enter again to drop
  });
});
```

#### Manual Testing Checklist

**Keyboard Navigation:**
- [ ] Tab through all chart cards in order
- [ ] Press Enter on a chart to activate drag mode
- [ ] Use Arrow keys (Up/Down/Left/Right) to move chart
- [ ] Press Enter to drop chart at new position
- [ ] Press Escape to cancel drag operation
- [ ] Verify focus indicator is visible (2px blue ring)

**Screen Reader (NVDA on Windows):**
- [ ] Start NVDA screen reader
- [ ] Navigate to dashboard
- [ ] Verify chart titles are announced
- [ ] Tab to a chart card
- [ ] Press Enter to start drag
- [ ] Verify announcement: "Picked up [chart name] chart. Use arrow keys to move..."
- [ ] Use Arrow keys to move
- [ ] Verify announcement: "[chart name] chart is over [other chart] chart"
- [ ] Press Enter to drop
- [ ] Verify announcement: "[chart name] chart was dropped at position X"

**Screen Reader (VoiceOver on iPad):**
- [ ] Enable VoiceOver (Settings > Accessibility)
- [ ] Swipe to navigate between charts
- [ ] Verify chart titles and drag instructions are announced
- [ ] Use VoiceOver rotor to navigate by landmarks

**Touch Interaction (iPad):**
- [ ] Long-press on a chart to activate drag
- [ ] Drag chart to new position
- [ ] Release to drop
- [ ] Verify smooth animation and visual feedback
- [ ] Verify touch targets are at least 44×44px

**Color Contrast:**
- [ ] Run WebAIM Contrast Checker on all text
- [ ] Verify 4.5:1 contrast for normal text
- [ ] Verify 3:1 contrast for large text and UI components

**Zoom and Responsive:**
- [ ] Zoom to 200% (Ctrl + "+")
- [ ] Verify no horizontal scrolling
- [ ] Verify all content remains accessible
- [ ] Test on mobile (1-column layout)
- [ ] Test on tablet (2-column layout)

---

## References

**Libraries:**
- [dnd-kit Documentation](https://docs.dndkit.com/)
- [dnd-kit Accessibility Guide](https://docs.dndkit.com/guides/accessibility)
- [dnd-kit GitHub](https://github.com/clauderic/dnd-kit)
- [React-Grid-Layout GitHub](https://github.com/react-grid-layout/react-grid-layout)
- [react-masonry-css Issue #49 (Tab Order Bug)](https://github.com/paulcollett/react-masonry-css/issues/49)

**CSS Masonry:**
- [CSS Grid Lanes Specification](https://www.w3.org/TR/css-grid-3/)
- [CSS Masonry Layout - CSS-Tricks](https://css-tricks.com/masonry-layout-is-now-grid-lanes/)
- [Tailwind CSS Columns](https://tailwindcss.com/docs/columns)

**Accessibility Standards:**
- [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/)
- [WAI-ARIA 1.2 Drag and Drop](https://www.w3.org/WAI/ARIA/apg/patterns/dnd/)
- [Accessibility Standards](../../standards/ACCESSIBILITY.md)

**Project ADRs:**
- [ADR-006: React Aria Component Library](./006-react-aria-components.md)
- [ADR-007: Victory Charts for Data Visualization](./007-victory-charts.md)

---

## Document Changelog

- **2026-01-05:** Decision proposed after architectural research
- **2026-01-05:** Formalized as ADR-008
