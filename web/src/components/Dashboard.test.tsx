/**
 * Dashboard Component Tests
 *
 * Tests for accessibility compliance (WCAG 2.2 Level AA) and functionality.
 * Uses vitest-axe for automated accessibility checking.
 */

import { render, screen, waitFor } from '@testing-library/react';
import { axe } from 'vitest-axe';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Dashboard from './Dashboard';

// Mock the API service
vi.mock('../api', () => ({
  DefaultService: {
    getLatestWeatherWeatherLatestGet: vi.fn(),
    getDatabaseStatsWeatherStatsGet: vi.fn(),
    getWeatherDataWeatherGet: vi.fn(),
    apiGetWeatherRangeApiWeatherRangeGet: vi.fn(),
  },
}));

// Mock the onboarding API
vi.mock('../services/onboardingApi', () => ({
  getCredentialStatus: vi.fn(),
  getBackfillProgress: vi.fn(),
  getDevices: vi.fn(),
  selectDevice: vi.fn(),
}));

// Import mocks after vi.mock
import { DefaultService } from '../api';
import { getCredentialStatus, getBackfillProgress, getDevices } from '../services/onboardingApi';

const mockWeatherData = {
  id: 1,
  dateutc: 1704628800000,
  date: '2024-01-07T12:00:00',
  tempf: 72.5,
  feelsLike: 70.0,
  humidity: 45,
  windspeedmph: 5.2,
  windgustmph: 8.1,
  hourlyrainin: 0,
  dailyrainin: 0,
};

const mockStats = {
  total_records: 1000,
  date_range_days: 30,
  min_date: '2024-01-01',
  max_date: '2024-01-07',
};

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default: credentials configured, no backfill running
    vi.mocked(getCredentialStatus).mockResolvedValue({ configured: true, has_api_key: true, has_app_key: true });
    vi.mocked(getBackfillProgress).mockResolvedValue({
      status: 'idle',
      progress_id: null,
      message: 'No backfill in progress',
      total_records: 0,
      inserted_records: 0,
      skipped_records: 0,
      current_date: null,
      start_date: null,
      end_date: null,
      estimated_time_remaining_seconds: null,
      requests_made: 0,
      requests_per_second: 0,
      records_per_request: 0,
    });
    vi.mocked(DefaultService.getDatabaseStatsWeatherStatsGet).mockResolvedValue(mockStats);
    vi.mocked(DefaultService.getLatestWeatherWeatherLatestGet).mockResolvedValue(mockWeatherData);
    vi.mocked(DefaultService.getWeatherDataWeatherGet).mockResolvedValue([mockWeatherData]);
    vi.mocked(DefaultService.apiGetWeatherRangeApiWeatherRangeGet).mockResolvedValue([mockWeatherData]);
    // Mock getDevices for DeviceManager component
    vi.mocked(getDevices).mockResolvedValue({
      devices: [
        {
          mac_address: 'AA:BB:CC:DD:EE:FF',
          name: 'Test Weather Station',
          last_data: '2024-01-07T12:00:00Z',
          location: 'Test City',
        },
      ],
      selected_device_mac: 'AA:BB:CC:DD:EE:FF',
    });
  });

  describe('Accessibility', () => {
    it('should have no accessibility violations in loaded state', async () => {
      const { container } = render(<Dashboard />);

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.queryByText('Checking configuration...')).not.toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Weather Dashboard' })).toBeInTheDocument();
      });

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no accessibility violations in loading state', async () => {
      // Keep loading by not resolving promises immediately
      vi.mocked(getCredentialStatus).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      const { container } = render(<Dashboard />);

      // Verify we're showing loading state
      expect(screen.getByText('Checking configuration...')).toBeInTheDocument();

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper heading hierarchy', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('heading', { level: 1, name: 'Weather Dashboard' })).toBeInTheDocument();
      });
    });

    it('should have skip link target on main content', async () => {
      const { container } = render(<Dashboard />);

      // Wait for dashboard to fully load
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Weather Dashboard' })).toBeInTheDocument();
      });

      // Main element should have id for skip link
      const main = container.querySelector('#main-content');
      expect(main).toBeInTheDocument();
      expect(main?.tagName).toBe('MAIN');
    });

    it('should have accessible reset layout button', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        const resetButton = screen.getByRole('button', { name: /reset.*layout/i });
        expect(resetButton).toBeInTheDocument();
        expect(resetButton).toHaveAttribute('aria-label');
      });
    });

    it('should hide loading spinner from screen readers', async () => {
      vi.mocked(getCredentialStatus).mockImplementation(
        () => new Promise(() => {})
      );

      const { container } = render(<Dashboard />);

      const spinner = container.querySelector('.dashboard__loading-spinner');
      expect(spinner).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Rendering States', () => {
    it('should show loading state while checking configuration', () => {
      vi.mocked(getCredentialStatus).mockImplementation(
        () => new Promise(() => {})
      );

      render(<Dashboard />);

      expect(screen.getByText('Checking configuration...')).toBeInTheDocument();
    });

    it('should show onboarding when credentials not configured', async () => {
      vi.mocked(getCredentialStatus).mockResolvedValue({ configured: false, has_api_key: false, has_app_key: false });

      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('Welcome to Weather Dashboard')).toBeInTheDocument();
      });
    });

    it('should show dashboard when credentials are configured', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('Weather Dashboard')).toBeInTheDocument();
      });

      // Should show stats
      await waitFor(() => {
        expect(screen.getByText(/1,000 readings/)).toBeInTheDocument();
      });
    });

    it('should show empty state when no data exists', async () => {
      vi.mocked(DefaultService.getDatabaseStatsWeatherStatsGet).mockResolvedValue({
        total_records: 0,
        date_range_days: 0,
        min_date: null,
        max_date: null,
      });

      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('No Weather Data Yet')).toBeInTheDocument();
      });
    });

    it('should show error state when API fails', async () => {
      vi.mocked(DefaultService.getDatabaseStatsWeatherStatsGet).mockRejectedValue(
        new Error('API Error')
      );

      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Error:/)).toBeInTheDocument();
      });
    });
  });

  describe('Structure', () => {
    it('should have header, main content areas', async () => {
      const { container } = render(<Dashboard />);

      // Wait for dashboard to fully load
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Weather Dashboard' })).toBeInTheDocument();
      });

      expect(container.querySelector('header')).toBeInTheDocument();
      expect(container.querySelector('main')).toBeInTheDocument();
    });

    it('should render DateRangeSelector', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        // DateRangeSelector renders these preset buttons
        expect(screen.getByText('Last 24h')).toBeInTheDocument();
      });
    });
  });
});
