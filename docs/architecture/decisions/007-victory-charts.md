# ADR-007: Victory Charts for Data Visualization

**Status:** ✅ Accepted (Phase 3)
**Date:** 2026-01-03
**Deciders:** Janna Spicer, Architecture Review

> **Update (2026-01-09):** This ADR references TailwindCSS and Recharts. TailwindCSS was later replaced with CSS Custom Properties (design tokens). Victory Charts decision stands - it is now the charting library in use.

---

## Context

The Weather App needs a charting library for visualizing time-series weather data (temperature, humidity, pressure, wind speed). The charts must:
- Support WCAG 2.2 Level AA accessibility compliance
- Work on desktop and iPad browsers (touch + keyboard + mouse)
- Display time-series data with responsive design
- Integrate with React + TypeScript + CSS design tokens
- Provide excellent user experience for all users (inclusive design)

### Current State (Phase 2)
- **Recharts** is currently in use for Phase 2 prototype
- Minimal frontend implementation (easy to migrate now)
- No accessibility work has been done yet

### User Requirements

From user discussion (2026-01-03):
> "we're building an app for desktop or ipad use, both using a browser"
> "we really do want to provide for a great user experience for all users, with true inclusive design"
> "we haven't really built any of the front end yet, so this is the best time to make these decisions"

### Inclusive Design Standards

From [docs/standards/ACCESSIBILITY.md](../standards/ACCESSIBILITY.md):
- Charts must have ARIA labels and descriptions
- Keyboard navigation for data points
- Alternative data table view for screen readers
- Color-blind friendly palettes
- Sufficient color contrast (4.5:1 minimum)

---

## Decision

We will **migrate from Recharts to Victory Charts** for data visualization.

---

## Rationale

### Comparison with Alternatives

| Feature | Victory Charts | Recharts (Current) | Tremor |
|---------|---------------|-------------------|---------|
| **Accessibility** | ✅ Built-in ARIA support | ❌ Manual implementation | ❌ Inherits Recharts limitations |
| **WCAG 2.2 Support** | ✅ Good baseline | ❌ None (DIY) | ❌ None (DIY) |
| **Keyboard Navigation** | ✅ VictoryVoronoi built-in | ❌ Manual | ❌ Manual |
| **Cross-Platform** | ✅ Web + React Native | ❌ Web-only | ❌ Web-only |
| **TypeScript Support** | ✅ Excellent | ✅ Good | ✅ Good |
| **Bundle Size** | ✅ ~50KB gzipped | ✅ ~45KB gzipped | ⚠️ ~100KB+ (includes extras) |
| **Performance** | ✅ SVG + Canvas options | ✅ SVG only | ✅ SVG (via Recharts) |
| **Customization** | ✅ Full control | ✅ Full control | ❌ Opinionated design |
| **iPad/Touch Support** | ✅ VictoryVoronoi hover | ⚠️ Basic | ⚠️ Basic |
| **Learning Curve** | ✅ Similar to Recharts | ✅ Low | ✅ Very low |
| **Migration Effort** | ✅ Low (1-2 days) | N/A (current) | ⚠️ Medium |

### Key Benefits

1. **Built-in Accessibility Support**
   ```typescript
   // Victory includes VictoryAccessibleSVG for ARIA support
   import { VictoryChart, VictoryLine, VictoryVoronoiContainer } from 'victory';

   <VictoryChart
     containerComponent={
       <VictoryVoronoiContainer
         voronoiDimension="x"
         labels={({ datum }) => `${datum.time}: ${datum.temp}°F`}
         labelComponent={
           <VictoryTooltip
             flyoutStyle={{ fill: "white", stroke: "#333" }}
             style={{ fill: "#333", fontSize: 14 }}
           />
         }
       />
     }
   >
     <VictoryLine
       data={data}
       x="time"
       y="temperature"
       style={{
         data: { stroke: "#3b82f6", strokeWidth: 2 }
       }}
     />
   </VictoryChart>
   ```

2. **Keyboard Navigation & Screen Reader Support**
   - VictoryVoronoi provides automatic keyboard navigation
   - Tab to enter chart, arrow keys to navigate data points
   - Screen reader announces data point values automatically
   - ARIA labels and descriptions included by default

3. **Cross-Platform Future-Proofing**
   - Victory works identically on React and React Native
   - If mobile becomes native app (Phase 4+), charts are reusable
   - Same API, same components, same behavior

4. **Touch Optimization for iPad**
   - VictoryVoronoiContainer handles touch, mouse, and pen input
   - Larger touch targets for data point interaction
   - Smooth panning and zooming (VictoryZoomContainer)

5. **Performance Options**
   ```typescript
   // Victory supports both SVG and Canvas rendering
   import { VictoryChart, VictoryLine, VictoryCanvas } from 'victory';

   // Use Canvas for large datasets (>1000 points)
   <VictoryChart containerComponent={<VictoryCanvas />}>
     <VictoryLine data={largeDataset} />
   </VictoryChart>
   ```

