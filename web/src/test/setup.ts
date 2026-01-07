/**
 * Vitest Test Setup
 *
 * Global test configuration for React component testing.
 * Includes:
 * - @testing-library/jest-dom matchers
 * - vitest-axe accessibility matchers
 * - Global cleanup after each test
 */

import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, expect } from 'vitest'
import * as matchers from 'vitest-axe/matchers'

// Extend Vitest's expect with axe matchers for accessibility testing
expect.extend(matchers)

// Cleanup after each test to prevent memory leaks
afterEach(() => {
  cleanup()
})

// Mock matchMedia for components that use it (e.g., prefers-reduced-motion)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
})
