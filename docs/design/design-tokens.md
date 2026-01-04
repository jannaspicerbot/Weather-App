# Design Token System

## Overview

The Weather Dashboard uses a **semantic design token system** that completely decouples colors from implementation. This means:

- ✅ **No hard-coded colors anywhere in the codebase**
- ✅ **Change entire palette by editing one file**
- ✅ **User-selectable palettes** (future feature)
- ✅ **Automatic light/dark theme support**
- ✅ **Type-safe with TypeScript**

## Architecture

```
Raw Color Palette (JSON/CSS)
         ↓
Semantic Tokens (e.g., "color-water", "color-text-primary")
         ↓
Component Usage (never references hex codes)
```

**Key principle:** Components use semantic names like `--color-water`, never `#3B6B8F`

---

## Implementation Approach

### Option 1: CSS Custom Properties (Recommended for MVP)

**Pros:**
- Native browser support (no build step)
- Works with any framework (React, vanilla JS)
- Hot-reload friendly
- Easy to override per-component
- Automatic dark mode with `@media (prefers-color-scheme: dark)`

**Cons:**
- Less type-safety (but TypeScript types can help)
- No compile-time validation

### Option 2: TypeScript/JavaScript Tokens

**Pros:**
- Type-safe
- Compile-time validation
- Can be used in JS logic
- Better IDE autocomplete

**Cons:**
- Requires build step
- More complex theme switching

### Recommendation: **Hybrid Approach**
- Use CSS Custom Properties for theming
- Export TypeScript types for autocomplete/validation
- Best of both worlds

---

## File Structure

```
src/
├── styles/
│   ├── tokens/
│   │   ├── palettes.json          # All palette definitions
│   │   ├── tokens.css             # Semantic token mappings
│   │   └── themes.css             # Light/dark theme variables
│   ├── global.css                 # Global styles using tokens
│   └── index.css                  # Entry point
├── types/
│   └── theme.types.ts             # TypeScript types
└── utils/
    └── theme.ts                   # Theme switching logic
```

---

## Palette Definitions

### palettes.json

This file contains ALL palette options. Changing the active palette is just changing which one is loaded.