6. **Similar API to Recharts (Easy Migration)**
   ```typescript
   // Recharts (current)
   <ResponsiveContainer width="100%" height={400}>
     <LineChart data={data}>
       <XAxis dataKey="time" />
       <YAxis />
       <Line dataKey="temperature" stroke="#3b82f6" />
     </LineChart>
   </ResponsiveContainer>

   // Victory (after migration)
   <VictoryChart width={600} height={400}>
     <VictoryAxis />
     <VictoryAxis dependentAxis />
     <VictoryLine
       data={data}
       x="time"
       y="temperature"
       style={{ data: { stroke: "#3b82f6" } }}
     />
   </VictoryChart>
   ```

### Alignment with Inclusive Design Standards

From [docs/standards/ACCESSIBILITY.md](../standards/ACCESSIBILITY.md):

| Requirement | Victory Support |
|-------------|-----------------|
| **ARIA Labels** | ✅ Built-in via VictoryAccessibleSVG |
| **Keyboard Navigation** | ✅ VictoryVoronoi provides arrow key navigation |
| **Screen Reader** | ✅ Automatic announcements of data points |
| **Data Table Alternative** | ⚠️ Must build manually (same as Recharts) |
| **Color Contrast** | ✅ Customizable, supports WCAG palettes |
| **Touch Targets** | ✅ VictoryVoronoi increases hit areas |

### Why Not Recharts?

Recharts is a solid library, but:
- **Accessibility is manual work** - No built-in ARIA support, keyboard navigation, or screen reader features
- **Web-only** - If mobile becomes native, need to rebuild charts
- **Accessibility debt** - Every chart requires custom ARIA wrapper, keyboard handlers, and screen reader logic

**Effort comparison:**
- **Keep Recharts:** Low migration cost (none), but HIGH ongoing accessibility maintenance
- **Migrate to Victory:** Low-medium migration cost (1-2 days), but LOW ongoing accessibility maintenance

### Why Not Tremor?

Tremor is pre-built dashboard charts, but:
- **Opinionated design** - All charts look "Tremor-ish"
- **Inherits Recharts limitations** - Built on Recharts, same accessibility gaps
- **Limited flexibility** - Can't customize beyond Tremor's design system
- **Conflicts with design goals** - We chose React Aria for flexibility, Tremor removes that

---

## Consequences

### Positive

- ✅ **Better accessibility baseline** - Reduces accessibility tech debt significantly
- ✅ **WCAG 2.2 compliant** - Built-in ARIA support for screen readers and keyboard users
- ✅ **Future-proof** - React Native support if mobile becomes native app
- ✅ **iPad optimized** - Touch, keyboard, and screen reader support
- ✅ **Performance options** - Canvas rendering for large datasets
- ✅ **Maintained by Formidable Labs** - Production-grade library used by major companies
- ✅ **Similar API to Recharts** - Easy to learn, minimal migration effort

### Negative

- ⚠️ **Migration required** - 1-2 days to convert existing Recharts components
- ⚠️ **Smaller community** - Less Stack Overflow content vs Recharts
- ⚠️ **Still need data table alternative** - Screen reader users need tabular data view

### Neutral

- Victory is slightly larger bundle (~5KB more gzipped) but includes accessibility features
- Different styling API (inline styles vs CSS classes) but works with TailwindCSS

### Mitigation Strategies

**Migration Effort:**
- Current frontend is minimal (Phase 2 prototype only)
- ~3-5 chart components to migrate
- Victory API is similar to Recharts (1-2 days work)

**Community Support:**
- Victory has excellent documentation with live examples
- Formidable Labs provides commercial support
- Leverage ChatGPT/Claude for Victory pattern generation

**Data Table Alternative:**
- Build reusable `<ChartWithTable>` component
- Provide `<details>` toggle for screen reader users
- Use same pattern across all charts

---

## Implementation

### Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   └── charts/                # Reusable Victory chart components
│   │       ├── TemperatureChart.tsx
│   │       ├── HumidityChart.tsx
│   │       ├── PressureChart.tsx
│   │       ├── WindSpeedChart.tsx
│   │       └── ChartWithTable.tsx  # Accessible wrapper with data table
```

### Sample Component (Accessible Temperature Chart)

```typescript
// src/components/charts/TemperatureChart.tsx
import {
  VictoryChart,
  VictoryLine,
  VictoryAxis,
  VictoryVoronoiContainer,
  VictoryTooltip,
  VictoryTheme
} from 'victory';

interface TemperatureChartProps {
  data: Array<{ time: Date; temperature: number }>;
  width?: number;
  height?: number;
}

