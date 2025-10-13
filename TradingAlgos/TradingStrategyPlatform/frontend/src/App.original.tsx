import React, { useState } from 'react';
import StrategyTesterPage from './components/StrategyTesterPage';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-gray-900">
                  AstraCharts Trading Platform
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <nav className="flex space-x-8">
                <a
                  href="#"
                  className="text-primary-600 hover:text-primary-800 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Live Chart
                </a>
                <a
                  href="#"
                  className="text-gray-900 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium bg-gray-100"
                >
                  Strategy Tester
                </a>
                <a
                  href="#"
                  className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Saved Strategies
                </a>
              </nav>
            </div>
          </div>
        </div>
      </header>

      <main>
        <StrategyTesterPage />
      </main>
    </div>
  );
};

export default App;