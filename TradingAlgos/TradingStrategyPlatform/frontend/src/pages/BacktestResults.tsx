import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const BacktestResults: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        Backtest Results
      </Typography>
      <Paper sx={{ p: 3, mt: 2 }}>
        <Box sx={{ textAlign: 'center', py: 5 }}>
          <Typography variant="h6" color="text.secondary">
            📊 Backtest Results Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Run a backtest to see detailed results and analytics here.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default BacktestResults;
