import React, { useState } from 'react';
import TopBar from './TopBar';
import LeftPanel from './LeftPanel';
import CenterPanel from './CenterPanel';
import RightPanel from './RightPanel';
import { StrategyJSON, BacktestResult } from '../types/strategy';

const StrategyTesterPage: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('RELIANCE');
  const [timeframe, setTimeframe] = useState<string>('1D');
  const [dateRange, setDateRange] = useState({
    from: '2024-01-01',
    to: '2024-12-31'
  });
  const [currentStrategy, setCurrentStrategy] = useState<StrategyJSON | null>(null);
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  const handleRunBacktest = async () => {
    if (!currentStrategy) return;
    
    setIsRunning(true);
    try {
      const response = await fetch('/api/backtest/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_json: currentStrategy,
          symbol: selectedSymbol,
          timeframe: timeframe,
          from_date: dateRange.from,
          to_date: dateRange.to,
          mode: 'detailed'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to run backtest');
      }

      const jobData = await response.json();
      
      // Poll for results
      const pollForResults = async (jobId: string) => {
        const resultResponse = await fetch(`/api/backtest/${jobId}/result`);
        if (resultResponse.ok) {
          const result = await resultResponse.json();
          setBacktestResult(result);
        } else {
          // Check job status
          const statusResponse = await fetch(`/api/backtest/${jobId}/status`);
          const statusData = await statusResponse.json();
          
          if (statusData.status === 'completed') {
            const resultResponse = await fetch(`/api/backtest/${jobId}/result`);
            const result = await resultResponse.json();
            setBacktestResult(result);
          } else if (statusData.status === 'failed') {
            throw new Error('Backtest failed');
          } else {
            // Still running, poll again
            setTimeout(() => pollForResults(jobId), 2000);
          }
        }
      };

      await pollForResults(jobData.job_id);
      
    } catch (error) {
      console.error('Backtest error:', error);
      alert('Failed to run backtest: ' + error);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Top Bar */}
      <TopBar
        selectedSymbol={selectedSymbol}
        onSymbolChange={setSelectedSymbol}
        timeframe={timeframe}
        onTimeframeChange={setTimeframe}
        dateRange={dateRange}
        onDateRangeChange={setDateRange}
        onRunBacktest={handleRunBacktest}
        isRunning={isRunning}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Strategy Definition */}
        <div className="w-80 flex-shrink-0 sidebar overflow-y-auto">
          <LeftPanel
            currentStrategy={currentStrategy}
            onStrategyChange={setCurrentStrategy}
          />
        </div>

        {/* Center Panel - Chart */}
        <div className="flex-1 flex flex-col">
          <CenterPanel
            symbol={selectedSymbol}
            timeframe={timeframe}
            dateRange={dateRange}
            backtestResult={backtestResult}
          />
        </div>

        {/* Right Panel - Results */}
        <div className="w-80 flex-shrink-0 overflow-y-auto bg-white border-l border-gray-200">
          <RightPanel
            backtestResult={backtestResult}
            isRunning={isRunning}
          />
        </div>
      </div>
    </div>
  );
};

export default StrategyTesterPage;