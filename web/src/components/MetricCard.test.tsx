/**
 * MetricCard Component Tests
 *
 * Tests for accessibility compliance (WCAG 2.2 Level AA) and functionality.
 * Uses vitest-axe for automated accessibility checking.
 */

import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'
import { describe, it, expect } from 'vitest'
import { MetricCard } from './MetricCard'

describe('MetricCard', () => {
  describe('Accessibility', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(
        <MetricCard
          label="Temperature"
          value="72°F"
          icon="🌡️"
          colorCategory="water"
        />
      )

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('should have proper ARIA labels for screen readers', () => {
      render(
        <MetricCard
          label="Humidity"
          value="45%"
          icon="💧"
          colorCategory="water"
        />
      )

      // The article should have an accessible label combining label and value
      const article = screen.getByRole('region', { name: 'Humidity: 45%' })
      expect(article).toBeInTheDocument()
    })

    it('should hide decorative icons from screen readers', () => {
      const { container } = render(
        <MetricCard
          label="Wind Speed"
          value="10 mph"
          icon="💨"
          colorCategory="growth"
        />
      )

      // Icon container should have aria-hidden="true"
      const iconElement = container.querySelector('.metric-card__icon')
      expect(iconElement).toHaveAttribute('aria-hidden', 'true')
    })

    it('should include screen-reader-only description when provided', () => {
      render(
        <MetricCard
          label="Pressure"
          value="30.12 inHg"
          icon="🔘"
          colorCategory="interactive"
          description="Barometric pressure is rising, indicating fair weather"
        />
      )

      // Description should be present but visually hidden (sr-only class)
      const description = screen.getByText(
        'Barometric pressure is rising, indicating fair weather'
      )
      expect(description).toBeInTheDocument()
      expect(description).toHaveClass('sr-only')
    })
  })

  describe('Rendering', () => {
    it('should render label and value', () => {
      render(
        <MetricCard
          label="Temperature"
          value="72°F"
          icon="🌡️"
        />
      )

      expect(screen.getByText('Temperature')).toBeInTheDocument()
      expect(screen.getByText('72°F')).toBeInTheDocument()
    })

    it('should render icon', () => {
      render(
        <MetricCard
          label="Humidity"
          value="45%"
          icon="💧"
        />
      )

      expect(screen.getByText('💧')).toBeInTheDocument()
    })

    it('should apply correct color category class', () => {
      const { container, rerender } = render(
        <MetricCard
          label="Temperature"
          value="72°F"
          icon="🌡️"
          colorCategory="water"
        />
      )

      expect(container.querySelector('.metric-card--water')).toBeInTheDocument()

      rerender(
        <MetricCard
          label="Wind"
          value="10 mph"
          icon="💨"
          colorCategory="growth"
        />
      )

      expect(container.querySelector('.metric-card--growth')).toBeInTheDocument()

      rerender(
        <MetricCard
          label="UV Index"
          value="5"
          icon="☀️"
          colorCategory="interactive"
        />
      )

      expect(container.querySelector('.metric-card--interactive')).toBeInTheDocument()
    })

    it('should default to water color category', () => {
      const { container } = render(
        <MetricCard
          label="Temperature"
          value="72°F"
          icon="🌡️"
        />
      )

      expect(container.querySelector('.metric-card--water')).toBeInTheDocument()
    })
  })
})
