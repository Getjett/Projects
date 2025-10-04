import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const PatternCreator: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        Pattern Creator
      </Typography>
      <Paper sx={{ p: 3, mt: 2 }}>
        <Box sx={{ textAlign: 'center', py: 5 }}>
          <Typography variant="h6" color="text.secondary">
            🎨 Pattern Creator Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Create custom candlestick patterns here.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default PatternCreator;
