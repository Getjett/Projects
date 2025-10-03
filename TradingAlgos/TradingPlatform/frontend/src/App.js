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
  CircularProgress
} from '@mui/material';

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
