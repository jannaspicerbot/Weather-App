import { useState, useEffect, useRef } from 'react';
import { getDevices, selectDevice, type DeviceInfo } from '../services/onboardingApi';

/**
 * DeviceManager Component
 *
 * Allows users to view and switch between weather stations after initial onboarding.
 * Displays current device and provides dropdown to select different device.
 *
 * Features:
 * - Shows currently selected device in header
 * - Dropdown menu to view all devices
 * - Click to switch devices
 * - Refreshes dashboard data after switch
 * - Error handling and loading states
 */
export default function DeviceManager() {
  const [isOpen, setIsOpen] = useState(false);
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [currentDevice, setCurrentDevice] = useState<DeviceInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Load devices on mount
  useEffect(() => {
    loadDevices();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const loadDevices = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getDevices();
      setDevices(response.devices);

      // Find currently selected device
      const selected = response.devices.find(d => d.mac_address === response.selected_device_mac);
      setCurrentDevice(selected || response.devices[0] || null);
    } catch (err) {
      console.error('Failed to load devices:', err);
      setError('Failed to load devices');
    } finally {
      setLoading(false);
    }
  };

  const handleDeviceSelect = async (deviceMac: string) => {
    if (deviceMac === currentDevice?.mac_address) {
      setIsOpen(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await selectDevice(deviceMac);

      // Update current device
      const selected = devices.find(d => d.mac_address === deviceMac);
      setCurrentDevice(selected || null);

      setIsOpen(false);

      // Reload page to refresh all data with new device
      window.location.reload();
    } catch (err) {
      console.error('Failed to switch device:', err);
      setError('Failed to switch device');
    } finally {
      setLoading(false);
    }
  };

  const formatLastData = (lastData: string | null): string => {
    if (!lastData) return 'No data';

    try {
      const date = new Date(lastData);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
      return `${Math.floor(diffMins / 1440)}d ago`;
    } catch {
      return 'Unknown';
    }
  };

  const formatMacAddress = (mac: string): string => {
    // Show last 4 octets for brevity
    const parts = mac.split(':');
    if (parts.length >= 4) {
      return parts.slice(-4).join(':');
    }
    return mac;
  };

  if (loading && !currentDevice) {
    return (
      <div className="device-manager">
        <button className="device-manager__button" disabled>
          <span className="device-manager__icon">📡</span>
          <span className="device-manager__label">Loading...</span>
        </button>
      </div>
    );
  }

  if (error && !currentDevice) {
    return (
      <div className="device-manager">
        <button className="device-manager__button device-manager__button--error" disabled>
          <span className="device-manager__icon">⚠️</span>
          <span className="device-manager__label">Error</span>
        </button>
      </div>
    );
  }

  return (
    <div className="device-manager" ref={dropdownRef}>
      <button
        className="device-manager__button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Device selection menu"
        aria-expanded={isOpen}
        disabled={loading}
      >
        <span className="device-manager__icon">📡</span>
        <span className="device-manager__label">
          {currentDevice?.name || formatMacAddress(currentDevice?.mac_address || '')}
        </span>
        <span className="device-manager__chevron">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className="device-manager__dropdown">
          <div className="device-manager__dropdown-header">
            <h3>Select Weather Station</h3>
            {devices.length > 1 && (
              <span className="device-manager__count">{devices.length} devices</span>
            )}
          </div>

          {error && (
            <div className="device-manager__error">
              {error}
            </div>
          )}

          <div className="device-manager__list">
            {devices.map((device) => {
              const isSelected = device.mac_address === currentDevice?.mac_address;

              return (
                <button
                  key={device.mac_address}
                  className={`device-manager__option ${isSelected ? 'device-manager__option--selected' : ''}`}
                  onClick={() => handleDeviceSelect(device.mac_address)}
                  disabled={loading}
                >
                  <div className="device-manager__option-header">
                    <div className="device-manager__option-name">
                      {device.name || 'Unnamed Device'}
                    </div>
                    {isSelected && (
                      <span className="device-manager__selected-badge">
                        ✓ Active
                      </span>
                    )}
                  </div>

                  <div className="device-manager__option-details">
                    {device.location && (
                      <>
                        <span className="device-manager__location">
                          {device.location}
                        </span>
                        <span className="device-manager__divider">•</span>
                      </>
                    )}
                    <span className="device-manager__mac">
                      {formatMacAddress(device.mac_address)}
                    </span>
                    <span className="device-manager__divider">•</span>
                    <span className="device-manager__last-data">
                      {formatLastData(device.last_data)}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          {devices.length === 0 && (
            <div className="device-manager__empty">
              No devices found
            </div>
          )}
        </div>
      )}
    </div>
  );
}
