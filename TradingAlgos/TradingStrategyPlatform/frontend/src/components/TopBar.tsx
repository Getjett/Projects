import React from 'react';
import { DateRange } from '../types/strategy';

interface TopBarProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
  timeframe: string;
  onTimeframeChange: (timeframe: string) => void;
  dateRange: DateRange;
  onDateRangeChange: (range: DateRange) => void;
  onRunBacktest: () => void;
  isRunning: boolean;
}

const TopBar: React.FC<TopBarProps> = ({
  selectedSymbol,
  onSymbolChange,
  timeframe,
  onTimeframeChange,
  dateRange,
  onDateRangeChange,
  onRunBacktest,
  isRunning
}) => {
  const symbols = [
    'RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK', 
    'KOTAKBANK', 'HDFCBANK', 'BHARTIARTL', 'ITC', 'SBIN'
  ];

  const timeframes = [
    { value: '1m', label: '1 Min' },
    { value: '5m', label: '5 Min' },
    { value: '15m', label: '15 Min' },
    { value: '1h', label: '1 Hour' },
    { value: '1D', label: '1 Day' }
  ];

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-6">
          {/* Symbol Selector */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Symbol:</label>
            <select
              value={selectedSymbol}
              onChange={(e) => onSymbolChange(e.target.value)}
              className="input-field w-32"
            >
              {symbols.map(symbol => (
                <option key={symbol} value={symbol}>
                  {symbol}
                </option>
              ))}
            </select>
          </div>

          {/* Timeframe Selector */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Timeframe:</label>
            <select
              value={timeframe}
              onChange={(e) => onTimeframeChange(e.target.value)}
              className="input-field w-24"
            >
              {timeframes.map(tf => (
                <option key={tf.value} value={tf.value}>
                  {tf.label}
                </option>
              ))}
            </select>
          </div>

          {/* Date Range Picker */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">From:</label>
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) => onDateRangeChange({ ...dateRange, from: e.target.value })}
              className="input-field w-36"
            />
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">To:</label>
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) => onDateRangeChange({ ...dateRange, to: e.target.value })}
              className="input-field w-36"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-4">
          <button
            onClick={onRunBacktest}
            disabled={isRunning}
            className={`px-6 py-2 rounded-md font-medium ${
              isRunning 
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                : 'bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500'
            }`}
          >
            {isRunning ? 'Running...' : 'Run Backtest'}
          </button>

          <button
            className="button-secondary"
            disabled={isRunning}
          >
            Replay
          </button>

          <button
            className="button-secondary"
            disabled={isRunning}
          >
            Stop
          </button>
        </div>
      </div>
    </div>
  );
};

export default TopBar;