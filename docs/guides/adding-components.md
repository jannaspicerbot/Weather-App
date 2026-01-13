# Guide: Adding New React Components

**Step-by-step guide for adding React components to Weather App**
**Time estimate:** 45-90 minutes for complete component
**Prerequisites:** REACT-STANDARDS.md, ACCESSIBILITY.md, component-patterns.md

---

## Table of Contents

1. [Quick Start Checklist](#quick-start-checklist)
2. [Step-by-Step Guide](#step-by-step-guide)
3. [Example Walkthrough](#example-walkthrough)
4. [Testing Your Component](#testing-your-component)
5. [Common Patterns](#common-patterns)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start Checklist

Use this checklist while building your component:

**Planning:**
- [ ] Identify component purpose and behavior
- [ ] Design props interface
- [ ] Plan state management approach
- [ ] Consider accessibility requirements

**Implementation:**
- [ ] Create component file with TypeScript
- [ ] Define props interface
- [ ] Implement component logic
- [ ] Add accessibility features (ARIA, keyboard)
- [ ] Style with CSS custom properties
- [ ] Handle loading/error/empty states

**Accessibility (REQUIRED):**
- [ ] Semantic HTML elements
- [ ] Keyboard navigation (Tab, Enter, Escape, Arrows)
- [ ] ARIA labels and roles
- [ ] Screen reader testing
- [ ] Focus management
- [ ] Color contrast (4.5:1 minimum)

**Testing:**
- [ ] Write unit tests (logic)
- [ ] Write integration tests (rendering)
- [ ] Test keyboard navigation
- [ ] Test with screen reader
- [ ] Test at 200% zoom
- [ ] Test on mobile (touch targets 48x48px)

**Documentation:**
- [ ] Add JSDoc comments
- [ ] Document props with descriptions
- [ ] Add usage examples
- [ ] Update Storybook (if applicable)

---

## Step-by-Step Guide

### Step 1: Plan Your Component

**Questions to answer:**

1. **What does this component do?**
   - Example: "Display current weather conditions with refresh button"

2. **What data does it need?**
   - Props from parent
   - API data to fetch
   - Local state to manage

3. **What interactions does it support?**
   - Click handlers
   - Form inputs
   - Keyboard shortcuts
   - Hover states

4. **What states does it have?**
   - Loading (fetching data)
   - Error (failed to load)
   - Empty (no data)
   - Success (data loaded)

5. **How will users navigate it?**
   - Mouse/touch
   - Keyboard (Tab, Enter, Escape, Arrows)
   - Screen reader

6. **Is it reusable?**
   - Generic component (many uses)
   - Specific component (one use case)

---

### Step 2: Create Component File

**Location:** `src/components/ComponentName.tsx`

**File structure:**
```
src/
├── components/
│   ├── WeatherCard.tsx          # Component
│   ├── WeatherCard.module.css   # Styles
│   └── WeatherCard.test.tsx     # Tests
```

**Initial template:**
```typescript
import React from 'react';
import styles from './WeatherCard.module.css';

interface WeatherCardProps {
  /** Add prop descriptions */
}

/**
 * WeatherCard component.
 *
 * Add component description here.
 *
 * @example
 * <WeatherCard data={weatherData} />
 */
export function WeatherCard(props: WeatherCardProps) {
  return (
    <div className={styles.container}>
      {/* Component content */}
    </div>
  );
}
```

---

### Step 3: Define Props Interface

**With TypeScript:**

```typescript
interface WeatherCardProps {
  /** Weather reading data */
  data: WeatherReading;

  /** Optional callback when refresh clicked */
  onRefresh?: () => void;

  /** Whether card is in loading state */
  isLoading?: boolean;

  /** Optional error message */
  error?: string | null;

  /** Optional CSS class name */
  className?: string;
}

interface WeatherReading {
  timestamp: string;
  temperature_f: number;
  humidity: number;
  station_id: string;
}
```

**Key points:**
- Document each prop with JSDoc
- Use TypeScript interfaces (not `any`)
- Mark optional props with `?`
- Provide default values in component
- Use specific types (not `object`)

---

### Step 4: Implement Component Logic

**Basic structure:**

```typescript
import React, { useState, useEffect } from 'react';

export function WeatherCard({
  data,
  onRefresh,
  isLoading = false,
  error = null,
  className = ''
}: WeatherCardProps) {
  // Local state
  const [isExpanded, setIsExpanded] = useState(false);

  // Derived values
  const formattedDate = new Date(data.timestamp).toLocaleString();

  // Event handlers
  const handleRefreshClick = () => {
    onRefresh?.();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setIsExpanded(!isExpanded);
    }
  };

  // Effects
  useEffect(() => {
    // Side effects here
  }, [dependencies]);

  // Loading state
  if (isLoading) {
    return <LoadingSpinner />;
  }

  // Error state
  if (error) {
    return <ErrorMessage message={error} />;
  }

  // Main render
  return (
    <article className={`${styles.card} ${className}`}>
      {/* Content */}
    </article>
  );
}
```

**Key points:**
- Handle loading/error/empty states first
- Use semantic HTML (`<article>`, `<section>`, etc.)
- Destructure props with defaults
- Group related state/logic together

---

### Step 5: Add Accessibility Features

**Semantic HTML:**

```typescript
return (
  <article
    className={styles.card}
    aria-labelledby="weather-card-title"
  >
    <header className={styles.header}>
      <h3 id="weather-card-title" className="sr-only">
        Weather for {data.station_id}
      </h3>
      <span className={styles.station}>{data.station_id}</span>
      <time dateTime={data.timestamp}>{formattedDate}</time>
    </header>

    <div className={styles.body}>
      <div className={styles.stat}>
        <span className={styles.label}>Temperature</span>
        <span
          className={styles.value}
          aria-label={`${data.temperature_f} degrees Fahrenheit`}
        >
          {data.temperature_f}°F
        </span>
      </div>
    </div>
  </article>
);
```

**Keyboard navigation:**

```typescript
import { useButton } from '@react-aria/button';

export function RefreshButton({ onPress }: { onPress: () => void }) {
  const ref = React.useRef<HTMLButtonElement>(null);
  const { buttonProps, isPressed } = useButton({ onPress }, ref);

  return (
    <button
      {...buttonProps}
      ref={ref}
      className={styles.refreshButton}
      aria-label="Refresh weather data"
    >
      <RefreshIcon aria-hidden="true" />
      Refresh
    </button>
  );
}
```

**Focus management:**

```typescript
import { useFocusRing } from '@react-aria/focus';

export function InteractiveCard({ onClick }: Props) {
  const { isFocusVisible, focusProps } = useFocusRing();

  return (
    <div
      {...focusProps}
      tabIndex={0}
      className={`
        ${styles.card}
        ${isFocusVisible ? styles.focusVisible : ''}
      `}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      role="button"
    >
      {/* Content */}
    </div>
  );
}
```

**Screen reader labels:**

```typescript
return (
  <div className={styles.stats}>
    <div className={styles.stat}>
      <span className="sr-only">Temperature:</span>
      <span aria-label={`${temp} degrees Fahrenheit`}>
        {temp}°F
      </span>
    </div>

    <div className={styles.stat}>
      <span className="sr-only">Humidity:</span>
      <span aria-label={`${humidity} percent humidity`}>
        {humidity}%
      </span>
    </div>
  </div>
);
```

---

### Step 6: Add Styles

**Create CSS Module:** `ComponentName.module.css`

```css
/* Use CSS custom properties from :root */
.card {
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
}

/* Focus visible (keyboard navigation) */
.card:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Responsive design */
@media (max-width: 768px) {
  .card {
    padding: var(--spacing-sm);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .card {
    border: 2px solid var(--color-border);
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .card {
    background-color: var(--color-surface-dark);
  }
}
```

**CSS Custom Properties (in your global CSS):**

```css
:root {
  /* Colors */
  --color-primary: #007bff;
  --color-surface: #ffffff;
  --color-surface-dark: #1a1a1a;
  --color-text: #333333;
  --color-border: #e0e0e0;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* Typography */
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-size-xl: 1.5rem;
}
```

---

### Step 7: Write Tests

**Location:** `src/components/ComponentName.test.tsx`

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { WeatherCard } from './WeatherCard';

const mockData = {
  timestamp: '2026-01-13T12:00:00Z',
  temperature_f: 72.5,
  humidity: 65,
  station_id: 'STATION001'
};

describe('WeatherCard', () => {
  it('renders weather data correctly', () => {
    render(<WeatherCard data={mockData} />);

    expect(screen.getByText('STATION001')).toBeInTheDocument();
    expect(screen.getByText(/72.5°F/)).toBeInTheDocument();
    expect(screen.getByText(/65%/)).toBeInTheDocument();
  });

  it('calls onRefresh when refresh button clicked', () => {
    const handleRefresh = vi.fn();
    render(<WeatherCard data={mockData} onRefresh={handleRefresh} />);

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);

    expect(handleRefresh).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<WeatherCard data={mockData} isLoading={true} />);

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.queryByText('STATION001')).not.toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<WeatherCard data={mockData} error="Failed to load" />);

    expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
    expect(screen.queryByText('STATION001')).not.toBeInTheDocument();
  });

  it('is keyboard accessible', () => {
    const handleRefresh = vi.fn();
    render(<WeatherCard data={mockData} onRefresh={handleRefresh} />);

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    refreshButton.focus();

    fireEvent.keyDown(refreshButton, { key: 'Enter' });
    expect(handleRefresh).toHaveBeenCalled();
  });

  it('has accessible labels', () => {
    render(<WeatherCard data={mockData} />);

    // Check ARIA labels
    expect(screen.getByLabelText(/72.5 degrees fahrenheit/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/65 percent humidity/i)).toBeInTheDocument();
  });
});
```

**Accessibility tests:**

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

describe('WeatherCard Accessibility', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(<WeatherCard data={mockData} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('supports keyboard navigation', () => {
    render(<WeatherCard data={mockData} />);

    // Tab to interactive elements
    const button = screen.getByRole('button');
    button.focus();
    expect(button).toHaveFocus();

    // Activate with Enter
    fireEvent.keyDown(button, { key: 'Enter' });
    // Assert expected behavior
  });
});
```

---

## Example Walkthrough

### Complete Example: Temperature Chart Component

**Goal:** Create a line chart showing temperature over time with accessibility features.

#### 1. Plan

- **Purpose:** Display temperature trends visually
- **Data:** Array of weather readings
- **Interactions:** Hover to see values, keyboard navigation
- **States:** Loading, error, empty, success
- **Accessibility:** Data table alternative, keyboard support

#### 2. Create Interface

```typescript
// src/components/TemperatureChart.tsx

import React from 'react';
import { VictoryChart, VictoryLine, VictoryAxis } from 'victory';

interface TemperatureChartProps {
  /** Weather readings to display */
  data: WeatherReading[];

  /** Optional title for chart */
  title?: string;

  /** Whether data is loading */
  isLoading?: boolean;

  /** Optional error message */
  error?: string | null;

  /** Optional CSS class */
  className?: string;
}

interface WeatherReading {
  timestamp: string;
  temperature_f: number;
  station_id: string;
}
```

#### 3. Implement Component

```typescript
export function TemperatureChart({
  data,
  title = 'Temperature Over Time',
  isLoading = false,
  error = null,
  className = ''
}: TemperatureChartProps) {
  // Transform data for Victory
  const chartData = React.useMemo(() => {
    return data.map(reading => ({
      x: new Date(reading.timestamp),
      y: reading.temperature_f
    }));
  }, [data]);

  // Loading state
  if (isLoading) {
    return (
      <div className={styles.loading} role="status" aria-live="polite">
        <LoadingSpinner />
        <span>Loading chart data...</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={styles.error} role="alert">
        <ErrorIcon aria-hidden="true" />
        <span>{error}</span>
      </div>
    );
  }

  // Empty state
  if (data.length === 0) {
    return (
      <div className={styles.empty} role="status">
        <EmptyIcon aria-hidden="true" />
        <span>No data available</span>
      </div>
    );
  }

  // Main render
  return (
    <div className={`${styles.container} ${className}`}>
      <h3 className={styles.title}>{title}</h3>

      {/* Visual chart */}
      <div
        className={styles.chart}
        role="img"
        aria-label={`Temperature chart showing ${data.length} readings from ${new Date(data[0].timestamp).toLocaleDateString()} to ${new Date(data[data.length - 1].timestamp).toLocaleDateString()}`}
      >
        <VictoryChart
          width={800}
          height={400}
          padding={{ top: 20, bottom: 60, left: 60, right: 20 }}
        >
          <VictoryAxis
            tickFormat={(date) => date.toLocaleDateString()}
            label="Date"
            style={{
              axisLabel: { padding: 40, fontSize: 14 },
              tickLabels: { fontSize: 12 }
            }}
          />
          <VictoryAxis
            dependentAxis
            label="Temperature (°F)"
            style={{
              axisLabel: { padding: 45, fontSize: 14 },
              tickLabels: { fontSize: 12 }
            }}
          />
          <VictoryLine
            data={chartData}
            style={{
              data: {
                stroke: 'var(--color-primary)',
                strokeWidth: 2
              }
            }}
          />
        </VictoryChart>
      </div>

      {/* Data table alternative for screen readers */}
      <details className={styles.dataTable}>
        <summary>View data table</summary>
        <table>
          <caption className="sr-only">Temperature readings</caption>
          <thead>
            <tr>
              <th scope="col">Date/Time</th>
              <th scope="col">Temperature (°F)</th>
              <th scope="col">Station</th>
            </tr>
          </thead>
          <tbody>
            {data.map((reading, index) => (
              <tr key={index}>
                <td>{new Date(reading.timestamp).toLocaleString()}</td>
                <td>{reading.temperature_f}</td>
                <td>{reading.station_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
```

#### 4. Add Styles

```css
/* TemperatureChart.module.css */

.container {
  background-color: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
}

.title {
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-md);
  color: var(--color-text);
}

.chart {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

/* Loading state */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: var(--spacing-md);
}

/* Error state */
.error {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background-color: var(--color-error-bg);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-md);
  color: var(--color-error);
}

/* Empty state */
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xl);
  color: var(--color-text-secondary);
}

/* Data table */
.dataTable {
  margin-top: var(--spacing-lg);
}

.dataTable summary {
  cursor: pointer;
  padding: var(--spacing-sm);
  background-color: var(--color-surface-alt);
  border-radius: var(--radius-sm);
}

.dataTable summary:hover {
  background-color: var(--color-surface-hover);
}

.dataTable table {
  width: 100%;
  margin-top: var(--spacing-md);
  border-collapse: collapse;
}

.dataTable th,
.dataTable td {
  padding: var(--spacing-sm);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

/* Responsive */
@media (max-width: 768px) {
  .chart {
    overflow-x: auto;
  }
}
```

#### 5. Write Tests

```typescript
// TemperatureChart.test.tsx

describe('TemperatureChart', () => {
  const mockData = [
    { timestamp: '2026-01-13T12:00:00Z', temperature_f: 72, station_id: 'S1' },
    { timestamp: '2026-01-13T13:00:00Z', temperature_f: 75, station_id: 'S1' },
    { timestamp: '2026-01-13T14:00:00Z', temperature_f: 73, station_id: 'S1' }
  ];

  it('renders chart with data', () => {
    render(<TemperatureChart data={mockData} />);

    expect(screen.getByText(/temperature over time/i)).toBeInTheDocument();
    // Victory creates SVG, check for it
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<TemperatureChart data={[]} isLoading={true} />);

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText(/loading chart data/i)).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<TemperatureChart data={[]} error="Failed to load" />);

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
  });

  it('shows empty state', () => {
    render(<TemperatureChart data={[]} />);

    expect(screen.getByText(/no data available/i)).toBeInTheDocument();
  });

  it('provides data table alternative', () => {
    render(<TemperatureChart data={mockData} />);

    const details = screen.getByText(/view data table/i).closest('details');
    expect(details).toBeInTheDocument();

    // Open details
    fireEvent.click(screen.getByText(/view data table/i));

    // Check table content
    expect(screen.getByRole('table')).toBeInTheDocument();
    expect(screen.getByText('72')).toBeInTheDocument();
    expect(screen.getByText('75')).toBeInTheDocument();
  });

  it('has accessible aria-label', () => {
    render(<TemperatureChart data={mockData} />);

    const chart = screen.getByRole('img');
    expect(chart).toHaveAttribute('aria-label');
    expect(chart.getAttribute('aria-label')).toContain('3 readings');
  });

  it('memoizes chart data', () => {
    const { rerender } = render(<TemperatureChart data={mockData} />);

    // Rerender with same data
    rerender(<TemperatureChart data={mockData} />);

    // Data should not be recalculated (would need spy to verify)
  });
});
```

#### 6. Usage Example

```typescript
// In a parent component
function WeatherDashboard() {
  const { data, loading, error } = useWeatherData('STATION001');

  return (
    <div>
      <h2>Station Dashboard</h2>
      <TemperatureChart
        data={data}
        isLoading={loading}
        error={error}
        title="24-Hour Temperature Trend"
      />
    </div>
  );
}
```

---

## Common Patterns

### Pattern 1: Loading States

```typescript
function DataComponent({ isLoading, data, error }: Props) {
  if (isLoading) {
    return (
      <div role="status" aria-live="polite">
        <LoadingSpinner />
        <span className="sr-only">Loading data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert">
        <ErrorIcon aria-hidden="true" />
        <span>{error}</span>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div role="status">
        <EmptyIcon aria-hidden="true" />
        <span>No data available</span>
      </div>
    );
  }

  return <div>{/* Render data */}</div>;
}
```

### Pattern 2: Custom Hook for Data Fetching

```typescript
function useWeatherData(stationId: string) {
  const [data, setData] = useState<WeatherReading[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch(`/api/weather/station/${stationId}`);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const json = await response.json();

        if (!cancelled) {
          setData(json);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unknown error');
          setData(null);
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
  }, [stationId]);

  return { data, loading, error };
}
```

### Pattern 3: Compound Components

```typescript
// Parent component
function WeatherCard({ children }: { children: React.ReactNode }) {
  return <article className={styles.card}>{children}</article>;
}

// Sub-components
WeatherCard.Header = function Header({ title }: { title: string }) {
  return <header className={styles.header}>{title}</header>;
};

WeatherCard.Body = function Body({ children }: { children: React.ReactNode }) {
  return <div className={styles.body}>{children}</div>;
};

WeatherCard.Footer = function Footer({ children }: { children: React.ReactNode }) {
  return <footer className={styles.footer}>{children}</footer>;
};

// Usage
<WeatherCard>
  <WeatherCard.Header title="Current Weather" />
  <WeatherCard.Body>
    <p>72°F</p>
  </WeatherCard.Body>
  <WeatherCard.Footer>
    <button>Refresh</button>
  </WeatherCard.Footer>
</WeatherCard>
```

---

## Troubleshooting

### Issue: "Component not rendering"

**Possible causes:**
1. Component not exported
2. Import path incorrect
3. Parent not rendering component

**Solutions:**
```typescript
// Make sure it's exported
export function MyComponent() { }  // ✅
// not: function MyComponent() { }  // ❌

// Check import path
import { MyComponent } from './components/MyComponent';  // ✅
// not: import { MyComponent } from './MyComponent';      // ❌
```

### Issue: "Props not updating"

**Cause:** Component not re-rendering when props change

**Solution:**
```typescript
// Use useEffect to respond to prop changes
useEffect(() => {
  // Do something when prop changes
}, [propName]);

// Or useMemo for derived values
const derivedValue = useMemo(() => {
  return computeValue(prop);
}, [prop]);
```

### Issue: "Keyboard navigation not working"

**Cause:** Missing tabindex or keyboard event handlers

**Solution:**
```typescript
// Add tabIndex for focusable elements
<div
  tabIndex={0}
  onKeyDown={handleKeyDown}
  role="button"
>

// Implement keyboard handler
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    handleClick();
  }
};
```

### Issue: "Tests failing"

**Common causes:**
1. Async operations not awaited
2. Missing test IDs or labels
3. State not updated in test

**Solutions:**
```typescript
// Use waitFor for async operations
import { waitFor } from '@testing-library/react';

await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument();
});

// Use findBy queries (automatically wait)
const element = await screen.findByText('Loaded');

// Add test IDs if needed
<div data-testid="weather-card">
```

---

## Checklist for PR

Before submitting PR for new component:

**Implementation:**
- [ ] TypeScript interfaces defined
- [ ] Props documented with JSDoc
- [ ] Loading/error/empty states handled
- [ ] Component exported properly

**Accessibility (REQUIRED):**
- [ ] Semantic HTML used
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] ARIA labels added where needed
- [ ] Tested with screen reader (VoiceOver/NVDA)
- [ ] Color contrast meets 4.5:1
- [ ] Touch targets 48x48px minimum
- [ ] Focus indicators visible
- [ ] Works at 200% zoom

**Testing:**
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Accessibility tests (jest-axe)
- [ ] All tests passing
- [ ] Coverage > 80%

**Styles:**
- [ ] CSS modules used
- [ ] CSS custom properties used
- [ ] Responsive design implemented
- [ ] Dark mode support (if applicable)
- [ ] High contrast mode support

**Documentation:**
- [ ] Component documented in Storybook
- [ ] Usage examples provided
- [ ] Props interface documented

---

**See also:**
- REACT-STANDARDS.md - React best practices
- ACCESSIBILITY.md - Complete accessibility guide
- component-patterns.md - Code examples
- TESTING.md - Testing strategies

**Questions?** Check CLAUDE.md or ask before implementing.
