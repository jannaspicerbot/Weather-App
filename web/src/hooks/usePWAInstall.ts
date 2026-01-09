import { useState, useEffect, useCallback } from 'react'

/**
 * BeforeInstallPromptEvent is not in standard TypeScript types
 * This interface extends Event with the PWA-specific properties
 */
interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[]
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed'
    platform: string
  }>
  prompt(): Promise<void>
}

declare global {
  interface WindowEventMap {
    beforeinstallprompt: BeforeInstallPromptEvent
  }
}

interface UsePWAInstallReturn {
  /** Whether the app can be installed (prompt available and not already installed) */
  canInstall: boolean
  /** Whether the app is already installed as a PWA */
  isInstalled: boolean
  /** Whether the install prompt is currently being shown */
  isPrompting: boolean
  /** Trigger the install prompt */
  install: () => Promise<boolean>
  /** The platform the app will be installed on */
  platform: string | null
}

/**
 * Hook to detect PWA installability and trigger the install prompt
 *
 * Usage:
 * ```tsx
 * const { canInstall, isInstalled, install } = usePWAInstall()
 *
 * if (canInstall) {
 *   return <button onClick={install}>Install App</button>
 * }
 * ```
 */
export function usePWAInstall(): UsePWAInstallReturn {
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [isInstalled, setIsInstalled] = useState(false)
  const [isPrompting, setIsPrompting] = useState(false)
  const [platform, setPlatform] = useState<string | null>(null)

  useEffect(() => {
    // Check if already installed as standalone PWA
    const checkInstalled = () => {
      const isStandalone =
        window.matchMedia('(display-mode: standalone)').matches ||
        // iOS Safari specific check
        (window.navigator as Navigator & { standalone?: boolean }).standalone === true

      setIsInstalled(isStandalone)
    }

    checkInstalled()

    // Listen for display mode changes
    const mediaQuery = window.matchMedia('(display-mode: standalone)')
    const handleChange = (e: MediaQueryListEvent) => {
      setIsInstalled(e.matches)
    }
    mediaQuery.addEventListener('change', handleChange)

    // Capture the install prompt event
    const handleBeforeInstallPrompt = (e: BeforeInstallPromptEvent) => {
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault()
      // Store the event for later use
      setInstallPrompt(e)
      // Get the platform
      if (e.platforms && e.platforms.length > 0) {
        setPlatform(e.platforms[0])
      }
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

    // Listen for successful installation
    const handleAppInstalled = () => {
      setIsInstalled(true)
      setInstallPrompt(null)
    }

    window.addEventListener('appinstalled', handleAppInstalled)

    return () => {
      mediaQuery.removeEventListener('change', handleChange)
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
      window.removeEventListener('appinstalled', handleAppInstalled)
    }
  }, [])

  const install = useCallback(async (): Promise<boolean> => {
    if (!installPrompt) {
      return false
    }

    setIsPrompting(true)

    try {
      // Show the install prompt
      await installPrompt.prompt()

      // Wait for the user's choice
      const { outcome } = await installPrompt.userChoice

      if (outcome === 'accepted') {
        setInstallPrompt(null)
        return true
      }

      return false
    } catch (error) {
      console.error('Error during PWA installation:', error)
      return false
    } finally {
      setIsPrompting(false)
    }
  }, [installPrompt])

  return {
    canInstall: installPrompt !== null && !isInstalled,
    isInstalled,
    isPrompting,
    install,
    platform,
  }
}
