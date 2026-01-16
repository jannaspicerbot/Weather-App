/**
 * Demo Banner Component
 *
 * Displays a persistent banner when the app is running in demo mode.
 * Provides a way for users to exit demo mode and connect their real device.
 */

import { useState } from 'react';
import { disableDemoMode } from '../services/onboardingApi';

interface DemoBannerProps {
  onExitDemo: () => void;
}

export default function DemoBanner({ onExitDemo }: DemoBannerProps) {
  const [isExiting, setIsExiting] = useState(false);

  const handleExitDemo = async () => {
    setIsExiting(true);
    try {
      await disableDemoMode();
      onExitDemo();
    } catch (err) {
      console.error('Failed to exit demo mode:', err);
      setIsExiting(false);
    }
  };

  return (
    <div className="demo-banner" role="status" aria-live="polite">
      <div className="demo-banner__content">
        <svg
          className="demo-banner__icon"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <span className="demo-banner__text">
          <strong>Demo Mode</strong> - Viewing sample Seattle weather data
        </span>
      </div>
      <button
        type="button"
        className="demo-banner__button"
        onClick={handleExitDemo}
        disabled={isExiting}
      >
        {isExiting ? 'Exiting...' : 'Connect Real Device'}
      </button>
    </div>
  );
}
