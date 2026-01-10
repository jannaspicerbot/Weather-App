# Weather App Frontend

React + TypeScript dashboard for visualizing weather data from your Ambient Weather station.

## 🎨 Tech Stack

- **Framework:** React 18 with hooks
- **Language:** TypeScript 5+ (strict mode)
- **Build Tool:** Vite 5 (fast HMR, optimized builds)
- **Charts:** Victory Charts (accessible, theme-aware data visualization)
- **Components:** React Aria (WCAG 2.2 AA accessible component hooks)
- **Styling:** CSS Custom Properties (semantic design tokens)
- **Routing:** React Router v6 (future)
- **State:** React hooks (useState, useReducer, Context API)

## 🚀 Quick Start

### Development Server

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# The frontend expects the backend API at http://localhost:8000
# Make sure the FastAPI backend is running first
```

### Build for Production

```bash
# Create optimized production build
npm run build

# Preview production build locally
npm run preview

# The built files are in dist/ directory
```

### Code Quality

```bash
# Lint TypeScript code
npm run lint

# Type check without building
npm run type-check

# Format code (if Prettier is configured)
npm run format
```

## 📁 Project Structure

```
web/
├── src/
│   ├── components/         # React components
│   │   ├── charts/         # Chart components (Victory Charts)
│   │   ├── layout/         # Layout components (Header, Footer)
│   │   └── ui/             # UI components (Button, Card, etc.)
│   ├── services/           # API client and data fetching
│   │   └── api.ts          # Backend API integration
│   ├── types/              # TypeScript type definitions
│   │   └── weather.ts      # Weather data types
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   ├── App.tsx             # Main application component
│   ├── main.tsx            # Application entry point
│   └── index.css           # Global styles (design tokens)
├── public/                 # Static assets
├── dist/                   # Built files (generated, git-ignored)
├── index.html              # HTML entry point
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
├── tsconfig.node.json      # TypeScript config for Vite
└── package.json            # Dependencies and scripts
```

## 🎨 Design System

The Weather App uses a custom design system with semantic design tokens:

- **Color Palette:** See [../docs/design/design-tokens.md](../docs/design/design-tokens.md)
- **Typography:** System fonts with responsive scaling
- **Spacing:** Base-4 spacing scale (4px grid via CSS custom properties)
- **Accessibility:** WCAG 2.2 Level AA compliance

### Theme Support

The app supports both light and dark themes that respect the system preference:

The app automatically respects the user's system preference for light or dark mode using the CSS `prefers-color-scheme` media query. This follows WCAG guidelines for respecting user preferences.

```css
/* In index.css - theme switching is automatic via CSS custom properties */
:root {
  --color-bg-primary: #FAFBFC;    /* Light mode background */
  --color-text-primary: #0F1419;  /* Light mode text */
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #0F1419;  /* Dark mode background */
    --color-text-primary: #E8EBED; /* Dark mode text */
  }
}

/* Components use semantic classes - theme changes automatically */
.dashboard-container {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}
```

## 🌐 API Integration

The frontend communicates with the FastAPI backend via REST API.

### API Client

```typescript
// src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function fetchLatestWeather(): Promise<WeatherReading> {
  const response = await fetch(`${API_BASE_URL}/api/weather/latest`)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  return await response.json()
}
```

### Environment Variables

Create a `.env.local` file for local development:

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000

# Other environment variables (if needed)
```

**Note:** Environment variables must be prefixed with `VITE_` to be accessible in the frontend.

## 📊 Charts & Visualizations

The app uses **Victory Charts** for accessible, theme-aware data visualization.

### Why Victory Charts?

- ✅ **Accessible** - WCAG 2.2 Level AA compliant out of the box
- ✅ **Theme-Aware** - Easily customizable with design tokens
- ✅ **Performant** - Handles large datasets efficiently
- ✅ **React Native** - Same API works on web and mobile

See [ADR-007: Victory Charts](../docs/architecture/decisions/007-victory-charts.md) for the full rationale.

### Example Chart Component

```typescript
import { VictoryChart, VictoryLine, VictoryAxis, VictoryTheme } from 'victory'

export function TemperatureChart({ data }: { data: WeatherReading[] }) {
  return (
    <VictoryChart theme={VictoryTheme.material}>
      <VictoryAxis
        label="Time"
        tickFormat={(t) => new Date(t).toLocaleTimeString()}
      />
      <VictoryAxis
        dependentAxis
        label="Temperature (°F)"
      />
      <VictoryLine
        data={data}
        x="date"
        y="tempf"
        style={{
          data: { stroke: "#ef4444", strokeWidth: 2 }
        }}
      />
    </VictoryChart>
  )
}
```

## ♿ Accessibility

The Weather App follows **WCAG 2.2 Level AA** accessibility standards.

### Accessible Components

Use **React Aria** hooks for accessible component patterns:

