# Dashboard Layout Architecture

**Version:** 1.0
**Date:** 2026-01-07
**Status:** Active

---

## Overview

The Weather Dashboard follows a responsive grid layout optimized for desktop and tablet viewports. This document defines the visual architecture, component structure, and responsive behavior.

---

## Grid System

### Responsive Breakpoints

| Viewport | Width | Columns | Behavior |
|----------|-------|---------|----------|
| **Desktop** | ≥1024px | 2 columns | Side-by-side charts |
| **Tablet** | 768px - 1023px | 2 columns | Compressed spacing |
| **Mobile** | <768px | 1 column | Stacked charts |

### Layout Implementation

```css
/* Dashboard grid layout */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-6, 1.5rem);
  padding: var(--spacing-4, 1rem);
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-8, 2rem);
    padding: var(--spacing-6, 1.5rem);
  }
}
```

### Semantic CSS Implementation

```tsx
<div className="dashboard-grid">
  {/* Chart cards */}
</div>
```

```css
/* In index.css */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-6);
  padding: var(--spacing-4);
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-8);
    padding: var(--spacing-6);
  }
}
```

---

## Chart Containers (Cards)

Each chart is housed in a Card component with clear visual boundaries. The design achieves "subconscious differentiation" through semantic tokens for borders and elevation.

### Card Specifications

| Property | Token | Value | Purpose |
|----------|-------|-------|---------|
| **Background** | `var(--color-bg-secondary)` | Palette surface | Distinct layer from dashboard |
| **Border** | `var(--color-border)` | 1px solid | Clear boundary |
| **Border Radius** | - | 12px | Subtle rounded corners |
| **Shadow** | - | `0 1px 3px rgba(0,0,0,0.1)` | Subtle elevation (light mode) |
| **Padding** | - | 1.5rem (24px) | Internal breathing room |

### Card Component Structure

```tsx
// ChartCard.tsx
interface ChartCardProps {
  title: string;
  children: React.ReactNode;
  description?: string;
}

function ChartCard({ title, children, description }: ChartCardProps) {
  return (
    <article
      className="chart-card"
      role="region"
      aria-labelledby={`${title}-heading`}
    >
      <header className="chart-card-header">
        <h2 id={`${title}-heading`}>{title}</h2>
        {description && (
          <p className="chart-card-description">{description}</p>
        )}
      </header>
      <div className="chart-card-content">
        {children}
      </div>
    </article>
  );
}
```

### Card CSS Implementation

```css
.chart-card {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Dark mode shadow adjustment */
@media (prefers-color-scheme: dark) {
  .chart-card {
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  }
}

.chart-card-header {
  margin-bottom: 1rem;
}

.chart-card-header h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.chart-card-description {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
}

.chart-card-content {
  min-height: 300px;
}
```

### JSX + Semantic CSS Implementation

```tsx
<article
  className="chart-card"
  role="region"
  aria-labelledby="chart-heading"
>
  <header className="chart-card-header">
    <h2 id="chart-heading" className="chart-card-title">
      Temperature
    </h2>
  </header>
  <div className="chart-card-content">
    {/* Victory Chart */}
  </div>
</article>
```

The `.chart-card` styles are defined in the CSS section above, using design tokens for consistent theming.

---

## Surface Elevation System

The dashboard uses a layered surface system to create visual hierarchy:

```
┌─────────────────────────────────────────────────────┐
│  Dashboard Background: var(--color-bg-primary)      │
│  ┌─────────────────────────────────────────────┐   │
│  │  Card Surface: var(--color-bg-secondary)    │   │
│  │  ┌───────────────────────────────────────┐  │   │
│  │  │  Chart Area: transparent              │  │   │
│  │  │  Grid: var(--chart-grid)              │  │   │
│  │  └───────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Elevation Tokens

| Layer | Token | Light Mode | Dark Mode |
|-------|-------|------------|-----------|
| **Background** | `--color-bg-primary` | `#FAFBFC` | `#0F1419` |
| **Surface** | `--color-bg-secondary` | `#FFFFFF` | `#1C2128` |
| **Elevated** | `--color-bg-elevated` | `#FFFFFF` | `#242B3D` |