```json
{
  "soft-trust": {
    "name": "Soft Trust",
    "description": "Desaturated, calming, best for extended viewing",
    "light": {
      "background": "#FAFBFC",
      "surface": "#FFFFFF",
      "primary": "#3B6B8F",
      "secondary": "#557A5C",
      "accent": "#4A8A9E",
      "textPrimary": "#0F1419",
      "textSecondary": "#5A5A5A",
      "border": "#E8EBED",
      "grid": "#D4D8DD"
    },
    "dark": {
      "background": "#0F1419",
      "surface": "#1C2128",
      "primary": "#7BA3C0",
      "secondary": "#8CB896",
      "accent": "#6EB5CC",
      "textPrimary": "#F6F8FA",
      "textSecondary": "#D0D0D0",
      "border": "#2D333B",
      "grid": "#23292F"
    }
  },
  "serene-clarity": {
    "name": "Serene Clarity",
    "description": "Balanced, professional, high clarity",
    "light": {
      "background": "#F8FAFB",
      "surface": "#FFFFFF",
      "primary": "#0066CC",
      "secondary": "#2D7A4A",
      "accent": "#0099AA",
      "textPrimary": "#1A1F2E",
      "textSecondary": "#666666",
      "border": "#E1E4E8",
      "grid": "#D0D5DD"
    },
    "dark": {
      "background": "#1A1F2E",
      "surface": "#242B3D",
      "primary": "#66B2FF",
      "secondary": "#7EC983",
      "accent": "#4DB8D2",
      "textPrimary": "#F8FAFB",
      "textSecondary": "#CCCCCC",
      "border": "#3A4556",
      "grid": "#2F3947"
    }
  },
  "deep-confidence": {
    "name": "Deep Confidence",
    "description": "Highest contrast, maximum clarity",
    "light": {
      "background": "#FFFFFF",
      "surface": "#FAFBFC",
      "primary": "#0052A3",
      "secondary": "#1B7A3A",
      "accent": "#00A3CC",
      "textPrimary": "#000000",
      "textSecondary": "#4A4A4A",
      "border": "#E5E7EB",
      "grid": "#CBD5E1"
    },
    "dark": {
      "background": "#0A0E27",
      "surface": "#141A35",
      "primary": "#70B3FF",
      "secondary": "#5FD974",
      "accent": "#3FD9FF",
      "textPrimary": "#FFFFFF",
      "textSecondary": "#E8E8E8",
      "border": "#1F2847",
      "grid": "#293454"
    }
  },
  "adaptive-nature": {
    "name": "Adaptive Nature",
    "description": "Progressive gradients for weather maps",
    "light": {
      "background": "#F5F7FA",
      "surface": "#FFFFFF",
      "primary": "#1E90FF",
      "secondary": "#4CAF50",
      "accent": "#87CEEB",
      "textPrimary": "#0F172A",
      "textSecondary": "#64748B",
      "border": "#E2E8F0",
      "grid": "#CBD5E1"
    },
    "dark": {
      "background": "#141829",
      "surface": "#1E2238",
      "primary": "#6CB3FF",
      "secondary": "#7BDEBB",
      "accent": "#4A9FBF",
      "textPrimary": "#F8FAFC",
      "textSecondary": "#CBD5E1",
      "border": "#293454",
      "grid": "#1E2844"
    }
  },
  "accessible-harmony": {
    "name": "Accessible Harmony",
    "description": "WCAG AAA compliant, maximum accessibility",
    "light": {
      "background": "#FFFFFF",
      "surface": "#FAFAFA",
      "primary": "#003366",
      "secondary": "#2D5A3D",
      "accent": "#006688",
      "textPrimary": "#000000",
      "textSecondary": "#333333",
      "border": "#CCCCCC",
      "grid": "#DDDDDD"
    },
    "dark": {
      "background": "#000000",
      "surface": "#0A0A0A",
      "primary": "#99CCFF",
      "secondary": "#88DD99",
      "accent": "#44CCFF",
      "textPrimary": "#FFFFFF",
      "textSecondary": "#FFFFFF",
      "border": "#444444",
      "grid": "#333333"
    }
  }
}
```

---

## Semantic Token Mapping

### tokens.css

This is where the magic happens. Components reference semantic names, which map to palette colors.

```css
:root {
  /* === SEMANTIC COLOR TOKENS === */

  /* Backgrounds */
  --color-bg-primary: var(--palette-background);
  --color-bg-secondary: var(--palette-surface);
  --color-bg-elevated: var(--palette-surface);

  /* Weather-specific semantic colors */
  --color-water: var(--palette-primary);      /* Temperature, rain, humidity */
  --color-growth: var(--palette-secondary);   /* Wind, air quality, nature metrics */
  --color-interactive: var(--palette-accent); /* Buttons, links, hover states */

  /* Text */
  --color-text-primary: var(--palette-text-primary);
  --color-text-secondary: var(--palette-text-secondary);
  --color-text-on-primary: var(--palette-background);
  --color-text-on-secondary: var(--palette-background);

  /* Borders & Dividers */
  --color-border: var(--palette-border);
  --color-border-subtle: var(--palette-grid);
  --color-divider: var(--palette-border);

  /* Chart-specific */
  --chart-line-water: var(--palette-primary);
  --chart-line-growth: var(--palette-secondary);
  --chart-fill-water: var(--palette-primary);
  --chart-fill-growth: var(--palette-secondary);
  --chart-grid: var(--palette-grid);
  --chart-axis: var(--palette-text-secondary);

  /* Opacity variants (for fills, hovers, etc.) */
  --opacity-subtle: 0.1;
  --opacity-medium: 0.15;
  --opacity-strong: 0.25;

  /* Status colors (not palette-dependent) */
  --color-success: #2D7A4A;
  --color-warning: #FFA726;
  --color-error: #D32F2F;
  --color-info: var(--palette-accent);
}

/* Convert palette colors to CSS vars with alpha channel support */
:root {
  /* Water color with alpha variants */
  --color-water-rgb: var(--palette-primary-rgb);
  --color-water-10: rgba(var(--color-water-rgb), 0.1);
  --color-water-15: rgba(var(--color-water-rgb), 0.15);
  --color-water-25: rgba(var(--color-water-rgb), 0.25);

  /* Growth color with alpha variants */
  --color-growth-rgb: var(--palette-secondary-rgb);
  --color-growth-10: rgba(var(--color-growth-rgb), 0.1);
  --color-growth-15: rgba(var(--color-growth-rgb), 0.15);
  --color-growth-25: rgba(var(--color-growth-rgb), 0.25);
}
```

