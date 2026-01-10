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
  },
}));

// Mock the onboarding API
vi.mock('../services/onboardingApi', () => ({
  getCredentialStatus: vi.fn(),
  getBackfillProgress: vi.fn(),
}));

// Import mocks after vi.mock
import { DefaultService } from '../api';
import { getCredentialStatus, getBackfillProgress } from '../services/onboardingApi';

const mockWeatherData = {
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
    vi.mocked(getCredentialStatus).mockResolvedValue({ configured: true });
    vi.mocked(getBackfillProgress).mockResolvedValue({ status: 'idle' });
    vi.mocked(DefaultService.getDatabaseStatsWeatherStatsGet).mockResolvedValue(mockStats);
    vi.mocked(DefaultService.getLatestWeatherWeatherLatestGet).mockResolvedValue(mockWeatherData);
    vi.mocked(DefaultService.getWeatherDataWeatherGet).mockResolvedValue([mockWeatherData]);
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

      // Note: Victory charts add role="img" to SVGs without alt text, which is a library limitation.
      // The ChartCard wrapper provides proper accessibility via aria-labelledby on the figure element.
      // We exclude svg-img-alt rule since the parent figure provides the accessible name.
      const results = await axe(container, {
        rules: {
          'svg-img-alt': { enabled: false },
        },
      });
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
      vi.mocked(getCredentialStatus).mockResolvedValue({ configured: false });

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

      await waitFor(() => {
        expect(screen.queryByText('Checking configuration...')).not.toBeInTheDocument();
      });

      expect(container.querySelector('header')).toBeInTheDocument();
      expect(container.querySelector('main')).toBeInTheDocument();
    });

    it('should render DateRangeSelector', async () => {
      render(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('Date Range')).toBeInTheDocument();
      });
    });
  });
});
