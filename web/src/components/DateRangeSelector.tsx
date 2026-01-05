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

  const handleApply = () => {
    const newStart = new Date(startDate);
    const newEnd = new Date(endDate);

    if (newStart > newEnd) {
      alert('Start date must be before end date');
      return;
    }

    onChange(newStart, newEnd);
  };

  const handlePreset = (preset: '24h' | '7d' | '30d' | '1y') => {
    const now = new Date();
    const newEnd = now;
    let newStart: Date;

    switch (preset) {
      case '24h':
        newStart = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        break;
      case '7d':
        newStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        newStart = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case '1y':
        newStart = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
        break;
    }

    setStartDate(newStart.toISOString().split('T')[0]);
    setEndDate(newEnd.toISOString().split('T')[0]);
    onChange(newStart, newEnd);
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Date Range</h3>

      <div className="flex flex-wrap gap-4 items-end">
        {/* Quick Preset Buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => handlePreset('24h')}
            className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm font-medium transition-colors"
          >
            Last 24h
          </button>
          <button
            onClick={() => handlePreset('7d')}
            className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm font-medium transition-colors"
          >
            Last 7 Days
          </button>
          <button
            onClick={() => handlePreset('30d')}
            className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm font-medium transition-colors"
          >
            Last 30 Days
          </button>
          <button
            onClick={() => handlePreset('1y')}
            className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm font-medium transition-colors"
          >
            Last Year
          </button>
        </div>

        {/* Custom Date Inputs */}
        <div className="flex gap-2 items-center">
          <div>
            <label htmlFor="start-date" className="block text-xs text-gray-600 mb-1">
              Start Date
            </label>
            <input
              id="start-date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            />
          </div>

          <div>
            <label htmlFor="end-date" className="block text-xs text-gray-600 mb-1">
              End Date
            </label>
            <input
              id="end-date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            />
          </div>

          <button
            onClick={handleApply}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium transition-colors"
          >
            Apply
          </button>
        </div>

        {/* Export Button */}
        <div className="ml-auto">
          <button
            onClick={onExport}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export CSV
          </button>
        </div>
      </div>
    </div>
  );
}
