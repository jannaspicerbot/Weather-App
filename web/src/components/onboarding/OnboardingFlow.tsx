/**
 * Onboarding Flow Component
 *
 * Guides users through setting up their Ambient Weather credentials
 * and initiates the automatic data backfill process.
 */

import { useState } from 'react';
import CredentialInput from './CredentialInput';
import BackfillProgress from './BackfillProgress';
import {
  validateCredentials,
  saveCredentials,
  startBackfill,
  type DeviceInfo,
} from '../../services/onboardingApi';

type OnboardingStep = 'credentials' | 'backfill';

interface OnboardingFlowProps {
  onComplete: () => void;
}

export default function OnboardingFlow({ onComplete }: OnboardingFlowProps) {
  const [step, setStep] = useState<OnboardingStep>('credentials');
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
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

      setDevices(validation.devices);

      // Step 2: Save credentials to .env file
      await saveCredentials(apiKey, appKey);

      // Step 3: Start backfill automatically (per user preference)
      await startBackfill(apiKey, appKey);

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
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome to Weather Dashboard
        </h2>
        <p className="text-gray-600">
          {step === 'credentials'
            ? 'Connect your Ambient Weather account to get started.'
            : 'Setting up your weather data...'}
        </p>
      </div>

      {/* Progress indicator */}
      <div className="flex items-center mb-8">
        <div
          className={`flex items-center justify-center w-8 h-8 rounded-full ${
            step === 'credentials'
              ? 'bg-blue-600 text-white'
              : 'bg-green-500 text-white'
          }`}
        >
          {step === 'credentials' ? '1' : '✓'}
        </div>
        <div
          className={`flex-1 h-1 mx-2 ${
            step === 'backfill' ? 'bg-blue-600' : 'bg-gray-200'
          }`}
        />
        <div
          className={`flex items-center justify-center w-8 h-8 rounded-full ${
            step === 'backfill'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-500'
          }`}
        >
          2
        </div>
      </div>

      {/* Step labels */}
      <div className="flex justify-between text-sm text-gray-500 mb-6 -mt-4">
        <span className={step === 'credentials' ? 'text-blue-600 font-medium' : ''}>
          Connect Account
        </span>
        <span className={step === 'backfill' ? 'text-blue-600 font-medium' : ''}>
          Load Data
        </span>
      </div>

      {/* Content */}
      {step === 'credentials' && (
        <CredentialInput
          onSubmit={handleCredentialsSubmit}
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