---

## Theme Loading

### themes.css

This file loads the active palette and handles light/dark modes.

```css
/* Default palette: Soft Trust */
:root {
  /* Light theme (default) */
  --palette-background: #FAFBFC;
  --palette-surface: #FFFFFF;
  --palette-primary: #3B6B8F;
  --palette-primary-rgb: 59, 107, 143;
  --palette-secondary: #557A5C;
  --palette-secondary-rgb: 85, 122, 92;
  --palette-accent: #4A8A9E;
  --palette-text-primary: #0F1419;
  --palette-text-secondary: #5A5A5A;
  --palette-border: #E8EBED;
  --palette-grid: #D4D8DD;
}

/* Dark theme (system preference) */
@media (prefers-color-scheme: dark) {
  :root {
    --palette-background: #0F1419;
    --palette-surface: #1C2128;
    --palette-primary: #7BA3C0;
    --palette-primary-rgb: 123, 163, 192;
    --palette-secondary: #8CB896;
    --palette-secondary-rgb: 140, 184, 150;
    --palette-accent: #6EB5CC;
    --palette-text-primary: #F6F8FA;
    --palette-text-secondary: #D0D0D0;
    --palette-border: #2D333B;
    --palette-grid: #23292F;
  }
}

/* Manual dark mode override */
[data-theme="dark"] {
  --palette-background: #0F1419;
  --palette-surface: #1C2128;
  --palette-primary: #7BA3C0;
  --palette-primary-rgb: 123, 163, 192;
  --palette-secondary: #8CB896;
  --palette-secondary-rgb: 140, 184, 150;
  --palette-accent: #6EB5CC;
  --palette-text-primary: #F6F8FA;
  --palette-text-secondary: #D0D0D0;
  --palette-border: #2D333B;
  --palette-grid: #23292F;
}

/* Manual light mode override */
[data-theme="light"] {
  --palette-background: #FAFBFC;
  --palette-surface: #FFFFFF;
  --palette-primary: #3B6B8F;
  --palette-primary-rgb: 59, 107, 143;
  --palette-secondary: #557A5C;
  --palette-secondary-rgb: 85, 122, 92;
  --palette-accent: #4A8A9E;
  --palette-text-primary: #0F1419;
  --palette-text-secondary: #5A5A5A;
  --palette-border: #E8EBED;
  --palette-grid: #D4D8DD;
}

/* Palette-specific overrides (user selection) */
[data-palette="serene-clarity"] {
  /* Light mode */
  --palette-primary: #0066CC;
  --palette-primary-rgb: 0, 102, 204;
  --palette-secondary: #2D7A4A;
  --palette-secondary-rgb: 45, 122, 74;
  --palette-accent: #0099AA;
  /* ... rest of palette */
}

[data-palette="serene-clarity"][data-theme="dark"],
[data-palette="serene-clarity"]:where(:not([data-theme])) {
  @media (prefers-color-scheme: dark) {
    --palette-primary: #66B2FF;
    --palette-primary-rgb: 102, 178, 255;
    --palette-secondary: #7EC983;
    --palette-secondary-rgb: 126, 201, 131;
    --palette-accent: #4DB8D2;
    /* ... rest of dark palette */
  }
}
```

---

## Usage Examples

### React Component (Using Tokens)

