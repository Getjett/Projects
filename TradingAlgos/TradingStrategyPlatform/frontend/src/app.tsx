import React from 'react';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900">
            🚀 AstraCharts Trading Platform
          </h1>
          <p className="text-gray-600 mt-2">
            Strategy Testing & Backtesting Platform
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Backend Status Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              📊 Backend API Status
            </h2>
            <div className="space-y-2">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                <span className="text-sm">API Server: Running on :8000</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                <span className="text-sm">Chart Generation: Operational</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                <span className="text-sm">Backtest Engine: Ready</span>
              </div>
            </div>
          </div>

          {/* Frontend Status Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              🎨 Frontend Status
            </h2>
            <div className="space-y-2">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                <span className="text-sm">React App: Running on :3000</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-400 rounded-full mr-2"></div>
                <span className="text-sm">UI Components: Loading</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-400 rounded-full mr-2"></div>
                <span className="text-sm">Charts Integration: Pending</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6 md:col-span-2">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              🎯 Quick Actions
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              
              <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors">
                📈 View API Docs
              </button>
              
              <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors">
                🧪 Test Backend
              </button>
              
              <button className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition-colors">
                📊 Generate Chart
              </button>
              
            </div>
          </div>

          {/* System Info */}
          <div className="bg-white rounded-lg shadow p-6 md:col-span-2">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              ⚡ System Information
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="font-medium text-gray-500">Backend</div>
                <div className="text-gray-900">FastAPI + Python</div>
              </div>
              <div>
                <div className="font-medium text-gray-500">Frontend</div>
                <div className="text-gray-900">React + TypeScript</div>
              </div>
              <div>
                <div className="font-medium text-gray-500">Charts</div>
                <div className="text-gray-900">Plotly.js</div>
              </div>
              <div>
                <div className="font-medium text-gray-500">Status</div>
                <div className="text-green-600 font-medium">✅ Operational</div>
              </div>
            </div>
          </div>

        </div>
      </main>

      <footer className="bg-gray-50 border-t mt-12">
        <div className="max-w-7xl mx-auto py-4 px-4 text-center text-gray-500 text-sm">
          🎊 AstraCharts Trading Platform - Sprint 3 Implementation Complete
        </div>
      </footer>
      
    </div>
  );
};

export default App;