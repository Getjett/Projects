import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';

// Layout Components
import MainLayout from './components/Layout/MainLayout';

// Page Components
import Dashboard from './pages/Dashboard';
import StrategyBuilder from './pages/StrategyBuilder';
import BacktestResults from './pages/BacktestResults';
import PatternCreator from './pages/PatternCreator';
import Login from './pages/Login';
import Register from './pages/Register';

function App() {
  return (
    <Box sx={{ display: 'flex' }}>
      <Routes>
        {/* Auth Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Main App Routes */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="strategy-builder" element={<StrategyBuilder />} />
          <Route path="strategy-builder/:id" element={<StrategyBuilder />} />
          <Route path="backtest/:id" element={<BacktestResults />} />
          <Route path="pattern-creator" element={<PatternCreator />} />
        </Route>
        
        {/* 404 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Box>
  );
}

export default App;
