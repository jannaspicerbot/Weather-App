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
      <div className="mb-6 text-center">
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
        {/* Step 1 */}
        <div className="flex flex-col items-center">
          <div
            className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
              step === 'credentials'
                ? 'bg-blue-600 text-white'
                : 'bg-green-500 text-white'
            }`}
          >
            {step === 'credentials' ? '1' : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
          <span className={`mt-2 text-sm ${step === 'credentials' ? 'text-blue-600 font-medium' : 'text-gray-500'}`}>
            Connect Account
          </span>
        </div>

        {/* Connector line */}
        <div
          className={`flex-1 h-1 mx-4 mb-6 ${
            step === 'backfill' ? 'bg-blue-600' : 'bg-gray-200'
          }`}
        />

        {/* Step 2 */}
        <div className="flex flex-col items-center">
          <div
            className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
              step === 'backfill'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-500'
            }`}
          >
            2
          </div>
          <span className={`mt-2 text-sm ${step === 'backfill' ? 'text-blue-600 font-medium' : 'text-gray-500'}`}>
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

      {step === 'backfill' && (
        <BackfillProgress
          devices={devices}
          onComplete={handleBackfillComplete}
        />
      )}
    </div>
  );
}
