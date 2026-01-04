# Frontend Development Guidelines

**Purpose:** Standards and best practices for building the Weather Dashboard frontend

**Last Updated:** 2026-01-04
**Status:** Active

---

## Core Principles

### 1. Semantic Design Tokens (No Hard-Coded Colors)

**CRITICAL RULE:** Never use hex codes or RGB values directly in component code.

```tsx
// ❌ WRONG - Hard-coded color (breaks when palette changes)
<div style={{ backgroundColor: '#3B6B8F' }}>
  <VictoryLine style={{ data: { stroke: '#3B6B8F' } }} />
</div>

// ✅ CORRECT - Semantic token (automatically updates with palette)
<div style={{ backgroundColor: 'var(--color-water)' }}>
  <VictoryLine style={{ data: { stroke: 'var(--chart-line-water)' } }} />
</div>

// ✅ BETTER - CSS class
<div className="chart-container">
  <VictoryLine style={{ data: { stroke: 'var(--chart-line-water)' } }} />
</div>
```

**Why this matters:**
- Changing color palette = edit 1 CSS file, entire app updates
- User-selectable palettes work automatically
- Maintains consistency across all components
- Future-proof for theming features

**See:** [Design Token System](design-tokens.md) for full implementation details

---

### 2. TypeScript Type Safety

**CRITICAL RULE:** All components and functions must have proper TypeScript types.

```tsx
// ❌ WRONG - No type safety
function TemperatureChart({ data }) {
  return <div>{data.temp}</div>; // Runtime error if typo!
}

// ✅ CORRECT - Fully typed
interface TemperatureChartProps {
  data: WeatherReading[];
  width?: number;
  height?: number;
}

const TemperatureChart: React.FC<TemperatureChartProps> = ({
  data,
  width = 800,
  height = 400
}) => {
  return <div>{data[0].temperature}</div>; // Compile-time safety
};
```

**See:** [ADR-003: TypeScript Frontend](../architecture/decisions/003-typescript-frontend.md)

---

### 3. Accessible Design (WCAG 2.2 Level AA)

**CRITICAL RULE:** All UI components must meet WCAG 2.2 Level AA standards.

```tsx
// ❌ WRONG - Missing accessibility
<button onClick={handleClick}>
  <svg>...</svg>
</button>

// ✅ CORRECT - Accessible
<button
  onClick={handleClick}
  aria-label="Open settings menu"
  aria-expanded={isOpen}
>
  <svg aria-hidden="true">...</svg>
  <span className="sr-only">Settings</span>
</button>
```

**Requirements:**
- All interactive elements have proper ARIA labels
- Keyboard navigation works for all features
- Color is never the only way to convey information
- Text contrast meets 4.5:1 minimum (7:1 for AAA)
- Screen reader support tested with NVDA/JAWS

---

### 4. Responsive Design (Desktop + iPad)

**CRITICAL RULE:** All layouts must adapt to desktop and iPad viewports.

```css
/* Mobile-first approach */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

/* Tablet (iPad) */
@media (min-width: 768px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

**Breakpoints:**
- Mobile: < 768px
- Tablet (iPad): 768px - 1023px
- Desktop: ≥ 1024px

---

## Color Usage Rules

### Always Use Semantic Tokens

```css
/* Available semantic tokens */
--color-bg-primary         /* Main background */
--color-bg-secondary       /* Card/panel background */
--color-water              /* Temperature, rain, humidity data */
--color-growth             /* Wind, air quality, nature metrics */
--color-interactive        /* Buttons, links, hover states */
--color-text-primary       /* Headings, main text */
--color-text-secondary     /* Labels, metadata */
--color-border             /* Borders, dividers */

/* Chart-specific tokens */
--chart-line-water         /* Temperature/rain chart lines */
--chart-line-growth        /* Wind/humidity chart lines */
--chart-fill-water         /* Area fill for water metrics */
--chart-fill-growth        /* Area fill for growth metrics */
--chart-grid               /* Grid lines */
--chart-axis               /* Axis labels and ticks */
```

### Opacity Variants

```css
/* For semi-transparent backgrounds */
--color-water-10           /* 10% opacity */
--color-water-15           /* 15% opacity */
--color-water-25           /* 25% opacity */

