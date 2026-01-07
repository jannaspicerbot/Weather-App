/**
 * ChartCard Component
 *
 * Wrapper for chart components following design-tokens.md specifications.
 * Provides consistent styling, accessibility, and compact layout.
 *
 * Design specs from docs/design/dashboard-layout.md:
 * - Card Surface: var(--color-bg-secondary)
 * - Border: 1px solid var(--color-border)
 * - Border Radius: 12px
 * - Compact padding for charts
 */

import type { ReactNode } from 'react';

interface ChartCardProps {
  /** Chart title */
  title: string;
  /** Semantic color category */
  colorCategory?: 'water' | 'growth' | 'interactive';
  /** Chart content */
  children: ReactNode;
  /** Optional description for accessibility */
  description?: string;
}

export function ChartCard({
  title,
  colorCategory = 'water',
  children,
  description,
}: ChartCardProps) {
  const titleId = `chart-${title.toLowerCase().replace(/\s+/g, '-')}-title`;
  const descId = description
    ? `chart-${title.toLowerCase().replace(/\s+/g, '-')}-desc`
    : undefined;

  return (
    <figure
      className={`chart-card chart-card--${colorCategory}`}
      role="figure"
      aria-labelledby={titleId}
      aria-describedby={descId}
    >
      <figcaption className="chart-card__header">
        <h3 id={titleId} className="chart-card__title">
          {title}
        </h3>
        {description && (
          <p id={descId} className="sr-only">
            {description}
          </p>
        )}
      </figcaption>
      <div className="chart-card__content">{children}</div>
    </figure>
  );
}

export default ChartCard;
