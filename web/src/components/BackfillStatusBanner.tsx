/**
 * Backfill Status Banner Component
 *
 * Shows a compact status banner when backfill is running in the background.
 * Displayed at the top of the dashboard during data sync.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  getBackfillProgress,
  formatTimeRemaining,
  type BackfillProgress,
} from '../services/onboardingApi';

interface BackfillStatusBannerProps {
  onComplete: () => void;
}

export default function BackfillStatusBanner({ onComplete }: BackfillStatusBannerProps) {
  const [progress, setProgress] = useState<BackfillProgress | null>(null);
  const [isMinimized, setIsMinimized] = useState(false);

  const fetchProgress = useCallback(async () => {
    try {
      const data = await getBackfillProgress();
      setProgress(data);

      // Check if complete or failed
      if (data.status === 'completed' || data.status === 'failed' || data.status === 'idle') {
        if (data.status === 'completed') {
          // Show completion briefly then hide
          setTimeout(() => {
            onComplete();
          }, 3000);
        } else if (data.status === 'idle') {
          onComplete();
        }
      }
    } catch (err) {
      console.error('Failed to get backfill progress:', err);
    }
  }, [onComplete]);

  useEffect(() => {
    fetchProgress();
    // Poll every 30 seconds
    const interval = setInterval(fetchProgress, 30000);
    return () => clearInterval(interval);
  }, [fetchProgress]);

  if (!progress || progress.status === 'idle') {
    return null;
  }

  // Calculate progress percentage
  const estimatedTotalRequests = 730; // ~2 years of data
  const progressPct = Math.min(
    Math.round((progress.requests_made / estimatedTotalRequests) * 100),
    progress.status === 'completed' ? 100 : 99
  );

  if (isMinimized) {
    return (
      <button
        onClick={() => setIsMinimized(false)}
        className="backfill-banner__minimized"
      >
        <svg
          className="backfill-banner__minimized-icon"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            opacity="0.25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            opacity="0.75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        <span>Syncing {progressPct}%</span>
      </button>
    );
  }

  const statusClass =
    progress.status === 'completed'
      ? 'backfill-banner--complete'
      : progress.status === 'failed'
      ? 'backfill-banner--failed'
      : 'backfill-banner--loading';

  const iconClass =
    progress.status === 'completed'
      ? 'backfill-banner__icon--complete'
      : progress.status === 'failed'
      ? 'backfill-banner__icon--failed'
      : 'backfill-banner__icon--loading';

  const textClass =
    progress.status === 'completed'
      ? 'backfill-banner__text--complete'
      : progress.status === 'failed'
      ? 'backfill-banner__text--failed'
      : 'backfill-banner__text--loading';

  return (
    <div className={`backfill-banner ${statusClass}`}>
      <div className="backfill-banner__header">
        <div className="backfill-banner__title">
          {progress.status === 'completed' ? (
            <svg
              className={`backfill-banner__icon ${iconClass}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          ) : progress.status === 'failed' ? (
            <svg
              className={`backfill-banner__icon ${iconClass}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          ) : (
            <svg
              className={`backfill-banner__icon ${iconClass}`}
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                opacity="0.25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                opacity="0.75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          )}
          <span className={`backfill-banner__text ${textClass}`}>
            {progress.status === 'completed'
              ? 'Data sync complete!'
              : progress.status === 'failed'
              ? 'Data sync failed'
              : 'Syncing historical data...'}
          </span>
        </div>

        {progress.status === 'in_progress' && (
          <button
            onClick={() => setIsMinimized(true)}
            className="backfill-banner__minimize"
          >
            Minimize
          </button>
        )}
      </div>

      {/* Progress bar */}
      {progress.status === 'in_progress' && (
        <>
          <div className="backfill-banner__bar">
            <div
              className="backfill-banner__bar-fill"
              style={{ width: `${progressPct}%` }}
            />
          </div>

          <div className="backfill-banner__stats">
            <span>
              {progress.inserted_records.toLocaleString()} records loaded
            </span>
            <span>
              {progress.estimated_time_remaining_seconds !== null
                ? formatTimeRemaining(progress.estimated_time_remaining_seconds)
                : `${progressPct}%`}
            </span>
          </div>
        </>
      )}

      {progress.status === 'completed' && (
        <p className="backfill-banner__message backfill-banner__message--complete">
          Successfully loaded {progress.inserted_records.toLocaleString()} weather readings.
        </p>
      )}

      {progress.status === 'failed' && (
        <p className="backfill-banner__message backfill-banner__message--failed">{progress.message}</p>
      )}
    </div>
  );
}
