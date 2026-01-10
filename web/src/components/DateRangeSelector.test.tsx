/**
 * DateRangeSelector Component Tests
 *
 * Tests for accessibility compliance (WCAG 2.2 Level AA) and functionality.
 * Uses vitest-axe for automated accessibility checking.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe } from 'vitest-axe';
import { describe, it, expect, vi } from 'vitest';
import DateRangeSelector from './DateRangeSelector';

const defaultProps = {
  start: new Date('2024-01-01'),
  end: new Date('2024-01-07'),
  onChange: vi.fn(),
  onExport: vi.fn(),
};

describe('DateRangeSelector', () => {
  describe('Accessibility', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(<DateRangeSelector {...defaultProps} />);

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have properly labeled date inputs', () => {
      render(<DateRangeSelector {...defaultProps} />);

      // Check that labels are associated with inputs
      const startInput = screen.getByLabelText('Start Date');
      const endInput = screen.getByLabelText('End Date');

      expect(startInput).toBeInTheDocument();
      expect(endInput).toBeInTheDocument();
      expect(startInput).toHaveAttribute('type', 'date');
      expect(endInput).toHaveAttribute('type', 'date');
    });

    it('should have accessible preset buttons', () => {
      render(<DateRangeSelector {...defaultProps} />);

      // All preset buttons should be keyboard accessible
      const presetButtons = [
        screen.getByRole('button', { name: 'Last 24h' }),
        screen.getByRole('button', { name: 'Last 7 Days' }),
        screen.getByRole('button', { name: 'Last 30 Days' }),
        screen.getByRole('button', { name: 'Last Year' }),
      ];

      presetButtons.forEach((button) => {
        expect(button).toBeInTheDocument();
      });
    });

    it('should hide decorative SVG from screen readers', () => {
      const { container } = render(<DateRangeSelector {...defaultProps} />);

      const svg = container.querySelector('.date-range__export-btn svg');
      expect(svg).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Rendering', () => {
    it('should render all preset buttons', () => {
      render(<DateRangeSelector {...defaultProps} />);

      expect(screen.getByRole('button', { name: 'Last 24h' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Last 7 Days' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Last 30 Days' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Last Year' })).toBeInTheDocument();
    });

    it('should render date inputs with correct initial values', () => {
      render(<DateRangeSelector {...defaultProps} />);

      const startInput = screen.getByLabelText('Start Date') as HTMLInputElement;
      const endInput = screen.getByLabelText('End Date') as HTMLInputElement;

      expect(startInput.value).toBe('2024-01-01');
      expect(endInput.value).toBe('2024-01-07');
    });

    it('should render Apply and Export buttons', () => {
      render(<DateRangeSelector {...defaultProps} />);

      expect(screen.getByRole('button', { name: 'Apply' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Export CSV' })).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('should call onChange when Apply button is clicked', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<DateRangeSelector {...defaultProps} onChange={onChange} />);

      await user.click(screen.getByRole('button', { name: 'Apply' }));

      expect(onChange).toHaveBeenCalled();
    });

    it('should call onChange when preset button is clicked', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<DateRangeSelector {...defaultProps} onChange={onChange} />);

      await user.click(screen.getByRole('button', { name: 'Last 7 Days' }));

      expect(onChange).toHaveBeenCalled();
    });

    it('should call onExport when Export button is clicked', async () => {
      const user = userEvent.setup();
      const onExport = vi.fn();
      render(<DateRangeSelector {...defaultProps} onExport={onExport} />);

      await user.click(screen.getByRole('button', { name: 'Export CSV' }));

      expect(onExport).toHaveBeenCalled();
    });

    it('should highlight active preset button', async () => {
      const user = userEvent.setup();
      const { container } = render(<DateRangeSelector {...defaultProps} />);

      // Initially 24h is active (default)
      const button24h = screen.getByRole('button', { name: 'Last 24h' });
      expect(button24h).toHaveClass('date-range__preset--active');

      // Click 7 Days
      await user.click(screen.getByRole('button', { name: 'Last 7 Days' }));

      const button7d = screen.getByRole('button', { name: 'Last 7 Days' });
      expect(button7d).toHaveClass('date-range__preset--active');
      expect(button24h).toHaveClass('date-range__preset--inactive');
    });
  });
});