--color-growth-10
--color-growth-15
--color-growth-25
```

### Victory Charts Theme

```typescript
// src/utils/chartTheme.ts
export const weatherChartTheme = {
  axis: {
    style: {
      axis: { stroke: 'var(--color-border)' },
      grid: {
        stroke: 'var(--chart-grid)',
        strokeDasharray: '4,4'
      },
      tickLabels: {
        fill: 'var(--chart-axis)',
        fontSize: 12,
        fontFamily: 'Inter, system-ui, sans-serif'
      }
    }
  },
  line: {
    style: {
      data: {
        stroke: 'var(--chart-line-water)',
        strokeWidth: 2
      },
      labels: {
        fill: 'var(--color-text-primary)'
      }
    }
  },
  area: {
    style: {
      data: {
        fill: 'var(--color-water-15)',
        stroke: 'var(--chart-line-water)',
        strokeWidth: 2
      }
    }
  }
};

// Usage in component
<VictoryChart theme={weatherChartTheme}>
  <VictoryLine data={temperatureData} />
</VictoryChart>
```

---

## Component Structure

### File Organization

```
src/
├── components/
│   ├── charts/
│   │   ├── TemperatureChart.tsx
│   │   ├── HumidityChart.tsx
│   │   └── WindChart.tsx
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── DatePicker.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Dashboard.tsx
├── hooks/
│   ├── useWeatherData.ts
│   └── useTheme.ts
├── services/
│   └── weatherApi.ts
├── styles/
│   ├── tokens/
│   │   ├── palettes.json
│   │   ├── tokens.css
│   │   └── themes.css
│   └── global.css
├── types/
│   ├── weather.ts
│   └── theme.ts
└── utils/
    ├── chartTheme.ts
    └── theme.ts
```

### Component Template

```tsx
// src/components/charts/TemperatureChart.tsx
import React from 'react';
import { VictoryChart, VictoryLine, VictoryAxis } from 'victory';
import type { WeatherReading } from '@/types/weather';
import { weatherChartTheme } from '@/utils/chartTheme';

interface TemperatureChartProps {
  data: WeatherReading[];
  width?: number;
  height?: number;
  className?: string;
}

/**
 * Temperature chart component
 * Displays temperature trends over time with high/low range
 */
export const TemperatureChart: React.FC<TemperatureChartProps> = ({
  data,
  width = 800,
  height = 400,
  className
}) => {
  // Data transformation
  const chartData = data.map(reading => ({
    x: new Date(reading.timestamp),
    y: reading.temperature,
    high: reading.temperature + 2, // Example
    low: reading.temperature - 2
  }));

  return (
    <div className={className}>
      <VictoryChart
        theme={weatherChartTheme}
        width={width}
        height={height}
        aria-label="Temperature chart showing trends over time"
      >
        <VictoryAxis
          label="Time"
          style={{
            axisLabel: { fill: 'var(--color-text-secondary)' }
          }}
        />
        <VictoryAxis
          dependentAxis
          label="Temperature (°F)"
          style={{
            axisLabel: { fill: 'var(--color-text-secondary)' }
          }}
        />
        <VictoryLine
          data={chartData}
          style={{
            data: { stroke: 'var(--chart-line-water)' }
          }}
        />
      </VictoryChart>
    </div>
  );
};
```

---

## Styling Guidelines

### CSS Modules (Recommended)

```tsx
// TemperatureChart.module.css
.container {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
}

.title {
  color: var(--color-text-primary);
  font-size: 1.25rem;
  margin-bottom: 1rem;
}

.chartWrapper {
  /* Chart container styles */
}

// TemperatureChart.tsx
import styles from './TemperatureChart.module.css';

export const TemperatureChart = () => (
  <div className={styles.container}>
    <h2 className={styles.title}>Temperature</h2>
    <div className={styles.chartWrapper}>
      {/* Chart here */}
    </div>
  </div>
);
```

### Utility Classes (Optional)

```css
/* src/styles/utilities.css */
.text-primary { color: var(--color-text-primary); }
.text-secondary { color: var(--color-text-secondary); }
.bg-primary { background-color: var(--color-bg-primary); }
.bg-secondary { background-color: var(--color-bg-secondary); }
.border { border: 1px solid var(--color-border); }
.rounded { border-radius: 8px; }
.p-4 { padding: 1rem; }
.mb-4 { margin-bottom: 1rem; }

/* Screen reader only (accessibility) */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

---

## Data Fetching

### API Client Pattern

```typescript
// src/services/weatherApi.ts
import type { WeatherReading } from '@/types/weather';

const API_BASE = process.env.VITE_API_URL || 'http://localhost:8000/api';

export class WeatherAPI {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      }
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getLatest(): Promise<WeatherReading> {
    return this.request<WeatherReading>('/weather/latest');
  }

  async getRange(start: Date, end: Date): Promise<WeatherReading[]> {
    const params = new URLSearchParams({
      start: start.toISOString(),
      end: end.toISOString()
    });
    return this.request<WeatherReading[]>(`/weather/range?${params}`);
  }
}

export const weatherApi = new WeatherAPI();
```