---

## Dashboard Sections

### Header Section

```tsx
<header className="dashboard-header">
  <h1>Weather Dashboard</h1>
  <div className="header-actions">
    <DateRangeSelector />
    <ExportButton />
  </div>
</header>
```

### Current Conditions Section

Displays real-time weather metrics in a compact grid:

```
┌─────────────────────────────────────────────────────┐
│  Current Conditions                                  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐     │
│  │ Temp │ │Humid │ │ Wind │ │ Rain │ │Barom │     │
│  │ 72°F │ │ 45%  │ │5 mph │ │0.0 in│ │30.12 │     │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘     │
└─────────────────────────────────────────────────────┘
```

### Charts Section

Four primary chart cards in a 2x2 grid (desktop):

```
┌─────────────────────┐ ┌─────────────────────┐
│   Temperature       │ │   Humidity          │
│   ┌─────────────┐  │ │   ┌─────────────┐  │
│   │ [Line Chart]│  │ │   │ [Line Chart]│  │
│   └─────────────┘  │ │   └─────────────┘  │
└─────────────────────┘ └─────────────────────┘
┌─────────────────────┐ ┌─────────────────────┐
│   Wind              │ │   Precipitation     │
│   ┌─────────────┐  │ │   ┌─────────────┐  │
│   │ [Line Chart]│  │ │   │ [Line Chart]│  │
│   └─────────────┘  │ │   └─────────────┘  │
└─────────────────────┘ └─────────────────────┘
```

---

## Spacing System

Consistent spacing using a base-4 scale:

| Token | Value | Usage |
|-------|-------|-------|
| `--spacing-1` | 0.25rem (4px) | Tight spacing |
| `--spacing-2` | 0.5rem (8px) | Element gaps |
| `--spacing-3` | 0.75rem (12px) | Small padding |
| `--spacing-4` | 1rem (16px) | Standard padding |
| `--spacing-6` | 1.5rem (24px) | Card padding |
| `--spacing-8` | 2rem (32px) | Section gaps |
| `--spacing-12` | 3rem (48px) | Large sections |

---

## Drag-and-Drop Reordering

The dashboard supports user-configurable chart order via drag-and-drop:

### Visual Feedback States

| State | Visual Treatment |
|-------|------------------|
| **Default** | Normal card appearance |
| **Hover** | Subtle cursor change (`cursor: grab`) |
| **Dragging** | `opacity: 0.5`, `cursor: grabbing` |
| **Drop Target** | `outline: 2px dashed var(--color-interactive)` |
| **Dropped** | Brief highlight animation |

### Accessibility Requirements

- Keyboard support: `Enter`/`Space` to pick up, Arrow keys to move, `Enter` to drop
- Screen reader announcements for all drag operations
- Focus indicators visible during keyboard interaction

---

## Responsive Behavior

### Desktop (≥1024px)

- 2-column grid
- Full chart legends visible
- Date range selector inline
- Export button visible

### Tablet (768px - 1023px)

- 2-column grid with reduced spacing
- Condensed legends
- Date range selector may wrap

### Mobile (<768px)

- Single column, stacked cards
- Legends below charts
- Date range presets prioritized over custom dates
- Touch-optimized controls (44px minimum targets)

---

## Performance Considerations

### Chart Rendering

- Lazy load charts below the fold
- Use `React.memo()` for chart components
- Limit data points to ~1000 for smooth rendering
- Use strategic sampling for large date ranges

### Layout Stability

- Reserve space for charts to prevent layout shift
- Use `min-height: 300px` on chart containers
- Skeleton loaders during data fetch

---

## Related Documents

- [Design Tokens](./design-tokens.md) - Color and styling tokens
- [Accessibility Standards](../standards/ACCESSIBILITY.md) - Accessibility standards
- [Architecture Overview](../architecture/overview.md) - System architecture

---

## Document Changelog

- **2026-01-07:** Initial dashboard layout architecture document created
