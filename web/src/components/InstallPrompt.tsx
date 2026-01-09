/**
 * InstallPrompt Component
 *
 * Displays a PWA install button when the app is installable.
 * Only visible when:
 * - The browser supports PWA installation
 * - The app is not already installed
 * - The beforeinstallprompt event has been captured
 *
 * Follows design-tokens.md specifications for styling.
 */

import { usePWAInstall } from '../hooks/usePWAInstall'
import './InstallPrompt.css'

interface InstallPromptProps {
  /** Whether to show in compact mode (icon only) */
  compact?: boolean
  /** Custom class name */
  className?: string
}

export function InstallPrompt({ compact = false, className = '' }: InstallPromptProps) {
  const { canInstall, isInstalled, isPrompting, install } = usePWAInstall()

  // Don't render if can't install or already installed
  if (!canInstall || isInstalled) {
    return null
  }

  const handleInstall = async () => {
    const success = await install()
    if (success) {
      // Optional: Show success feedback
      console.log('App installed successfully!')
    }
  }

  if (compact) {
    return (
      <button
        className={`install-prompt install-prompt--compact ${className}`}
        onClick={handleInstall}
        disabled={isPrompting}
        aria-label="Install Weather Dashboard as an app"
        title="Install App"
      >
        <svg
          className="install-prompt__icon"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
      </button>
    )
  }

  return (
    <button
      className={`install-prompt ${className}`}
      onClick={handleInstall}
      disabled={isPrompting}
      aria-label="Install Weather Dashboard as an app"
    >
      <svg
        className="install-prompt__icon"
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="7 10 12 15 17 10" />
        <line x1="12" y1="15" x2="12" y2="3" />
      </svg>
      <span className="install-prompt__text">
        {isPrompting ? 'Installing...' : 'Install App'}
      </span>
    </button>
  )
}

export default InstallPrompt
