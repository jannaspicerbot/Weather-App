/**
 * MetricsGrid Component
 *
 * Container for sortable weather metric cards using dnd-kit.
 * Provides drag-and-drop functionality with full WCAG 2.2 AA accessibility:
 * - Keyboard navigation (Enter/Space to activate, Arrow keys to move, Enter to drop, Escape to cancel)
 * - Screen reader announcements for all drag operations
 * - Touch support for iPad (200ms delay to distinguish from scrolling)
 * - Mouse support for desktop
 *
 * Follows same patterns as DashboardGrid for charts, per docs/design/inclusive-design.md
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
import type { MetricId } from '../../hooks/useMetricsLayout';

interface MetricsGridProps {
  metricsOrder: MetricId[];
  onReorder: (newOrder: MetricId[]) => void;
  children: React.ReactNode;
}

// Human-readable metric names for screen reader announcements
const METRIC_NAMES: Record<MetricId, string> = {
  temperature: 'Temperature',
  feelsLike: 'Feels Like',
  humidity: 'Humidity',
  dewPoint: 'Dew Point',
  windSpeed: 'Wind Speed',
  windGust: 'Wind Gust',
  windDirection: 'Wind Direction',
  pressure: 'Pressure',
  hourlyRain: 'Hourly Rain',
  dailyRain: 'Daily Rain',
  solarRadiation: 'Solar Radiation',
  uvIndex: 'UV Index',
};

export function MetricsGrid({ metricsOrder, onReorder, children }: MetricsGridProps) {
  const [activeId, setActiveId] = useState<MetricId | null>(null);

  // Configure sensors for multi-modal accessibility per inclusive-design.md
  const sensors = useSensors(
    // Pointer (mouse) sensor with activation constraint to prevent accidental drags
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // User must drag 8px before drag starts
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
    setActiveId(event.active.id as MetricId);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = metricsOrder.indexOf(active.id as MetricId);
      const newIndex = metricsOrder.indexOf(over.id as MetricId);

      const newOrder = [...metricsOrder];
      newOrder.splice(oldIndex, 1);
      newOrder.splice(newIndex, 0, active.id as MetricId);

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
            const metricName = METRIC_NAMES[active.id as MetricId];
            return `Picked up ${metricName} card. Use arrow keys to move, Enter to drop, Escape to cancel.`;
          },
          onDragOver({ active, over }) {
            if (over) {
              const activeMetric = METRIC_NAMES[active.id as MetricId];
              const overMetric = METRIC_NAMES[over.id as MetricId];
              return `${activeMetric} card is over ${overMetric} card.`;
            }
            const activeMetric = METRIC_NAMES[active.id as MetricId];
            return `${activeMetric} card is no longer over a droppable area.`;
          },
          onDragEnd({ active, over }) {
            const activeMetric = METRIC_NAMES[active.id as MetricId];
            if (over) {
              const newPosition = metricsOrder.indexOf(over.id as MetricId) + 1;
              return `${activeMetric} card was dropped at position ${newPosition} of ${metricsOrder.length}.`;
            }
            return `${activeMetric} card was dropped.`;
          },
          onDragCancel({ active }) {
            const activeMetric = METRIC_NAMES[active.id as MetricId];
            return `Dragging ${activeMetric} card was cancelled.`;
          },
        },
      }}
    >
      <SortableContext items={metricsOrder} strategy={rectSortingStrategy}>
        <div
          className="current-conditions__grid"
          role="list"
          aria-label="Weather metrics - drag to reorder"
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
            Dragging {METRIC_NAMES[activeId]} card. Use arrow keys to move, Enter to drop, Escape to cancel.
          </p>
        )}
      </div>
    </DndContext>
  );
}
