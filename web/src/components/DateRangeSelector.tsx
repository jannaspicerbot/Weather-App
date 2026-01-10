/**
 * Date Range Selector Component
 *
 * Allows users to select a date range for historical data viewing
 */

import { useState } from 'react';

interface DateRangeSelectorProps {
  start: Date;
  end: Date;
  onChange: (start: Date, end: Date) => void;
  onExport: () => void;
}

export default function DateRangeSelector({ start, end, onChange, onExport }: DateRangeSelectorProps) {
  const [startDate, setStartDate] = useState(start.toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(end.toISOString().split('T')[0]);
  const [activePreset, setActivePreset] = useState<'24h' | '7d' | '30d' | '1y' | null>('24h');

  const handleApply = () => {
    // Parse dates in local timezone at start of day
    const newStart = new Date(startDate + 'T00:00:00');
    const newEnd = new Date(endDate + 'T23:59:59');

    if (newStart > newEnd) {
      alert('Start date must be before end date');
      return;
    }

    setActivePreset(null); // Clear preset when using custom dates
    onChange(newStart, newEnd);
  };

  const handlePreset = (preset: '24h' | '7d' | '30d' | '1y') => {
    const now = new Date();
    // Set end to end of current day
    const newEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
    let newStart: Date;

    switch (preset) {
      case '24h':
        // Start 24 hours ago
        newStart = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        break;
      case '7d':
        // Start at beginning of day 7 days ago (not 8 days)
        newStart = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 6, 0, 0, 0);
        break;
      case '30d':
        // Start at beginning of day 30 days ago (not 31 days)
        newStart = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 29, 0, 0, 0);
        break;
      case '1y':
        // Start at beginning of day 365 days ago
        newStart = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 364, 0, 0, 0);
        break;
    }

    setStartDate(newStart.toISOString().split('T')[0]);
    setEndDate(newEnd.toISOString().split('T')[0]);
    setActivePreset(preset);
    onChange(newStart, newEnd);
  };

  return (
    <div className="date-range">
      <h3 className="date-range__title">Date Range</h3>

      <div className="date-range__controls">
        {/* Quick Preset Buttons */}
        <div className="date-range__presets">
          <button
            onClick={() => handlePreset('24h')}
            className={`date-range__preset ${
              activePreset === '24h'
                ? 'date-range__preset--active'
                : 'date-range__preset--inactive'
            }`}
          >
            Last 24h
          </button>
          <button
            onClick={() => handlePreset('7d')}
            className={`date-range__preset ${
              activePreset === '7d'
                ? 'date-range__preset--active'
                : 'date-range__preset--inactive'
            }`}
          >
            Last 7 Days
          </button>
          <button
            onClick={() => handlePreset('30d')}
            className={`date-range__preset ${
              activePreset === '30d'
                ? 'date-range__preset--active'
                : 'date-range__preset--inactive'
            }`}
          >
            Last 30 Days
          </button>
          <button
            onClick={() => handlePreset('1y')}
            className={`date-range__preset ${
              activePreset === '1y'
                ? 'date-range__preset--active'
                : 'date-range__preset--inactive'
            }`}
          >
            Last Year
          </button>
        </div>

        {/* Custom Date Inputs */}
        <div className="date-range__custom">
          <div className="date-range__field">
            <label htmlFor="start-date" className="date-range__label">
              Start Date
            </label>
            <input
              id="start-date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="date-range__input"
            />
          </div>

          <div className="date-range__field">
            <label htmlFor="end-date" className="date-range__label">
              End Date
            </label>
            <input
              id="end-date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="date-range__input"
            />
          </div>

          <button
            onClick={handleApply}
            className="date-range__apply"
          >
            Apply
          </button>
        </div>

        {/* Export Button */}
        <div className="date-range__export">
          <button
            onClick={onExport}
            className="date-range__export-btn"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export CSV
          </button>
        </div>
      </div>
    </div>
  );
}
