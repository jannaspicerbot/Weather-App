/**
 * SortableChartCard Component
 *
 * Wrapper component that makes chart cards draggable/sortable using dnd-kit.
 * Provides full accessibility support (keyboard, screen reader, touch).
 *
 * Note: Visual styling is handled by ChartCard component inside.
 * This wrapper only adds drag-and-drop behavior.
 */

import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { ChartId } from '../../hooks/useDashboardLayout';

interface SortableChartCardProps {
  id: ChartId;
  children: React.ReactNode;
}

export function SortableChartCard({ id, children }: SortableChartCardProps) {
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
      className={`sortable-chart-card ${isDragging ? 'sortable-chart-card--dragging' : ''}`}
      aria-label={`${id} chart - draggable`}
      {...attributes}
      {...listeners}
    >
      {children}
    </div>
  );
}
