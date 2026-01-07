/**
 * MetricCard Component
 *
 * Individual weather metric display following design-tokens.md specifications.
 * Uses semantic tokens for colors and follows inclusive-design.md accessibility standards.
 *
 * Design specs from docs/design/dashboard-layout.md:
 * - Card Surface: var(--color-bg-secondary)
 * - Border: 1px solid var(--color-border)
 * - Border Radius: 12px
 * - Shadow: 0 1px 3px rgba(0,0,0,0.1)
 * - Padding: 1.5rem (24px)
 */

interface MetricCardProps {
  /** Display label for the metric */
  label: string;
  /** Formatted value with unit */
  value: string;
  /** Icon to display (emoji or component) */
  icon: string;
  /** Semantic color category for the metric */
  colorCategory?: 'water' | 'growth' | 'interactive';
  /** Optional description for screen readers */
  description?: string;
}

export function MetricCard({
  label,
  value,
  icon,
  colorCategory = 'water',
  description,
}: MetricCardProps) {
  // Map color categories to CSS custom properties
  const colorClass = {
    water: 'metric-card--water',
    growth: 'metric-card--growth',
    interactive: 'metric-card--interactive',
  }[colorCategory];

  return (
    <article
      className={`metric-card ${colorClass}`}
      role="region"
      aria-label={`${label}: ${value}`}
    >
      <div className="metric-card__icon" aria-hidden="true">
        {icon}
      </div>
      <div className="metric-card__content">
        <p className="metric-card__label">{label}</p>
        <p className="metric-card__value">{value}</p>
        {description && (
          <p className="metric-card__description sr-only">{description}</p>
        )}
      </div>
    </article>
  );
}

export default MetricCard;