export function TemperatureChart({ data, width = 600, height = 400 }: TemperatureChartProps) {
  return (
    <figure>
      <figcaption id="temp-chart-title" className="text-lg font-semibold mb-2">
        Temperature Trends - Last 24 Hours
      </figcaption>

      <div
        role="img"
        aria-labelledby="temp-chart-title"
        aria-describedby="temp-chart-desc"
      >
        <VictoryChart
          width={width}
          height={height}
          theme={VictoryTheme.material}
          containerComponent={
            <VictoryVoronoiContainer
              voronoiDimension="x"
              labels={({ datum }) =>
                `${datum.time.toLocaleTimeString()}: ${datum.temperature}°F`
              }
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
            tickFormat={(t) => new Date(t).toLocaleTimeString([], { hour: '2-digit' })}
            style={{
              tickLabels: { fill: "#64748b", fontSize: 12 }
            }}
          />
          <VictoryAxis
            dependentAxis
            tickFormat={(t) => `${t}°F`}
            style={{
              tickLabels: { fill: "#64748b", fontSize: 12 }
            }}
          />
          <VictoryLine
            data={data}
            x="time"
            y="temperature"
            style={{
              data: { stroke: "#3b82f6", strokeWidth: 2 }
            }}
          />
        </VictoryChart>
      </div>

      <p id="temp-chart-desc" className="sr-only">
        Line chart showing temperature ranging from{' '}
        {Math.min(...data.map(d => d.temperature))}°F to{' '}
        {Math.max(...data.map(d => d.temperature))}°F{' '}
        over the last 24 hours.
      </p>

      {/* Data table alternative for screen readers */}
      <details className="mt-4">
        <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
          View data as table
        </summary>
        <table className="mt-2 min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">
                Time
              </th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">
                Temperature (°F)
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.map((point, idx) => (
              <tr key={idx}>
                <td className="px-4 py-2 text-sm text-gray-900">
                  {point.time.toLocaleString()}
                </td>
                <td className="px-4 py-2 text-sm text-gray-900">
                  {point.temperature}°F
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  );
}
```

### Dependencies

```json
{
  "dependencies": {
    "victory": "^37.0.0",
    "victory-core": "^37.0.0",
    "victory-canvas": "^37.0.0"
  },
  "devDependencies": {
    "@types/victory": "^37.0.0"
  }
}
```

### Migration Steps

1. **Install Victory**
   ```bash
   npm install victory
   npm install -D @types/victory
   ```

2. **Remove Recharts**
   ```bash
   npm uninstall recharts
   ```

3. **Convert Chart Components** (estimated 1-2 days)
   - Temperature chart
   - Humidity chart
   - Pressure chart
   - Wind speed chart
   - Multi-metric dashboard

4. **Add Accessibility Wrappers**
   - ARIA labels and descriptions
   - Data table alternatives
   - Keyboard navigation instructions

5. **Test Accessibility**
   ```bash
   npm run test:a11y  # axe-core tests
   # Manual: Keyboard navigation, NVDA, VoiceOver
   ```

---

## Alternatives Considered

### 1. Keep Recharts
- **Pros:** No migration cost, familiar API, large community
- **Cons:** All accessibility work is manual, web-only, ongoing tech debt
- **Verdict:** SHORT-term gain, LONG-term pain (accessibility maintenance burden)

### 2. Tremor
- **Pros:** Fastest development, pre-built dashboard charts
- **Cons:** Opinionated design, inherits Recharts accessibility gaps, limited flexibility
- **Verdict:** Conflicts with React Aria decision (chose flexibility over speed)

### 3. Chart.js (via react-chartjs-2)
- **Pros:** Very popular, canvas-based (good performance)
- **Cons:** Poor accessibility, not React-native, imperative API (not declarative)
- **Verdict:** Accessibility worse than Recharts

### 4. D3.js (custom charts)
- **Pros:** Maximum control and flexibility
- **Cons:** Extremely steep learning curve, months of work, high accessibility risk
- **Verdict:** Over-engineered for this use case

---

## Validation

### Success Criteria
- [ ] All charts migrated from Recharts to Victory (1-2 days)
- [ ] Charts pass axe-core accessibility tests (0 violations)
- [ ] Keyboard navigation works (Tab to enter, arrow keys to navigate points)
- [ ] Screen reader announces data points correctly (NVDA, VoiceOver)
- [ ] Data table alternative provided for all charts
- [ ] Color contrast meets WCAG 2.2 Level AA (4.5:1 minimum)
- [ ] Touch targets work on iPad (no precision required)

### Testing Strategy
```bash
# Automated accessibility testing
npm run test:a11y  # axe-core + jest-axe

# Lighthouse CI (must pass accessibility score ≥95)
npm run lighthouse

# Manual testing
# 1. Keyboard-only navigation (Tab, Arrow keys, Escape)
# 2. NVDA screen reader on Windows
# 3. VoiceOver on iPad
# 4. Color contrast validation (WebAIM Contrast Checker)
# 5. Touch interaction on iPad (tooltips, zoom, pan)
```

---

## References

- [Victory Documentation](https://commerce.nearform.com/open-source/victory/)
- [Victory Accessibility Guide](https://commerce.nearform.com/open-source/victory/docs/victory-accessibility)
- [VictoryVoronoiContainer (keyboard nav)](https://commerce.nearform.com/open-source/victory/docs/victory-voronoi-container)
- [WCAG 2.2 Guidelines](https://www.w3.org/TR/WCAG22/)
- [Accessibility Standards](../standards/ACCESSIBILITY.md)

---

## Document Changelog

- **2026-01-03:** Decision made during Phase 3 planning (Web UI architecture)
- **2026-01-03:** Formalized as ADR-007
