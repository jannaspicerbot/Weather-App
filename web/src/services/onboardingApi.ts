/**
 * Onboarding API Service
 *
 * Handles API calls for credential validation, saving, and backfill management.
 * Used by the browser-based onboarding flow.
 */

import { API_BASE_URL } from '../lib/api-config';

// Types for API responses
export interface DeviceInfo {
  mac_address: string;
  name: string | null;
  last_data: string | null;
  location: string | null;
}

export interface CredentialStatus {
  configured: boolean;
  has_api_key: boolean;
  has_app_key: boolean;
}

export interface CredentialValidationResponse {
  valid: boolean;
  message: string;
  devices: DeviceInfo[];
}

export interface BackfillProgress {
  progress_id: number | null;
  status: 'idle' | 'in_progress' | 'completed' | 'failed';
  message: string;
  total_records: number;
  inserted_records: number;
  skipped_records: number;
  current_date: string | null;
  start_date: string | null;
  end_date: string | null;
  estimated_time_remaining_seconds: number | null;
  requests_made: number;
  requests_per_second: number;
  records_per_request: number;
}

/**
 * Check if credentials are configured on the server
 */
export async function getCredentialStatus(): Promise<CredentialStatus> {
  const response = await fetch(`${API_BASE_URL}/api/credentials/status`);
  if (!response.ok) {
    throw new Error('Failed to check credential status');
  }
  return response.json();
}

/**
 * Validate API credentials without saving them
 */
export async function validateCredentials(
  apiKey: string,
  appKey: string
): Promise<CredentialValidationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/credentials/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      api_key: apiKey,
      app_key: appKey,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Validation failed');
  }

  return response.json();
}

/**
 * Save validated credentials to the server's .env file
 * Optionally saves device MAC address selection
 */
export async function saveCredentials(
  apiKey: string,
  appKey: string,
  deviceMac?: string
): Promise<{ success: boolean; message: string }> {
  const body: { api_key: string; app_key: string; device_mac?: string } = {
    api_key: apiKey,
    app_key: appKey,
  };

  if (deviceMac) {
    body.device_mac = deviceMac;
  }

  const response = await fetch(`${API_BASE_URL}/api/credentials/save`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to save credentials');
  }

  return response.json();
}

/**
 * Get current backfill progress
 */
export async function getBackfillProgress(): Promise<BackfillProgress> {
  const response = await fetch(`${API_BASE_URL}/api/backfill/progress`);
  if (!response.ok) {
    throw new Error('Failed to get backfill progress');
  }
  return response.json();
}

/**
 * Start the backfill process
 */
export async function startBackfill(
  apiKey?: string,
  appKey?: string
): Promise<BackfillProgress> {
  const body: { api_key?: string; app_key?: string } = {};
  if (apiKey) body.api_key = apiKey;
  if (appKey) body.app_key = appKey;

  const response = await fetch(`${API_BASE_URL}/api/backfill/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to start backfill');
  }

  return response.json();
}

/**
 * Stop the current backfill process
 */
export async function stopBackfill(): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/backfill/stop`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to stop backfill');
  }

  return response.json();
}

/**
 * Get list of available devices (requires credentials to be configured)
 */
export async function getDevices(): Promise<{ devices: DeviceInfo[]; selected_device_mac: string | null }> {
  const response = await fetch(`${API_BASE_URL}/api/devices`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to fetch devices');
  }

  return response.json();
}

/**
 * Save device selection
 */
export async function selectDevice(deviceMac: string): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/devices/select`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      device_mac: deviceMac,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to save device selection');
  }

  return response.json();
}

/**
 * Format seconds to human-readable time string
 */
export function formatTimeRemaining(seconds: number | null): string {
  if (seconds === null || seconds <= 0) return '';

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m remaining`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s remaining`;
  } else {
    return `${secs}s remaining`;
  }
}