```tsx
// ❌ NEVER do this (hard-coded color)
const TemperatureChart = () => (
  <div style={{ backgroundColor: '#3B6B8F' }}>
    <VictoryLine style={{ data: { stroke: '#3B6B8F' } }} />
  </div>
);

// ✅ ALWAYS do this (semantic token)
const TemperatureChart = () => (
  <div style={{ backgroundColor: 'var(--color-water)' }}>
    <VictoryLine
      style={{
        data: { stroke: 'var(--chart-line-water)' }
      }}
    />
  </div>
);

// ✅ Better: Use CSS classes
const TemperatureChart = () => (
  <div className="chart-container">
    <VictoryLine
      style={{
        data: { stroke: 'var(--chart-line-water)' }
      }}
    />
  </div>
);

// CSS:
// .chart-container {
//   background-color: var(--color-bg-primary);
//   border: 1px solid var(--color-border);
// }
```

### Victory Charts Theme

```typescript
// src/utils/chartTheme.ts
export const weatherChartTheme = {
  axis: {
    style: {
      axis: {
        stroke: 'var(--color-border)'
      },
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
```

### TypeScript Types (Autocomplete Support)

```typescript
// src/types/theme.types.ts
export type ColorToken =
  | 'color-bg-primary'
  | 'color-bg-secondary'
  | 'color-water'
  | 'color-growth'
  | 'color-interactive'
  | 'color-text-primary'
  | 'color-text-secondary'
  | 'color-border'
  | 'chart-line-water'
  | 'chart-line-growth';

export type Palette =
  | 'soft-trust'
  | 'serene-clarity'
  | 'deep-confidence'
  | 'adaptive-nature'
  | 'accessible-harmony';

export type Theme = 'light' | 'dark' | 'auto';

export interface ThemeConfig {
  palette: Palette;
  theme: Theme;
}

// Helper function with TypeScript autocomplete
export const useColorToken = (token: ColorToken): string => {
  return `var(--${token})`;
};
```

---

## Theme Switching Logic

### src/utils/theme.ts

```typescript
export class ThemeManager {
  private static STORAGE_KEY = 'weather-app-theme';

  static setTheme(theme: Theme): void {
    const html = document.documentElement;

    if (theme === 'auto') {
      html.removeAttribute('data-theme');
      localStorage.removeItem(`${this.STORAGE_KEY}-mode`);
    } else {
      html.setAttribute('data-theme', theme);
      localStorage.setItem(`${this.STORAGE_KEY}-mode`, theme);
    }
  }

  static setPalette(palette: Palette): void {
    const html = document.documentElement;
    html.setAttribute('data-palette', palette);
    localStorage.setItem(`${this.STORAGE_KEY}-palette`, palette);
  }

  static getTheme(): Theme {
    const stored = localStorage.getItem(`${this.STORAGE_KEY}-mode`);
    return (stored as Theme) || 'auto';
  }

  static getPalette(): Palette {
    const stored = localStorage.getItem(`${this.STORAGE_KEY}-palette`);
    return (stored as Palette) || 'soft-trust';
  }

  static initialize(): void {
    this.setTheme(this.getTheme());
    this.setPalette(this.getPalette());
  }
}

// Initialize on app load
ThemeManager.initialize();
```

---

## How to Change Palettes

### 1. Change Default Palette (Developer)

**Edit one file:** `src/styles/tokens/themes.css`

Change line 2:
```css
/* Change from: */
:root { /* Soft Trust colors */ }

/* To: */
:root { /* Serene Clarity colors */ }
```

**Result:** Entire app updates instantly. Zero code changes needed.

### 2. User-Selectable Palette (Future Feature)

```tsx
// Settings component
const ThemeSettings = () => {
  const [palette, setPalette] = useState<Palette>('soft-trust');

  const handlePaletteChange = (newPalette: Palette) => {
    ThemeManager.setPalette(newPalette);
    setPalette(newPalette);
  };

  return (
    <select value={palette} onChange={(e) => handlePaletteChange(e.target.value as Palette)}>
      <option value="soft-trust">Soft Trust (Calm)</option>
      <option value="serene-clarity">Serene Clarity (Balanced)</option>
      <option value="deep-confidence">Deep Confidence (Bold)</option>
      <option value="adaptive-nature">Adaptive Nature (Gradients)</option>
      <option value="accessible-harmony">Accessible Harmony (AAA)</option>
    </select>
  );
};
```

