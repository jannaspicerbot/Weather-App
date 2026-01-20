/**
 * Onboarding Flow Component
 *
 * Guides users through setting up their Ambient Weather credentials
 * and initiates the automatic data backfill process.
 */

import { useState, useRef, useEffect } from 'react';
import CredentialInput from './CredentialInput';
import DeviceSelector from './DeviceSelector';
import BackfillProgress from './BackfillProgress';
import {
  validateCredentials,
  saveCredentials,
  startBackfill,
  enableDemoMode,
  generateDemoDatabase,
  getDemoStatus,
  cancelGeneration,
  type DeviceInfo,
  type DemoGenerationProgress,
} from '../../services/onboardingApi';

type OnboardingStep = 'credentials' | 'device-selection' | 'backfill' | 'demo-generating';

interface OnboardingFlowProps {
  onComplete: () => void;
  onDemoModeEnabled?: () => void;
}

export default function OnboardingFlow({ onComplete, onDemoModeEnabled }: OnboardingFlowProps) {
  const [step, setStep] = useState<OnboardingStep>('credentials');
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [credentials, setCredentials] = useState<{ apiKey: string; appKey: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const [demoAvailable, setDemoAvailable] = useState<boolean | null>(null);

  // Demo generation state
  const [generationProgress, setGenerationProgress] = useState<DemoGenerationProgress | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Check if demo mode is available on mount
  useEffect(() => {
    getDemoStatus()
      .then((status) => setDemoAvailable(status.available || !status.generation_required))
      .catch(() => setDemoAvailable(true)); // Allow demo even if status check fails
  }, []);

  // Cleanup abort controller on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const handleDemoModeClick = async () => {
    setError(null);
    setIsDemoLoading(true);

    try {
      const status = await enableDemoMode();

      // Check if generation is required
      if (status.generation_required) {
        // Switch to generation step
        setStep('demo-generating');
        setIsDemoLoading(false);

        // Start generation with progress tracking
        abortControllerRef.current = new AbortController();

        try {
          await generateDemoDatabase(
            (progress) => {
              setGenerationProgress(progress);
            },
            abortControllerRef.current.signal
          );

          // Generation complete - now enable demo mode
          const enableStatus = await enableDemoMode();
          if (enableStatus.enabled) {
            if (onDemoModeEnabled) {
              onDemoModeEnabled();
            } else {
              onComplete();
            }
          } else {
            setError('Failed to enable demo mode after generation');
            setStep('credentials');
          }
        } catch (genErr) {
          if (genErr instanceof Error && genErr.name === 'AbortError') {
            // User cancelled - go back to credentials
            setStep('credentials');
          } else {
            setError(genErr instanceof Error ? genErr.message : 'Demo generation failed');
            setStep('credentials');
          }
        }
        return;
      }

      // Database already exists - demo mode enabled
      if (onDemoModeEnabled) {
        onDemoModeEnabled();
      } else {
        onComplete();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to enable demo mode');
    } finally {
      setIsDemoLoading(false);
    }
  };

  const handleCancelGeneration = async () => {
    // Abort the local request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    // Also cancel on the backend to stop actual generation
    try {
      await cancelGeneration();
    } catch {
      // Ignore cancellation errors - generation may already be stopped
    }

    setStep('credentials');
    setGenerationProgress(null);
  };

  const handleCredentialsSubmit = async (apiKey: string, appKey: string) => {
    setError(null);
    setIsLoading(true);

    try {
      // Step 1: Validate credentials
      const validation = await validateCredentials(apiKey, appKey);

      if (!validation.valid) {
        setError(validation.message);
        setIsLoading(false);
        return;
      }

      // Save credentials and devices for next step
      setCredentials({ apiKey, appKey });
      setDevices(validation.devices);

      // Move to device selection step
      setStep('device-selection');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeviceSelect = async (deviceMac: string) => {
    if (!credentials) return;

    setError(null);
    setIsLoading(true);

    try {
      // Step 2: Save credentials with device selection to .env file
      await saveCredentials(credentials.apiKey, credentials.appKey, deviceMac);

      // Step 3: Start backfill automatically
      await startBackfill(credentials.apiKey, credentials.appKey);

      // Move to backfill step
      setStep('backfill');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackfillComplete = () => {
    onComplete();
  };

  return (
    <div className="onboarding">
      {/* Header */}
      <div className="onboarding__header">
        <h2 className="onboarding__title">
          Welcome to Weather Dashboard
        </h2>
        <p className="onboarding__subtitle">
          {step === 'credentials'
            ? 'Connect your Ambient Weather account to get started.'
            : step === 'device-selection'
            ? 'Choose your weather station.'
            : step === 'demo-generating'
            ? 'Creating sample weather data...'
            : 'Setting up your weather data...'}
        </p>
      </div>

      {/* Progress indicator - 3 steps now */}
      <div className="onboarding__steps">
        {/* Step 1: Credentials */}
        <div className="onboarding__step">
          <div
            className={`onboarding__step-circle ${
              step === 'credentials'
                ? 'onboarding__step-circle--active'
                : 'onboarding__step-circle--complete'
            }`}
          >
            {step === 'credentials' ? '1' : (
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
          <span className={`onboarding__step-label ${step === 'credentials' ? 'onboarding__step-label--active' : ''}`}>
            Connect Account
          </span>
        </div>

        {/* Connector line */}
        <div
          className={`onboarding__step-connector ${
            step === 'device-selection' || step === 'backfill' ? 'onboarding__step-connector--complete' : ''
          }`}
        />

        {/* Step 2: Device Selection */}
        <div className="onboarding__step">
          <div
            className={`onboarding__step-circle ${
              step === 'device-selection'
                ? 'onboarding__step-circle--active'
                : step === 'backfill'
                ? 'onboarding__step-circle--complete'
                : 'onboarding__step-circle--pending'
            }`}
          >
            {step === 'backfill' ? (
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              '2'
            )}
          </div>
          <span className={`onboarding__step-label ${step === 'device-selection' ? 'onboarding__step-label--active' : ''}`}>
            Select Device
          </span>
        </div>

        {/* Connector line 2 */}
        <div
          className={`onboarding__step-connector ${
            step === 'backfill' ? 'onboarding__step-connector--complete' : ''
          }`}
        />

        {/* Step 3 */}
        <div className="onboarding__step">
          <div
            className={`onboarding__step-circle ${
              step === 'backfill'
                ? 'onboarding__step-circle--active'
                : 'onboarding__step-circle--pending'
            }`}
          >
            3
          </div>
          <span className={`onboarding__step-label ${step === 'backfill' ? 'onboarding__step-label--active' : ''}`}>
            Load Data
          </span>
        </div>
      </div>

      {/* Content */}
      {step === 'credentials' && (
        <>
          <CredentialInput
            onSubmit={handleCredentialsSubmit}
            isLoading={isLoading}
            error={error}
          />

          {/* Demo Mode Section */}
          {demoAvailable && (
            <div className="onboarding__demo-section">
              <div className="onboarding__demo-divider">
                <span>or</span>
              </div>
              <button
                type="button"
                className="onboarding__demo-button"
                onClick={handleDemoModeClick}
                disabled={isDemoLoading || isLoading}
              >
                {isDemoLoading ? (
                  <>
                    <span className="onboarding__demo-spinner" aria-hidden="true" />
                    Loading Demo...
                  </>
                ) : (
                  <>
                    <svg
                      className="onboarding__demo-icon"
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
                    Try Demo Mode
                  </>
                )}
              </button>
              <p className="onboarding__demo-description">
                Explore with sample Seattle weather data - no device required
              </p>
            </div>
          )}
        </>
      )}

      {step === 'device-selection' && (
        <DeviceSelector
          devices={devices}
          onSelect={handleDeviceSelect}
          isLoading={isLoading}
          error={error}
        />
      )}

      {step === 'backfill' && (
        <BackfillProgress
          devices={devices}
          onComplete={handleBackfillComplete}
        />
      )}

      {step === 'demo-generating' && (
        <div className="onboarding__demo-generation">
          <div className="onboarding__demo-generation-content">
            <h3 className="onboarding__demo-generation-title">
              Generating Demo Data
            </h3>
            <p className="onboarding__demo-generation-description">
              Creating 3 years of realistic Seattle weather data.
              This may take a few minutes.
            </p>

            {/* Progress bar */}
            <div className="onboarding__demo-progress">
              <div className="onboarding__demo-progress-bar">
                <div
                  className="onboarding__demo-progress-fill"
                  style={{ width: `${generationProgress?.percent || 0}%` }}
                />
              </div>
              <div className="onboarding__demo-progress-text">
                {generationProgress?.percent !== undefined ? (
                  <>
                    <span className="onboarding__demo-progress-percent">
                      {generationProgress.percent}%
                    </span>
                    {generationProgress.current_day !== undefined && generationProgress.total_days !== undefined && (
                      <span className="onboarding__demo-progress-days">
                        Day {generationProgress.current_day.toLocaleString()} of {generationProgress.total_days.toLocaleString()}
                      </span>
                    )}
                  </>
                ) : (
                  <span className="onboarding__demo-progress-starting">Starting...</span>
                )}
              </div>
            </div>

            {/* Cancel button */}
            <button
              type="button"
              className="onboarding__demo-cancel-button"
              onClick={handleCancelGeneration}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

