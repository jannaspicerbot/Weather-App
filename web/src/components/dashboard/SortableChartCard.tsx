/**
 * SortableChartCard Component
 *
 * Wrapper component that makes chart cards draggable/sortable using dnd-kit.
 * Provides full accessibility support (keyboard, screen reader, touch).
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
    <article
      ref={setNodeRef}
      style={style}
      className={`
        bg-white shadow-md rounded-lg p-6
        focus:outline-none
        focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
        ${isDragging ? 'cursor-grabbing z-10' : 'cursor-grab'}
      `}
      aria-label={`${id} chart - draggable`}
      {...attributes}
      {...listeners}
    >
      {children}
    </article>
  );
}
