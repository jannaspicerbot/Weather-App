# React & TypeScript Standards

**Framework:** React 18 + TypeScript
**Purpose:** Component development standards and patterns
**Reference:** Load this doc when building UI components
**Last Updated:** January 2026

---

## When to Use This Document

**Load before implementing:**
- New React components
- Modifying existing components
- State management
- API integration in UI
- Form handling

**MUST also load:** `docs/standards/ACCESSIBILITY.md` for all UI work

**Referenced from:** CLAUDE.md → "Working on UI components"

---

## Table of Contents

1. [Component Structure](#component-structure)
2. [TypeScript Patterns](#typescript-patterns)
3. [State Management](#state-management)
4. [API Integration](#api-integration)
5. [Styling](#styling)
6. [Accessibility Integration](#accessibility-integration)
7. [Performance](#performance)
8. [Testing](#testing)

---

## Component Structure

### File Organization

```
web/src/
├── components/
│   ├── WeatherChart/
│   │   ├── WeatherChart.tsx         # Component implementation
│   │   ├── WeatherChart.test.tsx    # Unit tests
│   │   ├── WeatherChart.module.css  # Component styles (if needed)
│   │   └── index.ts                 # Public exports
│   └── shared/
│       ├── Button/
│       ├── Card/
│       └── LoadingSpinner/
├── hooks/
│   ├── useWeatherData.ts
│   └── useApi.ts
├── utils/
│   └── dateFormatters.ts
└── types/
    └── weather.ts
```

### Component Template

```typescript
import React, { useState, useEffect } from 'react';
import { useButton } from '@react-aria/button';

/**
 * WeatherChart displays temperature data over time.
 *
 * @example
 * <WeatherChart
 *   data={weatherReadings}
 *   dateRange={{ start, end }}
 *   onRangeChange={handleRangeChange}
 * />
 */

// Props interface with JSDoc
interface WeatherChartProps {
  /** Array of weather readings to display */
  data: WeatherReading[];

  /** Date range for the chart */
  dateRange: DateRange;

  /** Callback when date range changes */
  onRangeChange: (range: DateRange) => void;

  /** Optional loading state */
  isLoading?: boolean;

  /** Optional error message */
  error?: string | null;
}

export function WeatherChart({
  data,
  dateRange,
  onRangeChange,
  isLoading = false,
  error = null
}: WeatherChartProps) {
  // State declarations
  const [selectedPoint, setSelectedPoint] = useState<WeatherReading | null>(null);

  // Effects
  useEffect(() => {
    // Effect logic
    return () => {
      // Cleanup
    };
  }, [data]);

  // Event handlers
  const handlePointClick = (point: WeatherReading) => {
    setSelectedPoint(point);
  };

  // Early returns for edge cases
  if (error) {
    return (
      <div role="alert" className="error">
        {error}
      </div>
    );
  }

  if (isLoading) {
    return (
      <div role="status" aria-live="polite">
        Loading chart data...
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="empty-state">
        No data available for selected range
      </div>
    );
  }

  // Main render
  return (
    <div className="weather-chart">
      {/* Component content */}
    </div>
  );
}
```

---

## TypeScript Patterns

### Props Types

```typescript
// Basic props
interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
}

// Props with generics
interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (row: T) => void;
}

// Props extending HTML attributes
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

// Props with children restrictions
interface LayoutProps {
  children: React.ReactElement<HeaderProps> | React.ReactElement<HeaderProps>[];
  sidebar?: React.ReactNode;
}

// Props with event handlers
interface FormProps {
  onSubmit: (data: FormData) => void | Promise<void>;
  onCancel?: () => void;
  onChange?: (field: string, value: unknown) => void;
}
```

### State Types

```typescript
// Simple state
const [count, setCount] = useState<number>(0);
const [name, setName] = useState<string>('');

// Object state
interface UserState {
  name: string;
  email: string;
  role: 'admin' | 'user';
}
const [user, setUser] = useState<UserState | null>(null);

// Array state
const [items, setItems] = useState<WeatherReading[]>([]);

// State with discriminated union
type LoadingState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: WeatherData[] }
  | { status: 'error'; error: string };

const [state, setState] = useState<LoadingState>({ status: 'idle' });

// Using the state
if (state.status === 'success') {
  // TypeScript knows state.data exists here
  console.log(state.data);
}
```

### Ref Types

```typescript
// DOM element refs
const inputRef = useRef<HTMLInputElement>(null);
const divRef = useRef<HTMLDivElement>(null);

// Component instance refs (rare, prefer callback patterns)
const chartRef = useRef<ChartComponent>(null);

// Mutable value refs
const timerRef = useRef<NodeJS.Timeout>();
const previousValueRef = useRef<string>();
```

### Event Handler Types

```typescript
// Mouse events
const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
  console.log(event.currentTarget);
};

// Keyboard events
const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
  if (event.key === 'Enter') {
    // Handle enter
  }
};

// Form events
const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
};

// Change events
const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  setValue(event.target.value);
};
```

---

## State Management

### Local Component State

```typescript
function WeatherDashboard() {
  // Simple values
  const [selectedStation, setSelectedStation] = useState<string>('STATION001');

  // Complex objects - use functional updates for nested state
  const [filters, setFilters] = useState<WeatherFilters>({
    dateRange: { start: new Date(), end: new Date() },
    stations: [],
    dataTypes: ['temperature', 'humidity']
  });

  const updateDateRange = (range: DateRange) => {
    setFilters(prev => ({
      ...prev,
      dateRange: range
    }));
  };

  return (
    // Component JSX
  );
}
```

### Shared State (Context)

```typescript
// WeatherContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface WeatherContextValue {
  selectedStation: string;
  setSelectedStation: (id: string) => void;
  refreshData: () => Promise<void>;
}

const WeatherContext = createContext<WeatherContextValue | undefined>(undefined);

export function WeatherProvider({ children }: { children: ReactNode }) {
  const [selectedStation, setSelectedStation] = useState<string>('STATION001');

  const refreshData = async () => {
    // Refresh logic
  };

  return (
    <WeatherContext.Provider value={{
      selectedStation,
      setSelectedStation,
      refreshData
    }}>
      {children}
    </WeatherContext.Provider>
  );
}

// Custom hook for consuming context
export function useWeather() {
  const context = useContext(WeatherContext);
  if (!context) {
    throw new Error('useWeather must be used within WeatherProvider');
  }
  return context;
}

// Usage in component
function StationSelector() {
  const { selectedStation, setSelectedStation } = useWeather();
  // Component logic
}
```

### Reducer Pattern (Complex State)

```typescript
import { useReducer } from 'react';

// State type
interface DashboardState {
  data: WeatherReading[];
  loading: boolean;
  error: string | null;
  filters: WeatherFilters;
}

// Action types
type DashboardAction =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: WeatherReading[] }
  | { type: 'FETCH_ERROR'; payload: string }
  | { type: 'UPDATE_FILTERS'; payload: Partial<WeatherFilters> }
  | { type: 'RESET' };

// Reducer function
function dashboardReducer(
  state: DashboardState,
  action: DashboardAction
): DashboardState {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };

    case 'FETCH_SUCCESS':
      return { ...state, loading: false, data: action.payload };

    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.payload };

    case 'UPDATE_FILTERS':
      return { ...state, filters: { ...state.filters, ...action.payload } };

    case 'RESET':
      return initialState;

    default:
      return state;
  }
}

// Usage
const initialState: DashboardState = {
  data: [],
  loading: false,
  error: null,
  filters: { /* defaults */ }
};

function Dashboard() {
  const [state, dispatch] = useReducer(dashboardReducer, initialState);

  const fetchData = async () => {
    dispatch({ type: 'FETCH_START' });
    try {
      const data = await api.getWeather();
      dispatch({ type: 'FETCH_SUCCESS', payload: data });
    } catch (error) {
      dispatch({ type: 'FETCH_ERROR', payload: error.message });
    }
  };

  return (
    // Component JSX
  );
}
```

---

## API Integration

### Custom Hook Pattern

```typescript
// hooks/useWeatherData.ts
import { useState, useEffect } from 'react';

interface UseWeatherDataOptions {
  stationId: string;
  dateRange: DateRange;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseWeatherDataReturn {
  data: WeatherReading[] | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useWeatherData({
  stationId,
  dateRange,
  autoRefresh = false,
  refreshInterval = 60000
}: UseWeatherDataOptions): UseWeatherDataReturn {
  const [data, setData] = useState<WeatherReading[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/weather/range?start=${dateRange.start}&end=${dateRange.end}&station=${stationId}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const json = await response.json();
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // Auto-refresh if enabled
    if (autoRefresh) {
      const interval = setInterval(fetchData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [stationId, dateRange.start, dateRange.end]);

  return { data, loading, error, refetch: fetchData };
}

// Usage in component
function WeatherDisplay({ stationId, dateRange }: Props) {
  const { data, loading, error, refetch } = useWeatherData({
    stationId,
    dateRange,
    autoRefresh: true
  });

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} onRetry={refetch} />;
  if (!data) return null;

  return <WeatherChart data={data} />;
}
```

### Error Handling

```typescript
// Error boundary component
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div role="alert">
          <h2>Something went wrong</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.message}</pre>
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary>
      <WeatherDashboard />
    </ErrorBoundary>
  );
}
```

---

## Styling

### CSS Custom Properties (Design Tokens)

```css
/* tokens.css - Design system */
:root {
  /* Colors */
  --color-primary: #0066cc;
  --color-text: #1a1a1a;
  --color-text-secondary: #666666;
  --color-background: #ffffff;
  --color-surface: #f5f5f5;
  --color-border: #e0e0e0;
  --color-error: #d32f2f;
  --color-success: #388e3c;

  /* Typography */
  --font-family-base: 'Inter', system-ui, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Border radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

```typescript
// Component styles
const styles = {
  container: {
    padding: 'var(--spacing-md)',
    backgroundColor: 'var(--color-surface)',
    borderRadius: 'var(--radius-md)',
    boxShadow: 'var(--shadow-sm)'
  },
  title: {
    fontSize: 'var(--font-size-xl)',
    color: 'var(--color-text)',
    marginBottom: 'var(--spacing-md)'
  }
};

function Card({ children }: { children: React.ReactNode }) {
  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Weather Data</h2>
      {children}
    </div>
  );
}
```

### Responsive Design

```css
.weather-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-md);
  padding: var(--spacing-md);
}

/* Mobile-first approach */
@media (min-width: 768px) {
  .weather-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .weather-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## Accessibility Integration

### Using React Aria

```typescript
import { useButton } from '@react-aria/button';
import { useTextField } from '@react-aria/textfield';

// Accessible button
function AccessibleButton({ onPress, children }: Props) {
  const ref = React.useRef(null);
  const { buttonProps } = useButton({ onPress }, ref);

  return (
    <button {...buttonProps} ref={ref} className="btn">
      {children}
    </button>
  );
}

// Accessible text input
function AccessibleTextField({ label, value, onChange }: Props) {
  const ref = React.useRef(null);
  const { labelProps, inputProps } = useTextField(
    { label, value, onChange },
    ref
  );

  return (
    <div>
      <label {...labelProps}>{label}</label>
      <input {...inputProps} ref={ref} />
    </div>
  );
}
```

### ARIA Attributes

```typescript
function WeatherAlert({ message, severity }: Props) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      className={`alert alert-${severity}`}
    >
      <span aria-label={`${severity} alert`}>
        {severity === 'error' ? '⚠️' : 'ℹ️'}
      </span>
      {message}
    </div>
  );
}

function LoadingState() {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <span className="sr-only">Loading weather data...</span>
      <div className="spinner" aria-hidden="true" />
    </div>
  );
}
```

**See ACCESSIBILITY.md for complete guidelines**

---

## Performance

### React.memo

```typescript
// Memoize expensive components
const WeatherChart = React.memo(function WeatherChart({ data }: Props) {
  // Component logic
}, (prevProps, nextProps) => {
  // Custom comparison (optional)
  return prevProps.data === nextProps.data;
});
```

### useMemo

```typescript
function DataTable({ data, filters }: Props) {
  // Memoize expensive filtering
  const filteredData = useMemo(() => {
    return data
      .filter(item => item.temperature > filters.minTemp)
      .sort((a, b) => b.timestamp - a.timestamp);
  }, [data, filters.minTemp]);

  return <Table data={filteredData} />;
}
```

### useCallback

```typescript
function Parent() {
  const [count, setCount] = useState(0);

  // Memoize callback to prevent child re-renders
  const handleClick = useCallback(() => {
    setCount(c => c + 1);
  }, []); // Empty deps = never recreated

  return <Child onClick={handleClick} />;
}
```

### Code Splitting

```typescript
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const WeatherChart = lazy(() => import('./components/WeatherChart'));
const DataExport = lazy(() => import('./components/DataExport'));

function Dashboard() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <WeatherChart data={data} />
      <DataExport data={data} />
    </Suspense>
  );
}
```

---

## Testing

### Component Tests

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { WeatherChart } from './WeatherChart';

describe('WeatherChart', () => {
  const mockData = [
    { timestamp: '2026-01-13T12:00:00Z', temperature: 72 },
    { timestamp: '2026-01-13T13:00:00Z', temperature: 74 }
  ];

  it('renders chart with data', () => {
    render(<WeatherChart data={mockData} />);
    expect(screen.getByRole('img')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<WeatherChart data={[]} isLoading />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<WeatherChart data={[]} error="Failed to load" />);
    expect(screen.getByRole('alert')).toHaveTextContent('Failed to load');
  });

  it('calls onRangeChange when date changes', async () => {
    const handleRangeChange = jest.fn();
    render(
      <WeatherChart
        data={mockData}
        onRangeChange={handleRangeChange}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /change range/i }));
    await waitFor(() => {
      expect(handleRangeChange).toHaveBeenCalled();
    });
  });
});
```

### Accessibility Tests

```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('has no accessibility violations', async () => {
  const { container } = render(<WeatherChart data={mockData} />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

## Checklist for New Components

- [ ] TypeScript types for all props
- [ ] Proper error and loading states
- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] ARIA attributes (roles, labels, live regions)
- [ ] Screen reader tested (quick pass)
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Unit tests written
- [ ] Accessibility tests (axe-core)
- [ ] Follows naming conventions
- [ ] Uses design tokens (CSS custom properties)
- [ ] Documented with JSDoc
- [ ] No console errors or warnings

---

**See also:**
- docs/standards/ACCESSIBILITY.md - Complete accessibility guidelines
- docs/examples/component-patterns.md - Real component examples
- docs/standards/TESTING.md - Testing strategies

**Questions?** Refer to CLAUDE.md or ask before implementing.
