/**
 * API service for Weather App
 * Type-safe API client using axios and TypeScript
 */

import axios, { AxiosInstance } from 'axios';
import type { WeatherReading, WeatherStats, DateRangeQuery, APIResponse } from '../types/weather';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class WeatherAPI {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get latest weather readings
   */
  async getLatestReadings(limit: number = 100): Promise<WeatherReading[]> {
    const response = await this.client.get<WeatherReading[]>('/api/weather/latest', {
      params: { limit },
    });
    return response.data;
  }

  /**
   * Get weather readings within a date range
   */
  async getReadingsByDateRange(query: DateRangeQuery): Promise<WeatherReading[]> {
    const response = await this.client.get<WeatherReading[]>('/api/weather/range', {
      params: {
        start_date: query.startDate,
        end_date: query.endDate,
        limit: query.limit,
      },
    });
    return response.data;
  }

  /**
   * Get weather database statistics
   */
  async getStats(): Promise<WeatherStats> {
    const response = await this.client.get<WeatherStats>('/api/weather/stats');
    return response.data;
  }

  /**
   * Get health status
   */
  async getHealth(): Promise<APIResponse<{ status: string }>> {
    const response = await this.client.get<APIResponse<{ status: string }>>('/api/health');
    return response.data;
  }

  /**
   * Export data to CSV
   */
  async exportToCSV(query: DateRangeQuery): Promise<Blob> {
    const response = await this.client.get('/api/weather/export', {
      params: {
        start_date: query.startDate,
        end_date: query.endDate,
      },
      responseType: 'blob',
    });
    return response.data;
  }
}

// Export singleton instance
export const weatherAPI = new WeatherAPI();

// Export class for testing or custom instances
export { WeatherAPI };
