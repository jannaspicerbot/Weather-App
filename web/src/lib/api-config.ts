/**
 * API Configuration
 *
 * Configures the OpenAPI client with the correct base URL.
 * Uses environment variables for flexibility across environments.
 */

import { OpenAPI } from '../api';

// Configure API base URL from environment variable
// In development, use empty string to let Vite proxy handle requests
// In production, set VITE_API_URL to the actual API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/**
 * Initialize the API client with configuration
 * Call this before making any API requests
 */
export function initializeApiClient() {
  OpenAPI.BASE = API_BASE_URL;
  OpenAPI.WITH_CREDENTIALS = false;
  OpenAPI.CREDENTIALS = 'same-origin';
}

/**
 * Update the API base URL dynamically (useful for testing)
 */
export function setApiBaseUrl(url: string) {
  OpenAPI.BASE = url;
}

// Export the configured base URL for reference
export { API_BASE_URL };
