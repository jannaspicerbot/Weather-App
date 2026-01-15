# React Component Pattern Examples

**Real examples from Weather App project**
**Reference:** Use these as templates for new components
**Load after:** REACT-STANDARDS.md and ACCESSIBILITY.md

---

## Table of Contents

1. [Simple Display Component](#simple-display-component)
2. [Interactive Button Component](#interactive-button-component)
3. [Form Input Component](#form-input-component)
4. [Data Table Component](#data-table-component)
5. [Chart Component](#chart-component)
6. [Modal Dialog Component](#modal-dialog-component)
7. [Custom Hook Example](#custom-hook-example)

---

## Simple Display Component

### Weather Card

```typescript
import React from 'react';

interface WeatherCardProps {
  /** Weather reading data */
  data: WeatherReading;
  /** Optional CSS class name */
  className?: string;
}

interface WeatherReading {
  timestamp: string;
  temperature_f: number;
  humidity: number;
  station_id: string;
}

/**
 * Displays a single weather reading in a card format.
 *
 * @example
 * <WeatherCard data={reading} />
 */
export function WeatherCard({ data, className = '' }: WeatherCardProps) {
  const formattedDate = new Date(data.timestamp).toLocaleString();

  return (
    <article
      className={`weather-card ${className}`}
      aria-labelledby="weather-card-title"
    >
      <h3 id="weather-card-title" className="sr-only">
        Weather reading for {data.station_id}
      </h3>

      <div className="weather-card__header">
        <span className="weather-card__station">{data.station_id}</span>
        <time dateTime={data.timestamp}>{formattedDate}</time>
      </div>

      <div className="weather-card__body">
        <div className="weather-stat">
          <span className="weather-stat__label">Temperature</span>
          <span className="weather-stat__value" aria-label={`${data.temperature_f} degrees Fahrenheit`}>
            {data.temperature_f}°F
          </span>
        </div>

        <div className="weather-stat">
          <span className="weather-stat__label">Humidity</span>
          <span className="weather-stat__value" aria-label={`${data.humidity} percent humidity`}>
            {data.humidity}%
          </span>
        </div>
      </div>
    </article>
  );
}
```

**Key points:**
- Semantic HTML (`<article>`, `<time>`)
- Screen reader-only title (`sr-only` class)
- ARIA labels for values with units
- TypeScript interfaces for all props
- JSDoc for component description

---

## Interactive Button Component

### Accessible Action Button

Native `<button>` elements provide built-in keyboard support (Enter, Space) and accessibility. No library needed.

```typescript
import React from 'react';

interface ActionButtonProps {
  /** Button text content */
  children: React.ReactNode;
  /** Click handler */
  onClick: () => void;
  /** Optional variant style */
  variant?: 'primary' | 'secondary' | 'danger';
  /** Whether button is disabled */
  disabled?: boolean;
  /** Optional aria-label for screen readers */
  ariaLabel?: string;
  /** Button type */
  type?: 'button' | 'submit' | 'reset';
}

/**
 * Accessible button using semantic HTML.
 *
 * Native <button> provides:
 * - Keyboard navigation (Enter, Space)
 * - Focus management
 * - Disabled state
 *
 * @example
 * <ActionButton onClick={handleClick} variant="primary">
 *   Refresh Data
 * </ActionButton>
 */
export function ActionButton({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  ariaLabel,
  type = 'button'
}: ActionButtonProps) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      className={`btn btn--${variant}`}
    >
      {children}
    </button>
  );
}
```

**CSS with :focus-visible:**
```css
.btn {
  padding: var(--spacing-md);
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  cursor: pointer;
  transition: all 0.2s ease;
}

/* Focus ring only for keyboard navigation (native browser support) */
.btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.btn:active {
  transform: scale(0.98);
}

.btn--primary {
  background-color: var(--color-primary);
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

**Key points:**
- Semantic `<button>` provides keyboard support automatically
- `:focus-visible` CSS shows focus ring only for keyboard users
- `:active` pseudo-class handles pressed state
- Native `disabled` attribute handles disabled state
- No JavaScript library needed for accessibility

---

## Form Input Component

### Text Input with Label and Error

Native `<input>` with `<label>` provides built-in accessibility. Use `htmlFor` to associate label with input.

```typescript
import React, { useId } from 'react';

interface TextInputProps {
  /** Input label */
  label: string;
  /** Current value */
  value: string;
  /** Change handler */
  onChange: (value: string) => void;
  /** Optional error message */
  error?: string;
  /** Optional placeholder */
  placeholder?: string;
  /** Input type */
  type?: 'text' | 'email' | 'password' | 'number';
  /** Whether input is required */
  required?: boolean;
  /** Whether input is disabled */
  disabled?: boolean;
}

/**
 * Accessible text input using semantic HTML.
 *
 * @example
 * <TextInput
 *   label="Station ID"
 *   value={stationId}
 *   onChange={setStationId}
 *   error={errors.stationId}
 *   required
 * />
 */
export function TextInput({
  label,
  value,
  onChange,
  error,
  placeholder,
  type = 'text',
  required = false,
  disabled = false
}: TextInputProps) {
  const inputId = useId();
  const errorId = useId();

  return (
    <div className="text-input">
      <label htmlFor={inputId} className="text-input__label">
        {label}
        {required && (
          <span className="text-input__required" aria-hidden="true">
            *
          </span>
        )}
      </label>

      <input
        id={inputId}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? errorId : undefined}
        className={`text-input__field ${error ? 'text-input__field--error' : ''}`}
      />

      {error && (
        <div
          id={errorId}
          className="text-input__error"
          role="alert"
        >
          {error}
        </div>
      )}
    </div>
  );
}
```

**CSS:**
```css
.text-input__field:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.text-input__field--error {
  border-color: var(--color-error);
}

.text-input__error {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-xs);
}
```

**Key points:**
- Native `<label>` with `htmlFor` creates accessible association
- `aria-invalid` and `aria-describedby` link error message
- Error message with `role="alert"` announces to screen readers
- `:focus-visible` CSS handles focus ring
- No JavaScript library needed

---

## Data Table Component

### Sortable Weather Data Table

Semantic `<table>` elements with `<button>` for sortable headers provide accessibility automatically.

```typescript
import React, { useState, useMemo } from 'react';

interface WeatherTableProps {
  /** Array of weather readings */
  data: WeatherReading[];
  /** Optional row click handler */
  onRowClick?: (reading: WeatherReading) => void;
}

type SortKey = keyof WeatherReading;
type SortOrder = 'asc' | 'desc';

/**
 * Sortable table displaying weather data.
 *
 * Features:
 * - Keyboard navigation
 * - Click to sort columns
 * - Row selection
 *
 * @example
 * <WeatherTable
 *   data={readings}
 *   onRowClick={handleRowClick}
 * />
 */
export function WeatherTable({ data, onRowClick }: WeatherTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>('timestamp');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  // Sort data
  const sortedData = React.useMemo(() => {
    return [...data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];

      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortKey, sortOrder]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      // Toggle order
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      // New column, default to ascending
      setSortKey(key);
      setSortOrder('asc');
    }
  };

  const handleKeyDown = (
    event: React.KeyboardEvent,
    reading: WeatherReading
  ) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onRowClick?.(reading);
    }
  };

  return (
    <div className="weather-table-container" role="region" aria-label="Weather data table">
      <table className="weather-table">
        <thead>
          <tr>
            <th>
              <button
                onClick={() => handleSort('timestamp')}
                className="weather-table__sort-button"
                aria-label={`Sort by timestamp ${sortKey === 'timestamp' ? sortOrder : ''}`}
              >
                Time
                {sortKey === 'timestamp' && (
                  <span aria-hidden="true">
                    {sortOrder === 'asc' ? ' ↑' : ' ↓'}
                  </span>
                )}
              </button>
            </th>
            <th>
              <button
                onClick={() => handleSort('station_id')}
                className="weather-table__sort-button"
                aria-label={`Sort by station ${sortKey === 'station_id' ? sortOrder : ''}`}
              >
                Station
                {sortKey === 'station_id' && (
                  <span aria-hidden="true">
                    {sortOrder === 'asc' ? ' ↑' : ' ↓'}
                  </span>
                )}
              </button>
            </th>
            <th>
              <button
                onClick={() => handleSort('temperature_f')}
                className="weather-table__sort-button"
                aria-label={`Sort by temperature ${sortKey === 'temperature_f' ? sortOrder : ''}`}
              >
                Temperature
                {sortKey === 'temperature_f' && (
                  <span aria-hidden="true">
                    {sortOrder === 'asc' ? ' ↑' : ' ↓'}
                  </span>
                )}
              </button>
            </th>
            <th>Humidity</th>
          </tr>
        </thead>
        <tbody>
          {sortedData.map((reading, index) => (
            <tr
              key={`${reading.station_id}-${reading.timestamp}`}
              onClick={() => onRowClick?.(reading)}
              onKeyDown={(e) => handleKeyDown(e, reading)}
              tabIndex={onRowClick ? 0 : undefined}
              className={onRowClick ? 'weather-table__row--clickable' : ''}
              role={onRowClick ? 'button' : undefined}
            >
              <td>
                <time dateTime={reading.timestamp}>
                  {new Date(reading.timestamp).toLocaleString()}
                </time>
              </td>
              <td>{reading.station_id}</td>
              <td>
                <span aria-label={`${reading.temperature_f} degrees Fahrenheit`}>
                  {reading.temperature_f}°F
                </span>
              </td>
              <td>
                <span aria-label={`${reading.humidity} percent humidity`}>
                  {reading.humidity}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {sortedData.length === 0 && (
        <div className="weather-table__empty" role="status">
          No weather data available
        </div>
      )}
    </div>
  );
}
```

**Key points:**
- Sortable columns with keyboard support
- ARIA labels for sort direction
- Keyboard navigation (Enter/Space for row selection)
- Proper semantic table structure
- Empty state with `role="status"`

---

## Chart Component

### Accessible Weather Chart (Victory)

```typescript
import React from 'react';
import { VictoryChart, VictoryLine, VictoryAxis, VictoryTheme } from 'victory';

interface WeatherChartProps {
  /** Array of weather readings */
  data: WeatherReading[];
  /** Optional loading state */
  isLoading?: boolean;
  /** Optional error state */
  error?: string | null;
}

/**
 * Line chart displaying temperature over time.
 *
 * Accessibility features:
 * - Keyboard accessible
 * - Screen reader friendly
 * - High contrast colors
 *
 * @example
 * <WeatherChart data={readings} />
 */
export function WeatherChart({
  data,
  isLoading = false,
  error = null
}: WeatherChartProps) {
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
      <div
        className="weather-chart weather-chart--loading"
        role="status"
        aria-live="polite"
      >
        <div className="loading-spinner" aria-hidden="true" />
        <span>Loading chart data...</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div
        className="weather-chart weather-chart--error"
        role="alert"
      >
        <span className="error-icon" aria-hidden="true">⚠️</span>
        <span>{error}</span>
      </div>
    );
  }

  // Empty state
  if (data.length === 0) {
    return (
      <div className="weather-chart weather-chart--empty" role="status">
        No data available for the selected range
      </div>
    );
  }

  return (
    <div
      className="weather-chart"
      role="img"
      aria-label={`Temperature chart showing ${data.length} readings from ${new Date(data[0].timestamp).toLocaleDateString()} to ${new Date(data[data.length - 1].timestamp).toLocaleDateString()}`}
    >
      <h3 className="weather-chart__title">
        Temperature Over Time
      </h3>

      <VictoryChart
        theme={VictoryTheme.material}
        width={800}
        height={400}
        containerComponent={
          <VictoryVoronoiContainer
            labels={({ datum }) =>
              `${datum.x.toLocaleString()}: ${datum.y}°F`
            }
          />
        }
      >
        <VictoryAxis
          tickFormat={(date) => date.toLocaleDateString()}
          label="Date"
          style={{
            axisLabel: { padding: 30, fontSize: 14 }
          }}
        />
        <VictoryAxis
          dependentAxis
          label="Temperature (°F)"
          style={{
            axisLabel: { padding: 40, fontSize: 14 }
          }}
        />
        <VictoryLine
          data={chartData}
          style={{
            data: { stroke: 'var(--color-primary)' }
          }}
        />
      </VictoryChart>

      {/* Data table alternative for screen readers */}
      <details className="weather-chart__data">
        <summary>View data table</summary>
        <table className="sr-only">
          <caption>Temperature readings</caption>
          <thead>
            <tr>
              <th>Date/Time</th>
              <th>Temperature (°F)</th>
            </tr>
          </thead>
          <tbody>
            {data.map((reading, index) => (
              <tr key={index}>
                <td>{new Date(reading.timestamp).toLocaleString()}</td>
                <td>{reading.temperature_f}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
```

**Key points:**
- Loading, error, and empty states
- `role="img"` with descriptive aria-label
- Data table alternative for screen readers
- High contrast colors
- Keyboard accessible tooltips (Victory built-in)

---

## Modal Dialog Component

### Accessible Modal with Native `<dialog>`

The native `<dialog>` element provides built-in accessibility:
- Focus trapping (automatic)
- Escape key closes (automatic)
- Backdrop click closes (with small handler)
- Focus restoration on close (automatic)
- Proper ARIA roles (automatic)

```typescript
import React, { useEffect, useRef, useId } from 'react';

interface ModalProps {
  /** Modal title */
  title: string;
  /** Modal content */
  children: React.ReactNode;
  /** Whether modal is open */
  isOpen: boolean;
  /** Close handler */
  onClose: () => void;
  /** Optional footer actions */
  footer?: React.ReactNode;
}

/**
 * Accessible modal using native <dialog> element.
 *
 * The browser provides:
 * - Focus trapping inside modal
 * - Escape key closes
 * - Focus restoration on close
 * - Proper ARIA roles
 *
 * @example
 * <Modal
 *   isOpen={isOpen}
 *   onClose={() => setIsOpen(false)}
 *   title="Confirm Delete"
 * >
 *   Are you sure you want to delete this reading?
 * </Modal>
 */
export function Modal({
  title,
  children,
  isOpen,
  onClose,
  footer
}: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleId = useId();

  // Sync dialog open state with isOpen prop
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen && !dialog.open) {
      dialog.showModal();
    } else if (!isOpen && dialog.open) {
      dialog.close();
    }
  }, [isOpen]);

  // Handle backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === dialogRef.current) {
      onClose();
    }
  };

  // Handle native close event (Escape key)
  const handleClose = () => {
    onClose();
  };

  return (
    <dialog
      ref={dialogRef}
      className="modal"
      aria-labelledby={titleId}
      onClick={handleBackdropClick}
      onClose={handleClose}
    >
      <div className="modal__container">
        <div className="modal__header">
          <h2 id={titleId} className="modal__title">
            {title}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="modal__close"
            aria-label="Close dialog"
          >
            <span aria-hidden="true">×</span>
          </button>
        </div>

        <div className="modal__body">
          {children}
        </div>

        {footer && (
          <div className="modal__footer">
            {footer}
          </div>
        )}
      </div>
    </dialog>
  );
}
```

**CSS for dialog:**
```css
.modal {
  border: none;
  border-radius: var(--radius-lg);
  padding: 0;
  max-width: 500px;
  width: 90%;
}

.modal::backdrop {
  background: rgba(0, 0, 0, 0.5);
}

.modal__container {
  padding: var(--spacing-lg);
}

.modal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.modal__close:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.modal__footer {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
  margin-top: var(--spacing-lg);
}
```

**Usage example:**
```typescript
function DeleteConfirmation() {
  const [isOpen, setIsOpen] = useState(false);

  const handleDelete = () => {
    // Delete logic
    setIsOpen(false);
  };

  return (
    <>
      <ActionButton onClick={() => setIsOpen(true)} variant="danger">
        Delete
      </ActionButton>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Confirm Delete"
        footer={
          <>
            <ActionButton onClick={() => setIsOpen(false)} variant="secondary">
              Cancel
            </ActionButton>
            <ActionButton onClick={handleDelete} variant="danger">
              Delete
            </ActionButton>
          </>
        }
      >
        <p>
          Are you sure you want to delete this weather reading?
          This action cannot be undone.
        </p>
      </Modal>
    </>
  );
}
```

**Key points:**
- Native `<dialog>` provides focus trapping automatically
- Escape key closes via native `onClose` event
- `::backdrop` pseudo-element for overlay styling
- Click outside handled with simple click handler
- Focus restoration is automatic
- No JavaScript library needed

---

## Custom Hook Example

### useWeatherData Hook

```typescript
import { useState, useEffect, useCallback } from 'react';

interface UseWeatherDataOptions {
  /** Station ID to fetch */
  stationId: string;
  /** Auto-refresh interval in ms */
  refreshInterval?: number;
  /** Whether to auto-refresh */
  autoRefresh?: boolean;
}

interface UseWeatherDataReturn {
  /** Weather data */
  data: WeatherReading[] | null;
  /** Loading state */
  loading: boolean;
  /** Error state */
  error: Error | null;
  /** Manual refetch function */
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch and manage weather data.
 *
 * Features:
 * - Auto-refresh support
 * - Error handling
 * - Loading states
 * - Manual refetch
 *
 * @example
 * const { data, loading, error, refetch } = useWeatherData({
 *   stationId: 'STATION001',
 *   autoRefresh: true,
 *   refreshInterval: 60000
 * });
 */
export function useWeatherData({
  stationId,
  refreshInterval = 60000,
  autoRefresh = false
}: UseWeatherDataOptions): UseWeatherDataReturn {
  const [data, setData] = useState<WeatherReading[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/weather/station/${stationId}?limit=100`
      );

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const json = await response.json();
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [stationId]);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchData]);

  return { data, loading, error, refetch: fetchData };
}
```

**Usage:**
```typescript
function WeatherDisplay({ stationId }: { stationId: string }) {
  const { data, loading, error, refetch } = useWeatherData({
    stationId,
    autoRefresh: true,
    refreshInterval: 60000 // 1 minute
  });

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} onRetry={refetch} />;
  if (!data) return null;

  return (
    <div>
      <ActionButton onClick={refetch}>Refresh</ActionButton>
      <WeatherTable data={data} />
    </div>
  );
}
```

---

## Common Patterns Summary

### 1. Always Include
- TypeScript interfaces for props
- JSDoc comments
- Proper ARIA attributes
- Loading/error/empty states
- Keyboard support

### 2. Accessibility Checklist
- Semantic HTML elements
- ARIA roles when needed
- Keyboard navigation
- Focus management
- Screen reader labels

### 3. State Management
- useState for simple state
- useReducer for complex state
- Custom hooks for reusable logic
- Context for shared state

### 4. Performance
- useMemo for expensive calculations
- useCallback for stable callbacks
- React.memo for expensive components

---

**See also:**
- REACT-STANDARDS.md - Full standards
- ACCESSIBILITY.md - Complete accessibility guide
- TESTING.md - Component testing strategies

**Questions?** Check CLAUDE.md or ask before implementing.