### 3. Dynamic Palette Loading

```typescript
// Advanced: Load palettes from API/JSON
async function loadPalette(paletteId: string) {
  const palettes = await fetch('/palettes.json').then(r => r.json());
  const palette = palettes[paletteId];

  // Inject CSS variables
  const root = document.documentElement;
  const theme = document.documentElement.getAttribute('data-theme') || 'light';
  const colors = palette[theme];

  Object.entries(colors).forEach(([key, value]) => {
    root.style.setProperty(`--palette-${key}`, value);
  });
}
```

---

## Benefits of This Approach

### 1. Zero Hard-coded Colors
```tsx
// ❌ Bad - will break when palette changes
<div style={{ color: '#3B6B8F' }}>Temperature</div>

// ✅ Good - automatically updates with palette
<div style={{ color: 'var(--color-water)' }}>Temperature</div>
```

### 2. Instant Theme Switching
```typescript
// Change entire app theme with one line
ThemeManager.setTheme('dark');
```

### 3. User Customization
```typescript
// Let users choose their favorite palette
ThemeManager.setPalette('deep-confidence');
```

### 4. Easy Maintenance
- Change palette: Edit 1 file (`themes.css`)
- Add new palette: Add entry to `palettes.json`
- Update colors: Never touch component code

### 5. Type Safety
```typescript
// TypeScript autocomplete for all color tokens
const color = useColorToken('color-water'); // ✅ Autocomplete!
const bad = useColorToken('color-invalid'); // ❌ TypeScript error
```

---

## Migration Checklist

When implementing the frontend:

- [ ] Create `palettes.json` with all 5 palette definitions
- [ ] Create `tokens.css` with semantic token mappings
- [ ] Create `themes.css` with Soft Trust as default
- [ ] Never use hex codes directly in components
- [ ] Always use `var(--semantic-token-name)`
- [ ] Create TypeScript types for autocomplete
- [ ] Implement ThemeManager utility
- [ ] Test theme switching (light/dark)
- [ ] Test palette switching (all 5 palettes)
- [ ] Verify Victory Charts use theme tokens

---

## Future Enhancements

### 1. Custom User Palettes
Allow users to create their own color schemes:
```typescript
interface CustomPalette {
  name: string;
  colors: PaletteColors;
  createdBy: string;
}
```

### 2. Palette Presets per Chart Type
```typescript
// Different default palettes for different chart types
const chartPalettes = {
  temperature: 'serene-clarity',  // Blue-focused
  humidity: 'soft-trust',          // Calming
  wind: 'deep-confidence',         // High contrast
};
```

### 3. Color Blindness Simulation Mode
```typescript
ThemeManager.setAccessibilityMode('deuteranopia');
// Automatically adjusts colors for colorblind users
```

### 4. Export/Import Themes
```typescript
// Share your favorite palette configuration
const config = ThemeManager.exportConfig();
ThemeManager.importConfig(config);
```

---

## Summary

**To answer your questions:**

1. **How difficult to change palette later?**
   - Edit 1 file: `themes.css`
   - Zero component code changes
   - Takes ~2 minutes

2. **Let users change palette?**
   - Yes! Just add a `<select>` dropdown
   - Call `ThemeManager.setPalette()`
   - Persists to localStorage

3. **All variables, no hard-coding?**
   - ✅ Zero hex codes in components
   - ✅ All colors via semantic tokens
   - ✅ Type-safe with TypeScript
   - ✅ Future-proof architecture

**Effort to implement:**
- Initial setup: ~2 hours
- Adding new palette: ~15 minutes
- Switching default: ~2 minutes
- User palette selector: ~1 hour

This is the industry-standard approach used by design systems like Material-UI, Chakra UI, and Tailwind CSS.
