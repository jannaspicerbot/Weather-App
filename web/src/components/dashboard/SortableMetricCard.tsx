/**
 * SortableMetricCard Component
 *
 * Wrapper component that makes metric cards draggable/sortable using dnd-kit.
 * Provides full accessibility support per docs/standards/ACCESSIBILITY.md:
 * - Keyboard navigation (Enter/Space to activate, Arrow keys to move)
 * - Screen reader announcements for all drag operations
 * - Touch support for iPad (44x44px minimum touch targets)
 *
 * Note: Visual styling is handled by MetricCard component inside.
 * This wrapper only adds drag-and-drop behavior.
 */

import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { MetricId } from '../../hooks/useMetricsLayout';

interface SortableMetricCardProps {
  id: MetricId;
  children: React.ReactNode;
}

export function SortableMetricCard({ id, children }: SortableMetricCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`sortable-metric-card ${isDragging ? 'sortable-metric-card--dragging' : ''}`}
      {...attributes}
      {...listeners}
      role="listitem"
    >
      {children}
    </div>
  );
}
