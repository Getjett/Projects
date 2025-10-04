import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const StrategyBuilder: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        Strategy Builder
      </Typography>
      <Paper sx={{ p: 3, mt: 2 }}>
        <Box sx={{ textAlign: 'center', py: 5 }}>
          <Typography variant="h6" color="text.secondary">
            🚧 Strategy Builder Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            This feature is under development. You'll be able to create custom trading strategies here.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default StrategyBuilder;
