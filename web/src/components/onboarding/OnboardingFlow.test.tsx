/**
 * OnboardingFlow Component Tests
 *
 * Tests for accessibility compliance (WCAG 2.2 Level AA) and functionality.
 * Uses vitest-axe for automated accessibility checking.
 */

import { render, screen } from '@testing-library/react';
import { axe } from 'vitest-axe';
import { describe, it, expect, vi } from 'vitest';
import OnboardingFlow from './OnboardingFlow';

// Mock the onboarding API
vi.mock('../../services/onboardingApi', () => ({
  validateCredentials: vi.fn(),
  saveCredentials: vi.fn(),
  startBackfill: vi.fn(),
  enableDemoMode: vi.fn(),
  generateDemoDatabase: vi.fn(),
  getDemoStatus: vi.fn().mockResolvedValue({ available: true, generation_required: false }),
  cancelGeneration: vi.fn().mockResolvedValue({ success: true, message: 'Cancelled' }),
}));

const defaultProps = {
  onComplete: vi.fn(),
};

describe('OnboardingFlow', () => {
  describe('Accessibility', () => {
    it('should have no accessibility violations on credentials step', async () => {
      const { container } = render(<OnboardingFlow {...defaultProps} />);

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper heading hierarchy', () => {
      render(<OnboardingFlow {...defaultProps} />);

      // Main title should be h2 (assuming dashboard h1 wraps this)
      const title = screen.getByRole('heading', { level: 2, name: 'Welcome to Weather Dashboard' });
      expect(title).toBeInTheDocument();
    });

    it('should have descriptive step indicators', () => {
      const { container } = render(<OnboardingFlow {...defaultProps} />);

      // Step labels should be visible (use container query to be specific)
      const stepLabels = container.querySelectorAll('.onboarding__step-label');
      expect(stepLabels).toHaveLength(3);
      expect(stepLabels[0]).toHaveTextContent('Connect Account');
      expect(stepLabels[1]).toHaveTextContent('Select Device');
      expect(stepLabels[2]).toHaveTextContent('Load Data');
    });

    it('should hide decorative SVG icons from screen readers', () => {
      const { container } = render(<OnboardingFlow {...defaultProps} />);

      // Check for aria-hidden on SVG elements
      const svgs = container.querySelectorAll('svg');
      svgs.forEach((svg) => {
        expect(svg).toHaveAttribute('aria-hidden', 'true');
      });
    });
  });

  describe('Rendering', () => {
    it('should render welcome message', () => {
      render(<OnboardingFlow {...defaultProps} />);

      expect(screen.getByText('Welcome to Weather Dashboard')).toBeInTheDocument();
      expect(
        screen.getByText('Connect your Ambient Weather account to get started.')
      ).toBeInTheDocument();
    });

    it('should render step indicator with three steps', () => {
      const { container } = render(<OnboardingFlow {...defaultProps} />);

      // All step numbers should be present
      const stepCircles = container.querySelectorAll('.onboarding__step-circle');
      expect(stepCircles).toHaveLength(3);
      expect(stepCircles[0]).toHaveTextContent('1');
      expect(stepCircles[1]).toHaveTextContent('2');
      expect(stepCircles[2]).toHaveTextContent('3');

      // All step labels should be present
      const stepLabels = container.querySelectorAll('.onboarding__step-label');
      expect(stepLabels[0]).toHaveTextContent('Connect Account');
      expect(stepLabels[1]).toHaveTextContent('Select Device');
      expect(stepLabels[2]).toHaveTextContent('Load Data');
    });

    it('should show credentials step as active by default', () => {
      const { container } = render(<OnboardingFlow {...defaultProps} />);

      // First step circle should have active class, others pending
      const stepCircles = container.querySelectorAll('.onboarding__step-circle');
      expect(stepCircles[0]).toHaveClass('onboarding__step-circle--active');
      expect(stepCircles[1]).toHaveClass('onboarding__step-circle--pending');
      expect(stepCircles[2]).toHaveClass('onboarding__step-circle--pending');
    });

    it('should render CredentialInput component on credentials step', () => {
      render(<OnboardingFlow {...defaultProps} />);

      // CredentialInput contains these elements
      expect(screen.getByLabelText('API Key')).toBeInTheDocument();
      expect(screen.getByLabelText('Application Key')).toBeInTheDocument();
    });
  });

  describe('Visual Feedback', () => {
    it('should indicate first step is active', () => {
      const { container } = render(<OnboardingFlow {...defaultProps} />);

      const firstStepLabel = container.querySelector('.onboarding__step-label--active');
      expect(firstStepLabel).toHaveTextContent('Connect Account');
    });

    it('should show connector line between steps', () => {
      const { container } = render(<OnboardingFlow {...defaultProps} />);

      const connector = container.querySelector('.onboarding__step-connector');
      expect(connector).toBeInTheDocument();
      // Connector should not be complete on first step
      expect(connector).not.toHaveClass('onboarding__step-connector--complete');
    });
  });
});
