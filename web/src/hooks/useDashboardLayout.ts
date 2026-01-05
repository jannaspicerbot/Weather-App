/**
 * useDashboardLayout Hook
 *
 * Manages dashboard chart ordering with localStorage persistence.
 * Allows users to customize their dashboard layout via drag-and-drop.
 */

import { useState, useEffect } from 'react';

export type ChartId = 'temperature' | 'humidity' | 'wind' | 'precipitation';

const DEFAULT_LAYOUT: ChartId[] = ['temperature', 'humidity', 'wind', 'precipitation'];
const STORAGE_KEY = 'dashboard-layout';

export function useDashboardLayout() {
  const [chartOrder, setChartOrder] = useState<ChartId[]>(() => {
    // Load from localStorage on mount
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
          const parsed = JSON.parse(saved);
          // Validate that all expected charts are present
          if (Array.isArray(parsed) && parsed.length === DEFAULT_LAYOUT.length) {
            return parsed;
          }
        }
      } catch (error) {
        console.error('Failed to load dashboard layout from localStorage:', error);
      }
    }
    return DEFAULT_LAYOUT;
  });

  useEffect(() => {
    // Persist to localStorage whenever order changes
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(chartOrder));
      } catch (error) {
        console.error('Failed to save dashboard layout to localStorage:', error);
      }
    }
  }, [chartOrder]);

  const resetLayout = () => {
    setChartOrder(DEFAULT_LAYOUT);
  };

  return { chartOrder, setChartOrder, resetLayout };
}
