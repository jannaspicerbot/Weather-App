/**
 * DashboardGrid Component
 *
 * Container for sortable dashboard widgets using dnd-kit.
 * Provides drag-and-drop functionality with full WCAG 2.2 AA accessibility:
 * - Keyboard navigation (Enter/Space to activate, Arrow keys to move, Enter to drop, Escape to cancel)
 * - Screen reader announcements for all drag operations
 * - Touch support for iPad
 * - Mouse support for desktop
 *
 * Compact 2x2 grid layout to fit all charts on screen without scrolling.
 */

import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from '@dnd-kit/core';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy,
} from '@dnd-kit/sortable';
import { useState } from 'react';
import type { ChartId } from '../../hooks/useDashboardLayout';

interface DashboardGridProps {
  chartOrder: ChartId[];
  onReorder: (newOrder: ChartId[]) => void;
  children: React.ReactNode;
}

// Human-readable chart names for announcements
const CHART_NAMES: Record<ChartId, string> = {
  temperature: 'Temperature',
  humidity: 'Humidity',
  wind: 'Wind',
  precipitation: 'Precipitation',
};

export function DashboardGrid({ chartOrder, onReorder, children }: DashboardGridProps) {
  const [activeId, setActiveId] = useState<ChartId | null>(null);

  // Configure sensors for multi-modal accessibility
  const sensors = useSensors(
    // Pointer (mouse) sensor with activation constraint to prevent accidental drags
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // User must drag 8px before drag starts (prevents accidental drags)
      },
    }),
    // Touch sensor for iPad with delay to distinguish from scrolling
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 200, // 200ms press before drag activates
        tolerance: 5, // Allow 5px movement during delay
      },
    }),
    // Keyboard sensor for accessibility (WCAG 2.1.1)
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as ChartId);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = chartOrder.indexOf(active.id as ChartId);
      const newIndex = chartOrder.indexOf(over.id as ChartId);

      const newOrder = [...chartOrder];
      newOrder.splice(oldIndex, 1);
      newOrder.splice(newIndex, 0, active.id as ChartId);

      onReorder(newOrder);
    }

    setActiveId(null);
  };

  const handleDragCancel = () => {
    setActiveId(null);
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
      accessibility={{
        announcements: {
          onDragStart({ active }) {
            const chartName = CHART_NAMES[active.id as ChartId];
            return `Picked up ${chartName} chart. Use arrow keys to move, Enter to drop, Escape to cancel.`;
          },
          onDragOver({ active, over }) {
            if (over) {
              const activeChart = CHART_NAMES[active.id as ChartId];
              const overChart = CHART_NAMES[over.id as ChartId];
              return `${activeChart} chart is over ${overChart} chart.`;
            }
            const activeChart = CHART_NAMES[active.id as ChartId];
            return `${activeChart} chart is no longer over a droppable area.`;
          },
          onDragEnd({ active, over }) {
            const activeChart = CHART_NAMES[active.id as ChartId];
            if (over) {
              const newPosition = chartOrder.indexOf(over.id as ChartId) + 1;
              return `${activeChart} chart was dropped at position ${newPosition} of ${chartOrder.length}.`;
            }
            return `${activeChart} chart was dropped.`;
          },
          onDragCancel({ active }) {
            const activeChart = CHART_NAMES[active.id as ChartId];
            return `Dragging ${activeChart} chart was cancelled.`;
          },
        },
      }}
    >
      <SortableContext items={chartOrder} strategy={rectSortingStrategy}>
        <div
          className="charts-grid"
          role="region"
          aria-label="Weather charts - drag to reorder"
        >
          {children}
        </div>
      </SortableContext>

      {/* Live region for screen reader announcements */}
      <div
        className="sr-only"
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        {activeId && (
          <p>
            Dragging {CHART_NAMES[activeId]} chart. Use arrow keys to move, Enter to drop, Escape to cancel.
          </p>
        )}
      </div>

      {/* Compact instructions tooltip */}
      <details className="dashboard-instructions">
        <summary className="dashboard-instructions__toggle">
          Reorder charts
        </summary>
        <div className="dashboard-instructions__content">
          <p><strong>Mouse:</strong> Drag charts</p>
          <p><strong>Touch:</strong> Long-press and drag</p>
          <p><strong>Keyboard:</strong> Tab → Enter → Arrows → Enter</p>
        </div>
      </details>
    </DndContext>
  );
}
