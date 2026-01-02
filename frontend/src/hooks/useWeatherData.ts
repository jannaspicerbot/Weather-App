/**
 * React Query hooks for weather data
 * Provides type-safe data fetching with caching and automatic refetching
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { weatherAPI } from '../services/api';
import type { WeatherReading, WeatherStats, DateRangeQuery } from '../types/weather';

/**
 * Hook to fetch latest weather readings
 */
export function useLatestWeather(limit: number = 100): UseQueryResult<WeatherReading[], Error> {
  return useQuery({
    queryKey: ['weather', 'latest', limit],
    queryFn: () => weatherAPI.getLatestReadings(limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000, // Auto-refetch every 5 minutes
  });
}

/**
 * Hook to fetch weather readings by date range
 */
export function useWeatherByDateRange(query: DateRangeQuery): UseQueryResult<WeatherReading[], Error> {
  return useQuery({
    queryKey: ['weather', 'range', query],
    queryFn: () => weatherAPI.getReadingsByDateRange(query),
    enabled: Boolean(query.startDate && query.endDate),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to fetch weather statistics
 */
export function useWeatherStats(): UseQueryResult<WeatherStats, Error> {
  return useQuery({
    queryKey: ['weather', 'stats'],
    queryFn: () => weatherAPI.getStats(),
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
}

/**
 * Hook to check API health
 */
export function useAPIHealth(): UseQueryResult<{ status: string }, Error> {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await weatherAPI.getHealth();
      return response.data || { status: 'unknown' };
    },
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Check every minute
  });
}