### Custom Hook

```typescript
// src/hooks/useWeatherData.ts
import { useState, useEffect } from 'react';
import { weatherApi } from '@/services/weatherApi';
import type { WeatherReading } from '@/types/weather';

export function useWeatherData(start: Date, end: Date) {
  const [data, setData] = useState<WeatherReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const readings = await weatherApi.getRange(start, end);
        if (!cancelled) {
          setData(readings);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err as Error);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [start, end]);

  return { data, loading, error };
}
```

---

## Testing

### Component Tests

```typescript
// src/components/charts/TemperatureChart.test.tsx
import { render, screen } from '@testing-library/react';
import { TemperatureChart } from './TemperatureChart';
import type { WeatherReading } from '@/types/weather';

const mockData: WeatherReading[] = [
  {
    timestamp: new Date('2026-01-01T12:00:00Z'),
    temperature: 72.5,
    humidity: 65,
    // ... other fields
  }
];

describe('TemperatureChart', () => {
  it('renders without crashing', () => {
    render(<TemperatureChart data={mockData} />);
    expect(screen.getByLabelText(/temperature chart/i)).toBeInTheDocument();
  });

  it('displays correct temperature data', () => {
    render(<TemperatureChart data={mockData} />);
    // Test that chart renders data correctly
  });

  it('is accessible', () => {
    const { container } = render(<TemperatureChart data={mockData} />);
    // Run accessibility tests (e.g., axe-core)
  });
});
```

---

## Performance

### Code Splitting

```typescript
// Lazy load heavy chart components
import { lazy, Suspense } from 'react';

const TemperatureChart = lazy(() => import('@/components/charts/TemperatureChart'));

function Dashboard() {
  return (
    <Suspense fallback={<div>Loading chart...</div>}>
      <TemperatureChart data={data} />
    </Suspense>
  );
}
```

### Memoization

```typescript
import { useMemo } from 'react';

const TemperatureChart = ({ data }: Props) => {
  // Only recalculate when data changes
  const chartData = useMemo(() => {
    return data.map(reading => ({
      x: new Date(reading.timestamp),
      y: reading.temperature
    }));
  }, [data]);

  return <VictoryLine data={chartData} />;
};
```

---

## Checklist for New Components

Before committing a new component, verify:

- [ ] Uses semantic color tokens (no hard-coded hex codes)
- [ ] Fully typed with TypeScript
- [ ] Has proper ARIA labels and keyboard support
- [ ] Responsive (tested on desktop + iPad)
- [ ] Uses design tokens from `tokens.css`
- [ ] Follows file naming conventions
- [ ] Includes JSDoc comments
- [ ] Has unit tests
- [ ] Meets WCAG 2.2 AA contrast requirements
- [ ] Tested in both light and dark themes
- [ ] No console errors or warnings

---

## Common Mistakes to Avoid

### ❌ Hard-coded Colors

```tsx
// WRONG
<div style={{ color: '#3B6B8F' }}>
```

### ❌ Missing TypeScript Types

```tsx
// WRONG
function MyComponent({ data }) {
  return <div>{data.value}</div>;
}
```

### ❌ Poor Accessibility

```tsx
// WRONG - no ARIA label, no keyboard support
<div onClick={handleClick}>
  <img src="icon.svg" />
</div>
```

### ❌ Non-Responsive Design

```css
/* WRONG - fixed width */
.container {
  width: 1200px;
}
```

### ❌ Importing Entire Library

```tsx
// WRONG - imports entire Victory library
import * as Victory from 'victory';
```

---

## Resources

- [Design Token System](design-tokens.md) - Complete token architecture
- [Color Palette Options](color-palette-options.md) - All available palettes
- [Color Palette Testing](color-palette-testing.md) - Accessibility validation
- [ADR-003: TypeScript Frontend](../architecture/decisions/003-typescript-frontend.md) - TypeScript standards
- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/) - Accessibility reference
- [Victory Charts Documentation](https://formidable.com/open-source/victory/) - Charting library

---

## Questions?

If you're unsure about any guideline:
1. Check the linked resources above
2. Review existing components for patterns
3. Ask in GitHub discussions

**Remember:** The goal is consistent, accessible, maintainable code that works for all users.
