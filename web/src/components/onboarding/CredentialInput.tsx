/**
 * Credential Input Component
 *
 * Form for entering Ambient Weather API credentials.
 * Includes help text and links to get credentials.
 */

import { useState } from 'react';

interface CredentialInputProps {
  onSubmit: (apiKey: string, appKey: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export default function CredentialInput({
  onSubmit,
  isLoading,
  error,
}: CredentialInputProps) {
  const [apiKey, setApiKey] = useState('');
  const [appKey, setAppKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [showAppKey, setShowAppKey] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(apiKey.trim(), appKey.trim());
  };

  const isValid = apiKey.trim().length > 0 && appKey.trim().length > 0;

  return (
    <form onSubmit={handleSubmit} className="credential-form">
      {/* Error message */}
      {error && (
        <div className="credential-form__error">
          <div className="credential-form__error-icon">
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
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
            <p className="credential-form__error-title">Connection Failed</p>
            <p className="credential-form__error-message">{error}</p>
          </div>
        </div>
      )}

      {/* Help text */}
      <div className="credential-form__help">
        <h3 className="credential-form__help-title">
          How to get your API credentials
        </h3>
        <ol className="credential-form__help-list">
          <li>
            Go to{' '}
            <a
              href="https://ambientweather.net/account"
              target="_blank"
              rel="noopener noreferrer"
            >
              ambientweather.net/account
            </a>
          </li>
          <li>Click on "API Keys" in the left sidebar</li>
          <li>Create a new Application Key if you don't have one</li>
          <li>Copy both your API Key and Application Key below</li>
        </ol>
      </div>

      {/* API Key input */}
      <div className="credential-form__field">
        <label htmlFor="apiKey" className="credential-form__label">
          API Key
        </label>
        <div className="credential-form__input-wrapper">
          <input
            type={showApiKey ? 'text' : 'password'}
            id="apiKey"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your Ambient Weather API Key"
            className="credential-form__input"
            disabled={isLoading}
            autoComplete="off"
          />
          <button
            type="button"
            onClick={() => setShowApiKey(!showApiKey)}
            className="credential-form__toggle"
            tabIndex={-1}
            aria-label={showApiKey ? 'Hide API key' : 'Show API key'}
          >
            {showApiKey ? (
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            ) : (
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* App Key input */}
      <div className="credential-form__field">
        <label htmlFor="appKey" className="credential-form__label">
          Application Key
        </label>
        <div className="credential-form__input-wrapper">
          <input
            type={showAppKey ? 'text' : 'password'}
            id="appKey"
            value={appKey}
            onChange={(e) => setAppKey(e.target.value)}
            placeholder="Enter your Ambient Weather Application Key"
            className="credential-form__input"
            disabled={isLoading}
            autoComplete="off"
          />
          <button
            type="button"
            onClick={() => setShowAppKey(!showAppKey)}
            className="credential-form__toggle"
            tabIndex={-1}
            aria-label={showAppKey ? 'Hide application key' : 'Show application key'}
          >
            {showAppKey ? (
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            ) : (
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Submit button */}
      <button
        type="submit"
        disabled={!isValid || isLoading}
        className={`credential-form__submit ${
          isValid && !isLoading
            ? 'credential-form__submit--enabled'
            : 'credential-form__submit--disabled'
        }`}
      >
        {isLoading ? (
          <span className="credential-form__submit-content">
            <svg
              className="credential-form__spinner"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              style={{ width: '1.25rem', height: '1.25rem' }}
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
          'Connect Account'
        )}
      </button>

      {/* Privacy note */}
      <p className="credential-form__privacy">
        Your credentials are stored locally on this server and are never shared with third parties.
      </p>
    </form>
  );
}