```typescript
import { useButton } from 'react-aria'

function Button(props) {
  const ref = useRef()
  const { buttonProps } = useButton(props, ref)

  return (
    <button {...buttonProps} ref={ref} className="btn">
      {props.children}
    </button>
  )
}
```

### Accessibility Checklist

- ✅ Keyboard navigation (Tab, Enter, Space, Arrow keys)
- ✅ Screen reader support (ARIA labels, roles, live regions)
- ✅ Color contrast (4.5:1 for text, 3:1 for UI components)
- ✅ Focus indicators (visible focus outlines)
- ✅ Alt text for images and icons
- ✅ Semantic HTML (headings, landmarks, lists)

See [../docs/design/inclusive-design.md](../docs/design/inclusive-design.md) for complete accessibility guidelines.

## 🧪 Testing

### Unit Tests (Vitest)

```bash
# Run unit tests
npm test

# Run tests in watch mode
npm test -- --watch

# Generate coverage report
npm test -- --coverage
```

### Component Tests (React Testing Library)

```typescript
import { render, screen } from '@testing-library/react'
import { TemperatureChart } from './TemperatureChart'

test('renders temperature chart with data', () => {
  const data = [
    { date: '2024-01-01T12:00:00', tempf: 72.5 },
    { date: '2024-01-01T13:00:00', tempf: 73.2 }
  ]

  render(<TemperatureChart data={data} />)

  expect(screen.getByLabelText('Temperature (°F)')).toBeInTheDocument()
})
```

### Accessibility Tests (axe-core)

```bash
# Run accessibility tests
npm run test:a11y

# CI/CD runs these automatically
```

## 🔧 Configuration

### TypeScript

The project uses **strict TypeScript** for type safety:

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### ESLint

Production-ready ESLint configuration with type-aware rules:

```javascript
// eslint.config.js
export default {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended-type-checked',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended'
  ],
  parserOptions: {
    project: ['./tsconfig.json', './tsconfig.node.json']
  }
}
```

### Vite

Vite configuration with path aliases and optimizations:

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@services': '/src/services',
      '@types': '/src/types'
    }
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['victory']
        }
      }
    }
  }
})
```

## 📖 Documentation

For complete documentation, see:

- **[Frontend Guidelines](../docs/design/frontend-guidelines.md)** - Component structure, patterns, best practices
- **[Design Token System](../docs/design/design-tokens.md)** - Color palette, typography, spacing
- **[Inclusive Design](../docs/design/inclusive-design.md)** - Accessibility standards (WCAG 2.2 AA)
- **[API Reference](../docs/technical/api-reference.md)** - Backend API endpoints and schemas
- **[Architecture Overview](../docs/architecture/overview.md)** - System design and data flow

## 🤝 Contributing

When contributing to the frontend:

1. **Follow the design system** - Use design tokens, not hard-coded values
2. **Write accessible components** - Use React Aria hooks and ARIA attributes
3. **Type everything** - No `any` types, use strict TypeScript
4. **Test your components** - Write unit and accessibility tests
5. **Document complex logic** - Add JSDoc comments for exported functions

See [../docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) for complete contribution guidelines.

## 🐛 Troubleshooting

**"Cannot connect to backend API"**
- Ensure the FastAPI backend is running at `http://localhost:8000`
- Check CORS configuration in the backend
- Verify `VITE_API_URL` environment variable

**"Module not found" errors**
- Run `npm install` to install dependencies
- Check import paths (use `@/` aliases if configured)
- Restart the Vite dev server

**TypeScript errors**
- Run `npm run type-check` to see all type errors
- Ensure all dependencies have type definitions (`@types/*` packages)
- Check `tsconfig.json` configuration

**Build fails**
- Clear the Vite cache: `rm -rf node_modules/.vite`
- Delete `dist/` and rebuild: `rm -rf dist && npm run build`
- Check for circular dependencies

## 📦 Dependencies

### Production Dependencies

- `react` & `react-dom` - UI framework
- `victory` - Charting library
- `react-aria` - Accessible component hooks

### Development Dependencies

- `vite` - Build tool
- `typescript` - Type safety
- `@vitejs/plugin-react` - React plugin for Vite
- `eslint` - Code linting
- `vitest` - Unit testing
- `@testing-library/react` - Component testing

See [package.json](package.json) for the complete list.

## 🔗 Resources

- **React Documentation:** https://react.dev/
- **TypeScript Documentation:** https://www.typescriptlang.org/docs/
- **Vite Documentation:** https://vitejs.dev/
- **Victory Charts:** https://commerce.nearform.com/open-source/victory/
- **React Aria:** https://react-spectrum.adobe.com/react-aria/
- **CSS Custom Properties:** https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties

---

**Part of the Weather App project** - See [../README.md](../README.md) for the full project documentation.
