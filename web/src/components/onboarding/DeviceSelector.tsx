/**
 * Device Selector Component
 *
 * Allows users to select which weather device/station to use.
 * Displayed during onboarding after credential validation.
 */

import { useState } from 'react';
import { type DeviceInfo } from '../../services/onboardingApi';

interface DeviceSelectorProps {
  devices: DeviceInfo[];
  onSelect: (deviceMac: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export default function DeviceSelector({
  devices,
  onSelect,
  isLoading,
  error,
}: DeviceSelectorProps) {
  const [selectedMac, setSelectedMac] = useState<string>(
    devices.length > 0 ? devices[0].mac_address : ''
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedMac) {
      await onSelect(selectedMac);
    }
  };

  if (devices.length === 0) {
    return (
      <div className="device-selector">
        <div className="device-selector__error">
          <p>No weather stations found in your account.</p>
          <p>Please check your Ambient Weather account and try again.</p>
        </div>
      </div>
    );
  }

  // If only one device, auto-select it and show confirmation
  if (devices.length === 1) {
    const device = devices[0];
    return (
      <form onSubmit={handleSubmit} className="device-selector">
        {error && (
          <div className="device-selector__error">
            <p>{error}</p>
          </div>
        )}

        <div className="device-selector__single">
          <div className="device-selector__icon">
            <svg
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div className="device-selector__single-info">
            <h3 className="device-selector__single-title">Weather Station Found</h3>
            <p className="device-selector__single-name">
              {device.name || 'Weather Station'}
            </p>
            {device.location && (
              <p className="device-selector__single-location">
                {device.location}
              </p>
            )}
            <p className="device-selector__single-mac">
              Device ID: {device.mac_address.slice(0, 8)}...
            </p>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className={`device-selector__submit ${
            isLoading
              ? 'device-selector__submit--disabled'
              : 'device-selector__submit--enabled'
          }`}
        >
          {isLoading ? (
            <span className="device-selector__submit-content">
              <svg
                className="device-selector__spinner"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                aria-hidden="true"
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
              Connecting...
            </span>
          ) : (
            'Continue with This Device'
          )}
        </button>
      </form>
    );
  }

  // Multiple devices - show selection list
  return (
    <form onSubmit={handleSubmit} className="device-selector">
      {error && (
        <div className="device-selector__error">
          <p>{error}</p>
        </div>
      )}

      <div className="device-selector__help">
        <h3 className="device-selector__help-title">
          Select Your Weather Station
        </h3>
        <p className="device-selector__help-text">
          We found {devices.length} weather stations in your account.
          Choose which one you'd like to use for this dashboard.
        </p>
      </div>

      <div className="device-selector__list">
        {devices.map((device) => (
          <label
            key={device.mac_address}
            className={`device-selector__option ${
              selectedMac === device.mac_address
                ? 'device-selector__option--selected'
                : ''
            }`}
          >
            <input
              type="radio"
              name="device"
              value={device.mac_address}
              checked={selectedMac === device.mac_address}
              onChange={(e) => setSelectedMac(e.target.value)}
              className="device-selector__radio"
            />
            <div className="device-selector__option-content">
              <div className="device-selector__option-header">
                <span className="device-selector__option-name">
                  {device.name || 'Weather Station'}
                </span>
                {selectedMac === device.mac_address && (
                  <svg
                    className="device-selector__option-check"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </div>
              <div className="device-selector__option-details">
                {device.location && (
                  <span className="device-selector__option-location">
                    {device.location}
                  </span>
                )}
                <span className="device-selector__option-mac">
                  {device.location ? '•' : 'Device ID:'} {device.mac_address.slice(0, 12)}...
                </span>
                {device.last_data && (
                  <>
                    <span className="device-selector__option-divider">•</span>
                    <span className="device-selector__option-date">
                      Last data: {new Date(device.last_data).toLocaleDateString()}
                    </span>
                  </>
                )}
              </div>
            </div>
          </label>
        ))}
      </div>

      <button
        type="submit"
        disabled={!selectedMac || isLoading}
        className={`device-selector__submit ${
          selectedMac && !isLoading
            ? 'device-selector__submit--enabled'
            : 'device-selector__submit--disabled'
        }`}
      >
        {isLoading ? (
          <span className="device-selector__submit-content">
            <svg
              className="device-selector__spinner"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
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
            Connecting...
          </span>
        ) : (
          'Continue with Selected Device'
        )}
      </button>

      <p className="device-selector__note">
        You can change your device selection later in the dashboard settings.
      </p>
    </form>
  );
}
