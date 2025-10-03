import React, { useState, useEffect } from 'react';
import { 
  ThemeProvider, 
  createTheme, 
  CssBaseline, 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Grid, 
  Paper, 
  Box,
  Card,
  CardContent,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Area,
  AreaChart
} from 'recharts';

// Simple Trading Platform Frontend
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00d4aa',
    },
    secondary: {
      main: '#ff6b6b',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
});

// Historical Data Dialog Component
function HistoricalDataDialog({ open, onClose }) {
  const [symbol, setSymbol] = useState('RELIANCE');
  const [timeframe, setTimeframe] = useState('5minute');
  const [days, setDays] = useState(30);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [symbols, setSymbols] = useState([]);

  // Fetch available symbols
  useEffect(() => {
    if (open) {
      fetch('http://localhost:5000/api/data/symbols')
        .then(response => response.json())
        .then(data => setSymbols(data.symbols || []))
        .catch(error => console.error('Error fetching symbols:', error));
    }
  }, [open]);

  const fetchHistoricalData = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:5000/api/data/historical/${symbol}?timeframe=${timeframe}&days=${days}`
      );
      const result = await response.json();
      setData(result.data || []);
    } catch (error) {
      console.error('Error fetching historical data:', error);
      setData([]);
    }
    setLoading(false);
  };

  const handleSearch = () => {
    fetchHistoricalData();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>📈 Historical Market Data</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 3, mt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                select
                fullWidth
                label="Symbol"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
              >
                {symbols.map((sym) => (
                  <MenuItem key={sym} value={sym}>
                    {sym}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                select
                fullWidth
                label="Timeframe"
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
              >
                <MenuItem value="1minute">1 Minute</MenuItem>
                <MenuItem value="5minute">5 Minute</MenuItem>
                <MenuItem value="15minute">15 Minute</MenuItem>
                <MenuItem value="day">Daily</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                type="number"
                fullWidth
                label="Days"
                value={days}
                onChange={(e) => setDays(e.target.value)}
                inputProps={{ min: 1, max: 365 }}
              />
            </Grid>
          </Grid>
          <Box sx={{ mt: 2 }}>
            <Button 
              variant="contained" 
              onClick={handleSearch}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? 'Loading...' : 'Fetch Data'}
            </Button>
          </Box>
        </Box>

        {data.length > 0 && (
          <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Date/Time</TableCell>
                  <TableCell align="right">Open</TableCell>
                  <TableCell align="right">High</TableCell>
                  <TableCell align="right">Low</TableCell>
                  <TableCell align="right">Close</TableCell>
                  <TableCell align="right">Volume</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.slice(0, 50).map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      {new Date(row.date).toLocaleString()}
                    </TableCell>
                    <TableCell align="right">₹{row.open}</TableCell>
                    <TableCell align="right">₹{row.high}</TableCell>
                    <TableCell align="right">₹{row.low}</TableCell>
                    <TableCell align="right">₹{row.close}</TableCell>
                    <TableCell align="right">{row.volume.toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {data.length > 50 && (
          <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
            Showing first 50 records of {data.length} total records
          </Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [historicalDataOpen, setHistoricalDataOpen] = useState(false);

  useEffect(() => {
    fetch('http://localhost:5000/api/dashboard')
      .then(response => response.json())
      .then(data => {
        setDashboardData(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error fetching dashboard data:', error);
        setIsLoading(false);
      });
  }, []);

  const handleViewHistoricalData = () => {
    setHistoricalDataOpen(true);
  };

  const handleCreateStrategy = () => {
    alert('Strategy Builder coming soon! For now, you can create strategies via the backend API.');
  };

  const handleRunBacktest = () => {
    // Quick backtest demo
    fetch('http://localhost:5000/api/backtest/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: 'Quick Test',
        symbol: 'RELIANCE',
        timeframe: '5minute',
        strategy_id: 1
      })
    })
    .then(response => response.json())
    .then(data => {
      alert(`Backtest completed! Return: ${data.results?.return_percentage?.toFixed(2)}%`);
      // Refresh dashboard
      window.location.reload();
    })
    .catch(error => {
      console.error('Error running backtest:', error);
      alert('Error running backtest');
    });
  };

  const handleMLModels = () => {
    alert('ML Models feature coming soon! The backend already supports ML model training and prediction.');
  };

  if (isLoading) {
    return <Typography>Loading dashboard data...</Typography>;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Strategies
              </Typography>
              <Typography variant="h4" component="div">
                {dashboardData?.summary?.total_strategies || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Backtests
              </Typography>
              <Typography variant="h4" component="div">
                {dashboardData?.summary?.total_backtests || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Kite API Status
              </Typography>
              <Chip 
                label={dashboardData?.summary?.kite_connected ? "Connected" : "Disconnected"} 
                color={dashboardData?.summary?.kite_connected ? "success" : "error"}
              />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Platform Status
              </Typography>
              <Chip label="Online" color="success" />
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Backtests */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Backtests
            </Typography>
            {dashboardData?.recent_backtests?.length > 0 ? (
              <Grid container spacing={2}>
                {dashboardData.recent_backtests.map((backtest, index) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6">{backtest.name}</Typography>
                        <Typography color="textSecondary">
                          Symbol: {backtest.symbol}
                        </Typography>
                        <Typography variant="h4" color="primary">
                          {backtest.return_pct ? `${backtest.return_pct.toFixed(2)}%` : 'N/A'}
                        </Typography>
                        <Typography variant="caption">
                          {new Date(backtest.created_at).toLocaleDateString()}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Typography>No backtests available</Typography>
            )}
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={handleCreateStrategy}
              >
                Create Strategy
              </Button>
              <Button 
                variant="contained" 
                color="secondary"
                onClick={handleRunBacktest}
              >
                Run Backtest
              </Button>
              <Button 
                variant="outlined"
                onClick={handleViewHistoricalData}
              >
                View Historical Data
              </Button>
              <Button 
                variant="outlined"
                onClick={handleMLModels}
              >
                ML Models
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Historical Data Dialog */}
      <HistoricalDataDialog 
        open={historicalDataOpen} 
        onClose={() => setHistoricalDataOpen(false)} 
      />
    </Container>
  );
}

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <div className="App">
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              🚀 Advanced Trading Platform
            </Typography>
            <Typography variant="body2">
              v1.0.0
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Dashboard />
      </div>
    </ThemeProvider>
  );
}

export default App;