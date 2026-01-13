/**
 * Onboarding Flow Component
 *
 * Guides users through setting up their Ambient Weather credentials
 * and initiates the automatic data backfill process.
 */

import { useState } from 'react';
import CredentialInput from './CredentialInput';
import DeviceSelector from './DeviceSelector';
import BackfillProgress from './BackfillProgress';
import {
  validateCredentials,
  saveCredentials,
  startBackfill,
  type DeviceInfo,
} from '../../services/onboardingApi';

type OnboardingStep = 'credentials' | 'device-selection' | 'backfill';

interface OnboardingFlowProps {
  onComplete: () => void;
}

export default function OnboardingFlow({ onComplete }: OnboardingFlowProps) {
  const [step, setStep] = useState<OnboardingStep>('credentials');
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [credentials, setCredentials] = useState<{ apiKey: string; appKey: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

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
        <CredentialInput
          onSubmit={handleCredentialsSubmit}
          isLoading={isLoading}
          error={error}
        />
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
    </div>
  );
}

